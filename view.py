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

        with self.canvas.before:
            # Grass top
            Color(0.3, 0.7, 0.3, 1)  # green
            self.grass_top = Rectangle()

            # Grass bottom
            Color(0.3, 0.7, 0.3, 1)
            self.grass_bottom = Rectangle()

            # Track background (sand)
            Color(0.82, 0.71, 0.55, 1)  # light brown
            self.track_bg = Rectangle()

        # Image finish line
        self.finish_line_image = Image(
            source='assets/images/finish_line_1.png',
            allow_stretch=True,
            keep_ratio=False
        )
        self.add_widget(self.finish_line_image)

        self.bind(pos=self._update_layout, size=self._update_layout)

        self.horses = []
        self.bind(size=lambda *a: Clock.schedule_once(self._setup, 0))

    def _update_layout(self, *args):
        x, y, w, h = self.x, self.y, self.width, self.height
        grass_height = h * 0.05

        # Top grass
        self.grass_top.pos = (x, y + h - grass_height)
        self.grass_top.size = (w, grass_height)

        # Bottom grass
        self.grass_bottom.pos = (x, y)
        self.grass_bottom.size = (w, grass_height)

        # Track background (between the two green strips)
        self.track_bg.pos = (x, y + grass_height)
        self.track_bg.size = (w, h - 2 * grass_height)

        # Finish line (between the grass areas)
        finish_x = x + w * 0.9
        track_y = y + grass_height
        track_height = h - 2 * grass_height
        self.finish_line_image.size = (60, track_height)
        self.finish_line_image.pos = (finish_x, track_y)

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
        self.size = (180, 60)  # adjust based on your image resolution

        # Load the horse image
        self.image = Image(
            source=f'assets/images/horses/horse_{self.number}.png',
            size=self.size,
            allow_stretch=True,
            keep_ratio=True
        )
        self.add_widget(self.image)

        # Add number label on top of image
        self.label = Label(
            text=str(number),
            size_hint=(None, None),
            size=(self.width, self.height),
            color=(1, 1, 1, 1),  # white
            font_size='16sp',
            bold=True
        )
        self.add_widget(self.label)

        # Keep position of image and label synced with the widget
        self.bind(pos=self._update_positions, size=self._update_positions)

    def _update_positions(self, *args):
        self.image.pos = self.pos
        self.image.size = self.size
        # Shift label slightly left (e.g., 20 pixels)
        self.label.center_x = self.center_x - 18
        self.label.center_y = self.center_y



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
        print(f"You chose horse nr. {instance.text}")
        horse_number = int(instance.text)
        amount = int(self.bet_input.text)
        self.controller.place_bet(horse_number, amount)

    def update_balance(self, balance):
        self.balance_label.text = f"{self.lang.get('balance')}: ${balance}"

    def start_race_animation(self, horse_speeds, finish_x):
        self.finish_x = finish_x
        self.event = Clock.schedule_interval(self._animate, 1 / 60)

    # def _animate(self, dt):
    #     race_finished = self.controller.update_speeds_and_positions()
    #     for sprite in self.track.horses:
    #         horse_num = sprite.number
    #         # Get current horse position from model
    #         horse_pos = self.controller.model.horses[horse_num - 1].position
    #         new_x = self.track.x + horse_pos
    #         # Clamp position to finish line
    #         if new_x + sprite.width >= self.track.x + self.finish_x:
    #             new_x = self.track.x + self.finish_x - sprite.width
    #         sprite.x = new_x
    #
    #     if race_finished:
    #         Clock.unschedule(self.event)
    #         self.controller.on_race_end()

    def _animate(self, dt):
        self.controller.update_speeds_and_positions()  # we no longer expect True/False

        for sprite in self.track.horses:
            horse_num = sprite.number
            horse_pos = self.controller.model.horses[horse_num - 1].position
            new_x = self.track.x + horse_pos
            sprite.x = new_x  # Don't clamp anymore

    def reset_track(self):
        self.track._setup()
        self.control_panel.opacity = 1
        self.control_panel.disabled = False

    from kivy.uix.boxlayout import BoxLayout

    def show_result(self, winner, player_won, payout):
        # First line: which horse won
        line1 = Label(
            text=f"Horse number {winner} wins!",
            font_size='22sp',
            bold=True,
            color=(1, 1, 1, 1)
        )

        # Second line: win/loss info
        if player_won:
            line2 = Label(
                text=f"You won ${payout}!",
                font_size='18sp',
                color=(0, 0.5, 0, 1)  # greenish
            )
        else:
            line2 = Label(
                text=f"You lost ${payout}.",
                font_size='18sp',
                color=(0.6, 0, 0, 1)  # reddish
            )

        # Layout to stack both lines
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(line1)
        content.add_widget(line2)

        self.result_popup = Popup(
            title='Race Result',
            content=content,
            size_hint=(None, None),
            size=(300, 200),
            auto_dismiss=False
        )
        self.result_popup.open()


