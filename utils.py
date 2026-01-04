import os
import re
from typing import List
from datetime import datetime
import subprocess
import shutil
class Utils:
    """
    A utility class providing common helper functions for various tasks.
    """
    @staticmethod
    def stop_vm():
        try:
            subprocess.run(['sudo', '/sbin/shutdown', 'now'], check=True)
            print("Reboot command issued successfully.")
          
        except subprocess.CalledProcessError as e:
            print(f"Failed to reboot the VM: {e}")
            
        except Exception as e:
            print(f"An error occurred: {e}")
           

    @staticmethod
    def get_ordered_audio_files(folder_path: str) -> List[str]:
        """
        Returns a list of .mp3 filenames from the folder, ordered by the number in the filename.

        Example:
            Input: ['peter_audio_1.mp3', 'stewie_audio_2.mp3', 'peter_3.mp3']
            Output: ['peter_audio_1.mp3', 'stewie_audio_2.mp3', 'peter_3.mp3']
        """
        try:
            audio_files = [
                f for f in os.listdir(folder_path)
                if os.path.isfile(os.path.join(folder_path, f)) and f.endswith(".mp3")
            ]

            def extract_number(filename: str) -> int:
                match = re.search(r'(\d+)', filename)
                return int(match.group(1)) if match else float('inf')

            sorted_files = sorted(audio_files, key=extract_number)
            return sorted_files

        except Exception as e:
            print(f"[Utils] Error reading audio files from '{folder_path}': {e}")
            return []


    @staticmethod
    def archive_audio_assets():
        """
        Moves all files from 'audio_assets/' to 'archive/YYYY-MM-DD/' and ensures the source folder is empty.
        """
        source_dir = 'audio_assests'
        archive_root = 'archives_audios'
        today_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        target_dir = os.path.join(archive_root, today_str)

        try:
            os.makedirs(target_dir, exist_ok=True)

            for filename in os.listdir(source_dir):
                src_path = os.path.join(source_dir, filename)
                if os.path.isfile(src_path):
                    shutil.move(src_path, os.path.join(target_dir, filename))

            print(f"Archived files to {target_dir}.")
        except Exception as e:
            print(f"[Utils] Error archiving audio assets: {e}")

    @staticmethod
    def generate_video_title(dialogue_data):
        """
        Generate YouTube-optimized title from dialogue content

        Args:
            dialogue_data (list): List of dialogue dictionaries

        Returns:
            str: YouTube video title (max 100 chars)
        """
        if dialogue_data and len(dialogue_data) > 0:
            first_line = dialogue_data[0].get('sentence', '')
            # Extract topic after character name (Peter: or Stewie:)
            if ':' in first_line:
                topic = first_line.split(':', 1)[-1].strip()
            else:
                topic = first_line.strip()

            # Truncate to ~60 chars for optimal YouTube SEO
            if len(topic) > 60:
                topic = topic[:57] + "..."

            return f"{topic} | Stewie & Peter Explain"

        return "Coding Tutorial | Stewie & Peter Explain"

    @staticmethod
    def generate_video_description(dialogue_data):
        """
        Generate YouTube description from dialogue content

        Args:
            dialogue_data (list): List of dialogue dictionaries

        Returns:
            str: YouTube video description (max 5000 chars)
        """
        description_parts = [
            "🎮 Stewie and Peter explain coding concepts in a fun and engaging way!",
            "",
            "📝 Transcript:",
            ""
        ]

        # Add all dialogue lines
        for item in dialogue_data:
            sentence = item.get('sentence', '')
            if sentence:
                description_parts.append(sentence)

        # Add footer with call-to-action and hashtags
        description_parts.extend([
            "",
            "---",
            "🔔 Subscribe for more coding tutorials!",
            "💬 Follow us on Instagram: @stewie_codes_absurd",
            "👍 Like this video if you learned something new!",
            "💭 Comment what topic we should cover next!",
            "",
            "📚 More Resources:",
            "• GitHub: [Add your GitHub link]",
            "• Discord: [Add your Discord link]",
            "",
            "#coding #programming #tutorial #tech #education #python #javascript #webdev #learntocode #softwaredevelopment"
        ])

        description = "\n".join(description_parts)

        # Ensure description doesn't exceed YouTube's 5000 char limit
        if len(description) > 5000:
            description = description[:4997] + "..."

        return description

# Utils.archive_audio_assets()