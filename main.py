import os
from dotenv import load_dotenv
import random
import subprocess
import urllib.request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import instaloader
import asyncio

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

class InstaReelBot:
    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.L = instaloader.Instaloader(
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            post_metadata_txt_pattern=''
        )
        
    def extract_shortcode(self, url):
        """Extract shortcode from Instagram URL"""
        if 'instagram.com' not in url:
            return None
        
        if '/reel/' in url:
            shortcode = url.split('/reel/')[1].split('/')[0].split('?')[0]
        elif '/p/' in url:
            shortcode = url.split('/p/')[1].split('/')[0].split('?')[0]
        else:
            return None
        
        return shortcode
    
    def generate_thumbnails(self, video_file, shortcode):
        """Generate 5 random thumbnails from video"""
        thumbnails = []
        
        try:
            # Get video duration
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
                 '-of', 'default=noprint_wrappers=1:nokey=1', video_file],
                capture_output=True,
                text=True
            )
            duration = float(result.stdout.strip())
            
            # Generate 5 random timestamps
            timestamps = sorted(random.sample(range(1, int(duration)), min(5, int(duration)-1)))
            
            for i, timestamp in enumerate(timestamps, 1):
                thumbnail_file = f"{shortcode}_thumb_{i}.jpg"
                
                subprocess.run([
                    'ffmpeg', '-ss', str(timestamp), '-i', video_file,
                    '-vframes', '1', '-q:v', '2', thumbnail_file, '-y'
                ], capture_output=True, stderr=subprocess.DEVNULL)
                
                if os.path.exists(thumbnail_file):
                    thumbnails.append(thumbnail_file)
            
        except Exception as e:
            print(f"Thumbnail error: {str(e)}")
        
        return thumbnails
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
**Instagram Reel Downloader Bot**

**How to use:**
Send me an Instagram Reel link in this format:
`/reel https://www.instagram.com/reel/xxxxx/`

**I will send you:**
• Account username
• Full caption
• High quality video
• 5 random thumbnails

**Ready to download!**
"""
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def reel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /reel command with URL"""
        try:
            # Check if URL is provided
            if not context.args:
                await update.message.reply_text(
                    "Please provide an Instagram Reel URL!\n\n"
                    "Usage: `/reel https://www.instagram.com/reel/xxxxx/`",
                    parse_mode='Markdown'
                )
                return
            
            url = context.args[0]
            
            # Send processing message
            processing_msg = await update.message.reply_text("Processing your reel...")
            
            # Extract shortcode
            shortcode = self.extract_shortcode(url)
            if not shortcode:
                await processing_msg.edit_text("Invalid Instagram URL. Please check and try again.")
                return
            
            # Get post information
            post = instaloader.Post.from_shortcode(self.L.context, shortcode)
            
            if not post.is_video:
                await processing_msg.edit_text("This post is not a video/reel.")
                return
            
            # Extract information
            username = post.owner_username
            caption = post.caption if post.caption else "No caption available"
            likes = post.likes
            video_url = post.video_url
            
            # Send caption and info
            info_message = f"""
✅ **Reel Found!**

👤 **Account:** @{username}
❤️ **Likes:** {likes:,}

📝 **Caption:**
{caption[:800]}{"..." if len(caption) > 800 else ""}

⬇️ Downloading video...
"""
            await processing_msg.edit_text(info_message, parse_mode='Markdown')
            
            # Download video
            video_filename = f"{shortcode}.mp4"
            urllib.request.urlretrieve(video_url, video_filename)
            
            # Send video
            await update.message.reply_text("📹 Sending video...")
            with open(video_filename, 'rb') as video:
                await update.message.reply_video(
                    video=video,
                    caption=f"🎥 **@{username}**\n\n{caption[:200]}{'...' if len(caption) > 200 else ''}",
                    parse_mode='Markdown',
                    supports_streaming=True
                )
            
            # Generate and send thumbnails
            await update.message.reply_text("Generating thumbnails...")
            thumbnails = self.generate_thumbnails(video_filename, shortcode)
            
            if thumbnails:
                media_group = []
                for i, thumb in enumerate(thumbnails[:5], 1):
                    with open(thumb, 'rb') as photo:
                        media_group.append({
                            'type': 'photo',
                            'media': photo.read(),
                            'caption': f"Thumbnail {i}/5" if i == 1 else ""
                        })
                
                # Send as media group
                from telegram import InputMediaPhoto
                media_list = [InputMediaPhoto(media=m['media'], caption=m['caption']) for m in media_group]
                await update.message.reply_media_group(media=media_list)
            
            # Cleanup files
            try:
                os.remove(video_filename)
                for thumb in thumbnails:
                    if os.path.exists(thumb):
                        os.remove(thumb)
            except:
                pass
            
            await update.message.reply_text("Done! Enjoy your reel!")
            
        except Exception as e:
            error_message = f"Error: {str(e)}\n\nPlease make sure the reel is public and try again."
            await update.message.reply_text(error_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
**Help - How to Use**

1️⃣ Copy an Instagram Reel link
2️⃣ Send: `/reel [paste link here]`
3️⃣ Wait for the bot to process
4️⃣ Receive video + thumbnails!

**Example:**
`/reel https://www.instagram.com/reel/ABC123xyz/`

**Note:** Only public reels can be downloaded.
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    def run(self):
        """Run the bot"""
        print("Starting Telegram Bot...")
        
        # Create application
        app = Application.builder().token(self.bot_token).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("reel", self.reel_command))
        app.add_handler(CommandHandler("help", self.help_command))
        
        print("Bot is running! Press Ctrl+C to stop.")
        
        # Run the bot
        app.run_polling(allowed_updates=Update.ALL_TYPES)

if not BOT_TOKEN:
    print("BOT_TOKEN not found!")
    print("Please create a .env file and add your Bot Token.")
    print("Example: BOT_TOKEN=\"12345:ABCDEF...\"")
else:
    bot = InstaReelBot(BOT_TOKEN)
    bot.run()
