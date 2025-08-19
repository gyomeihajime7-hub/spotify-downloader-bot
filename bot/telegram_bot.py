import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from bot.spotify_handler import SpotifyHandler
from bot.simple_youtube_downloader import SimpleYouTubeDownloader
from bot.demo_songs import DemoSongs
from utils.helpers import is_spotify_link, format_duration, clean_filename
import asyncio
import os

logger = logging.getLogger(__name__)

class SpotifyDownloaderBot:
    def __init__(self, token):
        self.token = token
        self.spotify_handler = SpotifyHandler()
        self.audio_downloader = SimpleYouTubeDownloader()
        self.demo_songs = DemoSongs()
        self.app = Application.builder().token(token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup bot command and message handlers"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
        logger.info("Bot handlers setup completed")

    def start_polling(self):
        """Start the bot polling"""
        logger.info("Bot started polling...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        if not update.message:
            return
            
        keyboard = [
            [InlineKeyboardButton("🎵 Try Demo Songs", callback_data="demo_songs")],
            [InlineKeyboardButton("❓ Help & Instructions", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_message = """
🎵 *Welcome to Spotify Music Downloader Bot!* 🎵

Hey there! I'm your personal music assistant! 🤖✨

*What can I do?*
• 📱 Download songs from Spotify links
• 📀 Process entire albums and playlists
• 🎛️ Choose audio quality before download
• 🎧 Find music from multiple sources

*How to use:*
1️⃣ Send me any Spotify link (song/album/playlist)
2️⃣ Choose your preferred audio quality
3️⃣ Get your music instantly! 🚀

Ready to discover some music? Try the demo below! 👇
        """
        
        await update.message.reply_text(
            welcome_message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        if not update.message:
            return
            
        help_text = """
🆘 *Help & Instructions* 🆘

*Supported Links:*
• 🎵 Spotify Songs: `open.spotify.com/track/...`
• 📀 Spotify Albums: `open.spotify.com/album/...`
• 📋 Spotify Playlists: `open.spotify.com/playlist/...`

*How it works:*
1️⃣ Send me a Spotify link
2️⃣ I'll extract the metadata
3️⃣ Choose your preferred quality
4️⃣ I'll find and download the audio
5️⃣ Enjoy your music! 🎊

*Quality Options:*
• 🔥 High Quality (320kbps)
• ⚡ Medium Quality (192kbps)
• 📱 Low Quality (128kbps)

*Tips:*
• Use /start to return to main menu
• Try demo songs to test the bot
• Be patient for large playlists! ⏳

Need more help? Just ask! 😊
        """
        
        keyboard = [
            [InlineKeyboardButton("🏠 Back to Start", callback_data="back_start")],
            [InlineKeyboardButton("🎵 Try Demo", callback_data="demo_songs")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            help_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        if not update.message or not update.message.text:
            return
            
        message_text = update.message.text.strip()
        
        if is_spotify_link(message_text):
            await self.process_spotify_link(update, context, message_text)
        else:
            await update.message.reply_text(
                "🤔 That doesn't look like a Spotify link!\n\n"
                "Please send me a valid Spotify link:\n"
                "• 🎵 Song: `open.spotify.com/track/...`\n"
                "• 📀 Album: `open.spotify.com/album/...`\n"
                "• 📋 Playlist: `open.spotify.com/playlist/...`\n\n"
                "Or try our demo songs! 👇",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🎵 Try Demo Songs", callback_data="demo_songs")
                ]])
            )

    async def process_spotify_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE, spotify_url):
        """Process Spotify link and show quality options"""
        if not update.message:
            return
            
        processing_msg = await update.message.reply_text("🔍 *Analyzing Spotify link...*", parse_mode='Markdown')
        
        try:
            # Validate Spotify URL format first
            content_type, spotify_id = self.spotify_handler.extract_spotify_id(spotify_url)
            if not content_type or not spotify_id:
                await processing_msg.edit_text(
                    "❌ *Invalid Spotify Link*\n\n"
                    "Please send a valid Spotify link:\n"
                    "• 🎵 Songs: `open.spotify.com/track/...`\n"
                    "• 📀 Albums: `open.spotify.com/album/...`\n"
                    "• 📋 Playlists: `open.spotify.com/playlist/...`",
                    parse_mode='Markdown'
                )
                return
            
            # Extract metadata from Spotify
            metadata = await self.spotify_handler.get_metadata(spotify_url)
            
            if not metadata:
                await processing_msg.edit_text(
                    "❌ *Could not fetch metadata*\n\n"
                    "This could happen if:\n"
                    "• The track/album/playlist doesn't exist\n"
                    "• The link is from a different region\n"
                    "• Spotify is temporarily unavailable\n\n"
                    "Please try another link or try again later.",
                    parse_mode='Markdown'
                )
                return
            
            # Store metadata in context for later use
            if context.user_data is not None:
                context.user_data['metadata'] = metadata
                context.user_data['spotify_url'] = spotify_url
            
            # Create quality selection keyboard
            keyboard = [
                [InlineKeyboardButton("🔥 High Quality (320kbps)", callback_data="quality_high")],
                [InlineKeyboardButton("⚡ Medium Quality (192kbps)", callback_data="quality_medium")],
                [InlineKeyboardButton("📱 Low Quality (128kbps)", callback_data="quality_low")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Format metadata message
            if metadata['type'] == 'track':
                info_text = f"""
🎵 *Found Track:*
*Title:* {metadata['name']}
*Artist:* {metadata['artists']}
*Duration:* {format_duration(metadata.get('duration_ms', 0))}
*Album:* {metadata.get('album', 'Unknown')}

Please select your preferred audio quality:
                """
            elif metadata['type'] == 'album':
                info_text = f"""
📀 *Found Album:*
*Title:* {metadata['name']}
*Artist:* {metadata['artists']}
*Tracks:* {metadata.get('total_tracks', 0)} songs
*Release Date:* {metadata.get('release_date', 'Unknown')}

Please select your preferred audio quality:
                """
            else:  # playlist
                info_text = f"""
📋 *Found Playlist:*
*Title:* {metadata['name']}
*Owner:* {metadata.get('owner', 'Unknown')}
*Tracks:* {metadata.get('total_tracks', 0)} songs
*Description:* {metadata.get('description', 'No description')}

Please select your preferred audio quality:
                """
            
            await processing_msg.edit_text(
                info_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error processing Spotify link: {e}")
            await processing_msg.edit_text(
                f"❌ *Error processing link:* {str(e)}\n\n"
                "Please try again with a valid Spotify link.",
                parse_mode='Markdown'
            )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        if not query:
            return
            
        await query.answer()
        
        if query.data == "demo_songs":
            await self.show_demo_songs(query, context)
        elif query.data == "help":
            await self.show_help(query, context)
        elif query.data == "back_start":
            await self.show_start_menu(query, context)
        elif query.data and query.data.startswith("demo_"):
            await self.process_demo_song(query, context)
        elif query.data and query.data.startswith("quality_"):
            await self.process_quality_selection(query, context)
        elif query.data == "cancel":
            await query.edit_message_text("❌ Operation cancelled.")

    async def show_demo_songs(self, query, context):
        """Show demo songs selection"""
        demo_tracks = self.demo_songs.get_random_tracks(6)
        
        keyboard = []
        for i, track in enumerate(demo_tracks):
            keyboard.append([InlineKeyboardButton(
                f"🎵 {track['name']} - {track['artist']}", 
                callback_data=f"demo_{i}"
            )])
        
        keyboard.append([InlineKeyboardButton("🔄 More Songs", callback_data="demo_songs")])
        keyboard.append([InlineKeyboardButton("🏠 Back to Start", callback_data="back_start")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Store demo tracks in context
        context.user_data['demo_tracks'] = demo_tracks
        
        await query.edit_message_text(
            """
🎵 *Demo Songs - Try These Popular Tracks!* 🎵

Select any song below to test the bot:
👇 *Click to download:*
            """,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    async def process_demo_song(self, query, context):
        """Process selected demo song"""
        try:
            demo_index = int(query.data.split("_")[1])
            demo_tracks = context.user_data.get('demo_tracks', [])
            
            if demo_index < len(demo_tracks):
                selected_track = demo_tracks[demo_index]
                spotify_url = selected_track['spotify_url']
                
                # Process the demo track
                await query.edit_message_text("🔍 *Processing demo track...*", parse_mode='Markdown')
                await self.process_spotify_link_direct(query, context, spotify_url)
            
        except Exception as e:
            logger.error(f"Error processing demo song: {e}")
            await query.edit_message_text(f"❌ Error processing demo song: {str(e)}")

    async def process_spotify_link_direct(self, query, context, spotify_url):
        """Process Spotify link directly for demo songs"""
        try:
            metadata = await self.spotify_handler.get_metadata(spotify_url)
            
            if not metadata:
                await query.edit_message_text("❌ Could not fetch metadata for demo track.")
                return
            
            context.user_data['metadata'] = metadata
            context.user_data['spotify_url'] = spotify_url
            
            # Auto-select medium quality for demo
            await self.download_and_send(query, context, 'medium')
            
        except Exception as e:
            logger.error(f"Error processing demo link: {e}")
            await query.edit_message_text(f"❌ Error: {str(e)}")

    async def process_quality_selection(self, query, context):
        """Process quality selection and start download"""
        quality = query.data.split("_")[1]  # high, medium, low
        await self.download_and_send(query, context, quality)

    async def download_and_send(self, query, context, quality):
        """Download and send audio file"""
        metadata = context.user_data.get('metadata')
        
        if not metadata:
            await query.edit_message_text("❌ No metadata found. Please try again.")
            return
        
        try:
            if metadata['type'] == 'track':
                await self.download_single_track(query, context, metadata, quality)
            elif metadata['type'] == 'album':
                await self.download_album(query, context, metadata, quality)
            else:  # playlist
                await self.download_playlist(query, context, metadata, quality)
                
        except Exception as e:
            logger.error(f"Error in download_and_send: {e}")
            await query.edit_message_text(f"❌ Download failed: {str(e)}")

    async def download_single_track(self, query, context, metadata, quality):
        """Download a single track"""
        await query.edit_message_text("🎵 *Please wait, your music is being processed...*\n⏳ *This may take 30-60 seconds*", parse_mode='Markdown')
        
        try:
            # Search and download the track
            audio_file = await self.audio_downloader.download_track(metadata, quality)
            
            if audio_file and os.path.exists(audio_file):
                await query.edit_message_text("📤 *Uploading your song...*", parse_mode='Markdown')
                
                # Get album artwork for thumbnail
                thumbnail_data = None
                if metadata.get('album_art_url'):
                    try:
                        import requests
                        logger.info("📸 Fetching album artwork...")
                        response = requests.get(metadata['album_art_url'], timeout=5)
                        if response.status_code == 200:
                            thumbnail_data = response.content
                            logger.info("✅ Album artwork loaded")
                    except Exception as e:
                        logger.warning(f"⚠️ Could not load album artwork: {e}")
                
                # Send the audio file with thumbnail
                with open(audio_file, 'rb') as audio:
                    await context.bot.send_audio(
                        chat_id=query.message.chat_id,
                        audio=audio,
                        thumbnail=thumbnail_data,
                        title=metadata['name'],
                        performer=metadata['artists'],
                        duration=metadata.get('duration_ms', 0) // 1000,
                        caption=f"🎵 *{metadata['name']}*\n👤 *{metadata['artists']}*\n📀 *{metadata.get('album', 'Unknown')}*",
                        parse_mode='Markdown'
                    )
                
                await query.edit_message_text(
                    f"✅ *Download Complete!*\n\n"
                    f"🎵 *Track:* {metadata['name']}\n"
                    f"👤 *Artist:* {metadata['artists']}\n"
                    f"🔊 *Quality:* {quality.title()}\n\n"
                    f"Enjoy your music! 🎶",
                    parse_mode='Markdown'
                )
                
                # Clean up the file
                try:
                    os.remove(audio_file)
                except:
                    pass
            else:
                await query.edit_message_text(
                    "❌ *Download Failed*\n\n"
                    "Could not find or download this track from available sources.\n"
                    "Please try another song or check if the link is valid.",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"Error downloading track: {e}")
            await query.edit_message_text(f"❌ Download error: {str(e)}")

    async def download_album(self, query, context, metadata, quality):
        """Download an album"""
        await query.edit_message_text("📀 *Processing album...*", parse_mode='Markdown')
        
        try:
            tracks = metadata.get('tracks', [])
            total_tracks = len(tracks)
            
            if total_tracks == 0:
                await query.edit_message_text("❌ No tracks found in this album.")
                return
            
            successful_downloads = 0
            
            for i, track in enumerate(tracks, 1):
                await query.edit_message_text(
                    f"⬬ *Downloading Album...*\n\n"
                    f"📀 *{metadata['name']}*\n"
                    f"🎵 Processing: {track['name']}\n"
                    f"📊 Progress: {i}/{total_tracks}",
                    parse_mode='Markdown'
                )
                
                try:
                    audio_file = await self.audio_downloader.download_track(track, quality)
                    
                    if audio_file and os.path.exists(audio_file):
                        with open(audio_file, 'rb') as audio:
                            await context.bot.send_audio(
                                chat_id=query.message.chat_id,
                                audio=audio,
                                title=track['name'],
                                performer=track['artists'],
                                caption=f"🎵 {track['name']} - {track['artists']}\n📀 {metadata['name']}",
                                parse_mode='Markdown'
                            )
                        
                        successful_downloads += 1
                        
                        try:
                            os.remove(audio_file)
                        except:
                            pass
                
                except Exception as e:
                    logger.error(f"Error downloading track {track['name']}: {e}")
                    continue
            
            await query.edit_message_text(
                f"✅ *Album Download Complete!*\n\n"
                f"📀 *Album:* {metadata['name']}\n"
                f"👤 *Artist:* {metadata['artists']}\n"
                f"📊 *Downloaded:* {successful_downloads}/{total_tracks} tracks\n"
                f"🔊 *Quality:* {quality.title()}\n\n"
                f"Enjoy your music! 🎶",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error downloading album: {e}")
            await query.edit_message_text(f"❌ Album download error: {str(e)}")

    async def download_playlist(self, query, context, metadata, quality):
        """Download a playlist"""
        await query.edit_message_text("📋 *Processing playlist...*", parse_mode='Markdown')
        
        try:
            tracks = metadata.get('tracks', [])
            total_tracks = len(tracks)
            
            if total_tracks == 0:
                await query.edit_message_text("❌ No tracks found in this playlist.")
                return
            
            # Limit playlist size to prevent spam
            if total_tracks > 50:
                await query.edit_message_text(
                    f"⚠️ *Large Playlist Detected*\n\n"
                    f"This playlist has {total_tracks} tracks.\n"
                    f"To prevent spam, I'll download the first 50 tracks.\n\n"
                    f"Processing first 50 tracks...",
                    parse_mode='Markdown'
                )
                tracks = tracks[:50]
                total_tracks = 50
            
            successful_downloads = 0
            
            for i, track in enumerate(tracks, 1):
                await query.edit_message_text(
                    f"⬬ *Downloading Playlist...*\n\n"
                    f"📋 *{metadata['name']}*\n"
                    f"🎵 Processing: {track['name']}\n"
                    f"📊 Progress: {i}/{total_tracks}",
                    parse_mode='Markdown'
                )
                
                try:
                    audio_file = await self.audio_downloader.download_track(track, quality)
                    
                    if audio_file and os.path.exists(audio_file):
                        with open(audio_file, 'rb') as audio:
                            await context.bot.send_audio(
                                chat_id=query.message.chat_id,
                                audio=audio,
                                title=track['name'],
                                performer=track['artists'],
                                caption=f"🎵 {track['name']} - {track['artists']}\n📋 {metadata['name']}",
                                parse_mode='Markdown'
                            )
                        
                        successful_downloads += 1
                        
                        try:
                            os.remove(audio_file)
                        except:
                            pass
                
                except Exception as e:
                    logger.error(f"Error downloading track {track['name']}: {e}")
                    continue
            
            await query.edit_message_text(
                f"✅ *Playlist Download Complete!*\n\n"
                f"📋 *Playlist:* {metadata['name']}\n"
                f"📊 *Downloaded:* {successful_downloads}/{total_tracks} tracks\n"
                f"🔊 *Quality:* {quality.title()}\n\n"
                f"Enjoy your music! 🎶",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error downloading playlist: {e}")
            await query.edit_message_text(f"❌ Playlist download error: {str(e)}")

    async def show_help(self, query, context):
        """Show help message"""
        help_text = """
🆘 *Help & Instructions* 🆘

*Supported Links:*
• 🎵 Spotify Songs: `open.spotify.com/track/...`
• 📀 Spotify Albums: `open.spotify.com/album/...`
• 📋 Spotify Playlists: `open.spotify.com/playlist/...`

*How it works:*
1️⃣ Send me a Spotify link
2️⃣ I'll extract the metadata
3️⃣ Choose your preferred quality
4️⃣ I'll find and download the audio
5️⃣ Enjoy your music! 🎊

*Quality Options:*
• 🔥 High Quality (320kbps)
• ⚡ Medium Quality (192kbps)
• 📱 Low Quality (128kbps)

*Tips:*
• Use /start to return to main menu
• Try demo songs to test the bot
• Be patient for large playlists! ⏳

Need more help? Just ask! 😊
        """
        
        keyboard = [
            [InlineKeyboardButton("🏠 Back to Start", callback_data="back_start")],
            [InlineKeyboardButton("🎵 Try Demo", callback_data="demo_songs")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            help_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    async def show_start_menu(self, query, context):
        """Show start menu"""
        keyboard = [
            [InlineKeyboardButton("🎵 Try Demo Songs", callback_data="demo_songs")],
            [InlineKeyboardButton("❓ Help & Instructions", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_message = """
🎵 *Welcome to Spotify Music Downloader Bot!* 🎵

Hey there! I'm your personal music assistant! 🤖✨

*What can I do?*
• 📱 Download songs from Spotify links
• 📀 Process entire albums and playlists
• 🎛️ Choose audio quality before download
• 🎧 Find music from multiple sources

*How to use:*
1️⃣ Send me any Spotify link (song/album/playlist)
2️⃣ Choose your preferred audio quality
3️⃣ Get your music instantly! 🚀

Ready to discover some music? Try the demo below! 👇
        """
        
        await query.edit_message_text(
            welcome_message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

