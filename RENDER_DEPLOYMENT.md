# 🚀 Render.com Deployment Guide# 🚀 Render.com Deployment Guide



## Prerequisites## Prerequisites

- Render.com account- Render.com account

- GitHub repository with your bot code- GitHub repository with your bot code

- Telegram Bot Token from @BotFather- Telegram Bot Token from @BotFather



## Deployment Steps## Deployment Steps



### 1. Prepare Your Repository### 1. Prepare Your Repository

```bash```bash

# Make sure all files are committed# Make sure all files are committed

git add .git add .

git commit -m "Add webhook support and improve FFmpeg installation"git commit -m "Add Docker support for Render deployment"

git push origin maingit push origin main

``````



### 2. Create Web Service on Render### 2. Create Web Service on Render



1. **Go to [Render Dashboard](https://dashboard.render.com)**1. **Go to [Render Dashboard](https://dashboard.render.com)**

2. **Click "New +" → "Web Service"**2. **Click "New +" → "Web Service"**

3. **Connect your GitHub repository**3. **Connect your GitHub repository**



### 3. Configure Build Settings### 3. Configure Build Settings



**Basic Settings:****Basic Settings:**

- **Name**: `insta-reel-downloader-bot`- **Name**: `insta-reel-downloader-bot`

- **Region**: Choose closest to your users- **Region**: Choose closest to your users

- **Branch**: `main`- **Branch**: `main`

- **Runtime**: `Docker`- **Runtime**: `Docker`



**Build Settings:****Build Settings:**

- **Docker Command**: Leave empty (uses Dockerfile CMD)- **Docker Command**: Leave empty (uses Dockerfile CMD)

- **Dockerfile Path**: `./Dockerfile`- **Dockerfile Path**: `./Dockerfile`



### 4. Environment Variables### 4. Environment Variables



Add these in the "Environment" section:Add these in the "Environment" section:



| Key | Value || Key | Value |

|-----|-------||-----|-------|

| `BOT_TOKEN` | Your telegram bot token from @BotFather || `BOT_TOKEN` | Your telegram bot token from @BotFather |

| `WEBHOOK_URL` | Your Render service URL (e.g., `https://your-service.onrender.com`) || `PYTHONUNBUFFERED` | `1` |

| `PYTHONUNBUFFERED` | `1` |

### 5. Advanced Settings

**Note:** The `PORT` environment variable is automatically set by Render.

**Resources:**

### 5. Advanced Settings- **Instance Type**: `Starter` (free tier) or `Standard` for better performance

- **Health Check Path**: Leave empty (bot doesn't serve HTTP)

**Resources:**

- **Instance Type**: `Starter` (free tier) or `Standard` for better performance**Auto-Deploy:**

- **Health Check Path**: `/health` (bot now serves HTTP for webhooks)- ✅ **Enable Auto-Deploy** from main branch



**Auto-Deploy:**### 6. Deploy

- ✅ **Enable Auto-Deploy** from main branch

1. Click "Create Web Service"

### 6. Deploy2. Wait for build to complete (~5-10 minutes)

3. Check logs for "✅ Bot is running and ready to download Instagram reels!"

1. Click "Create Web Service"

2. Wait for build to complete (~5-10 minutes)## 🔍 Verification Steps

3. Check logs for "✅ Bot is running and ready to download Instagram reels!"

### Check Deployment Status

## 🔍 Verification Steps```bash

# In Render logs, you should see:

1. **Check Build Logs:**2024-XX-XX XX:XX:XX 🤖 Starting Instagram Reel Downloader Bot...

   - Should see FFmpeg installation success2024-XX-XX XX:XX:XX ✅ FFmpeg found - thumbnails will be available

   - Look for: "=== FFmpeg Installation Check ==="2024-XX-XX XX:XX:XX ✅ Bot is running and ready to download Instagram reels!

```

2. **Test the Bot:**

   - Send `/start` to your bot### Test Bot Commands

   - Try downloading a public reel1. Start a conversation with your bot on Telegram

2. Send `/start` - Should receive welcome message

3. **Monitor Logs:**3. Send `/cookies` - Should receive cookie setup instructions

   - Go to "Logs" tab in Render dashboard4. Send `/help` - Should receive help message

   - Should see webhook mode messages

## 📋 Render.com Configuration Summary

## 🆚 Webhook vs Polling Mode

**Service Type**: Web Service

### 🌐 Webhook Mode (Production - Render)**Environment**: Docker

- ✅ No conflicts with multiple instances**Port**: 8080 (automatically handled)

- ✅ Better performance and reliability**Build Time**: ~5-10 minutes

- ✅ Instant message processing**Resources**: 

- ✅ Lower resource usage- Free Tier: 512MB RAM, 0.1 CPU

- ✅ HTTP health checks available- Paid Tiers: More resources available



### 🔄 Polling Mode (Development - Local)## 🔧 Troubleshooting

- ✅ Easy local testing

- ❌ Can conflict with production instances### Build Fails

- ❌ Higher resource usage- Check Dockerfile syntax

- ❌ Periodic API calls- Ensure requirements.txt is valid

- Verify all files are committed to repository

## 💡 Tips for Success

### Bot Not Responding

### Starter Plan Benefits:- Check environment variables (especially BOT_TOKEN)

- ✅ Free tier available- View Render logs for error messages

- ✅ Automatic HTTPS- Verify bot token with @BotFather

- ✅ Custom domains supported

- ✅ Continuous deployment### FFmpeg Issues

- Our Dockerfile includes FFmpeg installation

### Standard Plan Benefits:- If thumbnails don't work, check container logs

- ✅ No sleep functionality- FFmpeg is automatically available in our setup

- ✅ Better performance

- ✅ More concurrent users### Memory Issues (Free Tier)

- ✅ Priority support- Free tier has 512MB RAM limit

- Bot should work fine with this

## 🔐 Security Notes- Consider upgrading if processing large videos



- Environment variables are encrypted on Render## 🎯 Production Optimizations

- Cookie files are stored in temporary container storage

- No persistent storage of user dataFor production deployment:

- Each deployment starts with clean state

1. **Upgrade Instance Type**

## 🔧 Troubleshooting   - Use Standard or Pro tier for better performance

   - More RAM for handling multiple users

### FFmpeg Issues

2. **Add Monitoring**

If you see errors related to FFmpeg or thumbnail generation:   - Set up Render health checks

   - Monitor logs regularly

**Common Error Messages:**

```3. **Environment Variables**

Thumbnail generation error: stdout and stderr arguments may not be used with capture_output   ```env

FFmpeg not found - skipping thumbnail generation   BOT_TOKEN=your_production_token

```   PYTHONUNBUFFERED=1

   LOG_LEVEL=INFO

**Solutions:**   ```



1. **Rebuild the service** - The Dockerfile installs FFmpeg during build:4. **Scaling Considerations**

   - Go to your Render dashboard   - Render auto-scales based on traffic

   - Click on your service   - Consider multiple instances for high usage

   - Click "Manual Deploy" → "Deploy latest commit"

## 📊 Expected Performance

2. **Check FFmpeg installation** - Look for these in build logs:

   ```**Free Tier (Starter):**

   === FFmpeg Installation Check ===- ✅ Handles ~10-50 users simultaneously

   === FFprobe Installation Check ===- ✅ Fast Instagram downloads with cookies

   === FFmpeg Location ===- ✅ Full thumbnail generation support

   ```- ⚠️ May sleep after 15 minutes of inactivity



3. **Verify the build logs**:**Paid Tiers:**

   - In Render dashboard, go to "Events" tab- ✅ No sleep functionality

   - Look for FFmpeg installation success messages- ✅ Better performance

   - Should see: `ffmpeg version` and `ffprobe version` outputs- ✅ More concurrent users

- ✅ Priority support

4. **If FFmpeg still missing**:

   - The bot will work without thumbnails## 🔐 Security Notes

   - Users will get videos without thumbnail previews

   - No functionality is lost, just aesthetic feature- Environment variables are encrypted on Render

- Cookie files are stored in temporary container storage

### Bot Conflict Issues- No persistent storage of user data

- Each deployment starts with clean state

**Error Messages:**

```## 🔧 Troubleshooting

Conflict: terminated by other getUpdates request; make sure that only one bot instance is running

```### FFmpeg Issues



**Solutions:**If you see errors related to FFmpeg or thumbnail generation:



1. **Use Webhook Mode** (Recommended):**Common Error Messages:**

   - Set `WEBHOOK_URL` environment variable```

   - Render will automatically set `PORT`Thumbnail generation error: stdout and stderr arguments may not be used with capture_output

   - Bot switches to webhook mode automaticallyFFmpeg not found - skipping thumbnail generation

```

2. **Stop Other Instances**:

   - Stop any local bot instances**Solutions:**

   - Only run one bot instance at a time

   - Webhook mode prevents conflicts1. **Rebuild the service** - The Dockerfile installs FFmpeg during build:

   - Go to your Render dashboard

3. **Clear Pending Updates**:   - Click on your service

   - Bot automatically clears pending updates on start   - Click "Manual Deploy" → "Deploy latest commit"

   - No manual intervention needed

2. **Check FFmpeg installation** - Add this to your environment variables for debugging:

### Common Deploy Issues   ```

   PYTHONUNBUFFERED=1

**Build Failures:**   ```

- Check that `Dockerfile` exists in repository root

- Verify `requirements.txt` has all dependencies3. **Verify the build logs**:

- Ensure `BOT_TOKEN` environment variable is set   - In Render dashboard, go to "Events" tab

   - Look for FFmpeg installation success messages

**Runtime Issues:**   - Should see: `ffmpeg version` and `ffprobe version` outputs

- Check logs in Render dashboard → "Logs" tab

- Verify bot token is valid4. **If FFmpeg still missing**:

- Test webhook URL: `https://your-service.onrender.com/health`   - The bot will work without thumbnails

- Should return "OK"   - Users will get videos without thumbnail previews

   - No functionality is lost, just aesthetic feature

**Webhook Setup Issues:**

- Ensure `WEBHOOK_URL` matches your actual Render URL### Common Deploy Issues

- Check that service is not sleeping (use Standard plan to avoid)

- Verify `/webhook` endpoint is accessible**Build Failures:**

- Check that `Dockerfile` exists in repository root

### Local Development- Verify `requirements.txt` has all dependencies

- Ensure `BOT_TOKEN` environment variable is set

For local testing without conflicts:

**Runtime Issues:**

```bash- Check logs in Render dashboard → "Logs" tab

# Don't set WEBHOOK_URL and PORT for local development- Verify bot token is valid

export BOT_TOKEN="your_bot_token_here"- Test bot locally first: `docker build -t bot . && docker run bot`

python main.py

```---



The bot will automatically use polling mode for local development.🎉 **Your Instagram Reel Downloader Bot is now ready for production on Render.com!**

---

🎉 **Your Instagram Reel Downloader Bot is now ready for production on Render.com!**