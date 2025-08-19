from flask import Flask
import threading
import time
import logging
import os

logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    """Health check endpoint"""
    return """
    <html>
        <head>
            <title>Spotify Downloader Bot</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #1DB954; color: white; }
                .container { max-width: 600px; margin: 0 auto; text-align: center; }
                .status { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎵 Spotify Downloader Bot</h1>
                <div class="status">
                    <h2>✅ Bot is running successfully!</h2>
                    <p>Your Telegram bot is active and ready to download music.</p>
                </div>
            </div>
        </body>
    </html>
    """

@app.route('/health')
def health():
    """Simple health check"""
    return {"status": "healthy", "service": "spotify-downloader-bot"}

def run_flask():
    """Run Flask server in a separate thread"""
    try:
        # Use PORT environment variable for Render, fallback to 8080 for local
        port = int(os.environ.get('PORT', 8080))
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Flask server error: {e}")

def keep_alive():
    """Start the Flask server to keep the bot alive"""
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting Flask keep-alive server on port {port}...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    time.sleep(2)  # Give the server time to start
    logger.info("Keep-alive server started successfully")
