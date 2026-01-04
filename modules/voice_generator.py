"""
AI voice generation for video narration
"""

import os
import logging
from pathlib import Path
from openai import OpenAI
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

class VoiceGenerator:
    """Generate AI voiceovers for video scripts"""

    def __init__(self, config):
        self.config = config['voice']
        self.logger = logging.getLogger(__name__)
        self.provider = self.config['provider']

        # Initialize provider client
        if self.provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found")
            self.client = OpenAI(api_key=api_key)

        elif self.provider == 'elevenlabs':
            api_key = os.getenv('ELEVENLABS_API_KEY')
            if not api_key:
                raise ValueError("ELEVENLABS_API_KEY not found")
            try:
                from elevenlabs import generate, set_api_key
                set_api_key(api_key)
                self.elevenlabs_generate = generate
            except ImportError:
                raise ImportError("elevenlabs package not installed. Run: pip install elevenlabs")

    def generate_voice(self, text, output_path):
        """
        Generate voiceover for the given text

        Args:
            text (str): Script text to convert to speech
            output_path (str): Path to save the audio file

        Returns:
            str: Path to generated audio file
        """
        self.logger.info(f"Generating voice using {self.provider}")

        # Create output directory
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        try:
            if self.provider == 'openai':
                return self._generate_openai(text, output_path)
            elif self.provider == 'elevenlabs':
                return self._generate_elevenlabs(text, output_path)
            elif self.provider == 'gtts':
                return self._generate_gtts(text, output_path)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

        except Exception as e:
            self.logger.error(f"Error generating voice: {e}")
            raise

    def _generate_openai(self, text, output_path):
        """Generate voice using OpenAI TTS"""
        settings = self.config['openai']

        self.logger.info(f"Using OpenAI TTS model: {settings['model']}, voice: {settings['voice']}")

        response = self.client.audio.speech.create(
            model=settings['model'],
            voice=settings['voice'],
            input=text,
            speed=settings.get('speed', 1.0)
        )

        # Save to file
        response.stream_to_file(output_path)
        self.logger.info(f"Voice generated: {output_path}")

        return output_path

    def _generate_elevenlabs(self, text, output_path):
        """Generate voice using ElevenLabs"""
        settings = self.config['elevenlabs']

        self.logger.info(f"Using ElevenLabs voice ID: {settings['voice_id']}")

        audio = self.elevenlabs_generate(
            text=text,
            voice=settings['voice_id'],
            model=settings['model']
        )

        # Save to file
        with open(output_path, 'wb') as f:
            f.write(audio)

        self.logger.info(f"Voice generated: {output_path}")
        return output_path

    def _generate_gtts(self, text, output_path):
        """Generate voice using Google TTS (free)"""
        settings = self.config['gtts']

        self.logger.info("Using Google TTS (free)")

        tts = gTTS(
            text=text,
            lang=settings.get('language', 'en'),
            slow=settings.get('slow', False)
        )

        tts.save(output_path)
        self.logger.info(f"Voice generated: {output_path}")

        return output_path

    def get_audio_duration(self, audio_path):
        """Get duration of audio file in seconds"""
        from pydub import AudioSegment

        audio = AudioSegment.from_file(audio_path)
        duration = len(audio) / 1000.0  # Convert ms to seconds

        return duration


if __name__ == "__main__":
    # Test voice generation
    import yaml

    with open('../config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    generator = VoiceGenerator(config)

    test_text = """
    Welcome to this tutorial! Today we're going to learn about Python programming.
    Python is one of the most popular programming languages in the world.
    It's easy to learn, powerful, and versatile.
    """

    output = "test_voice.mp3"
    generator.generate_voice(test_text, output)
    print(f"✅ Voice generated: {output}")

    duration = generator.get_audio_duration(output)
    print(f"Duration: {duration:.2f} seconds")
