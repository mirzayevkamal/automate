# YouTube Content Automation System

**Fully automated AI-powered YouTube content creation and publishing**

## What It Does

1. ✅ You provide a list of topics
2. ✅ AI generates engaging scripts automatically
3. ✅ AI creates professional voiceovers
4. ✅ System creates videos with visuals and subtitles
5. ✅ Auto-uploads to YouTube on schedule
6. ✅ Runs X times per day (configurable)

## Features

- 🤖 **AI Script Generation** - Uses OpenAI GPT to create engaging content
- 🎙️ **AI Voice Generation** - Multiple TTS options (OpenAI, ElevenLabs, free)
- 🎬 **Automatic Video Creation** - Stock footage + animated subtitles
- 📺 **YouTube Auto-Upload** - SEO-optimized titles and descriptions
- ⏰ **Scheduled Publishing** - Set how many videos per day
- 📊 **Topic Management** - Queue system ensures all topics are covered
- 🔄 **Retry Logic** - Handles failures gracefully
- 📝 **Full Logging** - Track everything that happens

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Topics

Edit `topics.txt` - one topic per line:

```
How to learn Python programming
5 JavaScript tips for beginners
Understanding REST APIs
Docker for developers
```

### 3. Set Up Credentials

Copy `.env.example` to `.env` and add:

- OpenAI API key (for script generation)
- YouTube credentials (for uploading)
- Optional: ElevenLabs API key (for better voices)

### 4. Configure Schedule

Edit `config.yaml`:

```yaml
videos_per_day: 3  # How many videos to generate per day
upload_times: ["09:00", "14:00", "20:00"]  # When to upload
```

### 5. Run

**One-time test:**
```bash
python main.py --test
```

**Schedule (runs continuously):**
```bash
python main.py --schedule
```

**Or use cron:**
```bash
crontab -e
# Add: 0 9,14,20 * * * cd /path/to/project && python main.py --run-once
```

## Architecture

```
Topics List → Script Generator → Voice Generator → Video Creator → YouTube Uploader
     ↓              ↓                   ↓                ↓              ↓
  topics.txt    OpenAI API         TTS Service      MoviePy        YouTube API
```

## Cost Estimate

**Minimal setup (Free tier):**
- Script: OpenAI API ~$0.01/video
- Voice: Free TTS (gTTS)
- Video: Free (MoviePy + Pexels)
- Upload: Free (YouTube API)
- **Total: ~$0.30/month for 30 videos**

**Premium setup:**
- Script: OpenAI GPT-4 ~$0.10/video
- Voice: ElevenLabs ~$0.30/video
- **Total: ~$12/month for 30 videos**

## Video Styles

Choose from:

1. **Simple Text** - Animated text on gradient background
2. **Stock Footage** - Auto-fetched from Pexels/Pixabay
3. **Code Tutorials** - Syntax-highlighted code snippets
4. **Slideshow** - AI-generated images + narration

Configure in `config.yaml`

## Requirements

- Python 3.9+
- FFmpeg
- ImageMagick
- 2GB RAM minimum
- Internet connection

## Directory Structure

```
youtube-automation/
├── main.py                 # Entry point
├── config.yaml            # Configuration
├── topics.txt             # Your topics list
├── .env                   # API keys (create from .env.example)
├── modules/
│   ├── script_generator.py    # AI script creation
│   ├── voice_generator.py     # TTS
│   ├── video_creator.py       # Video assembly
│   ├── youtube_uploader.py    # Upload to YouTube
│   └── scheduler.py           # Job scheduling
├── templates/             # Script templates
├── assets/               # Fonts, backgrounds, music
├── output/              # Generated videos
└── logs/                # Execution logs
```

## Example Output

**Input topic:** "How to learn Python programming"

**Generated script:** 2-3 minute educational script
**Voice:** Natural-sounding AI narration
**Video:**
- Animated title sequence
- Stock footage or code snippets
- Word-by-word subtitles
- Outro with CTA

**YouTube:**
- Title: "How to Learn Python Programming in 2026 | Complete Beginner's Guide"
- Description: Full transcript + resources
- Tags: Auto-generated SEO tags
- Thumbnail: Auto-generated

## Customization

All customizable via `config.yaml`:

- Video length (30s - 15min)
- Voice style (male/female, speed, accent)
- Visual style (minimal, rich, code-focused)
- Upload schedule
- SEO settings
- More...

## License

MIT - Use freely for your YouTube channel!
