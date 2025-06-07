"""
File: main.py

Description:
    Entry point for the Horse Race Betting Game application.
    Configures application settings, initializes MVC components, and launches the Kivy app.

Version: 1.0
Author: Robbe de Guytenaer, Bernardo José Willis Lozano
"""

from kivy.app import App
from kivy.config import Config
# Set window size before the app is built
Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '600')

from language_manager import LanguageManager
from model import GameState
from view import GameView
from controller import GameController


class HorseRaceGameApp(App):
    """
    Main application class for the Horse Race Betting Game.

    Responsibilities:
        - Configure application window dimensions.
        - Instantiate language manager, model, view, and controller.
        - Wire up MVC components.
        - Return the root widget for rendering.
    """

    def build(self) -> GameView:
        """
        Build and return the root view for the application.

        Returns:
            GameView: The initialized view bound to its controller.
        """
        # Load localized strings
        lang_mgr = LanguageManager(default_language='en')

        # Initialize the game state with a starting balance
        model = GameState(balance=100)

        # Create the game view, passing in the language manager for text rendering
        view = GameView(lang_mgr)

        # Instantiate the controller with model and view, then bind it to the view
        controller = GameController(model, view)
        view.controller = controller

        return view


if __name__ == '__main__':
    HorseRaceGameApp().run()
