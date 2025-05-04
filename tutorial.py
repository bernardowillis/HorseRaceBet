### tutorial.py
from kivy.uix.modalview import ModalView
from kivy.uix.label import Label

class TutorialOverlay(ModalView):
    """
    Displays a modal tutorial overlay for first-time users.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (400, 300)
        self.auto_dismiss = False
        self.add_widget(Label(text="Tutorial steps go here"))

    def start(self):
        self.open()

    def next_step(self):
        pass  # Add tutorial logic