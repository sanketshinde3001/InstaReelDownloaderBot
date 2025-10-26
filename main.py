import os
from dotenv import load_dotenv
import random
import subprocess
import logging
import json
from telegram import Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, ContextTypes
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
        
    def download_reel(self, url):
        """Download Instagram reel using yt-dlp"""
        try:
            ydl_opts = {
                'format': 'best',
                'outtmpl': '%(id)s.%(ext)s',
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                return {
                    'video_file': f"{info['id']}.{info['ext']}",
                    'username': info.get('uploader', 'Unknown'),
                    'caption': info.get('description', 'No caption'),
                    'likes': info.get('like_count', 0),
                    'shortcode': info['id']
                }
        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            return None
    
    def generate_thumbnails(self, video_file, shortcode):
        """Generate 5 random thumbnails from video"""
        thumbnails = []
        
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
                logger.error("FFprobe failed")
                return []
                
            duration = float(result.stdout.strip())
            
            if duration < 2:
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
                ], capture_output=True, stderr=subprocess.DEVNULL, timeout=10)
                
                if result.returncode == 0 and os.path.exists(thumbnail_file):
                    thumbnails.append(thumbnail_file)
            
        except Exception as e:
            logger.error(f"Thumbnail error: {str(e)}")
        
        return thumbnails
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 **Instagram Reel Downloader Bot**

📌 **How to use:**
Send me an Instagram Reel link:
`/reel https://www.instagram.com/reel/xxxxx/`

✨ **I will send you:**
• Account username
• Full caption
• High quality video
• 5 random thumbnails

🚀 **Ready to download!**
"""
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def reel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /reel command with URL"""
        video_file = None
        thumbnails = []
        
        try:
            if not context.args:
                await update.message.reply_text(
                    "❌ Please provide an Instagram Reel URL!\n\n"
                    "Usage: `/reel https://www.instagram.com/reel/xxxxx/`",
                    parse_mode='Markdown'
                )
                return
            
            url = context.args[0]
            
            if 'instagram.com' not in url:
                await update.message.reply_text("❌ Please provide a valid Instagram URL.")
                return
            
            processing_msg = await update.message.reply_text("⏳ Processing your reel... This may take a moment.")
            
            # Download reel
            result = self.download_reel(url)
            
            if not result:
                await processing_msg.edit_text("❌ Failed to download. The reel might be private or the link is invalid.")
                return
            
            video_file = result['video_file']
            username = result['username']
            caption = result['caption']
            likes = result['likes']
            shortcode = result['shortcode']
            
            # Send info
            info_message = f"""
✅ **Reel Found!**

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
            await update.message.reply_text("🖼️ Generating thumbnails...")
            thumbnails = self.generate_thumbnails(video_file, shortcode)
            
            if thumbnails:
                media_group = []
                for i, thumb in enumerate(thumbnails[:5], 1):
                    with open(thumb, 'rb') as photo:
                        media_group.append(InputMediaPhoto(
                            media=photo.read(),
                            caption=f"📸 Thumbnail {i}/{len(thumbnails)}" if i == 1 else ""
                        ))
                
                await update.message.reply_media_group(media=media_group)
            else:
                await update.message.reply_text("⚠️ Could not generate thumbnails, but video sent successfully!")
            
            await update.message.reply_text("✅ Done! Enjoy your reel! 🎉")
            
        except Exception as e:
            logger.error(f"Error in reel_command: {str(e)}")
            error_message = f"❌ Error: Something went wrong. Please try again or check if the reel is public."
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
📖 **Help - How to Use**

1️⃣ Copy an Instagram Reel link
2️⃣ Send: `/reel [paste link here]`
3️⃣ Wait for processing (10-30 seconds)
4️⃣ Receive video + thumbnails!

**Example:**
`/reel https://www.instagram.com/reel/ABC123xyz/`

**Note:** Only public reels can be downloaded.

**Supported formats:**
• /reel/xxxxx/
• /p/xxxxx/
• Short links (instagr.am)
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    def run(self):
        """Run the bot"""
        logger.info("🤖 Starting Telegram Bot...")
        
        app = Application.builder().token(self.bot_token).build()
        
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("reel", self.reel_command))
        app.add_handler(CommandHandler("help", self.help_command))
        
        logger.info("✅ Bot is running!")
        
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN environment variable not set!")
    
    bot = InstaReelBot(BOT_TOKEN)
    bot.run()
