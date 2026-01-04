"""
Topic queue management system
"""

import os
import logging
import random
from pathlib import Path

class TopicManager:
    """Manage video topics queue"""

    def __init__(self, config):
        self.config = config['topics']
        self.logger = logging.getLogger(__name__)
        self.topics_file = self.config['file']
        self.used_topics_file = f"{self.topics_file}.used"
        self.topics = []
        self.used_topics = []

        self._load_topics()

    def _load_topics(self):
        """Load topics from file"""
        # Load available topics
        if os.path.exists(self.topics_file):
            with open(self.topics_file, 'r') as f:
                lines = f.readlines()

            # Filter out comments and empty lines
            self.topics = [
                line.strip()
                for line in lines
                if line.strip() and not line.strip().startswith('#')
            ]

            self.logger.info(f"Loaded {len(self.topics)} topics from {self.topics_file}")
        else:
            self.logger.warning(f"Topics file not found: {self.topics_file}")
            self.topics = []

        # Load used topics
        if os.path.exists(self.used_topics_file):
            with open(self.used_topics_file, 'r') as f:
                self.used_topics = [line.strip() for line in f.readlines() if line.strip()]
            self.logger.info(f"Loaded {len(self.used_topics)} used topics")
        else:
            self.used_topics = []

        # Shuffle if configured
        if self.config.get('shuffle', False):
            random.shuffle(self.topics)
            self.logger.info("Topics shuffled")

    def get_next_topic(self):
        """
        Get the next topic to process

        Returns:
            str or None: Next topic, or None if no topics available
        """
        # Reload topics in case file was updated
        self._load_topics()

        # Get topics that haven't been used
        available = [t for t in self.topics if t not in self.used_topics]

        if not available:
            if self.config.get('repeat_when_exhausted', True):
                self.logger.info("All topics used, resetting queue")
                self._reset_used_topics()
                available = self.topics
            else:
                self.logger.warning("No topics available and repeat is disabled")
                return None

        if not available:
            return None

        # Get first available topic
        topic = available[0]
        self.logger.info(f"Next topic: {topic}")

        return topic

    def mark_topic_used(self, topic):
        """Mark a topic as used"""
        if topic not in self.used_topics:
            self.used_topics.append(topic)

            # Append to used topics file
            with open(self.used_topics_file, 'a') as f:
                f.write(f"{topic}\n")

            self.logger.info(f"Topic marked as used: {topic}")

    def mark_topic_failed(self, topic):
        """Mark a topic as failed (don't mark as used)"""
        self.logger.warning(f"Topic failed: {topic}")
        # Don't add to used topics so it can be retried

    def _reset_used_topics(self):
        """Reset the used topics list"""
        if os.path.exists(self.used_topics_file):
            # Backup old used topics
            backup = f"{self.used_topics_file}.backup"
            if os.path.exists(backup):
                os.remove(backup)
            os.rename(self.used_topics_file, backup)

        self.used_topics = []
        self.logger.info("Used topics reset")

    def get_topics_count(self):
        """Get count of total and remaining topics"""
        return {
            'total': len(self.topics),
            'used': len(self.used_topics),
            'remaining': len([t for t in self.topics if t not in self.used_topics])
        }

    def add_topic(self, topic):
        """Add a new topic to the list"""
        if topic not in self.topics:
            self.topics.append(topic)

            # Append to topics file
            with open(self.topics_file, 'a') as f:
                f.write(f"{topic}\n")

            self.logger.info(f"Topic added: {topic}")

    def remove_topic(self, topic):
        """Remove a topic from the list"""
        if topic in self.topics:
            self.topics.remove(topic)

            # Rewrite topics file
            with open(self.topics_file, 'w') as f:
                for t in self.topics:
                    f.write(f"{t}\n")

            self.logger.info(f"Topic removed: {topic}")


if __name__ == "__main__":
    # Test topic manager
    import yaml

    with open('../config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    manager = TopicManager(config)

    print("Topics count:", manager.get_topics_count())

    # Get next 5 topics
    for i in range(5):
        topic = manager.get_next_topic()
        if topic:
            print(f"{i+1}. {topic}")
            manager.mark_topic_used(topic)

    print("\nAfter using 5 topics:", manager.get_topics_count())
