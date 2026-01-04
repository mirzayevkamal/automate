# Setup Guide - YouTube Content Automation

Complete setup instructions to get your automation running.

---

## Prerequisites

- Python 3.9 or higher
- FFmpeg installed
- ImageMagick installed
- 2GB+ RAM
- OpenAI API key
- Google Cloud account (for YouTube API)

---

## Step 1: System Dependencies

### Ubuntu/Debian:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv ffmpeg imagemagick
```

### macOS:

```bash
brew install python ffmpeg imagemagick
```

### Windows:

- Install Python from python.org
- Install FFmpeg: https://ffmpeg.org/download.html
- Install ImageMagick: https://imagemagick.org/script/download.php

---

## Step 2: Project Setup

```bash
# Clone or download the project
cd youtube-automation

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

---

## Step 3: OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-proj-...`)
5. Save it - you'll need it in Step 5

**Cost:** ~$0.01-0.10 per video (depending on model)

---

## Step 4: YouTube API Setup

### 4.1 Create Google Cloud Project

1. Go to https://console.cloud.google.com/
2. Click "Select a project" → "New Project"
3. Name it: "YouTube Automation"
4. Click "Create"

### 4.2 Enable YouTube Data API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "YouTube Data API v3"
3. Click it and press "Enable"

### 4.3 Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Configure Consent Screen"
   - Choose "External"
   - App name: "YouTube Automation"
   - User support email: your email
   - Developer contact: your email
   - Click "Save and Continue"
   - Scopes: Skip (click "Save and Continue")
   - Test users: Add your Google account email
   - Click "Save and Continue"

3. Back to "Credentials" tab
4. Click "Create Credentials" → "OAuth client ID"
5. Application type: "Desktop app"
6. Name: "YouTube Automation Desktop"
7. Click "Create"

### 4.4 Download Credentials

1. Click the download icon (⬇) next to your credential
2. Save as `client_secrets.json` in the project directory
3. **Important:** Never commit this file to git!

---

## Step 5: Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env file
nano .env  # or use any text editor
```

Add your keys:

```env
OPENAI_API_KEY=sk-proj-your_actual_key_here
```

Save and close.

---

## Step 6: Configure Topics

Edit `topics.txt` with your video topics:

```bash
nano topics.txt
```

Add one topic per line:

```
How to learn Python programming
JavaScript tips for beginners
Understanding Docker containers
Git basics for developers
```

---

## Step 7: Configure Settings (Optional)

Edit `config.yaml` to customize:

```bash
nano config.yaml
```

Key settings:

```yaml
schedule:
  videos_per_day: 3  # How many videos per day
  upload_times:      # When to generate/upload
    - "09:00"
    - "14:00"
    - "20:00"

youtube:
  privacy_status: "public"  # or "unlisted", "private"
```

---

## Step 8: First Run (Test)

```bash
# Make sure venv is activated
source venv/bin/activate

# Run a test video
python main.py --test
```

**What happens:**
1. Script is generated using AI
2. Voice is generated using OpenAI TTS
3. Video is created with subtitles
4. Browser opens for YouTube authentication
5. Video uploads to YouTube
6. You get the YouTube link!

**First-time authentication:**
- Browser will open
- Sign in with your YouTube channel's Google account
- Grant permissions
- A token file is saved for future runs

---

## Step 9: Run on Schedule

### Option A: Using Built-in Scheduler

```bash
# Run continuously (keeps running, executes on schedule)
python main.py --schedule
```

Keep this running in a terminal or use screen/tmux:

```bash
screen -S youtube-automation
python main.py --schedule
# Press Ctrl+A then D to detach
# Reattach with: screen -r youtube-automation
```

### Option B: Using Cron (Linux/macOS)

```bash
# Edit crontab
crontab -e

# Add entries for your schedule (example: 9am, 2pm, 8pm)
0 9 * * * cd /path/to/youtube-automation && venv/bin/python main.py --run-once
0 14 * * * cd /path/to/youtube-automation && venv/bin/python main.py --run-once
0 20 * * * cd /path/to/youtube-automation && venv/bin/python main.py --run-once
```

### Option C: Using systemd (Linux)

Create service file:

```bash
sudo nano /etc/systemd/system/youtube-automation.service
```

Add:

```ini
[Unit]
Description=YouTube Content Automation
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/youtube-automation
Environment="PATH=/path/to/youtube-automation/venv/bin"
ExecStart=/path/to/youtube-automation/venv/bin/python main.py --schedule
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable youtube-automation
sudo systemctl start youtube-automation
sudo systemctl status youtube-automation
```

---

## Usage Examples

```bash
# Generate one test video
python main.py --test

# Generate one video and exit
python main.py --run-once

# Run on schedule (continuous)
python main.py --schedule

# Generate for specific topic
python main.py --topic "How to learn Python"
```

---

## Monitoring

### View Logs

```bash
# Live logs
tail -f logs/automation_20260104.log

# Check systemd service logs
sudo journalctl -u youtube-automation -f
```

### Check Topics Progress

```bash
# View remaining topics
cat topics.txt.used
```

---

## Cost Estimation

**Per video:**
- Script generation (GPT-4o-mini): ~$0.01
- Voice generation (OpenAI TTS): ~$0.02
- Video creation: Free (MoviePy)
- YouTube upload: Free
- **Total: ~$0.03 per video**

**Monthly (3 videos/day):**
- 90 videos × $0.03 = **~$2.70/month**

**Using premium options:**
- GPT-4o: ~$0.10/video
- ElevenLabs voice: ~$0.30/video
- **Total: ~$36/month for 90 videos**

---

## Troubleshooting

### "ModuleNotFoundError"

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "OPENAI_API_KEY not found"

Make sure .env file exists and contains your key:

```bash
cat .env  # Should show your key
```

### "client_secrets.json not found"

Download OAuth credentials from Google Cloud Console

### YouTube upload fails

- Check client_secrets.json exists
- Delete youtube_token.pickle and re-authenticate
- Check API quota (10,000 units/day)

### Video rendering is slow

- Use faster model: gpt-4o-mini instead of gpt-4o
- Disable subtitles temporarily
- Reduce video resolution in config.yaml

### "Permission denied" for ImageMagick

```bash
# Linux: Edit policy file
sudo nano /etc/ImageMagick-6/policy.xml
# Comment out restrictive policies
```

---

## Next Steps

1. ✅ Generate your first test video
2. ✅ Add more topics to topics.txt
3. ✅ Set up scheduling (cron or systemd)
4. ✅ Monitor logs for issues
5. ✅ Customize config.yaml for your style
6. ✅ Sit back and let AI create your content!

---

## Support

- Check logs in `logs/` directory
- Review config in `config.yaml`
- See README.md for architecture details

**Happy automating! 🚀**
