"""
YouTube upload functionality
"""

import os
import logging
import pickle
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

class YouTubeUploader:
    """Upload videos to YouTube"""

    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

    def __init__(self, config):
        self.config = config['youtube']
        self.logger = logging.getLogger(__name__)
        self.youtube = None
        self.authenticate()

    def authenticate(self):
        """Authenticate with YouTube API"""
        creds = None
        token_file = 'youtube_token.pickle'
        client_secrets = 'client_secrets.json'

        # Load existing credentials
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
                self.logger.info("Loaded existing YouTube credentials")

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.logger.info("Refreshing expired token...")
                creds.refresh(Request())
            else:
                if not os.path.exists(client_secrets):
                    raise FileNotFoundError(f"Missing {client_secrets}. Download from Google Cloud Console.")

                self.logger.info("Starting OAuth 2.0 flow...")
                flow = InstalledAppFlow.from_client_secrets_file(client_secrets, self.SCOPES)
                creds = flow.run_local_server(port=8080)

            # Save credentials
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
                self.logger.info("Saved credentials")

        self.youtube = build('youtube', 'v3', credentials=creds)
        self.logger.info("YouTube API client ready")

    def upload_video(self, video_path, script_data, topic):
        """
        Upload video to YouTube

        Args:
            video_path (str): Path to video file
            script_data (dict): Generated script data
            topic (str): Original topic

        Returns:
            str: Video ID if successful, None if failed
        """
        if not self.config['enabled']:
            self.logger.info("YouTube upload is disabled")
            return None

        self.logger.info(f"Uploading video: {video_path}")

        # Generate metadata
        title = self._generate_title(script_data, topic)
        description = self._generate_description(script_data, topic)
        tags = self._generate_tags(script_data, topic)

        # Build request body
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': self.config['category_id']
            },
            'status': {
                'privacyStatus': self.config['privacy_status'],
                'selfDeclaredMadeForKids': False,
            }
        }

        # Create media upload
        media = MediaFileUpload(
            video_path,
            mimetype='video/mp4',
            resumable=True,
            chunksize=1024*1024
        )

        try:
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )

            # Upload with progress
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    self.logger.info(f"Upload progress: {progress}%")

            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            self.logger.info(f"✅ Video uploaded successfully!")
            self.logger.info(f"📺 URL: {video_url}")
            self.logger.info(f"🆔 Video ID: {video_id}")

            return video_id

        except HttpError as e:
            self.logger.error(f"YouTube API error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Upload failed: {e}")
            return None

    def _generate_title(self, script_data, topic):
        """Generate YouTube title"""
        template = self.config.get('title_template', '{topic}')

        # Use script title if available, otherwise topic
        title_text = script_data.get('title', topic)

        title = template.format(
            topic=title_text,
            year=datetime.now().year
        )

        # Ensure within YouTube's limit
        if len(title) > 100:
            title = title[:97] + "..."

        return title

    def _generate_description(self, script_data, topic):
        """Generate YouTube description"""
        template = self.config.get('description_template', '{transcript}')

        transcript = script_data.get('full_script', '')
        description_text = script_data.get('description', '')

        description = template.format(
            topic=topic,
            transcript=transcript,
            description=description_text
        )

        # Ensure within YouTube's limit
        if len(description) > 5000:
            description = description[:4997] + "..."

        return description

    def _generate_tags(self, script_data, topic):
        """Generate YouTube tags"""
        tags = []

        # Add script-generated tags
        if script_data.get('tags'):
            tags.extend(script_data['tags'])

        # Add configured additional tags
        additional = self.config.get('tags_additional', [])
        tags.extend(additional)

        # Add topic as tag
        if topic and topic not in tags:
            tags.append(topic)

        # Ensure unique and within limits
        tags = list(dict.fromkeys(tags))  # Remove duplicates
        tags = tags[:15]  # YouTube limit is ~500 chars total, ~15 tags typical

        return tags


if __name__ == "__main__":
    # Test YouTube uploader
    import yaml

    with open('../config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    uploader = YouTubeUploader(config)
    print("✅ YouTube uploader initialized")
