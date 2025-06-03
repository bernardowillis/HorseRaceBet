### main.py
from kivy.config import Config
Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '600')
from kivy.app import App
from language_manager import LanguageManager
from model import GameState, UndoRedoManager
from view import GameView
from controller import GameController

class HorseRaceGameApp(App):
    """
    Main application class. Initializes MVC components and launches the app.
    """
    def build(self):
        # Initialize language manager
        lang_mgr = LanguageManager(default_language='en')
        # Initialize model and undo manager
        undo_mgr = UndoRedoManager()
        model = GameState(balance=100, undo_manager=undo_mgr)
        # Initialize view
        view = GameView(lang_mgr)
        # Initialize controller and bind to view
        controller = GameController(model, view)
        view.controller = controller
        return view

if __name__ == '__main__':
    HorseRaceGameApp().run()