import os
import logging
from dotenv import load_dotenv
from bot.telegram_bot import SpotifyDownloaderBot
from keep_alive import keep_alive

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Main function to start the bot"""
    try:
        # Start the keep-alive server
        logger.info("Starting keep-alive server...")
        keep_alive()
        
        # Get bot token from environment
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        
        # Clear any existing webhooks and pending updates
        import requests
        import time
        
        # First, delete webhook with pending updates
        webhook_url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook?drop_pending_updates=true"
        response = requests.post(webhook_url)
        logger.info(f"Webhook deletion response: {response.json()}")
        
        # Wait longer for cleanup to ensure no conflicts
        logger.info("Waiting for cleanup to complete...")
        time.sleep(5)
        
        # Try to clear any remaining updates
        try:
            get_updates_url = f"https://api.telegram.org/bot{bot_token}/getUpdates?offset=-1"
            requests.post(get_updates_url, timeout=10)
            logger.info("Cleared any remaining updates")
        except Exception as e:
            logger.warning(f"Could not clear updates: {e}")
        
        time.sleep(2)
        
        # Initialize and start the bot
        logger.info("Initializing Spotify Downloader Bot...")
        bot = SpotifyDownloaderBot(bot_token)
        
        logger.info("Starting bot polling...")
        bot.start_polling()
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == '__main__':
    main()
