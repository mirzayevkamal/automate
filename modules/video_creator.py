"""
Video creation with visuals, audio, and subtitles
"""

import os
import logging
import requests
from pathlib import Path
from moviepy.editor import (
    VideoFileClip, AudioFileClip, ImageClip, TextClip,
    CompositeVideoClip, CompositeAudioClip, ColorClip,
    concatenate_videoclips
)
from PIL import Image, ImageDraw, ImageFont
import numpy as np

class VideoCreator:
    """Create videos from scripts and audio"""

    def __init__(self, config):
        self.config = config['video']
        self.logger = logging.getLogger(__name__)
        self.resolution = tuple(self.config['resolution'])
        self.fps = self.config['fps']

    def create_video(self, script_data, audio_path, output_path, topic):
        """
        Create a complete video

        Args:
            script_data (dict): Generated script data
            audio_path (str): Path to voiceover audio
            output_path (str): Path to save final video
            topic (str): Video topic

        Returns:
            str: Path to created video
        """
        self.logger.info("Creating video...")

        # Create output directory
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        try:
            # Load audio to get duration
            audio = AudioFileClip(audio_path)
            duration = audio.duration

            # Create background
            background = self._create_background(duration, topic)

            # Create subtitles
            subtitle_clips = []
            if self.config['subtitles']['enabled']:
                subtitle_clips = self._create_subtitles(
                    script_data['full_script'],
                    duration
                )

            # Create intro
            clips = []
            if self.config['intro']['enabled']:
                intro = self._create_intro()
                clips.append(intro)

            # Main content
            clips.append(background)

            # Create outro
            if self.config['outro']['enabled']:
                outro = self._create_outro()
                clips.append(outro)

            # Combine clips
            if len(clips) > 1:
                video = concatenate_videoclips(clips)
            else:
                video = background

            # Add subtitles
            if subtitle_clips:
                video = CompositeVideoClip([video] + subtitle_clips)

            # Add audio
            video = video.set_audio(audio)

            # Write final video
            self.logger.info(f"Rendering video to: {output_path}")
            video.write_videofile(
                output_path,
                codec=self.config['codec'],
                fps=self.fps,
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                logger=None  # Suppress moviepy logs
            )

            self.logger.info("Video created successfully")
            return output_path

        except Exception as e:
            self.logger.error(f"Error creating video: {e}")
            raise

    def _create_background(self, duration, topic):
        """Create background visual"""
        bg_config = self.config['background']
        bg_type = bg_config['type']

        if bg_type == 'gradient':
            return self._create_gradient_background(duration)
        elif bg_type == 'solid':
            return self._create_solid_background(duration)
        elif bg_type == 'stock':
            return self._create_stock_background(duration, topic)
        else:
            # Default to gradient
            return self._create_gradient_background(duration)

    def _create_gradient_background(self, duration):
        """Create a gradient background"""
        colors = self.config['background'].get('gradient_colors', ['#667eea', '#764ba2'])

        # Convert hex to RGB
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        color1 = hex_to_rgb(colors[0])
        color2 = hex_to_rgb(colors[1])

        # Create gradient image
        width, height = self.resolution
        gradient = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(gradient)

        for y in range(height):
            ratio = y / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Save temporary image
        temp_path = "temp/gradient_bg.png"
        Path(temp_path).parent.mkdir(exist_ok=True)
        gradient.save(temp_path)

        # Create clip
        clip = ImageClip(temp_path).set_duration(duration)
        return clip

    def _create_solid_background(self, duration):
        """Create solid color background"""
        color = self.config['background'].get('solid_color', '#000000')

        # Convert hex to RGB
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))

        clip = ColorClip(size=self.resolution, color=rgb, duration=duration)
        return clip

    def _create_stock_background(self, duration, topic):
        """Create background from stock footage"""
        # For now, use gradient as fallback
        # TODO: Implement Pexels/Pixabay integration
        self.logger.warning("Stock footage not implemented yet, using gradient")
        return self._create_gradient_background(duration)

    def _create_subtitles(self, text, total_duration):
        """Create animated subtitles"""
        subtitle_config = self.config['subtitles']
        style = subtitle_config['style']

        if style == 'word_by_word':
            return self._create_word_by_word_subtitles(text, total_duration, subtitle_config)
        elif style == 'sentence':
            return self._create_sentence_subtitles(text, total_duration, subtitle_config)
        else:
            return []

    def _create_word_by_word_subtitles(self, text, duration, config):
        """Create word-by-word animated subtitles"""
        words = text.split()
        word_duration = duration / len(words)

        clips = []
        current_time = 0

        for word in words:
            try:
                clip = (
                    TextClip(
                        word,
                        fontsize=config['font_size'],
                        color=config['color'],
                        font=config.get('font', 'Arial-Bold'),
                        stroke_color=config.get('stroke_color'),
                        stroke_width=config.get('stroke_width', 2)
                    )
                    .set_start(current_time)
                    .set_duration(word_duration)
                    .set_position(('center', config.get('position', 'center')))
                    .crossfadein(0.1)
                    .crossfadeout(0.1)
                )
                clips.append(clip)
                current_time += word_duration
            except Exception as e:
                self.logger.warning(f"Could not create subtitle for word '{word}': {e}")

        return clips

    def _create_sentence_subtitles(self, text, duration, config):
        """Create sentence-by-sentence subtitles"""
        # Simple implementation: split by periods
        sentences = [s.strip() + '.' for s in text.split('.') if s.strip()]
        sentence_duration = duration / len(sentences) if sentences else duration

        clips = []
        current_time = 0

        for sentence in sentences:
            try:
                clip = (
                    TextClip(
                        sentence,
                        fontsize=config['font_size'] - 20,
                        color=config['color'],
                        font=config.get('font', 'Arial-Bold'),
                        method='caption',
                        size=(self.resolution[0] * 0.8, None),
                        stroke_color=config.get('stroke_color'),
                        stroke_width=config.get('stroke_width', 2)
                    )
                    .set_start(current_time)
                    .set_duration(sentence_duration)
                    .set_position(('center', 'bottom'))
                )
                clips.append(clip)
                current_time += sentence_duration
            except Exception as e:
                self.logger.warning(f"Could not create subtitle for sentence: {e}")

        return clips

    def _create_intro(self):
        """Create intro sequence"""
        intro_config = self.config['intro']
        duration = intro_config['duration']
        text = intro_config['text']

        # Create gradient background
        bg = self._create_gradient_background(duration)

        # Add text
        try:
            title = (
                TextClip(
                    text,
                    fontsize=100,
                    color='white',
                    font='Arial-Bold'
                )
                .set_duration(duration)
                .set_position('center')
                .crossfadein(0.5)
                .crossfadeout(0.5)
            )

            intro = CompositeVideoClip([bg, title])
            return intro
        except Exception as e:
            self.logger.warning(f"Could not create intro: {e}")
            return bg

    def _create_outro(self):
        """Create outro sequence"""
        outro_config = self.config['outro']
        duration = outro_config['duration']
        text = outro_config['text']

        # Create gradient background
        bg = self._create_gradient_background(duration)

        # Add text
        try:
            cta = (
                TextClip(
                    text,
                    fontsize=80,
                    color='yellow',
                    font='Arial-Bold'
                )
                .set_duration(duration)
                .set_position('center')
                .crossfadein(0.5)
            )

            outro = CompositeVideoClip([bg, cta])
            return outro
        except Exception as e:
            self.logger.warning(f"Could not create outro: {e}")
            return bg
