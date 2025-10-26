# 🚀 Render.com Deployment Guide

## Prerequisites
- Render.com account
- GitHub repository with your bot code
- Telegram Bot Token from @BotFather

## Deployment Steps

### 1. Prepare Your Repository
```bash
# Make sure all files are committed
git add .
git commit -m "Add Docker support for Render deployment"
git push origin main
```

### 2. Create Web Service on Render

1. **Go to [Render Dashboard](https://dashboard.render.com)**
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repository**

### 3. Configure Build Settings

**Basic Settings:**
- **Name**: `insta-reel-downloader-bot`
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Runtime**: `Docker`

**Build Settings:**
- **Docker Command**: Leave empty (uses Dockerfile CMD)
- **Dockerfile Path**: `./Dockerfile`

### 4. Environment Variables

Add these in the "Environment" section:

| Key | Value |
|-----|-------|
| `BOT_TOKEN` | Your telegram bot token from @BotFather |
| `PYTHONUNBUFFERED` | `1` |

### 5. Advanced Settings

**Resources:**
- **Instance Type**: `Starter` (free tier) or `Standard` for better performance
- **Health Check Path**: Leave empty (bot doesn't serve HTTP)

**Auto-Deploy:**
- ✅ **Enable Auto-Deploy** from main branch

### 6. Deploy

1. Click "Create Web Service"
2. Wait for build to complete (~5-10 minutes)
3. Check logs for "✅ Bot is running and ready to download Instagram reels!"

## 🔍 Verification Steps

### Check Deployment Status
```bash
# In Render logs, you should see:
2024-XX-XX XX:XX:XX 🤖 Starting Instagram Reel Downloader Bot...
2024-XX-XX XX:XX:XX ✅ FFmpeg found - thumbnails will be available
2024-XX-XX XX:XX:XX ✅ Bot is running and ready to download Instagram reels!
```

### Test Bot Commands
1. Start a conversation with your bot on Telegram
2. Send `/start` - Should receive welcome message
3. Send `/cookies` - Should receive cookie setup instructions
4. Send `/help` - Should receive help message

## 📋 Render.com Configuration Summary

**Service Type**: Web Service
**Environment**: Docker
**Port**: 8080 (automatically handled)
**Build Time**: ~5-10 minutes
**Resources**: 
- Free Tier: 512MB RAM, 0.1 CPU
- Paid Tiers: More resources available

## 🔧 Troubleshooting

### Build Fails
- Check Dockerfile syntax
- Ensure requirements.txt is valid
- Verify all files are committed to repository

### Bot Not Responding
- Check environment variables (especially BOT_TOKEN)
- View Render logs for error messages
- Verify bot token with @BotFather

### FFmpeg Issues
- Our Dockerfile includes FFmpeg installation
- If thumbnails don't work, check container logs
- FFmpeg is automatically available in our setup

### Memory Issues (Free Tier)
- Free tier has 512MB RAM limit
- Bot should work fine with this
- Consider upgrading if processing large videos

## 🎯 Production Optimizations

For production deployment:

1. **Upgrade Instance Type**
   - Use Standard or Pro tier for better performance
   - More RAM for handling multiple users

2. **Add Monitoring**
   - Set up Render health checks
   - Monitor logs regularly

3. **Environment Variables**
   ```env
   BOT_TOKEN=your_production_token
   PYTHONUNBUFFERED=1
   LOG_LEVEL=INFO
   ```

4. **Scaling Considerations**
   - Render auto-scales based on traffic
   - Consider multiple instances for high usage

## 📊 Expected Performance

**Free Tier (Starter):**
- ✅ Handles ~10-50 users simultaneously
- ✅ Fast Instagram downloads with cookies
- ✅ Full thumbnail generation support
- ⚠️ May sleep after 15 minutes of inactivity

**Paid Tiers:**
- ✅ No sleep functionality
- ✅ Better performance
- ✅ More concurrent users
- ✅ Priority support

## 🔐 Security Notes

- Environment variables are encrypted on Render
- Cookie files are stored in temporary container storage
- No persistent storage of user data
- Each deployment starts with clean state

---

🎉 **Your Instagram Reel Downloader Bot is now ready for production on Render.com!**