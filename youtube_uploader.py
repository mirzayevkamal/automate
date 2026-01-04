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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class YouTubeUploader:
    """
    YouTube API v3 uploader for automated video publishing
    """

    # YouTube API scopes
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

    # YouTube video categories
    # Full list: https://developers.google.com/youtube/v3/docs/videoCategories/list
    CATEGORIES = {
        'education': '27',
        'science_tech': '28',
        'howto': '26',
        'entertainment': '24',
        'gaming': '20'
    }

    def __init__(self):
        """Initialize YouTube uploader with credentials"""
        self.setup_logging()
        self.youtube = None
        self.authenticate()

    def setup_logging(self):
        """Set up logging configuration"""
        os.makedirs('runtime_logs', exist_ok=True)
        self.logger = logging.getLogger("YouTubeUploader")
        self.logger.setLevel(logging.INFO)

        handler = logging.FileHandler('runtime_logs/youtube_uploader.log')
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.info("YouTube Uploader initialized")

    def authenticate(self):
        """
        Authenticate with YouTube API using OAuth 2.0

        First run: Opens browser for user consent
        Subsequent runs: Uses saved token
        """
        creds = None
        token_file = 'youtube_token.pickle'
        client_secrets = 'client_secrets.json'

        # Check if we have saved credentials
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
                self.logger.info("Loaded existing YouTube credentials")

        # If credentials don't exist or are invalid, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.logger.info("Refreshing expired YouTube token...")
                creds.refresh(Request())
            else:
                if not os.path.exists(client_secrets):
                    error_msg = f"Missing {client_secrets}. Download from Google Cloud Console."
                    self.logger.error(error_msg)
                    raise FileNotFoundError(error_msg)

                self.logger.info("Starting OAuth 2.0 flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets, self.SCOPES
                )
                # Run local server for OAuth callback
                creds = flow.run_local_server(port=8080)
                self.logger.info("OAuth 2.0 authentication successful")

            # Save credentials for future use
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
                self.logger.info("Saved YouTube credentials to file")

        # Build YouTube API client
        self.youtube = build('youtube', 'v3', credentials=creds)
        self.logger.info("YouTube API client ready")

    def upload_video(
        self,
        video_path,
        title=None,
        description=None,
        tags=None,
        category_id=None,
        privacy_status=None
    ):
        """
        Upload a video to YouTube

        Args:
            video_path (str): Path to video file
            title (str): Video title (max 100 chars)
            description (str): Video description (max 5000 chars)
            tags (list): List of tags (max 500 chars total)
            category_id (str): YouTube category ID
            privacy_status (str): 'public', 'private', or 'unlisted'

        Returns:
            str: Video ID if successful, None if failed
        """

        # Validate video file exists
        if not os.path.exists(video_path):
            self.logger.error(f"Video file not found: {video_path}")
            return None

        # Get file size for logging
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        self.logger.info(f"Uploading video: {video_path} ({file_size_mb:.2f} MB)")

        # Set defaults from environment or fallback values
        if title is None:
            title = os.getenv('YOUTUBE_DEFAULT_TITLE',
                             f"Stewie & Peter: Coding Tutorial - {datetime.now().strftime('%Y-%m-%d')}")

        if description is None:
            description = os.getenv('YOUTUBE_DEFAULT_DESCRIPTION',
                                   "Stewie and Peter explain coding concepts in a fun and engaging way!")

        if tags is None:
            tags_str = os.getenv('YOUTUBE_DEFAULT_TAGS', 'coding,programming,tutorial')
            tags = [tag.strip() for tag in tags_str.split(',')]

        if category_id is None:
            category_id = os.getenv('YOUTUBE_CATEGORY_ID', self.CATEGORIES['science_tech'])

        if privacy_status is None:
            privacy_status = os.getenv('YOUTUBE_PRIVACY_STATUS', 'public')

        # Ensure title is within YouTube's limit
        if len(title) > 100:
            title = title[:97] + "..."
            self.logger.warning(f"Title truncated to 100 characters")

        # Build video metadata
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False,
            }
        }

        # Create media upload object
        media = MediaFileUpload(
            video_path,
            mimetype='video/mp4',
            resumable=True,
            chunksize=1024*1024  # 1MB chunks
        )

        try:
            self.logger.info("Initiating YouTube upload...")

            # Execute upload request
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )

            # Upload with progress tracking
            response = None
            last_progress = 0

            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    # Log every 25% progress
                    if progress >= last_progress + 25:
                        self.logger.info(f"Upload progress: {progress}%")
                        last_progress = progress

            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            self.logger.info(f"✅ Upload successful! Video ID: {video_id}")
            self.logger.info(f"📺 Video URL: {video_url}")

            return video_id

        except HttpError as e:
            self.logger.error(f"YouTube API error: {e}")
            if e.resp.status == 403:
                self.logger.error("Quota exceeded or insufficient permissions")
            elif e.resp.status == 401:
                self.logger.error("Authentication failed. Delete youtube_token.pickle and re-authenticate")
            return None

        except Exception as e:
            self.logger.error(f"Upload failed: {e}")
            return None

    def get_video_info(self, video_id):
        """
        Get information about an uploaded video

        Args:
            video_id (str): YouTube video ID

        Returns:
            dict: Video metadata
        """
        try:
            request = self.youtube.videos().list(
                part='snippet,status,statistics',
                id=video_id
            )
            response = request.execute()

            if response['items']:
                return response['items'][0]
            return None

        except HttpError as e:
            self.logger.error(f"Error fetching video info: {e}")
            return None

    def update_video(self, video_id, title=None, description=None, tags=None):
        """
        Update an existing video's metadata

        Args:
            video_id (str): YouTube video ID
            title (str): New title (optional)
            description (str): New description (optional)
            tags (list): New tags (optional)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # First, get current video data
            current = self.get_video_info(video_id)
            if not current:
                self.logger.error(f"Video {video_id} not found")
                return False

            # Update only provided fields
            snippet = current['snippet']
            if title:
                snippet['title'] = title
            if description:
                snippet['description'] = description
            if tags:
                snippet['tags'] = tags

            # Execute update
            request = self.youtube.videos().update(
                part='snippet',
                body={
                    'id': video_id,
                    'snippet': snippet
                }
            )
            request.execute()

            self.logger.info(f"✅ Video {video_id} updated successfully")
            return True

        except HttpError as e:
            self.logger.error(f"Error updating video: {e}")
            return False


# CLI usage for manual uploads
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python youtube_uploader.py <video_path> [title] [description]")
        print("\nExample:")
        print("  python youtube_uploader.py output_final_video.mp4 'My Title' 'My Description'")
        sys.exit(1)

    video_path = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else None
    description = sys.argv[3] if len(sys.argv) > 3 else None

    print("🚀 Starting YouTube upload...")
    uploader = YouTubeUploader()

    video_id = uploader.upload_video(
        video_path=video_path,
        title=title,
        description=description
    )

    if video_id:
        print(f"\n✅ Success! Video uploaded to:")
        print(f"📺 https://www.youtube.com/watch?v={video_id}")
    else:
        print("\n❌ Upload failed. Check runtime_logs/youtube_uploader.log for details")
        sys.exit(1)
