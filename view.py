### view.py
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.clock import Clock

class Separator(Widget):
    """
    Visual separator between UI sections.
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

class RaceTrack(Widget):
    """
    Widget that displays the horse race track and manages horse positions.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(1, 1, 1, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        self.bind(pos=self._draw_line, size=self._draw_line)
        self.horses = []
        self.bind(size=self._setup)

    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def _draw_line(self, *args):
        self.canvas.after.clear()
        with self.canvas.after:
            Color(0, 0, 0, 1)
            Line(points=[self.width*0.9, 0, self.width*0.9, self.height], width=2)

    def _setup(self, *args):
        self.clear_widgets()
        self.horses = []
        start_x = self.width * 0.1
        spacing = self.height / 7
        for i in range(6):
            horse = HorseSprite(i+1)
            horse.pos = (start_x, self.height - (i+1)*spacing - horse.height/2)
            self.horses.append(horse)
            self.add_widget(horse)

class HorseSprite(Widget):
    """
    Visual representation of a horse with a number label.
    """
    def __init__(self, number, **kwargs):
        super().__init__(**kwargs)
        self.number = number
        self.size = (50, 50)
        with self.canvas:
            Color(0.8, 0.3, 0.3, 1)
            self.ellipse = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self._update_graphics)
        self.label = Label(text=str(number), size_hint=(None, None))
        self.add_widget(self.label)
        self.bind(pos=self._update_label, size=self._update_label)

    def _update_graphics(self, *args):
        self.ellipse.pos = self.pos

    def _update_label(self, *args):
        self.label.center = self.center

class GameView(BoxLayout):
    """
    Main game view managing UI layout and triggering controller actions.
    """
    def __init__(self, lang_mgr, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.lang = lang_mgr
        self.track = RaceTrack(size_hint_y=5)
        self.add_widget(self.track)
        self.add_widget(Separator(size_hint_y=None, height=4))
        self._build_controls()

    def _build_controls(self):
        self.control_panel = BoxLayout(orientation='vertical', size_hint_y=0.35)
        top = BoxLayout()

        top.add_widget(Label(text=self.lang.get('bet_amount')))

        self.bet_input = TextInput(text='10', multiline=False, input_filter='int')
        top.add_widget(self.bet_input)

        self.balance_label = Label(text='')
        top.add_widget(self.balance_label)

        self.control_panel.add_widget(top)
        row = BoxLayout()
        for i in range(6):
            btn = Button(text=str(i+1))
            btn.bind(on_press=self._on_bet)
            row.add_widget(btn)
        self.control_panel.add_widget(row)
        self.add_widget(self.control_panel)

    def _on_bet(self, instance):
        horse_number = int(instance.text)
        amount = int(self.bet_input.text)
        self.controller.place_bet(horse_number, amount)

    def update_balance(self, balance):
        label = self.lang.get('balance')
        self.balance_label.text = f"{label}: ${balance}"

    def start_race_animation(self, horse_speeds, finish_x):
        self.horse_speeds = horse_speeds
        self.finish_x = finish_x
        self.event = Clock.schedule_interval(self._animate, 1/60)

    def _animate(self, dt):
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
        self.track._setup()

    def show_result(self, winner):
        pass  # Extend with result popup