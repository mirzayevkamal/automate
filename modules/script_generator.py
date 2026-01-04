"""
AI-powered script generation for YouTube videos
"""

import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ScriptGenerator:
    """Generate video scripts using AI"""

    def __init__(self, config):
        self.config = config['script']
        self.logger = logging.getLogger(__name__)

        # Initialize AI client
        if self.config['provider'] == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            self.client = OpenAI(api_key=api_key)
        else:
            raise ValueError(f"Unsupported provider: {self.config['provider']}")

    def generate_script(self, topic):
        """
        Generate a video script for the given topic

        Args:
            topic (str): The video topic

        Returns:
            dict: {
                'title': str,
                'hook': str,
                'main_content': str,
                'cta': str,
                'full_script': str,
                'tags': list,
                'description': str
            }
        """
        self.logger.info(f"Generating script for topic: {topic}")

        # Build the prompt
        prompt = self._build_prompt(topic)

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.config['model'],
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.config['temperature'],
                max_tokens=self.config['max_tokens']
            )

            script_text = response.choices[0].message.content
            self.logger.info("Script generated successfully")

            # Parse the response
            script_data = self._parse_script(script_text, topic)
            return script_data

        except Exception as e:
            self.logger.error(f"Error generating script: {e}")
            raise

    def _get_system_prompt(self):
        """Get the system prompt based on configuration"""
        style = self.config['style']
        tone = self.config['tone']
        length = self.config['target_length_seconds']

        return f"""You are an expert YouTube script writer specializing in {style} content.

Your scripts are:
- {tone} in tone
- Engaging and attention-grabbing
- Approximately {length} seconds when read aloud (~{length * 2.5} words)
- Optimized for viewer retention
- SEO-friendly

Output format:
TITLE: [Catchy, SEO-optimized title]
HOOK: [First 5-10 seconds - attention grabber]
MAIN: [Core content - educational and valuable]
CTA: [Call to action - subscribe, like, comment]
TAGS: [10 relevant SEO tags, comma-separated]
DESCRIPTION: [Brief 2-3 sentence description]
"""

    def _build_prompt(self, topic):
        """Build the user prompt"""
        include_hook = self.config.get('include_hook', True)
        include_cta = self.config.get('include_cta', True)

        prompt = f"""Create a YouTube video script about: {topic}

Requirements:
- Target length: ~{self.config['target_length_seconds']} seconds
- Style: {self.config['style']}
- Tone: {self.config['tone']}
"""

        if include_hook:
            prompt += "- Start with a strong hook to grab attention\n"
        if include_cta:
            prompt += "- End with a clear call-to-action\n"

        prompt += "\nMake it engaging, informative, and perfect for YouTube!"

        return prompt

    def _parse_script(self, script_text, topic):
        """Parse the AI-generated script into structured data"""
        lines = script_text.strip().split('\n')

        data = {
            'title': topic,
            'hook': '',
            'main_content': '',
            'cta': '',
            'full_script': '',
            'tags': [],
            'description': ''
        }

        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for section headers
            if line.startswith('TITLE:'):
                data['title'] = line.replace('TITLE:', '').strip()
            elif line.startswith('HOOK:'):
                current_section = 'hook'
                data['hook'] = line.replace('HOOK:', '').strip()
            elif line.startswith('MAIN:'):
                current_section = 'main'
                data['main_content'] = line.replace('MAIN:', '').strip()
            elif line.startswith('CTA:'):
                current_section = 'cta'
                data['cta'] = line.replace('CTA:', '').strip()
            elif line.startswith('TAGS:'):
                tags_text = line.replace('TAGS:', '').strip()
                data['tags'] = [tag.strip() for tag in tags_text.split(',')]
                current_section = None
            elif line.startswith('DESCRIPTION:'):
                current_section = 'description'
                data['description'] = line.replace('DESCRIPTION:', '').strip()
            elif current_section:
                # Continuation of current section
                data[current_section] += ' ' + line

        # Build full script
        parts = []
        if data['hook']:
            parts.append(data['hook'])
        if data['main_content']:
            parts.append(data['main_content'])
        if data['cta']:
            parts.append(data['cta'])

        data['full_script'] = ' '.join(parts).strip()

        # Fallback if parsing failed
        if not data['full_script']:
            data['full_script'] = script_text
            data['title'] = topic

        self.logger.debug(f"Parsed script: {len(data['full_script'])} characters")

        return data


if __name__ == "__main__":
    # Test the script generator
    import yaml

    with open('../config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    generator = ScriptGenerator(config)
    script = generator.generate_script("How to learn Python programming")

    print("=" * 50)
    print("TITLE:", script['title'])
    print("=" * 50)
    print("\nFULL SCRIPT:")
    print(script['full_script'])
    print("\n" + "=" * 50)
    print("TAGS:", script['tags'])
    print("DESCRIPTION:", script['description'])
