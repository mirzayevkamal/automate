# YouTube Integration Guide

This guide explains how to modify Stewie_it v1 to automatically upload videos to YouTube.

---

## Overview

**Changes needed:**
1. Set up YouTube Data API v3
2. Create OAuth 2.0 credentials
3. Install Google API Python client
4. Add YouTube uploader module
5. Integrate with existing workflow

**Benefits over Instagram:**
- ✅ File size limit: 256GB (vs Instagram's 100MB)
- ✅ No file size issues with Telegram's 50MB limit
- ✅ Better for longer content (15 min+ videos)
- ✅ More discovery features (SEO, recommendations)
- ✅ Easier API integration (no complex Graph API setup)

---

## Step 1: Set Up YouTube Data API

### 1.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Create Project"** or select existing project
3. Name it (e.g., "Stewie Video Bot")
4. Click **Create**

### 1.2 Enable YouTube Data API v3

1. In your project, go to **APIs & Services** → **Library**
2. Search for **"YouTube Data API v3"**
3. Click on it and press **Enable**

### 1.3 Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. If prompted, configure OAuth consent screen:
   - **User Type**: External
   - **App name**: Stewie Video Bot
   - **User support email**: Your email
   - **Developer contact**: Your email
   - **Scopes**: Add `../auth/youtube.upload`
   - **Test users**: Add your Google account email
   - Click **Save and Continue**

4. Back to Create OAuth client ID:
   - **Application type**: Desktop app
   - **Name**: Stewie Desktop Client
   - Click **Create**

5. **Download JSON file**:
   - Click the download icon next to your credential
   - Save as `client_secrets.json`
   - Upload this file to your project directory

---

## Step 2: Install YouTube API Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install Google API client
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```

Update `requirements.txt`:
```bash
echo "google-api-python-client>=2.0.0" >> requirements.txt
echo "google-auth-oauthlib>=0.5.0" >> requirements.txt
echo "google-auth-httplib2>=0.1.0" >> requirements.txt
```

---

## Step 3: Update Environment Variables

Add YouTube configuration to `.env`:

```env
# Telegram (existing)
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id

# YouTube Configuration
YOUTUBE_ENABLED=true
YOUTUBE_CATEGORY_ID=28  # Science & Technology category
YOUTUBE_DEFAULT_TAGS=coding,programming,tech,education,tutorial
YOUTUBE_PRIVACY_STATUS=public  # Options: public, private, unlisted
```

---

## Step 4: Create YouTube Uploader Module

Create a new file `youtube_uploader.py` in your project directory (see implementation below).

---

## Step 5: Modify `flow_main.py`

Update the video completion section to include YouTube upload:

```python
# In flow_main.py, around line 72-76
elif current_stage == 2:
    logging.info("Stage 2: Starting video editing...")
    bot.send_message("Ready to edit the video")
    assets = db.get_raedy_assests()

    # Generate video title and description from dialogue
    video_title = Utils.generate_video_title(assets)
    video_description = Utils.generate_video_description(assets)

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
        uploader = YouTubeUploader()

        video_id = uploader.upload_video(
            video_path="output_final_video.mp4",
            title=video_title,
            description=video_description
        )

        if video_id:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            bot.send_message(f"✅ Video uploaded to YouTube!\n{video_url}")
            logging.info(f"Video uploaded successfully: {video_id}")
        else:
            bot.send_message("❌ YouTube upload failed. Check logs.")

    except Exception as e:
        logging.error(f"Error uploading to YouTube: {e}")
        bot.send_message(f"❌ YouTube upload error: {str(e)}")

    # Still send via Telegram as backup
    try:
        bot.send_message("Also sending you the video file...")
        bot.send_video_file("output_final_video.mp4")
    except Exception as e:
        logging.error(f"Error while sending the video: {e}")

    db.truncate_dialouge_stage()
    Utils.archive_audio_assets()
```

---

## Step 6: Add Helper Functions to `utils.py`

Add these methods to the `Utils` class:

```python
@staticmethod
def generate_video_title(dialogue_data):
    """Generate YouTube title from dialogue content"""
    # Extract first dialogue to determine topic
    if dialogue_data and len(dialogue_data) > 0:
        first_line = dialogue_data[0].get('sentence', '')
        # Extract topic after character name
        topic = first_line.split(':', 1)[-1].strip()
        # Truncate to ~60 chars for optimal YouTube SEO
        if len(topic) > 60:
            topic = topic[:57] + "..."
        return f"{topic} | Stewie & Peter Explain"
    return "Coding Tutorial | Stewie & Peter Explain"

@staticmethod
def generate_video_description(dialogue_data):
    """Generate YouTube description from dialogue"""
    description_parts = [
        "🎮 Stewie and Peter explain coding concepts in a fun way!",
        "",
        "📝 Transcript:",
        ""
    ]

    for item in dialogue_data:
        sentence = item.get('sentence', '')
        description_parts.append(sentence)

    description_parts.extend([
        "",
        "---",
        "🔔 Subscribe for more coding tutorials!",
        "💬 Follow us on Instagram: @stewie_codes_absurd",
        "",
        "#coding #programming #tutorial #tech #education"
    ])

    return "\n".join(description_parts)
```

---

## Step 7: First-Time Authentication

The first time you run the YouTube upload:

1. The script will open a browser window
2. **Sign in** with your YouTube channel's Google account
3. **Grant permissions** for video upload
4. A `youtube_token.json` file will be created (stores auth token)
5. Future uploads will use this token automatically

**Important:** Add to `.gitignore`:
```
youtube_token.json
client_secrets.json
```

---

## Usage

### Automatic Upload

Once configured, every video will automatically:
1. ✅ Be edited and assembled
2. ✅ Upload to YouTube
3. ✅ Send YouTube link via Telegram
4. ✅ Send video file via Telegram (as backup)

### Manual Upload Only

If you want to disable auto-upload and upload manually:

```bash
# In .env
YOUTUBE_ENABLED=false
```

Then upload manually:
```bash
python3 youtube_uploader.py output_final_video.mp4 "Your Title" "Your Description"
```

---

## YouTube API Quotas

**Free tier limits:**
- **10,000 quota units/day**
- Video upload = **1,600 units**
- **~6 videos/day maximum**

If you need more:
- Request quota increase from Google Cloud Console
- Or create multiple projects with different credentials

---

## Privacy Settings

Configure in `.env`:

```env
# Options:
YOUTUBE_PRIVACY_STATUS=public    # Public, anyone can see
YOUTUBE_PRIVACY_STATUS=unlisted  # Only people with link
YOUTUBE_PRIVACY_STATUS=private   # Only you can see
```

---

## Troubleshooting

### "Invalid credentials" error
- Re-download `client_secrets.json` from Google Cloud Console
- Delete `youtube_token.json` and re-authenticate

### "Quota exceeded" error
- You've hit the 10,000 units/day limit
- Wait until midnight Pacific Time for quota reset
- Or request quota increase

### "Video processing failed"
- Check video file format (should be .mp4)
- Verify FFmpeg encoding settings
- Check file size (max 256GB, but practically <2GB recommended)

### OAuth consent screen verification
- During testing, your app works with test users only
- For public use, submit app for verification (takes 1-2 weeks)
- Or keep it in testing mode with up to 100 test users

---

## Advanced: Custom Thumbnails

To add custom thumbnails:

1. Enable in Google Cloud Console
2. Verify your YouTube channel (phone verification)
3. Modify `youtube_uploader.py` to include thumbnail upload:

```python
# After video upload succeeds
youtube.thumbnails().set(
    videoId=video_id,
    media_body=MediaFileUpload('thumbnail.jpg')
).execute()
```

---

## Cost Comparison

**YouTube API:**
- ✅ **Free** (10,000 units/day)
- ✅ 6+ videos/day at no cost
- ✅ Unlimited storage
- ✅ No bandwidth costs

**Instagram Graph API:**
- ⚠️ More complex setup
- ⚠️ Business account required
- ⚠️ 100MB file size limit
- ⚠️ Session management issues with EC2 IP rotation

**Winner:** YouTube is better for this use case!

---

## Next Steps

1. Create Google Cloud project and enable API
2. Download `client_secrets.json`
3. Install dependencies
4. Create `youtube_uploader.py` module
5. Update `flow_main.py` and `utils.py`
6. Run and authenticate on first upload
7. Enjoy automatic YouTube uploads! 🎉
