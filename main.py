#!/usr/bin/env python3
"""
YouTube Content Automation System
Main entry point
"""

import os
import sys
import logging
import argparse
import yaml
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Import modules
from modules.script_generator import ScriptGenerator
from modules.voice_generator import VoiceGenerator
from modules.video_creator import VideoCreator
from modules.youtube_uploader import YouTubeUploader
from modules.topic_manager import TopicManager
from modules.scheduler import VideoScheduler

# Load environment variables
load_dotenv()

def setup_logging(config):
    """Set up logging configuration"""
    log_config = config['system']
    log_dir = log_config['logs_dir']
    Path(log_dir).mkdir(exist_ok=True)

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_config['log_level']))

    # File handler
    if log_config.get('log_to_file', True):
        log_file = os.path.join(log_dir, f"automation_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Console handler
    if log_config.get('log_to_console', True):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger

def create_video_job(config, topic_manager, script_gen, voice_gen, video_creator, youtube_uploader):
    """Main job function to create one video"""
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Starting video generation job")
    logger.info("=" * 60)

    try:
        # Get next topic
        topic = topic_manager.get_next_topic()
        if not topic:
            logger.error("No topics available")
            return False

        logger.info(f"Topic: {topic}")

        # Create temp and output directories
        temp_dir = config['system']['temp_dir']
        output_dir = config['system']['output_dir']
        Path(temp_dir).mkdir(exist_ok=True)
        Path(output_dir).mkdir(exist_ok=True)

        # Generate timestamp for files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = f"video_{timestamp}"

        # Step 1: Generate script
        logger.info("Step 1/4: Generating script...")
        script_data = script_gen.generate_script(topic)
        logger.info(f"✓ Script generated: {len(script_data['full_script'])} characters")

        # Step 2: Generate voice
        logger.info("Step 2/4: Generating voice...")
        audio_path = os.path.join(temp_dir, f"{base_name}_audio.mp3")
        voice_gen.generate_voice(script_data['full_script'], audio_path)
        audio_duration = voice_gen.get_audio_duration(audio_path)
        logger.info(f"✓ Voice generated: {audio_duration:.1f} seconds")

        # Step 3: Create video
        logger.info("Step 3/4: Creating video...")
        video_path = os.path.join(output_dir, f"{base_name}.mp4")
        video_creator.create_video(script_data, audio_path, video_path, topic)
        logger.info(f"✓ Video created: {video_path}")

        # Step 4: Upload to YouTube
        if config['youtube']['enabled']:
            logger.info("Step 4/4: Uploading to YouTube...")
            video_id = youtube_uploader.upload_video(video_path, script_data, topic)

            if video_id:
                logger.info(f"✓ Video uploaded: https://youtube.com/watch?v={video_id}")

                # Mark topic as used
                topic_manager.mark_topic_used(topic)

                # Cleanup if configured
                if config['system'].get('cleanup_after_upload', False):
                    if os.path.exists(video_path):
                        os.remove(video_path)
                        logger.info("Video file cleaned up")
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                        logger.info("Audio file cleaned up")
            else:
                logger.error("Upload failed")
                topic_manager.mark_topic_failed(topic)
                return False
        else:
            logger.info("Step 4/4: YouTube upload disabled, video saved locally")
            topic_manager.mark_topic_used(topic)

        # Cleanup temp audio if configured
        if not config['system'].get('keep_audio', False):
            if os.path.exists(audio_path):
                os.remove(audio_path)

        logger.info("=" * 60)
        logger.info("✅ Job completed successfully!")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"❌ Job failed: {e}", exc_info=True)
        topic_manager.mark_topic_failed(topic)
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='YouTube Content Automation System')
    parser.add_argument('--config', default='config.yaml', help='Path to config file')
    parser.add_argument('--test', action='store_true', help='Run one test video')
    parser.add_argument('--run-once', action='store_true', help='Run one video and exit')
    parser.add_argument('--schedule', action='store_true', help='Run on schedule (continuous)')
    parser.add_argument('--topic', help='Generate video for specific topic (overrides queue)')

    args = parser.parse_args()

    # Load configuration
    if not os.path.exists(args.config):
        print(f"Error: Config file not found: {args.config}")
        sys.exit(1)

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    # Set up logging
    logger = setup_logging(config)
    logger.info("YouTube Content Automation System starting...")

    # Initialize components
    try:
        logger.info("Initializing components...")
        topic_manager = TopicManager(config)
        script_gen = ScriptGenerator(config)
        voice_gen = VoiceGenerator(config)
        video_creator = VideoCreator(config)
        youtube_uploader = YouTubeUploader(config)
        logger.info("✓ All components initialized")

        # Show topics count
        counts = topic_manager.get_topics_count()
        logger.info(f"Topics: {counts['remaining']} remaining of {counts['total']} total")

    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        sys.exit(1)

    # Define job function
    def job():
        create_video_job(config, topic_manager, script_gen, voice_gen, video_creator, youtube_uploader)

    # Run based on mode
    if args.topic:
        # Generate for specific topic
        logger.info(f"Generating video for topic: {args.topic}")
        # Temporarily override topic manager
        original_get = topic_manager.get_next_topic
        topic_manager.get_next_topic = lambda: args.topic
        job()

    elif args.test or args.run_once:
        # Run once
        logger.info("Running one video generation job...")
        success = job()
        sys.exit(0 if success else 1)

    elif args.schedule:
        # Run on schedule
        logger.info("Running in scheduled mode...")
        scheduler = VideoScheduler(config, job)
        scheduler.setup_schedule()

        next_run = scheduler.get_next_run_time()
        if next_run:
            logger.info(f"Next scheduled run: {next_run}")

        scheduler.run()

    else:
        # No mode specified, show help
        parser.print_help()
        print("\nExamples:")
        print("  python main.py --test              # Generate one test video")
        print("  python main.py --schedule          # Run on schedule (continuous)")
        print("  python main.py --topic 'Python'    # Generate for specific topic")

if __name__ == "__main__":
    main()
