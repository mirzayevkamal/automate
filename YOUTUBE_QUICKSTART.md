# YouTube Integration - Quick Start Guide

**TL;DR:** Add YouTube auto-upload to your Stewie_it bot in ~15 minutes

---

## Step 1: Google Cloud Setup (5 min)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "Stewie Video Bot"
3. Enable **YouTube Data API v3**
4. Create **OAuth 2.0 credentials** (Desktop app)
5. Download `client_secrets.json` → Upload to project directory

---

## Step 2: Install Dependencies (2 min)

```bash
source venv/bin/activate
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```

---

## Step 3: Configure Environment (1 min)

Add to `.env`:

```env
YOUTUBE_ENABLED=true
YOUTUBE_CATEGORY_ID=28
YOUTUBE_DEFAULT_TAGS=coding,programming,tech,education
YOUTUBE_PRIVACY_STATUS=public
```

---

## Step 4: Update flow_main.py (5 min)

Replace the **Stage 2** section (lines 58-77) with:

```python
elif current_stage == 2:
    logging.info("Stage 2: Starting video editing...")
    bot.send_message("Ready to edit the video")
    assets = db.get_raedy_assests()

    # Generate metadata
    video_title = Utils.generate_video_title(assets)
    video_description = Utils.generate_video_description(assets)

    # Edit video
    editor = DynamicVideoEditor(
        video_path=r"/home/ubuntu/mainrepo/stewie_v1/video_assests/video_without_audio.webm",
        output_path="output_final_video.mp4",
        dialogue_data=assets,
    )
    editor.edit()
    logging.info("Video editing completed.")

    # Upload to YouTube
    try:
        from youtube_uploader import YouTubeUploader
        import os

        if os.getenv('YOUTUBE_ENABLED', 'false').lower() == 'true':
            uploader = YouTubeUploader()
            video_id = uploader.upload_video(
                video_path="output_final_video.mp4",
                title=video_title,
                description=video_description
            )

            if video_id:
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                bot.send_message(f"✅ Video uploaded to YouTube!\n{video_url}")
                logging.info(f"Video uploaded: {video_id}")
            else:
                bot.send_message("❌ YouTube upload failed. Check logs.")
        else:
            logging.info("YouTube upload disabled")

    except Exception as e:
        logging.error(f"YouTube upload error: {e}")
        bot.send_message(f"❌ YouTube error: {str(e)}")

    # Send video via Telegram as backup
    try:
        bot.send_message("Sending video file...")
        bot.send_video_file("output_final_video.mp4")
    except Exception as e:
        logging.error(f"Error sending video: {e}")

    # Cleanup
    db.truncate_dialouge_stage()
    Utils.archive_audio_assets()
```

---

## Step 5: First Run (2 min)

1. Run the bot: `python3 flow_main.py`
2. When uploading first video, browser will open
3. Sign in with your YouTube channel account
4. Grant permissions
5. Done! Future uploads are automatic

---

## What You Get

✅ **Automatic YouTube uploads** after video editing
✅ **SEO-optimized titles** from dialogue content
✅ **Full transcripts** in video descriptions
✅ **Telegram notification** with YouTube link
✅ **Backup video file** sent via Telegram
✅ **Progress tracking** in logs

---

## Limits

- **6 videos/day** (free tier)
- **10,000 API quota units/day**
- Request increase for more

---

## Privacy Settings

Edit `.env` to change:

```env
YOUTUBE_PRIVACY_STATUS=public    # Anyone can watch
YOUTUBE_PRIVACY_STATUS=unlisted  # Only people with link
YOUTUBE_PRIVACY_STATUS=private   # Only you
```

---

## Manual Upload

Upload any video manually:

```bash
python3 youtube_uploader.py video.mp4 "My Title" "My Description"
```

---

## Troubleshooting

**"Invalid credentials"**
- Re-download `client_secrets.json`
- Delete `youtube_token.pickle` and re-authenticate

**"Quota exceeded"**
- Wait until midnight PT for reset
- Or request quota increase

**"ModuleNotFoundError"**
```bash
pip install google-api-python-client google-auth-oauthlib
```

---

## Full Documentation

See `YOUTUBE_INTEGRATION.md` for detailed guide

---

## Cost: $0

YouTube API is **completely free** (vs AWS EC2 costs)

**Ready to go? Follow the 5 steps above! 🚀**
