#!/bin/bash

# Stewie_it v1 - Quick Setup Script for Ubuntu/Debian
# Run this script on your AWS EC2 or Ubuntu server

set -e  # Exit on error

echo "==================================="
echo "Stewie_it v1 - Setup Script"
echo "==================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
   echo "Please do not run as root. Run as ubuntu or regular user."
   exit 1
fi

# Update system
echo "Step 1: Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo ""
echo "Step 2: Installing system dependencies..."
sudo apt install -y ffmpeg imagemagick wget unzip curl python3 python3-pip python3-venv

# Install Google Chrome
echo ""
echo "Step 3: Installing Google Chrome..."
if ! command -v google-chrome &> /dev/null; then
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo dpkg -i google-chrome-stable_current_amd64.deb || sudo apt-get install -f -y
    rm google-chrome-stable_current_amd64.deb
    echo "Google Chrome installed successfully"
else
    echo "Google Chrome already installed"
fi

# Install ChromeDriver
echo ""
echo "Step 4: Installing ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+' | head -1)
echo "Detected Chrome version: $CHROME_VERSION"

# Get the latest ChromeDriver version for this Chrome major version
DRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
echo "Installing ChromeDriver version: $DRIVER_VERSION"

wget "https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip"
unzip -o chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm chromedriver_linux64.zip
echo "ChromeDriver installed successfully"

# Create virtual environment
echo ""
echo "Step 5: Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo ""
echo "Step 6: Installing Python packages..."
pip install --upgrade pip
pip install pydub moviepy selenium duckduckgo-search python-dotenv requests pillow

# Create required directories
echo ""
echo "Step 7: Creating project directories..."
mkdir -p audio_assests
mkdir -p video_assests
mkdir -p image_assests
mkdir -p downloaded_images
mkdir -p runtime_logs
mkdir -p archives_audios

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Step 8: Creating .env file..."
    cp .env.example .env
    echo ".env file created from template"
    echo "IMPORTANT: Edit .env file and add your Telegram credentials!"
else
    echo ""
    echo "Step 8: .env file already exists, skipping..."
fi

# Verify installations
echo ""
echo "==================================="
echo "Verifying installations..."
echo "==================================="
echo "FFmpeg: $(ffmpeg -version 2>&1 | head -1)"
echo "ImageMagick: $(convert -version | head -1)"
echo "Chrome: $(google-chrome --version)"
echo "ChromeDriver: $(chromedriver --version)"
echo "Python: $(python3 --version)"

echo ""
echo "==================================="
echo "Setup completed successfully!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Telegram bot credentials:"
echo "   nano .env"
echo ""
echo "2. Add a gameplay video to video_assests/video_without_audio.webm"
echo ""
echo "3. Update video path in flow_main.py (line 63) if needed"
echo ""
echo "4. Run the application:"
echo "   source venv/bin/activate"
echo "   python3 flow_main.py"
echo ""
echo "For detailed instructions, see DEPLOYMENT_GUIDE.md"
echo "==================================="
