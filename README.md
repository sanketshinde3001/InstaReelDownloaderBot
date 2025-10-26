# 🤖 Instagram Reel Downloader Bot

A powerful Telegram bot that downloads Instagram Reels with high quality video and generates thumbnails. Features robust cookie authentication system to bypass Instagram's rate limits.

## ✨ Features

- 📥 **Download Instagram Reels** - High quality video downloads
- 🖼️ **5 Random Thumbnails** - Generated from the video (requires FFmpeg)
- 🍪 **Cookie Authentication** - Bypass Instagram rate limits
- 👤 **User Info** - Shows username, likes, and full caption
- 🔒 **Per-user Cookie Storage** - Secure and isolated authentication
- 🚀 **Fast & Reliable** - Optimized for performance

## 🚀 Quick Start

### 1. Bot Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/InstaReelDownloaderBot.git
cd InstaReelDownloaderBot

# Install dependencies
pip install -r requirements.txt

# Set up environment
echo "BOT_TOKEN=your_telegram_bot_token" > .env

# Run the bot
python main.py
```

### 2. Get Bot Token
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Create a new bot with `/newbot`
3. Copy the token to your `.env` file

## 🍪 Cookie Authentication (Recommended)

To avoid Instagram rate limits and access more content:

### Getting Cookies:
1. **Chrome/Edge**: Install "Get cookies.txt LOCALLY" extension
2. **Firefox**: Install "cookies.txt" add-on
3. Visit Instagram while logged in
4. Export cookies for instagram.com

### Using Cookies:
1. Send `/cookies` command to the bot
2. Upload your `cookies.txt` file
3. Enjoy unlimited downloads! 🎉

## 🛠️ Installation Requirements

### Required:
- Python 3.8+
- Telegram Bot Token
- Required Python packages (see requirements.txt)

### Optional (for thumbnails):
- **FFmpeg** - For thumbnail generation
- See [FFMPEG_INSTALL.md](FFMPEG_INSTALL.md) for installation guide

## 📋 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and basic info |
| `/reel <url>` | Download Instagram reel |
| `/cookies` | Setup authentication cookies |
| `/cookiestatus` | Check cookie status |
| `/help` | Detailed help message |

## 🔧 Configuration

### Environment Variables:
```bash
BOT_TOKEN=your_telegram_bot_token_here
```

### Supported URL formats:
- `https://www.instagram.com/reel/ABC123/`
- `https://www.instagram.com/p/ABC123/`
- `https://instagr.am/reel/ABC123/`

## 🐳 Docker Deployment

```dockerfile
FROM python:3.11-slim

# Install FFmpeg for thumbnails
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

## 🌐 Cloud Deployment

### Render.com:
1. Fork this repository
2. Connect to Render
3. Add environment variable: `BOT_TOKEN`
4. Deploy! 🚀

### Heroku:
```bash
# Install Heroku CLI
heroku create your-bot-name
heroku config:set BOT_TOKEN=your_token_here
git push heroku main
```

## 🔒 Security Features

- **Per-user cookie isolation** - No data sharing between users
- **Automatic cleanup** - Old cookies are removed after 24 hours
- **Secure file handling** - Temporary files are properly managed
- **Input validation** - All uploads are validated before use

## 🐛 Troubleshooting

### Common Issues:

**"Rate limit reached"** → Upload cookies via `/cookies` command

**"Thumbnails not available"** → Install FFmpeg (optional)

**"Bot not responding"** → Check BOT_TOKEN in environment

**"Download failed"** → Verify the Instagram URL is public

### Logs:
The bot provides detailed logging for debugging:
```bash
python main.py
# Check console output for detailed information
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## ⚠️ Disclaimer

This bot is for educational purposes. Please respect Instagram's Terms of Service and only download content you have permission to download.

## 📞 Support

- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/InstaReelDownloaderBot/issues)
- 💬 Telegram: [@yourusername](https://t.me/yourusername)

---

**Made with ❤️ for the community**
