# Deployment Guide: Stewie_it v1

## Prerequisites

- AWS Account with EC2 access
- Telegram account
- Basic knowledge of Linux/Ubuntu commands

---

## Step 1: Create Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow prompts to name your bot
4. Copy the **Bot Token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. Start a chat with your bot and send any message
6. Get your Chat ID:
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Look for `"chat":{"id":123456789}` in the response
   - Copy this Chat ID

---

## Step 2: Set Up AWS EC2 Instance

### Launch EC2 Instance

1. **Go to AWS Console** → EC2 → Launch Instance
2. **Choose AMI**: Ubuntu Server 22.04 LTS (or latest)
3. **Instance Type**: t3.medium or larger (needs Chrome + Selenium)
4. **Storage**: 20GB minimum
5. **Security Group**: Allow SSH (port 22) from your IP
6. **Key Pair**: Create/select a key pair for SSH access
7. Launch the instance

### Connect to EC2

```bash
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>
```

---

## Step 3: Install System Dependencies

Once connected to EC2, run:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install FFmpeg and ImageMagick
sudo apt install -y ffmpeg imagemagick

# Install Chrome (for Selenium)
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f -y

# Install ChromeDriver
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
DRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%%.*}")
wget "https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Verify installations
ffmpeg -version
convert -version
google-chrome --version
chromedriver --version
```

---

## Step 4: Install Python Dependencies

```bash
# Install Python 3 and pip
sudo apt install -y python3 python3-pip python3-venv

# Create project directory
mkdir -p /home/ubuntu/mainrepo/stewie_v1
cd /home/ubuntu/mainrepo/stewie_v1

# Clone or upload your repository
# git clone <your-repo-url> .
# OR upload files via SCP:
# scp -i your-key.pem -r /local/path/* ubuntu@<EC2_IP>:/home/ubuntu/mainrepo/stewie_v1/

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install pydub moviepy selenium duckduckgo-search python-dotenv requests
```

---

## Step 5: Configure Environment Variables

Create a `.env` file in your project directory:

```bash
nano .env
```

Add the following:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

Save and exit (Ctrl+X, then Y, then Enter)

---

## Step 6: Prepare Assets

### Create required directories:

```bash
mkdir -p audio_assests
mkdir -p video_assests
mkdir -p image_assests
mkdir -p downloaded_images
mkdir -p runtime_logs
mkdir -p archives_audios
```

### Add gameplay footage:

You need a background video (gameplay footage) in reel format (9:16 aspect ratio recommended).

```bash
# Upload your gameplay video to video_assests/
# Name it: video_without_audio.webm
# OR download a sample:
# wget -O video_assests/video_without_audio.webm <your_video_url>
```

### Character images:

The character images (peter.png, stewie.png) should already be in `image_assests/` from the repository.

---

## Step 7: Fix ImageMagick Path

Edit `editor_agent.py` to set correct ImageMagick path:

```bash
nano editor_agent.py
```

Uncomment line 16 and verify the path:

```python
from moviepy.config_defaults import IMAGEMAGICK_BINARY
IMAGEMAGICK_BINARY = r"/usr/bin/convert"  # Verify this path exists
```

Verify ImageMagick location:

```bash
which convert
# Should output: /usr/bin/convert
```

---

## Step 8: Fix Video Path

Edit `flow_main.py` to correct the video path:

```bash
nano flow_main.py
```

On line 63, update the video path to match your setup:

```python
video_path=r"/home/ubuntu/mainrepo/stewie_v1/video_assests/video_without_audio.webm"
```

---

## Step 9: Run the Application

### Manual Run (for testing):

```bash
cd /home/ubuntu/mainrepo/stewie_v1
source venv/bin/activate
python3 flow_main.py
```

### Run as Background Service (recommended):

Using `screen` or `tmux`:

```bash
# Using screen
screen -S stewie
cd /home/ubuntu/mainrepo/stewie_v1
source venv/bin/activate
python3 flow_main.py

# Detach: Press Ctrl+A then D
# Reattach: screen -r stewie
```

OR using `systemd`:

Create service file:

```bash
sudo nano /etc/systemd/system/stewie.service
```

Add:

```ini
[Unit]
Description=Stewie Video Generator
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/mainrepo/stewie_v1
Environment="PATH=/home/ubuntu/mainrepo/stewie_v1/venv/bin"
ExecStart=/home/ubuntu/mainrepo/stewie_v1/venv/bin/python3 flow_main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable stewie.service
sudo systemctl start stewie.service

# Check status
sudo systemctl status stewie.service

# View logs
sudo journalctl -u stewie.service -f
```

---

## Step 10: Using the Bot

### Send Content to Telegram Bot:

1. Open Telegram and find your bot
2. Send a message in this format:

```
from: [
  {
    "dialogue": "Peter: Time complexity tells you how long your code will take as input grows.",
    "character": "peter",
    "image": "peter.png",
    "image_search": "time complexity coding"
  },
  {
    "dialogue": "Stewie: So it's not about actual seconds?",
    "character": "stewie",
    "image": "stewie.png",
    "image_search": "algorithm speed"
  }
]
```

3. The bot will process your request through the 3 stages
4. You'll receive the final video via Telegram

---

## Monitoring & Logs

View application logs:

```bash
# Runtime logs
tail -f runtime_logs/flow_log.log
tail -f runtime_logs/voice_generator.log

# Error logs
tail -f errors.log
```

Check database status:

```bash
sqlite3 stewie_database.db "SELECT * FROM dialouge_stage;"
```

---

## AWS Cost Optimization

The script automatically shuts down the VM after completion (line 91 in flow_main.py).

To enable auto-start on new Telegram messages, you can set up:
- **AWS Lambda** to monitor Telegram updates
- **CloudWatch Events** to start EC2 instance
- **SNS notifications** for job completion

---

## Troubleshooting

### Common Issues:

**"ChromeDriver version mismatch"**
```bash
# Reinstall ChromeDriver matching Chrome version
google-chrome --version
# Download matching version from chromedriver.chromium.org
```

**"ModuleNotFoundError"**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**"Permission denied" for ImageMagick**
```bash
# Edit ImageMagick policy
sudo nano /etc/ImageMagick-6/policy.xml
# Comment out or remove restrictive PDF/video policies
```

**"Video path not found"**
- Verify video file exists: `ls -la video_assests/`
- Update path in flow_main.py line 63

**Telegram bot not responding**
- Verify .env file has correct token and chat ID
- Test API: `curl https://api.telegram.org/bot<TOKEN>/getMe`

---

## Optional: Instagram Auto-Posting

For automatic Instagram posting, you'll need:
1. Instagram Business Account
2. Facebook Developer App
3. Instagram Graph API access token

This is currently commented out in the codebase. Due to IP rotation on EC2, manual posting is recommended.

---

## Security Notes

- Keep your `.env` file secure and never commit it to git
- Add `.env` to `.gitignore`
- Use IAM roles for AWS access instead of hardcoded credentials
- Regularly update system packages and dependencies
- Use security groups to restrict EC2 access

---

## Next Steps

- Test the full workflow with a simple dialogue
- Set up CloudWatch monitoring for EC2 instance
- Configure backup for SQLite database
- Set up log rotation for runtime logs
- Consider using S3 for video storage if files exceed 50MB
