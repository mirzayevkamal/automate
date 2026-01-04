# Quick Start - 5 Minutes to Your First Video

**Goal:** Generate your first AI-powered YouTube video in 5 minutes

---

## Prerequisites Checklist

- [ ] Python 3.9+ installed
- [ ] FFmpeg installed
- [ ] OpenAI API key (get from https://platform.openai.com/api-keys)

---

## 1-Minute Setup

```bash
# Run automated setup
./setup.sh

# Edit .env and add your OpenAI API key
nano .env
```

In `.env`, add:
```
OPENAI_API_KEY=sk-proj-your_actual_key_here
```

Save and exit (Ctrl+X, Y, Enter)

---

## Generate First Video

```bash
# Activate environment
source venv/bin/activate

# Generate test video (no YouTube upload)
python main.py --test
```

**What this does:**
1. Takes first topic from `topics.txt`
2. Generates script using AI (~15 seconds)
3. Creates voiceover (~10 seconds)
4. Renders video (~30 seconds)
5. Saves to `output/` folder

**Total time:** ~1 minute

---

## View Your Video

```bash
# Find your video
ls -lh output/

# Play it (Linux)
vlc output/video_*.mp4

# Or open folder (macOS)
open output/
```

---

## Upload to YouTube

### One-time YouTube setup (2 minutes):

1. Go to https://console.cloud.google.com/
2. Create project → Enable YouTube Data API v3
3. Create OAuth credentials → Download `client_secrets.json`
4. Put file in project directory

### Upload test video:

```bash
python main.py --test
```

- First run: Browser opens → Sign in → Grant permissions
- Future runs: Automatic upload!

---

## Schedule Automated Videos

### Option 1: Built-in Scheduler

```bash
# Edit config.yaml to set times
nano config.yaml

# Run continuously
python main.py --schedule
```

### Option 2: Cron Job

```bash
crontab -e

# Add: Run at 9am, 2pm, 8pm daily
0 9,14,20 * * * cd /path/to/youtube-automation && venv/bin/python main.py --run-once
```

---

## Customize Your Videos

### Add more topics:

```bash
nano topics.txt
```

Add one topic per line:
```
How to use Docker
Python vs JavaScript
REST API tutorial
```

### Change video style:

```bash
nano config.yaml
```

```yaml
video:
  subtitles:
    enabled: true      # Word-by-word subtitles
    color: "yellow"    # Change color
    font_size: 80      # Change size

voice:
  provider: "openai"
  openai:
    voice: "nova"      # Try: alloy, echo, fable, onyx, shimmer
```

---

## Cost

**Free tier (first video):**
- Script: $0.01
- Voice: $0.02
- **Total: $0.03**

**Monthly (3 videos/day):**
- 90 videos × $0.03 = **$2.70/month**

(YouTube upload is free)

---

## Common Commands

```bash
# Generate one test video
python main.py --test

# Generate for specific topic
python main.py --topic "Python tutorial"

# Run on schedule
python main.py --schedule

# Check logs
tail -f logs/automation_*.log
```

---

## Troubleshooting

**"No module named 'openai'"**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**"OPENAI_API_KEY not found"**
```bash
# Check .env file exists and has key
cat .env
```

**Video rendering slow**
- First video takes longer (downloading models)
- Future videos are faster

---

## What's Next?

1. ✅ Generated first video
2. ✅ Uploaded to YouTube
3. ✅ Set up schedule
4. 🎉 Sit back and enjoy automated content!

**See SETUP.md for detailed configuration options**
