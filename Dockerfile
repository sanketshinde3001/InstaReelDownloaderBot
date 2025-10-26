FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including FFmpeg and tools needed for Render
RUN apt-get update && apt-get install -y \
    ffmpeg \
    ffprobe \
    curl \
    ca-certificates \
    wget \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && ffmpeg -version \
    && ffprobe -version

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for temporary files
RUN mkdir -p /tmp/bot_files && chmod 755 /tmp/bot_files

# Set environment variables for better Python behavior in containers
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TEMP_DIR=/tmp/bot_files

# Expose port 8080 (Render's default port)
EXPOSE 8080

# Run the bot
CMD ["python", "-u", "main.py"]
