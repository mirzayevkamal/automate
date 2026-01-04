#!/bin/bash

# YouTube Content Automation - Quick Setup Script

set -e

echo "=========================================="
echo "YouTube Content Automation - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION found"

# Check FFmpeg
echo ""
echo "Checking FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg not found. Installing..."
    sudo apt update && sudo apt install -y ffmpeg
else
    echo "✓ FFmpeg found"
fi

# Check ImageMagick
echo ""
echo "Checking ImageMagick..."
if ! command -v convert &> /dev/null; then
    echo "⚠️  ImageMagick not found. Installing..."
    sudo apt install -y imagemagick
else
    echo "✓ ImageMagick found"
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate venv and install dependencies
echo ""
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Create directories
echo ""
echo "Creating directories..."
mkdir -p output temp logs assets/music
echo "✓ Directories created"

# Create .env if doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys!"
    echo "   nano .env"
else
    echo ""
    echo "✓ .env file already exists"
fi

# Make main.py executable
chmod +x main.py

echo ""
echo "=========================================="
echo "✅ Setup completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Get OpenAI API key:"
echo "   https://platform.openai.com/api-keys"
echo ""
echo "2. Set up YouTube API:"
echo "   - See SETUP.md for detailed instructions"
echo "   - Download client_secrets.json"
echo ""
echo "3. Add your API keys to .env:"
echo "   nano .env"
echo ""
echo "4. Add topics to topics.txt:"
echo "   nano topics.txt"
echo ""
echo "5. Run a test video:"
echo "   source venv/bin/activate"
echo "   python main.py --test"
echo ""
echo "=========================================="
echo "For detailed setup: See SETUP.md"
echo "=========================================="
