"""
File: language_manager.py

Description:
    Loads and provides access to localized language strings from JSON files.

Version: 1.0
Author: Robbe de Guytenaer, Bernardo José Willis Lozano
"""

import json
import os


class LanguageManager:
    """
    Manages loading and retrieval of localized strings for different languages.

    Attributes:
        strings (dict): Mapping of translation keys to localized strings.
    """

    def __init__(self, default_language: str = 'en'):
        """
        Initialize the LanguageManager and load the default language.

        Args:
            default_language (str): ISO code of the language to load initially (e.g., 'en', 'es', 'sv').
        """
        self.strings: dict = {}
        self.load(default_language)

    def load(self, lang_code: str) -> None:
        """
        Load translation strings from a JSON file for the specified language.

        The JSON file should be located at 'assets/lang/{lang_code}.json'.

        Args:
            lang_code (str): ISO code of the language to load.

        Raises:
            FileNotFoundError: If the JSON file does not exist.
            json.JSONDecodeError: If the JSON file contains invalid JSON.
        """
        path = os.path.join('assets', 'lang', f'{lang_code}.json')
        with open(path, 'r', encoding='utf-8') as f:
            self.strings = json.load(f)

    def get(self, key: str) -> str:
        """
        Retrieve the localized string for the given key.

        If the key is not found in the loaded strings, the key itself is returned.

        Args:
            key (str): The translation key to look up.

        Returns:
            str: The localized string, or the key if no translation is found.
        """
        return self.strings.get(key, key)
