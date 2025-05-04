### controller.py
from kivy.clock import Clock
from model import GameState

class GameController:
    """
    Handles all interaction between view and model.
    """
    def __init__(self, model: GameState, view):
        self.model = model
        self.view = view
        self.view.update_balance(self.model.balance)

    def place_bet(self, horse_number, amount):
        try:
            self.model.place_bet(horse_number, amount)
        except ValueError as e:
            print(e)
            return
        self.model.setup_race()
        self.view.start_race_animation(
            self.model.horse_speeds,
            finish_x=self.view.track.width * 0.9
        )

    def on_race_end(self):
        self.model.resolve_race()
        self.view.update_balance(self.model.balance)
        self.view.show_result(self.model.winner)
        Clock.schedule_once(lambda dt: self._reset(), 2)

    def _reset(self):
        self.model.reset()
        self.view.reset_track()
