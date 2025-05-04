### language_manager.py
import json

class LanguageManager:
    """
    Loads and provides access to language strings.
    """
    def __init__(self, default_language='en'):
        self.strings = {}
        self.load(default_language)

    def load(self, lang_code):
        with open(f'strings_{lang_code}.json', 'r', encoding='utf-8') as f:
            self.strings = json.load(f)

    def get(self, key):
        return self.strings.get(key, key)
