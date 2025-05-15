from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.clock import Clock
# from kivy_garden.svg import Svg
from kivy.uix.image import Image


class RaceTrack(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # White background for the track
        with self.canvas:
            Color(1, 1, 1, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        # Finish line
        self.bind(pos=self._draw_line, size=self._draw_line)
        self.horses = []
        self.bind(size=lambda *a: Clock.schedule_once(self._setup, 0))

        # Load and add finish line image
        self.finish_line_image = Image(
            source='assets/images/finish_line_3.png',
            allow_stretch=True,
            keep_ratio=False
        )
        self.add_widget(self.finish_line_image)
        self.bind(pos=self._update_finish_line, size=self._update_finish_line)

    def _update_finish_line(self, *args):
        finish_x = self.x + self.width * 0.9
        self.finish_line_image.size = (60, self.height)  # adjust width as you like
        self.finish_line_image.pos = (finish_x, self.y)

    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def _draw_line(self, *args):
        self.canvas.after.clear()
        with self.canvas.after:
            Color(0, 0, 0, 1)
            Line(points=[self.width * 0.9, 0, self.width * 0.9, self.height], width=0.5)

    def _setup(self, dt=None):
        for horse in self.horses:
            self.remove_widget(horse)
        self.horses = []
        num_horses = 6
        tmp = HorseSprite(1)
        h = tmp.height
        empty = self.height - num_horses * h
        spacing = empty / (num_horses + 1)
        start_x = self.width * 0.1
        for i in range(num_horses):
            y = spacing * (i + 1) + h * i
            horse = HorseSprite(i + 1)
            horse.pos = (start_x, y)
            self.horses.append(horse)
            self.add_widget(horse)

class HorseSprite(Widget):
    def __init__(self, number, **kwargs):
        super().__init__(**kwargs)
        self.number = number
        self.size = (50, 50)
        with self.canvas:
            Color(0.8, 0.3, 0.3, 1)
            self.ellipse = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self._update_graphics)
        self.label = Label(text=str(number), size_hint=(None, None), color=(0, 0, 0, 1))
        self.add_widget(self.label)
        self.bind(pos=self._update_label, size=self._update_label)

    def _update_graphics(self, *args):
        self.ellipse.pos = self.pos

    def _update_label(self, *args):
        self.label.center = self.center

class GameView(FloatLayout):
    def __init__(self, lang_mgr, **kwargs):
        super().__init__(**kwargs)
        self.lang = lang_mgr

        # Full-screen race track
        self.track = RaceTrack(size_hint=(1, 1))
        self.add_widget(self.track)

        # Overlay betting panel at bottom
        self._build_controls()
        self.result_popup = None

    def _build_controls(self):
        self.control_panel = BoxLayout(orientation='vertical', size_hint=(1, 0.2), pos_hint={'x':0, 'y':0})
        with self.control_panel.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(pos=self.control_panel.pos, size=self.control_panel.size)
        self.control_panel.bind(
            pos=lambda *a: setattr(self.bg_rect, 'pos', self.control_panel.pos),
            size=lambda *a: setattr(self.bg_rect, 'size', self.control_panel.size)
        )
        top = BoxLayout(size_hint=(1, 0.4))
        top.add_widget(Label(text=self.lang.get('bet_amount'), color=(0,0,0,1)))
        self.bet_input = TextInput(text='10', multiline=False, input_filter='int',
                                   foreground_color=(0,0,0,1), background_color=(1,1,1,1))
        top.add_widget(self.bet_input)
        self.balance_label = Label(text='', color=(0,0,0,1))
        top.add_widget(self.balance_label)
        self.control_panel.add_widget(top)

        row = BoxLayout(size_hint=(1, 0.6))
        for i in range(6):
            btn = Button(text=str(i+1), color=(0,0,0,1), background_color=(1,1,1,1))
            btn.bind(on_press=self._on_bet)
            row.add_widget(btn)
        self.control_panel.add_widget(row)
        self.add_widget(self.control_panel)

    def _on_bet(self, instance):
        horse_number = int(instance.text)
        amount = int(self.bet_input.text)
        self.controller.place_bet(horse_number, amount)

    def update_balance(self, balance):
        self.balance_label.text = f"{self.lang.get('balance')}: ${balance}"

    def start_race_animation(self, horse_speeds, finish_x):
        self.finish_x = finish_x
        self.event = Clock.schedule_interval(self._animate, 1 / 60)

    def _animate(self, dt):
        race_finished = self.controller.update_speeds_and_positions()
        for sprite in self.track.horses:
            horse_num = sprite.number
            # Get current horse position from model
            horse_pos = self.controller.model.horses[horse_num - 1].position
            new_x = self.track.x + horse_pos
            # Clamp position to finish line
            if new_x + sprite.width >= self.track.x + self.finish_x:
                new_x = self.track.x + self.finish_x - sprite.width
            sprite.x = new_x

        if race_finished:
            Clock.unschedule(self.event)
            self.controller.on_race_end()

    def reset_track(self):
        self.track._setup()
        self.control_panel.opacity = 1
        self.control_panel.disabled = False

    def show_result(self, winner):
        msg = f"Horse number {winner} wins!"
        self.result_popup = Popup(
            title='Race Result',
            content=Label(text=msg, font_size='24sp'),
            size_hint=(None, None),
            size=(300, 200),
            auto_dismiss=False)
        self.result_popup.open()
        Clock.schedule_once(lambda dt: self.result_popup.dismiss(), 2)

