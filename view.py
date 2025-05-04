### view.py

from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.clock import Clock

# The main window is structured into three vertical parts:
# - Top:    Horse race area, handled by RaceTrack (80% of height)
# - Middle: Thin visual separator line (fixed 4px height)
# - Bottom: Betting interface (Bet input + horse selection buttons, 20% of height)

class RaceTrack(Widget):
    """
    Custom widget for the race track.
    Displays a white background, a finish line, and positions horse widgets.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Draw white background
        with self.canvas:
            Color(1, 1, 1, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)
            # Draw a test rectangle in the bottom-left corner
            Color(0.2, 0.6, 1, 1)  # blue rectangle
            self.test_rect = Rectangle(pos=(0, 0), size=(100, 40))
        self.bind(pos=self._update_bg, size=self._update_bg)
        self.bind(pos=self._draw_line, size=self._draw_line)

        # List to hold HorseSprite widgets
        self.horses = []

        # Delay setup until size is finalized
        self.bind(size=lambda *args: Clock.schedule_once(self._setup, 0))

    def _update_bg(self, *args):
        # Keep background rectangle synced with widget size
        self.bg.pos = self.pos
        self.bg.size = self.size

    def _draw_line(self, *args):
        # Draw a vertical finish line at 90% width
        self.canvas.after.clear()
        with self.canvas.after:
            Color(0, 0, 0, 1)
            Line(points=[
                self.width * 0.9,
                0,
                self.width * 0.9,
                self.height
            ], width=2)
        print(f"line_x_begin = {self.width*0.9}")
        print(f"line_y_end = {self.height}")

    def _setup(self, dt=None):
        # Place horses evenly on the track
        self.clear_widgets()
        self.horses = []

        start_x = self.width * 0.1
        num_horses = 6

        padding = 20
        usable_height = self.height - 2 * padding
        spacing = usable_height / (num_horses - 1)

        for i in range(num_horses):
            horse = HorseSprite(i + 1)
            horse_y = padding + i * spacing - horse.height / 2
            horse.pos = (start_x, horse_y)
            self.horses.append(horse)
            self.add_widget(horse)

        print(f"RaceTrack pos: {self.pos}, size: {self.size}")

class Separator(Widget):
    """
    Simple black horizontal line between the race track and betting panel.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0, 0, 0, 1)
            self.line = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self.line.pos = self.pos
        self.line.size = self.size

class HorseSprite(Widget):
    """
    Represents a horse as a colored circle with a number in the center.
    """
    def __init__(self, number, **kwargs):
        super().__init__(**kwargs)
        self.number = number
        self.size = (50, 50)

        # Draw the horse (circle)
        with self.canvas:
            Color(0.8, 0.3, 0.3, 1)
            self.ellipse = Ellipse(pos=self.pos, size=self.size)

        # Update graphics when position changes
        self.bind(pos=self._update_graphics)

        # Centered number label
        self.label = Label(text=str(number), size_hint=(None, None))
        self.add_widget(self.label)
        self.bind(pos=self._update_label, size=self._update_label)

    def _update_graphics(self, *args):
        self.ellipse.pos = self.pos

    def _update_label(self, *args):
        self.label.center = self.center

class GameView(BoxLayout):
    """
    The full game view with top track, separator, and bottom control panel.
    Inherits from BoxLayout with vertical stacking.
    """
    def __init__(self, lang_mgr, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.lang = lang_mgr

        # Top part: the race track
        self.track = RaceTrack(size_hint_y=0.8)
        self.add_widget(self.track)

        # Middle separator
        self.add_widget(Separator(size_hint_y=None, height=4))

        # Bottom part: betting input + horse buttons
        self._build_controls()

    def _build_controls(self):
        # Bottom section of the app: betting panel
        self.control_panel = BoxLayout(orientation='vertical', size_hint_y=0.2)

        # First row: betting input and balance
        top = BoxLayout(size_hint_y=0.4)
        top.add_widget(Label(text=self.lang.get('bet_amount')))
        self.bet_input = TextInput(text='10', multiline=False, input_filter='int')
        top.add_widget(self.bet_input)
        self.balance_label = Label(text='')
        top.add_widget(self.balance_label)
        self.control_panel.add_widget(top)

        # Second row: 6 horse selection buttons
        row = BoxLayout(size_hint_y=0.6)
        for i in range(6):
            btn = Button(text=str(i+1))
            btn.bind(on_press=self._on_bet)
            row.add_widget(btn)
        self.control_panel.add_widget(row)

        self.add_widget(self.control_panel)

    def _on_bet(self, instance):
        # Called when a horse button is pressed
        horse_number = int(instance.text)
        amount = int(self.bet_input.text)
        self.controller.place_bet(horse_number, amount)

    def update_balance(self, balance):
        # Updates balance display from model
        label = self.lang.get('balance')
        self.balance_label.text = f"{label}: ${balance}"

    def start_race_animation(self, horse_speeds, finish_x):
        # Begins frame-by-frame animation of the race
        self.horse_speeds = horse_speeds
        self.finish_x = finish_x
        self.event = Clock.schedule_interval(self._animate, 1/60)

    def _animate(self, dt):
        # Move horses forward based on their speed
        finished = False
        for sprite in self.track.horses:
            speed = self.horse_speeds[sprite.number]
            new_x = sprite.x + speed
            if new_x + sprite.width >= self.finish_x:
                new_x = self.finish_x - sprite.width
                finished = True
            sprite.x = new_x

        if finished:
            Clock.unschedule(self.event)
            self.controller.on_race_end()

    def reset_track(self):
        # Reposition horses to starting point
        self.track._setup()

    def show_result(self, winner):
        # Placeholder for popup/result display
        pass
