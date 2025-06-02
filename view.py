from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, Line
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.core.audio import SoundLoader

from kivy.core.text import LabelBase
LabelBase.register(name="Arcade", fn_regular="assets/fonts/arcade.ttf")


class RaceTrack(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


        with self.canvas.before:
            Color(1, 1, 1, 1)       # full opacity for all textures

            # textured rectangles
            self.grass_top    = Rectangle(source='assets/images/grass1.png')
            self.grass_bottom = Rectangle(source='assets/images/grass2.png')
            self.track_bg     = Rectangle(source='assets/images/racetrack.png')

        self.finish_line_image = Image(
            source="assets/images/finish_line_1.png",
            allow_stretch=True,
            keep_ratio=False,
        )
        self.add_widget(self.finish_line_image)

        self.bind(pos=self._update_layout, size=self._update_layout)

        self.horses = []
        self.bind(size=lambda *a: Clock.schedule_once(self._setup, 0))

    def _update_layout(self, *args):
        x, y, w, h = self.x, self.y, self.width, self.height
        grass_height = h * 0.05

        self.grass_top.pos = (x, y + h - grass_height)
        self.grass_top.size = (w, grass_height)

        self.grass_bottom.pos = (x, y)
        self.grass_bottom.size = (w, h * 0.20)

        self.track_bg.pos = (x, y + h * 0.20)
        self.track_bg.size = (w, h - (h * 0.20) - grass_height)

        finish_x = x + w * 0.9
        track_y = y + h * 0.20
        track_height = h - (h * 0.20) - grass_height
        self.finish_line_image.size = (60, track_height)
        self.finish_line_image.pos = (finish_x, track_y)

    def _setup(self, dt=None):
        for horse in self.horses:
            self.remove_widget(horse)
        self.horses = []

        num_horses = 6
        tmp = HorseSprite(1)
        h = tmp.height

        # ── NEW: leave room for the betting board ─────────────
        bottom_margin = self.height * 0.22      # matches panel (0.20) + a hair
        visible_height = self.height - bottom_margin
        # ───────────────────────────────────────────────────────

        empty = visible_height - num_horses * h
        spacing = empty / (num_horses + 1)
        start_x = self.width * 0.1

        for i in range(num_horses):
            # start every lane above the margin
            y = bottom_margin + spacing * (i + 1) + h * i
            horse = HorseSprite(i + 1)
            horse.pos = (start_x, y)
            self.horses.append(horse)
            self.add_widget(horse)

class HorseSprite(Widget):
    def __init__(self, number, **kwargs):
        super().__init__(**kwargs)
        self.number = number
        self.size = (100, 100)

        # Single assets used by every horse
        self.static_source   = f'assets/images/horses/horse{self.number}.png'
        self.animated_source = f'assets/images/horses/horserun{self.number}.gif'
        self.running = False

        self.image = Image(
            source=self.static_source,
            size=self.size,
            allow_stretch=True,
            keep_ratio=True,
        )
        self.image.anim_delay = -1  # freeze GIF if loaded too early
        self.add_widget(self.image)

        self.label = Label(
            text=str(number),
            size_hint=(None, None),
            size=(self.width, self.height),
            color=(1, 1, 1, 1),
            font_size="20sp",
            font_name="Arcade", 
            bold=True,
        )
        self.add_widget(self.label)

        self.bind(pos=self._update_positions, size=self._update_positions)

    def _update_positions(self, *args):
        self.image.pos = self.pos
        self.image.size = self.size
        self.label.center_x = self.center_x - 18
        self.label.center_y = self.center_y

    # ------------------- NEW --------------------
    def set_running(self, running: bool):
        if running == self.running:
            return
        self.running = running
        if running:
            self.image.source = self.animated_source
            self.image.anim_delay = 0.05  # ~20 fps
        else:
            self.image.source = self.static_source
            self.image.anim_delay = -1
        self.image.reload()
    # -------------------------------------------


class GameView(FloatLayout):
    def __init__(self, lang_mgr, **kwargs):
        super().__init__(**kwargs)
        self.lang = lang_mgr

        # ── NEW: load click sound once ────────────────────────────
        self.click_snd = SoundLoader.load("assets/sounds/click.mp3")
        if self.click_snd:                       # optional volume tweak
            self.click_snd.volume = 0.8

        self.pop_snd = SoundLoader.load("assets/sounds/popup.mp3")
        if self.pop_snd:                       # optional volume tweak
            self.pop_snd.volume = 1
        
        self.pistol_snd = SoundLoader.load("assets/sounds/starterpistol.mp3")
        self._pistol_event = None
        if self.pistol_snd:                       # optional volume tweak
            self.pistol_snd.volume = 0.8
        # ──────────────────────────────────────────────────────────
        # race-loop sound (plays while horses run)
        self.gallop_snd = SoundLoader.load("assets/sounds/horsegallop.mp3")
        self._gallop_event = None   # will hold the Clock event
        if self.gallop_snd:
            self.gallop_snd.loop = True          # keep repeating
            self.gallop_snd.volume = 0.4        # tweak to taste

        # win fanfare – plays only when the player's horse wins
        self.win_snd = SoundLoader.load("assets/sounds/win.mp3")
        if self.win_snd:
            self.win_snd.loop = False   # single play
            self.win_snd.volume = 0.9   # tweak to taste
        
        self.bg_music = SoundLoader.load("assets/sounds/music.mp3")
        if self.bg_music:
            self.bg_music.loop = True     # infinite loop
            self.bg_music.volume = 0.2    # subtle under the effects
            self.bg_music.play()          # start immediately
        
        self.bg_horse = SoundLoader.load("assets/sounds/horsebackground.mp3")
        if self.bg_horse:
            self.bg_horse.loop = True     # infinite loop
            self.bg_horse.volume = 0.5    # subtle under the effects
            self.bg_horse.play()          # start immediately

        self.track = RaceTrack(size_hint=(1, 1))
        self.add_widget(self.track)

        self._build_controls()
        self.result_popup = None

    # ────────────────────────────────────────────────────────────
    # HELPER: add a live border to any widget
    # ────────────────────────────────────────────────────────────
    def _add_border(self, widget, rgba=(0, 0, 0, 1), width=2):
        with widget.canvas.after:
            Color(*rgba)
            outline = Line(
                rectangle=(widget.x, widget.y, widget.width, widget.height),
                width=width,
                joint='miter'
            )

        # keep the border in sync with widget geometry
        def _update(*_):
            outline.rectangle = (
                widget.x, widget.y, widget.width, widget.height
            )

        widget.bind(pos=_update, size=_update)

         # ---------------------------------------------------------------
    # Utility: draw an image that tracks the widget's size & pos
    # ---------------------------------------------------------------
    def _add_texture_bg(self, widget, texture_path):
        with widget.canvas.before:
            tex = Rectangle(source=texture_path,
                            pos=widget.pos,
                            size=widget.size)

        def _sync(*_):
            tex.pos  = widget.pos
            tex.size = widget.size

        widget.bind(pos=_sync, size=_sync)

    # ────────────────────────────────────────────────────────────
    # BUILD BETTING PANEL (now with borders)
    # ────────────────────────────────────────────────────────────
    def _build_controls(self):
        # main golden panel
        self.control_panel = BoxLayout(
            orientation="vertical",
            size_hint=(1, 0.2),
            pos_hint={"x": 0, "y": 0},
        )
        with self.control_panel.canvas.before:
            self.bg_rect = Rectangle(
                source="assets/images/texture1.png",
                pos=self.control_panel.pos,
                size=self.control_panel.size
            )
        self.control_panel.bind(
            pos=lambda *a: setattr(self.bg_rect, "pos", self.control_panel.pos),
            size=lambda *a: setattr(self.bg_rect, "size", self.control_panel.size),
        )
        self._add_border(self.control_panel, (0, 0, 0, 1), 2)   # ← black outline

        # top row
        top = BoxLayout(size_hint=(1, 0.4))
        top.add_widget(Label(text=self.lang.get("bet_amount"), color=(0, 0, 0, 1), font_size="25sp", font_name="Arcade",))

        self.bet_input = TextInput(
            text="10",
            multiline=False,
            input_filter="int",
            foreground_color=(1, 1, 1, 1),
            background_normal="assets/images/texture3.png",
            background_active="assets/images/texture3.png",
            font_size="20sp",
            font_name="Arcade",
            halign="center",
        )
        # after creating bet_input
        def _recenter(_instance, _value):
            # line_height is the pixel height of the current font
            offset = (self.bet_input.height - self.bet_input.line_height) / 2
            # padding: [left, top, right, bottom]
            self.bet_input.padding = [0, offset, 0, offset]

        # run once now and bind so it updates on resize / font changes
        _recenter(None, None)
        self.bet_input.bind(size=_recenter, font_size=_recenter)
        
        top.add_widget(self.bet_input)
        self._add_border(self.bet_input, (0, 0, 0.000, 1), 2)       # ← white outline

        self.balance_label = Label(text="", color=(0, 0, 0, 1), font_size="25sp", font_name="Arcade",)
        top.add_widget(self.balance_label)
        self.control_panel.add_widget(top)

        # bottom row with 6 buttons
        row = BoxLayout(size_hint=(1, 0.5))
        for i in range(6):
            btn = Button(
                text=str(i + 1),
                color=(1, 1, 1, 1),
                background_normal="assets/images/texture2.png",
                background_down="assets/images/texture4.png",  # or same
                border=(0, 0, 0, 0),        # disable 9-patch cropping
                font_size="30sp",
                font_name="Arcade", 
            )
            btn.bind(on_release=self._on_bet)
            row.add_widget(btn)
            self._add_border(btn, (0, 0, 0.000, 1), 2)             # ← outline each button
        self.control_panel.add_widget(row)

        self.add_widget(self.control_panel)


    def _on_bet(self, instance):
        # ── NEW: audible feedback ────────────────────────────────
        if self.click_snd:
            self.click_snd.stop()    # in case previous click is still playing
            self.click_snd.play()
        # ──────────────────────────────────────────────────────────
        if self.pistol_snd:
            if self._pistol_event:            # cancel a stray old timer
                Clock.unschedule(self._pistol_event)
            self._pistol_event = Clock.schedule_once(
                lambda dt: (self.pistol_snd.stop(), self.pistol_snd.play()),
                0.01                        # ← delay in seconds
            )
        horse_number = int(instance.text)
        amount = int(self.bet_input.text)
        self.controller.place_bet(horse_number, amount)

    def update_balance(self, balance):
        self.balance_label.text = f"{self.lang.get('balance')}: ${balance}"

    def start_race_animation(self, horse_speeds, finish_x):
        # play gallop sound
        # schedule gallop loop to begin after 0.5 s
        if self.gallop_snd:
            if self._gallop_event:            # cancel a stray old timer
                Clock.unschedule(self._gallop_event)
            self._gallop_event = Clock.schedule_once(
                lambda dt: (self.gallop_snd.stop(), self.gallop_snd.play()),
                0.5                            # ← delay in seconds
            )

        # flip every sprite to the GIF
        for sprite in self.track.horses:
            sprite.set_running(True)

        self.finish_x = finish_x
        self.event = Clock.schedule_interval(self._animate, 1 / 60)

    def _animate(self, dt):
        self.controller.update_speeds_and_positions()
        for sprite in self.track.horses:
            horse_num = sprite.number
            horse_pos = self.controller.model.horses[horse_num - 1].position
            sprite.x = self.track.x + horse_pos

    def reset_track(self):

         # stop or cancel gallop loop
        if self.gallop_snd:
            self.gallop_snd.stop()
        if self._gallop_event:
            Clock.unschedule(self._gallop_event)
            self._gallop_event = None

        self.track._setup()
        self.control_panel.opacity = 1
        self.control_panel.disabled = False

    def show_result(self, winner, player_won, payout):
        from kivy.uix.boxlayout import BoxLayout

        if self.pop_snd:
            self.pop_snd.stop() 
            self.pop_snd.play()

        # play victory sound if you won
        if player_won and self.win_snd:
            self.win_snd.stop()
            self.win_snd.play()

        # ------------------------------------------------------------------
        # 1) Build the two lines of text
        # ------------------------------------------------------------------
        line1 = Label(
            text=f"Horse number {winner} wins!",
            font_size="22sp",
            font_name="Arcade",
            color=(1, 1, 1, 1),
        )

        if player_won:
            line2 = Label(
                text=f"You won ${payout}!",
                font_size="18sp",
                font_name="Arcade",
                color=(0, 0.6, 0, 1),
            )
        else:
            line2 = Label(
                text=f"You lost ${payout}.",
                font_size="18sp",
                font_name="Arcade",
                color=(0.8, 0, 0, 1),
            )

        # textured plates behind each label
        self._add_texture_bg(line1, "assets/images/texture4.png")
        self._add_texture_bg(line2, "assets/images/texture4.png")

        # stack them vertically
        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        content.add_widget(line1)
        content.add_widget(line2)

        # optional: texture behind the whole content box
        self._add_texture_bg(content, "assets/images/texture3.png")

        # ------------------------------------------------------------------
        # 2) Create the popup with a custom background + custom title font
        # ------------------------------------------------------------------
        self.result_popup = Popup(
            title="RACE RESULT",                       # text shown in the bar
            title_font="assets/fonts/arcade.ttf",      # <— arcade font
            title_size="28sp",
            title_align="center", 

            title_color=(1, 1, 1, 1),

            content=content,
            size_hint=(None, None),
            size=(420, 220),

            background="assets/images/texture2.png",   # <— your texture here
            border=(0, 0, 0, 0),                       # no 9-patch stretch
            separator_height=0,                        # hide grey line
            auto_dismiss=False,
        )
        self.result_popup.open()

