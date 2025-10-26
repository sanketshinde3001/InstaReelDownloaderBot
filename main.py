import os
from dotenv import load_dotenv
import random
import subprocess
import logging
import json
import tempfile
import re
import time
from telegram import Update, InputMediaPhoto, Document
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

load_dotenv()


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class InstaReelBot:
    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.user_cookies = {}  # Store cookies per user ID
        
    def cleanup_old_cookies(self):
        """Clean up temporary cookie files"""
        try:
            for user_id, cookie_file in list(self.user_cookies.items()):
                if os.path.exists(cookie_file):
                    # Check if file is older than 24 hours
                    file_age = os.path.getmtime(cookie_file)
                    if (time.time() - file_age) > 86400:  # 24 hours
                        os.remove(cookie_file)
                        del self.user_cookies[user_id]
                        logger.info(f"Cleaned up old cookies for user {user_id}")
        except Exception as e:
            logger.error(f"Error cleaning up cookies: {str(e)}")
        
    def download_reel(self, url, user_id=None):
        """Download Instagram reel using yt-dlp with user cookies"""
        try:
            ydl_opts = {
                'format': 'best',
                'outtmpl': '%(id)s.%(ext)s',
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            # Add cookies if user has provided them
            if user_id and user_id in self.user_cookies:
                cookies_file = self.user_cookies[user_id]
                if os.path.exists(cookies_file):
                    ydl_opts['cookiefile'] = cookies_file
                    logger.info(f"Using cookies for user {user_id}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Try to extract username from URL first (most reliable)
                username = 'Unknown'
                
                # Method 1: Extract from URL
                try:
                    # Extract username from Instagram URL patterns
                    # URLs like: https://www.instagram.com/reel/ABC123/ or https://www.instagram.com/p/ABC123/
                    # or https://www.instagram.com/username/reel/ABC123/
                    url_pattern = r'instagram\.com/(?:([^/]+)/(?:reel|p)/[^/]+|reel/[^/?]+.*[\?&]taken-by=([^&]+))'
                    match = re.search(url_pattern, url)
                    if match:
                        extracted_username = match.group(1) or match.group(2)
                        if extracted_username and not extracted_username in ['reel', 'p', 'tv']:
                            username = extracted_username
                            logger.info(f"Username extracted from URL: {username}")
                except Exception as e:
                    logger.error(f"Error extracting username from URL: {e}")
                
                # Method 2: Try yt-dlp fields if URL extraction failed
                if username == 'Unknown':
                    # Check webpage_url or original_url for username
                    for url_field in ['webpage_url', 'original_url', 'url']:
                        if info.get(url_field):
                            try:
                                match = re.search(r'instagram\.com/([^/]+)/', info[url_field])
                                if match and match.group(1) not in ['reel', 'p', 'tv']:
                                    username = match.group(1)
                                    logger.info(f"Username found in {url_field}: {username}")
                                    break
                            except:
                                continue
                
                # Method 3: Try yt-dlp metadata fields (avoid numeric IDs)
                if username == 'Unknown':
                    for field in ['uploader', 'channel', 'creator', 'uploader_id']:
                        field_value = info.get(field)
                        if field_value and not field_value.isdigit() and len(field_value) > 2:
                            username = field_value
                            logger.info(f"Username from {field}: {username}")
                            break
                
                # Clean up username
                if username != 'Unknown':
                    # Remove @ if it already exists
                    username = username.lstrip('@')
                    # Replace spaces with underscores
                    username = username.replace(' ', '_')
                    # Remove invalid characters but keep letters, numbers, dots, underscores
                    username = re.sub(r'[^a-zA-Z0-9._]', '', username)
                    # Make sure it's not empty after cleaning
                    if not username:
                        username = 'Unknown'
                
                logger.info(f"Final username: {username}")
                
                return {
                    'video_file': f"{info['id']}.{info['ext']}",
                    'username': username,
                    'caption': info.get('description', 'No caption'),
                    'likes': info.get('like_count', 0),
                    'shortcode': info['id']
                }
        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            return None
    
    def check_ffmpeg_installed(self):
        """Check if FFmpeg is available"""
        try:
            # Check FFmpeg
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5, text=True)
            if result.returncode == 0:
                logger.info("FFmpeg check successful")
                # Also check ffprobe
                probe_result = subprocess.run(['ffprobe', '-version'], capture_output=True, timeout=5, text=True)
                if probe_result.returncode == 0:
                    logger.info("FFprobe check successful")
                    return True
                else:
                    logger.error("FFprobe not found")
                    return False
            else:
                logger.error(f"FFmpeg check failed with return code: {result.returncode}")
                logger.error(f"FFmpeg stderr: {result.stderr}")
                return False
        except FileNotFoundError as e:
            logger.error(f"FFmpeg not found in PATH: {e}")
            # Try to find ffmpeg in common locations
            common_paths = ['/usr/bin/ffmpeg', '/usr/local/bin/ffmpeg', '/opt/ffmpeg/bin/ffmpeg']
            for path in common_paths:
                if os.path.exists(path):
                    logger.info(f"Found FFmpeg at: {path}")
                    return True
            return False
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg version check timed out")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking FFmpeg: {e}")
            return False
    
    def generate_thumbnails(self, video_file, shortcode):
        """Generate 5 random thumbnails from video"""
        thumbnails = []
        
        # Check if FFmpeg is available
        if not self.check_ffmpeg_installed():
            logger.warning("FFmpeg not found - skipping thumbnail generation")
            return []
        
        try:
            # Get video duration
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
                 '-of', 'default=noprint_wrappers=1:nokey=1', video_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.error("FFprobe failed - video duration check failed")
                return []
                
            duration = float(result.stdout.strip())
            
            if duration < 2:
                logger.info("Video too short for thumbnails")
                return []
            
            # Generate 5 random timestamps
            num_thumbs = min(5, int(duration) - 1)
            if num_thumbs < 1:
                return []
                
            timestamps = sorted(random.sample(range(1, int(duration)), num_thumbs))
            
            for i, timestamp in enumerate(timestamps, 1):
                thumbnail_file = f"{shortcode}_thumb_{i}.jpg"
                
                result = subprocess.run([
                    'ffmpeg', '-ss', str(timestamp), '-i', video_file,
                    '-vframes', '1', '-q:v', '2', thumbnail_file, '-y'
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
                
                if result.returncode == 0 and os.path.exists(thumbnail_file):
                    thumbnails.append(thumbnail_file)
                    logger.info(f"Generated thumbnail {i}/{num_thumbs}")
            
        except FileNotFoundError:
            logger.error("FFmpeg not found in system PATH - install FFmpeg to enable thumbnails")
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg timeout - thumbnail generation took too long")
        except Exception as e:
            logger.error(f"Thumbnail generation error: {str(e)}")
        
        return thumbnails
    
    def validate_cookies(self, cookies_content):
        """Validate cookies.txt format"""
        try:
            lines = cookies_content.strip().split('\n')
            valid_lines = 0
            
            for line in lines:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                    
                # Netscape cookies format: domain, flag, path, secure, expiration, name, value
                parts = line.split('\t')
                if len(parts) >= 7:
                    # Check if it contains instagram.com
                    if 'instagram.com' in parts[0] or '.instagram.com' in parts[0]:
                        valid_lines += 1
                        
            return valid_lines > 0
            
        except Exception as e:
            logger.error(f"Cookie validation error: {str(e)}")
            return False
    
    def save_user_cookies(self, user_id, cookies_content):
        """Save cookies to a temporary file for the user"""
        try:
            # Create a temporary file for this user's cookies
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'_cookies_{user_id}.txt')
            temp_file.write(cookies_content)
            temp_file.close()
            
            # Store the file path
            self.user_cookies[user_id] = temp_file.name
            logger.info(f"Saved cookies for user {user_id}")
            
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Error saving cookies: {str(e)}")
            return None
    
    async def cookies_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cookies command"""
        help_text = """
**Cookie Authentication Setup**

To bypass Instagram rate limits, you need to provide your browser cookies:

**How to get cookies.txt:**

1**Chrome/Edge:**
   • Install "Get cookies.txt LOCALLY" extension
   • Go to instagram.com and login
   • Click the extension → Export → instagram.com
   • Save as `cookies.txt`

2️**Firefox:**
   • Install "cookies.txt" add-on
   • Visit instagram.com (logged in)
   • Click add-on → Export cookies.txt

3️**Manual Method:**
   • Open Developer Tools (F12)
   • Go to Application/Storage → Cookies → instagram.com
   • Copy all cookie data

**Then send the cookies.txt file to this chat!**

**Important:** Only share cookies with trusted bots. Cookies contain login information.

**Send your cookies.txt file now, or use /start to go back**
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle uploaded documents (cookies.txt files)"""
        try:
            document = update.message.document
            user_id = update.message.from_user.id
            
            # Check if it's likely a cookies file
            if document.file_name and ('cookie' in document.file_name.lower() or document.file_name.endswith('.txt')):
                
                processing_msg = await update.message.reply_text("Processing your cookies file...")
                
                # Download the file
                file = await context.bot.get_file(document.file_id)
                file_content = await file.download_as_bytearray()
                cookies_text = file_content.decode('utf-8')
                
                # Validate cookies
                if self.validate_cookies(cookies_text):
                    # Save cookies for this user
                    cookies_file = self.save_user_cookies(user_id, cookies_text)
                    
                    if cookies_file:
                        await processing_msg.edit_text(
                            "**Cookies successfully uploaded and validated!**\n\n"
                            " Your Instagram downloads should now work without rate limits!\n"
                            "Cookies are stored securely and only used for your downloads.\n\n"
                            "Try downloading a reel now: `/reel [instagram_url]`",
                            parse_mode='Markdown'
                        )
                    else:
                        await processing_msg.edit_text(" Error saving cookies. Please try again.")
                else:
                    await processing_msg.edit_text(
                        " **Invalid cookies file!**\n\n"
                        "Please make sure:\n"
                        "• File contains Instagram cookies\n"
                        "• You're logged into Instagram when exporting\n"
                        "• Using Netscape cookies.txt format\n\n"
                        "Use `/cookies` for detailed instructions."
                    )
            else:
                await update.message.reply_text(
                    "Please send a cookies.txt file.\n"
                    "Use `/cookies` for instructions on how to get your cookies."
                )
                
        except Exception as e:
            logger.error(f"Error handling document: {str(e)}")
            await update.message.reply_text(
                " Error processing file. Please make sure it's a valid text file and try again."
            )
    
    async def cookie_status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check cookie status for user"""
        user_id = update.message.from_user.id
        
        if user_id in self.user_cookies and os.path.exists(self.user_cookies[user_id]):
            await update.message.reply_text(
                "**Cookies Active**\n\n"
                "Your authentication cookies are loaded and working.\n"
                "You can download Instagram content without rate limits!\n\n"
                "To update cookies, just send a new cookies.txt file.",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                " **No Cookies Found**\n\n"
                "You haven't uploaded authentication cookies yet.\n\n"
                "Use `/cookies` to setup authentication and avoid rate limits.",
                parse_mode='Markdown'
            )
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
**Instagram Reel Downloader Bot**

📌 **How to use:**
Send me an Instagram Reel link:
`/reel https://www.instagram.com/reel/xxxxx/`

**I will send you:**
• Account username  
• Full caption
• High quality video
• 5 random thumbnails

**Important for unlimited downloads:**
Use `/cookies` to setup authentication and avoid rate limits!

**Commands:**
• `/reel [url]` - Download Instagram reel
• `/cookies` - Setup authentication cookies
• `/help` - Show detailed help

**Ready to download!**
"""
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def reel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /reel command with URL"""
        video_file = None
        thumbnails = []
        
        try:
            if not context.args:
                await update.message.reply_text(
                    " Please provide an Instagram Reel URL!\n\n"
                    "Usage: `/reel https://www.instagram.com/reel/xxxxx/`",
                    parse_mode='Markdown'
                )
                return
            
            url = context.args[0]
            
            if 'instagram.com' not in url:
                await update.message.reply_text(" Please provide a valid Instagram URL.")
                return
            
            processing_msg = await update.message.reply_text("⏳ Processing your reel... This may take a moment.")
            
            # Download reel
            user_id = update.message.from_user.id
            result = self.download_reel(url, user_id)
            
            if not result:
                # Check if user has cookies
                if user_id not in self.user_cookies:
                    await processing_msg.edit_text(
                        " **Download Failed - Authentication Required**\n\n"
                        "Instagram requires login cookies to download content.\n\n"
                        "**Setup cookies to fix this:**\n"
                        "Use `/cookies` command for detailed instructions.\n\n"
                        "This will allow unlimited downloads without rate limits!",
                        parse_mode='Markdown'
                    )
                else:
                    await processing_msg.edit_text(" Failed to download. The reel might be private or the link is invalid.")
                return
            
            video_file = result['video_file']
            username = result['username']
            caption = result['caption']
            likes = result['likes']
            shortcode = result['shortcode']
            
            # Send info
            info_message = f"""
**Reel Found!**

👤 **Account:** @{username}
❤️ **Likes:** {likes:,}

📝 **Caption:**
{caption[:800]}{"..." if len(caption) > 800 else ""}

⬇️ Sending video...
"""
            await processing_msg.edit_text(info_message, parse_mode='Markdown')
            
            # Send video
            if os.path.exists(video_file):
                with open(video_file, 'rb') as video:
                    await update.message.reply_video(
                        video=video,
                        caption=f"🎥 **@{username}**\n\n{caption[:200]}{'...' if len(caption) > 200 else ''}",
                        parse_mode='Markdown',
                        supports_streaming=True
                    )
            
            # Generate thumbnails
            thumbnail_msg = await update.message.reply_text("🖼️ Generating thumbnails...")
            thumbnails = self.generate_thumbnails(video_file, shortcode)
            
            if thumbnails:
                media_group = []
                for i, thumb in enumerate(thumbnails[:5], 1):
                    with open(thumb, 'rb') as photo:
                        media_group.append(InputMediaPhoto(
                            media=photo.read(),
                            caption=f"📸 Thumbnail {i}/{len(thumbnails)}" if i == 1 else ""
                        ))
                
                await thumbnail_msg.delete()  # Remove the "generating" message
                await update.message.reply_media_group(media=media_group)
            else:
                await thumbnail_msg.edit_text(
                    "⚠️ **Thumbnails not available**\n\n"
                    "FFmpeg is not installed on the server.\n"
                    "Video downloaded successfully! \n\n"
                    "ℹ️ *Thumbnails require FFmpeg for video processing*"
                )
            
            await update.message.reply_text("Done! Enjoy your reel! ")
            
        except Exception as e:
            logger.error(f"Error in reel_command: {str(e)}")
            error_message = f" Error: Something went wrong. Please try again or check if the reel is public."
            try:
                await update.message.reply_text(error_message)
            except:
                pass
        
        finally:
            # Cleanup files
            try:
                if video_file and os.path.exists(video_file):
                    os.remove(video_file)
                for thumb in thumbnails:
                    if os.path.exists(thumb):
                        os.remove(thumb)
            except Exception as e:
                logger.error(f"Cleanup error: {str(e)}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
**Help - How to Use**

**Basic Usage:**
1️⃣ Copy an Instagram Reel link
2️⃣ Send: `/reel [paste link here]`
3️⃣ Wait for processing (10-30 seconds)
4️⃣ Receive video + thumbnails!

**Example:**
`/reel https://www.instagram.com/reel/ABC123xyz/`

**For Unlimited Downloads:**
Instagram rate-limits downloads. To avoid this:
• Use `/cookies` command
• Upload your browser cookies.txt file
• Enjoy unlimited, faster downloads!

**Commands:**
• `/start` - Welcome message
• `/reel [url]` - Download reel/post
• `/cookies` - Setup authentication
• `/cookiestatus` - Check cookie status
• `/help` - This help message

**Supported formats:**
• /reel/xxxxx/
• /p/xxxxx/
• Short links (instagr.am)

**Note:** Public reels work best. Private content requires cookies.
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log the error and send a message to the user if possible"""
        logger.error(f"Exception while handling an update: {context.error}")
        
        # Try to send error message to user if update has message
        if update and hasattr(update, 'effective_chat') and update.effective_chat:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=" Sorry, something went wrong. Please try again later."
                )
            except Exception as e:
                logger.error(f"Could not send error message to user: {e}")
    

    def run(self):
        """Run the bot"""
        try:
            logger.info("Starting Instagram Reel Downloader Bot...")
            
            # Check FFmpeg availability
            if self.check_ffmpeg_installed():
                logger.info("FFmpeg found - thumbnails will be available")
            else:
                logger.warning("FFmpeg not found - thumbnails will be disabled")
            
            # Clean up old cookies on startup
            self.cleanup_old_cookies()
            
            app = Application.builder().token(self.bot_token).build()
            
            # Add error handler
            app.add_error_handler(self.error_handler)
            
            app.add_handler(CommandHandler("start", self.start_command))
            app.add_handler(CommandHandler("reel", self.reel_command))
            app.add_handler(CommandHandler("cookies", self.cookies_command))
            app.add_handler(CommandHandler("cookiestatus", self.cookie_status_command))
            app.add_handler(CommandHandler("help", self.help_command))
            
            # Handle document uploads (cookies.txt files)
            app.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
            
            logger.info("Bot is running and ready to download Instagram reels!")
            
            # Check if we're on Render (webhook mode) or local (polling mode)
            port = os.getenv('PORT')
            
            # Auto-detect webhook URL from Render environment
            render_service_name = os.getenv('RENDER_SERVICE_NAME')
            webhook_url = os.getenv('WEBHOOK_URL')
            
            if not webhook_url and render_service_name:
                # Auto-generate webhook URL for Render
                webhook_url = f"https://{render_service_name}.onrender.com"
                logger.info(f"🔍 Auto-detected webhook URL: {webhook_url}")
            
            if port and webhook_url:
                # Webhook mode for production (Render)
                logger.info("🌐 Running in webhook mode for production")
                
                # Use telegram-bot's native webhook server - NO FLASK!
                app.run_webhook(
                    listen="0.0.0.0",
                    port=int(port),
                    url_path="/webhook",
                    webhook_url=f"{webhook_url}/webhook",
                    drop_pending_updates=True,
                    allowed_updates=Update.ALL_TYPES
                )
            else:
                # Polling mode for local development
                logger.info("Running in polling mode for development")
                
                # Run with conflict resolution
                app.run_polling(
                    allowed_updates=Update.ALL_TYPES,
                    drop_pending_updates=True,  # Clear any pending updates
                    timeout=30,
                    read_timeout=30,
                    write_timeout=30,
                    connect_timeout=30
                )
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            raise


if __name__ == "__main__":
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    if not BOT_TOKEN:
        raise ValueError(" BOT_TOKEN environment variable not set!")
    
    bot = InstaReelBot(BOT_TOKEN)
    bot.run()
