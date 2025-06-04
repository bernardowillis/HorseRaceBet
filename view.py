from kivy.uix.widget      import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout   import BoxLayout
from kivy.uix.label       import Label
from kivy.uix.button      import Button
from kivy.uix.textinput   import TextInput
from kivy.uix.popup       import Popup
from kivy.uix.image       import Image
from kivy.graphics        import Color, Rectangle, Line
from kivy.clock           import Clock
from kivy.core.audio      import SoundLoader
from kivy.core.window     import Window
from kivy.core.text       import LabelBase

# ──────────────────────────────────────────────────────────────
# Register custom font
# ──────────────────────────────────────────────────────────────
LabelBase.register(name="Arcade", fn_regular="assets/fonts/arcade.ttf")


# ──────────────────────────────────────────────────────────────
#  RACE TRACK + HORSE SPRITES
# ──────────────────────────────────────────────────────────────
class RaceTrack(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.grass_top    = Rectangle(source="assets/images/grass1.png")
            self.grass_bottom = Rectangle(source="assets/images/grass2.png")
            self.track_bg     = Rectangle(source="assets/images/racetrack.png")

        self.finish_line_image = Image(
            source="assets/images/finish_line_1.png",
            allow_stretch=True,
            keep_ratio=False,
        )
        self.add_widget(self.finish_line_image)

        self.bind(pos=self._update_layout, size=self._update_layout)

        self.horses = []
        self.bind(size=lambda *_: Clock.schedule_once(self._setup, 0))

    def _update_layout(self, *args):
        x, y, w, h = self.x, self.y, self.width, self.height
        grass_height  = h * 0.05
        bottom_height = h * 0.20

        self.grass_top.pos  = (x, y + h - grass_height)
        self.grass_top.size = (w, grass_height)

        self.grass_bottom.pos  = (x, y)
        self.grass_bottom.size = (w, bottom_height)

        self.track_bg.pos  = (x, y + bottom_height)
        self.track_bg.size = (w, h - bottom_height - grass_height)

        finish_x   = x + w * 0.9
        track_y    = y + bottom_height
        track_h    = h - bottom_height - grass_height
        self.finish_line_image.size = (60, track_h)
        self.finish_line_image.pos  = (finish_x, track_y)

    def _setup(self, dt=None):
        for h in self.horses:
            self.remove_widget(h)
        self.horses = []

        num_horses    = 6
        tmp           = HorseSprite(1)
        horse_h       = tmp.height
        bottom_margin = self.height * 0.22
        visible_h     = self.height - bottom_margin
        spacing       = (visible_h - num_horses * horse_h) / (num_horses + 1)
        start_x       = self.width * 0.1

        for i in range(num_horses):
            y = bottom_margin + spacing * (i + 1) + horse_h * i
            sprite = HorseSprite(i + 1)
            sprite.pos = (start_x, y)
            self.horses.append(sprite)
            self.add_widget(sprite)


class HorseSprite(Widget):
    def __init__(self, number, **kwargs):
        super().__init__(**kwargs)
        self.number = number
        self.size   = (100, 100)

        self.static_source   = f"assets/images/horses/horse{number}.png"
        self.animated_source = f"assets/images/horses/horserun{number}.gif"
        self.running         = False

        self.image = Image(
            source=self.static_source,
            size=self.size,
            allow_stretch=True,
            keep_ratio=True
        )
        self.image.anim_delay = -1
        self.add_widget(self.image)

        self.label = Label(
            text=str(number),
            size_hint=(None, None),
            size=(self.width, self.height),
            color=(1, 1, 1, 1),
            font_size="20sp",
            font_name="Arcade",
            bold=True
        )
        self.add_widget(self.label)

        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *args):
        self.image.pos = self.pos
        self.image.size = self.size
        self.label.center_x = self.center_x - 18
        self.label.center_y = self.center_y

    def set_running(self, running: bool):
        if running == self.running:
            return
        self.running = running
        if running:
            self.image.source     = self.animated_source
            self.image.anim_delay = 0.05
        else:
            self.image.source     = self.static_source
            self.image.anim_delay = -1
        self.image.reload()


# ──────────────────────────────────────────────────────────────
#  MAIN VIEW
# ──────────────────────────────────────────────────────────────
class GameView(FloatLayout):
    def __init__(self, lang_mgr, **kwargs):
        super().__init__(**kwargs)
        self.lang = lang_mgr

        # -------------------------------------------------------
        # Audio helpers
        # -------------------------------------------------------
        def _load(path, *, loop=False, vol=1.0):
            snd = SoundLoader.load(path)
            if snd:
                snd.loop = loop
                snd.volume = vol
                snd._orig_vol = vol
            return snd

        # UI / race sounds
        self.click_snd  = _load("assets/sounds/click.mp3",          vol=0.8)
        self.pop_snd    = _load("assets/sounds/popup.mp3",          vol=1.0)
        self.pistol_snd = _load("assets/sounds/starterpistol.mp3",  vol=0.8)
        self.win_snd    = _load("assets/sounds/win.mp3",            vol=0.9)
        # ambience
        self.bg_music   = _load("assets/sounds/music.mp3", loop=True,  vol=0.2)
        self.bg_horse   = _load("assets/sounds/horsebackground.mp3", loop=True, vol=0.5)
        self.gallop_snd = _load("assets/sounds/horsegallop.mp3", loop=True, vol=0.4)

        if self.bg_music:  self.bg_music.play()
        if self.bg_horse:  self.bg_horse.play()

        self._gallop_event  = None
        self._pistol_event  = None

        # mute flags
        self.music_muted  = False
        self.sounds_muted = False

        # -------------------------------------------------------
        # Track view
        # -------------------------------------------------------
        self.track = RaceTrack(size_hint=(1, 1))
        self.add_widget(self.track)

        # -------------------------------------------------------
        # Betting / deposit panel
        # -------------------------------------------------------
        self._build_controls()

        # -------------------------------------------------------
        # Settings gear (top-right)
        # -------------------------------------------------------
        self._build_settings_button()

        # -------------------------------------------------------
        # Tutorial button (top-right)
        # -------------------------------------------------------
        self._build_tutorial_button()
        # ── Tutorial state variables ───────────────────────────────────
        self._tutorial_step = 0
        self._tutorial_overlay = None  # we will store the overlay Widget here
        self._tutorial_rect = None  # <— new: will point to the Rectangle instruction
        self._tutorial_popup = None
        self._highlight_line = None
        self.highlight_widget = None

        # -------------------------------------------------------
        # Misc. labels / popups
        # -------------------------------------------------------
        self.result_popup         = None
        self._deposit_popup       = None

        self.bet_error_label = Label(
            text="",
            color=(1, 0, 0, 1),
            font_size="18sp",
            font_name="Arcade",
            size_hint=(None, None),
            size=(400, 30),
            opacity=0,
            halign="center",
            valign="middle"
        )
        self._bet_error_added = False
        self._bet_error_timer = None

        self.deposit_error_label = Label(
            text="",
            color=(1, 0, 0, 1),
            font_size="18sp",
            font_name="Arcade",
            size_hint=(None, None),
            size=(500, 30),
            opacity=0,
            halign="center",
            valign="middle"
        )

        # ────────────────────────────────────────────────────────
        # “Leading horse” label (hidden until race starts)
        # ────────────────────────────────────────────────────────
        self.leading_label = Label(
            text="",
            color=(1, 1, 0, 1),
            font_size="20sp",
            font_name="Arcade",
            size_hint=(0.5, None),
            height=30,
            opacity=0,
            halign="center",
            valign="middle",
            pos_hint={"center_x": 0.5, "y": 0.08}
        )
        self.add_widget(self.leading_label)

    # ──────────────────────────────────────────────────────────
    #  Generic drawing helpers
    # ──────────────────────────────────────────────────────────
    def _add_border(self, widget, rgba=(0, 0, 0, 1), width=2):
        with widget.canvas.after:
            Color(*rgba)
            ln = Line(
                rectangle=(widget.x, widget.y, widget.width, widget.height),
                width=width,
                joint="miter"
            )
        widget.bind(pos=lambda *_: self._sync_line(ln, widget),
                    size=lambda *_: self._sync_line(ln, widget))

    @staticmethod
    def _sync_line(line, w):
        line.rectangle = (w.x, w.y, w.width, w.height)

    def _add_texture_bg(self, widget, tex_path):
        with widget.canvas.before:
            tex = Rectangle(source=tex_path, pos=widget.pos, size=widget.size)
        widget.bind(pos=lambda *_: self._sync_rect(tex, widget),
                    size=lambda *_: self._sync_rect(tex, widget))

    @staticmethod
    def _sync_rect(rect, w):
        rect.pos, rect.size = w.pos, w.size

    # ──────────────────────────────────────────────────────────
    #  Settings button + popup
    # ──────────────────────────────────────────────────────────
    def _build_settings_button(self):
        gear = Button(
            text="",
            size_hint=(None, None), size=(45, 45),
            pos_hint={"right": .04, "top": .99},
            background_normal="assets/images/settings.png",
            background_down="assets/images/settings2.png",
            border=(0, 0, 0, 0),
            background_color=(1, 1, 1, 1),
        )
        gear.bind(on_release=lambda *_: self._show_settings_popup())
        self.add_widget(gear)



    def _toggle_music(self, btn):
        self.music_muted = not self.music_muted
        btn.text = "UNMUTE MUSIC" if self.music_muted else "MUTE MUSIC"
        for snd in (self.bg_music, self.bg_horse, self.gallop_snd):
            if snd:
                snd.volume = 0 if self.music_muted else snd._orig_vol

    def _toggle_sounds(self, btn):
        self.sounds_muted = not self.sounds_muted
        btn.text = "UNMUTE SOUNDS" if self.sounds_muted else "MUTE SOUNDS"
        for snd in (self.click_snd, self.pop_snd, self.pistol_snd, self.win_snd):
            if snd:
                snd.volume = 0 if self.sounds_muted else snd._orig_vol

    def _show_settings_popup(self):
        if self.pop_snd and not self.sounds_muted:
            self.pop_snd.stop()
            self.pop_snd.play()

        root = FloatLayout()

        close_btn = Button(
            text="X",
            font_size="22sp",
            font_name="Arcade",
            size_hint=(None, None),
            size=(50, 50),
            background_normal="assets/images/texture2.png",
            background_down="assets/images/texture4.png",
            border=(0, 0, 0, 0),
            pos_hint={"right": 1, "top": 1}
        )
        music_btn = Button(
            text="MUTE MUSIC" if not self.music_muted else "UNMUTE MUSIC",
            font_size="22sp",
            font_name="Arcade",
            size_hint=(0.8, 0.25),
            pos_hint={"center_x": 0.5, "center_y": 0.6},
            background_normal="assets/images/texture2.png",
            background_down="assets/images/texture4.png",
            border=(0, 0, 0, 0)
        )
        sounds_btn = Button(
            text="MUTE SOUNDS" if not self.sounds_muted else "UNMUTE SOUNDS",
            font_size="22sp",
            font_name="Arcade",
            size_hint=(0.8, 0.25),
            pos_hint={"center_x": 0.5, "center_y": 0.3},
            background_normal="assets/images/texture2.png",
            background_down="assets/images/texture4.png",
            border=(0, 0, 0, 0)
        )

        for b in (close_btn, music_btn, sounds_btn):
            self._add_border(b, (0, 0, 0, 1), 2)
            root.add_widget(b)

        music_btn.bind(on_release=lambda *_: self._toggle_music(music_btn))
        sounds_btn.bind(on_release=lambda *_: self._toggle_sounds(sounds_btn))

        settings_popup = Popup(
            title="SETTINGS",
            title_font="assets/fonts/arcade.ttf",
            title_size="26sp",
            title_align="center",
            title_color=(1, 1, 1, 1),
            content=root,
            size_hint=(None, None),
            size=(500, 350),
            background="assets/images/texture5.png",
            border=(0, 0, 0, 0),
            separator_height=0,
            auto_dismiss=False,
        )
        close_btn.bind(on_release=lambda *_: settings_popup.dismiss())
        settings_popup.open()

    # ──────────────────────────────────────────────────────────
    #  Settings button + popup
    # ──────────────────────────────────────────────────────────
    def _build_tutorial_button(self):
        book = Button(
            text="",
            size_hint=(None, None), size=(45, 45),
            pos_hint={"right": .04, "top": .93},
            background_normal="assets/images/tutorial1.png",
            background_down="assets/images/tutorial2.png",
            border=(0, 0, 0, 0),
            background_color=(1, 1, 1, 1),
        )
        book.bind(on_release=lambda *_: self._start_tutorial())
        self.add_widget(book)

    # ──────────────────────────────────────────────────────────
    #  Betting / Deposit panel
    # ──────────────────────────────────────────────────────────
    def _build_controls(self):
        self.control_panel = BoxLayout(
            orientation="vertical",
            size_hint=(1, 0.2),
            pos_hint={"x": 0, "y": 0}
        )
        # Background texture for the control panel
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
        self._add_border(self.control_panel, (0, 0, 0, 1), 2)

        # ---- top row (Bet amount, balance, Deposit button) ---- #
        top = BoxLayout(size_hint=(1, 0.4))

        # “Bet Amount” label
        top.add_widget(Label(
            text=self.lang.get("bet_amount"),
            color=(0, 0, 0, 1),
            font_size="25sp",
            font_name="Arcade"
        ))

        # Bet input field
        self.bet_input = TextInput(
            text="10",
            multiline=False,
            input_filter="int",
            foreground_color=(1, 1, 1, 1),
            background_normal="assets/images/texture3.png",
            background_active="assets/images/texture3.png",
            font_size="20sp",
            font_name="Arcade",
            halign="center"
        )

        def _recenter(_instance, _value):
            off = (self.bet_input.height - self.bet_input.line_height) / 2
            self.bet_input.padding = [0, max(0, off), 0, max(0, off)]

        _recenter(None, None)
        self.bet_input.bind(size=_recenter, font_size=_recenter)
        top.add_widget(self.bet_input)
        self._add_border(self.bet_input, (0, 0, 0, 1), 2)

        # Balance display
        self.balance_label = Label(
            text="",
            color=(0, 0, 0, 1),
            font_size="25sp",
            font_name="Arcade"
        )
        top.add_widget(self.balance_label)

        # **Deposit** button (store reference for tutorial highlighting)
        deposit_btn = Button(
            text="Deposit",
            color=(0, 0, 0, 1),
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            border=(0, 0, 0, 0),
            font_size="24sp",
            font_name="Arcade"
        )
        self.deposit_btn = deposit_btn
        deposit_btn.bind(on_release=lambda *_: self.show_deposit_popup())
        top.add_widget(deposit_btn)
        self._add_border(deposit_btn, (0, 0, 0, 1), 2)

        self.control_panel.add_widget(top)

        # ---- bottom row (Horse‐selection buttons) ---- #
        row = BoxLayout(size_hint=(1, 0.5))
        self.horse_buttons = []
        for i in range(6):
            btn = Button(
                text=str(i + 1),
                color=(1, 1, 1, 1),
                background_normal="assets/images/texture9.png",
                background_down="assets/images/texture11.png",
                border=(0, 0, 0, 0),
                font_size="30sp",
                font_name="Arcade"
            )
            self.horse_buttons.append(btn)
            btn.bind(on_release=self._on_bet)
            row.add_widget(btn)
            self._add_border(btn, (0, 0, 0, 1), 2)

        self.control_panel.add_widget(row)

        self.add_widget(self.control_panel)

    # ──────────────────────────────────────────────────────────
    #  Bet button handler
    # ──────────────────────────────────────────────────────────
    def _on_bet(self, instance):
        if self.click_snd and not self.sounds_muted:
            self.click_snd.stop()
            self.click_snd.play()
        if self.pistol_snd and not self.sounds_muted:
            if self._pistol_event:
                Clock.unschedule(self._pistol_event)
            self._pistol_event = Clock.schedule_once(
                lambda _dt: (self.pistol_snd.stop(), self.pistol_snd.play()),
                0.01
            )

        horse_number = int(instance.text)
        amount       = int(self.bet_input.text)
        try:
            self.controller.place_bet(horse_number, amount)
        except Exception:
            pass  # controller will call show_bet_error if needed

    # ----------------------------------------------------------
    # Balance update
    # ----------------------------------------------------------
    def update_balance(self, balance):
        self.balance_label.text = f"{self.lang.get('balance')}: ${balance}"

    # ----------------------------------------------------------
    # Start race animation
    # ----------------------------------------------------------
    def start_race_animation(self, horse_speeds, finish_x):
        if self.gallop_snd and not self.music_muted:
            if self._gallop_event:
                Clock.unschedule(self._gallop_event)
            self._gallop_event = Clock.schedule_once(
                lambda _dt: (self.gallop_snd.stop(), self.gallop_snd.play()),
                0.5
            )

        for sprite in self.track.horses:
            sprite.set_running(True)

        self.leading_label.opacity = 1
        self.finish_x = finish_x
        self.event = Clock.schedule_interval(self._animate, 1 / 60)

    def _animate(self, dt):
        self.controller.update_speeds_and_positions()
        for sprite in self.track.horses:
            horse_num = sprite.number
            horse_pos = self.controller.model.horses[horse_num - 1].position
            sprite.x = self.track.x + horse_pos

        # update leading horse label
        leader_num = max(
            self.track.horses,
            key=lambda spr: self.controller.model.horses[spr.number - 1].position
        ).number
        self.leading_label.text = f"Leading horse: {leader_num}"

    # ----------------------------------------------------------
    # Reset track
    # ----------------------------------------------------------
    def reset_track(self):
        if self.gallop_snd:
            self.gallop_snd.stop()
        if self._gallop_event:
            Clock.unschedule(self._gallop_event)
            self._gallop_event = None

        self.track._setup()
        self.control_panel.opacity  = 1
        self.control_panel.disabled = False

        self.leading_label.opacity = 0
        self.leading_label.text    = ""

    # ──────────────────────────────────────────────────────────
    #  Result popup
    # ──────────────────────────────────────────────────────────
    def show_result(self, winner, player_won, payout):
        if self.pop_snd and not self.sounds_muted:
            self.pop_snd.stop()
            self.pop_snd.play()
        if player_won and self.win_snd and not self.sounds_muted:
            self.win_snd.stop()
            self.win_snd.play()

        line1 = Label(
            text=f"Horse number {winner} wins!",
            font_size="22sp",
            font_name="Arcade",
            color=(0, 0, 0, 1)
        )

        if player_won:
            line2 = Label(
                text=f"You won ${payout}!",
                font_size="18sp",
                font_name="Arcade",
                color=(0, 0.6, 0, 1)
            )
        else:
            line2 = Label(
                text=f"You lost ${payout}.",
                font_size="18sp",
                font_name="Arcade",
                color=(0.8, 0, 0, 1)
            )

        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        content.add_widget(line1)
        content.add_widget(line2)

        self.result_popup = Popup(
            title="RACE RESULT",
            title_font="assets/fonts/arcade.ttf",
            title_size="28sp",
            title_align="center",
            title_color=(1, 1, 1, 1),
            content=content,
            size_hint=(None, None),
            size=(580, 240),
            background="assets/images/texture5.png",
            border=(0, 0, 0, 0),
            separator_height=0,
            auto_dismiss=False
        )

        # draw black border around popup
        with self.result_popup.canvas.after:
            Color(0, 0, 0, 1)
            outline = Line(
                rectangle=(self.result_popup.x,
                           self.result_popup.y,
                           self.result_popup.width,
                           self.result_popup.height),
                width=2
            )

        def _update_border(*args):
            outline.rectangle = (
                self.result_popup.x,
                self.result_popup.y,
                self.result_popup.width,
                self.result_popup.height
            )

        self.result_popup.bind(pos=_update_border, size=_update_border)
        self.result_popup.open()

    # ──────────────────────────────────────────────────────────
    #  Bet error (“not enough money”) label
    # ──────────────────────────────────────────────────────────
    def show_bet_error(self, msg):
        if not self._bet_error_added:
            Window.add_widget(self.bet_error_label)
            self._bet_error_added = True

        self.bet_error_label.text = msg
        self.bet_error_label.opacity = 1

        cp_x, cp_y   = self.control_panel.pos
        cp_w, cp_h   = self.control_panel.size
        lw, lh       = self.bet_error_label.size
        self.bet_error_label.pos = (
            cp_x + (cp_w - lw) / 2,
            cp_y + cp_h + 15
        )

        if self._bet_error_timer:
            Clock.unschedule(self._bet_error_timer)
        self._bet_error_timer = Clock.schedule_once(self._hide_bet_error, 2)

    def _hide_bet_error(self, dt):
        self.bet_error_label.opacity = 0
        self.bet_error_label.text    = ""

    # ──────────────────────────────────────────────────────────
    #  Deposit popup (updated styling)
    # ──────────────────────────────────────────────────────────
    def show_deposit_popup(self):
        content = BoxLayout(orientation="vertical", padding=15, spacing=15)

        content.add_widget(Label(
            text="ENTER DEPOSIT AMOUNT:",
            color=(0, 0, 0, 1),
            font_size="20sp",
            font_name="Arcade",
            size_hint=(1, 0.2),
            halign="center",
            valign="middle"
        ))

        self.deposit_input = TextInput(
            text="0",
            multiline=False,
            input_filter="int",
            foreground_color=(1, 1, 1, 1),
            background_normal="assets/images/texture3.png",
            background_active="assets/images/texture3.png",
            font_size="16sp",
            font_name="Arcade",
            halign="center",
            size_hint=(1, None),
            height=70,
            padding=[10, 0, 10, 0]
        )
        def _recenter_deposit(_inst, _val):
            offset = (self.deposit_input.height - self.deposit_input.line_height) / 2
            offset = max(offset, 0)
            self.deposit_input.padding = [10, offset, 10, offset]
        _recenter_deposit(None, None)
        self.deposit_input.bind(size=_recenter_deposit, font_size=_recenter_deposit)
        content.add_widget(self.deposit_input)

        self._deposit_button_row = BoxLayout(size_hint=(1, 0.3), spacing=20)
        # Create the "ADD" button
        add_btn = Button(
            text="ADD",
            color=(1, 1, 1, 1),
            background_normal="assets/images/texture10.png",
            background_down="assets/images/texture12.png",
            font_size="20sp",
            font_name="Arcade",
            size_hint=(0.45, 1)
        )

        # Add a black border to the ADD button
        with add_btn.canvas.after:
            Color(0, 0, 0, 1)
            add_outline = Line(rectangle=(0, 0, 0, 0), width=2)

        def update_add_border(*args):
            add_outline.rectangle = (*add_btn.pos, *add_btn.size)

        add_btn.bind(pos=update_add_border, size=update_add_border)

        # Create the "CANCEL" button
        cancel_btn = Button(
            text="CANCEL",
            color=(1, 1, 1, 1),
            background_normal="assets/images/texture10.png",
            background_down="assets/images/texture12.png",
            font_size="20sp",
            font_name="Arcade",
            size_hint=(0.45, 1)
        )

        # Add a black border to the CANCEL button
        with cancel_btn.canvas.after:
            Color(0, 0, 0, 1)
            cancel_outline = Line(rectangle=(0, 0, 0, 0), width=2)

        def update_cancel_border(*args):
            cancel_outline.rectangle = (*cancel_btn.pos, *cancel_btn.size)

        cancel_btn.bind(pos=update_cancel_border, size=update_cancel_border)

        self._deposit_button_row.add_widget(add_btn)
        self._deposit_button_row.add_widget(cancel_btn)
        content.add_widget(self._deposit_button_row)

        self._deposit_popup = Popup(
            title="DEPOSIT FUNDS",
            title_font="assets/fonts/arcade.ttf",
            title_size="26sp",
            title_align="center",
            title_color=(1, 1, 1, 1),
            content=content,
            size_hint=(None, None),
            size=(550, 350),
            background="assets/images/texture5.png",
            border=(0, 0, 0, 0),
            separator_height=0,
            auto_dismiss=False
        )

        add_btn.bind(on_release=lambda *_: self._on_deposit_add())
        cancel_btn.bind(on_release=lambda *_: self._on_deposit_cancel())

        with self._deposit_popup.canvas.after:
            Color(0, 0, 0, 1)
            outline = Line(
                rectangle=(self._deposit_popup.x,
                           self._deposit_popup.y,
                           self._deposit_popup.width,
                           self._deposit_popup.height),
                width=2
            )

        def _update_deposit_border(*args):
            outline.rectangle = (
                self._deposit_popup.x,
                self._deposit_popup.y,
                self._deposit_popup.width,
                self._deposit_popup.height
            )

        self._deposit_popup.bind(pos=_update_deposit_border, size=_update_deposit_border)
        self._deposit_popup.open()

    def _on_deposit_add(self):
        try:
            amount = int(self.deposit_input.text)
        except ValueError:
            self.show_deposit_error("Enter a valid number")
            return
        self.controller.deposit_money(amount)

    def _on_deposit_cancel(self):
        if self._deposit_popup:
            self._deposit_popup.dismiss()
            self._deposit_popup = None

    def dismiss_deposit_popup(self):
        if self._deposit_popup:
            self._deposit_popup.dismiss()
            self._deposit_popup = None

    def show_deposit_error(self, msg):
        if not hasattr(self, "_error_added"):
            Window.add_widget(self.deposit_error_label)
            self._error_added = True

        self.deposit_error_label.text = msg
        self.deposit_error_label.opacity = 1

        if self._deposit_popup:
            px, py = self._deposit_popup.pos
            pw, ph = self._deposit_popup.size
            lw, lh = self.deposit_error_label.size
            self.deposit_error_label.pos = (
                px + (pw - lw) / 2,
                py - (lh + 15)
            )

        if hasattr(self, "_deposit_error_timer") and self._deposit_error_timer:
            Clock.unschedule(self._deposit_error_timer)
        self._deposit_error_timer = Clock.schedule_once(self._hide_deposit_error, 2)

    def _hide_deposit_error(self, dt):
        self.deposit_error_label.opacity = 0
        self.deposit_error_label.text    = ""

    # ──────────────────────────────────────────────────────────
    #  TUTORIAL: step definitions + navigation
    # ──────────────────────────────────────────────────────────

    def _start_tutorial(self):
        # Initialize tutorial state:
        self._tutorial_step = 1
        self._show_tutorial_step()

    def _show_tutorial_step(self):
        # 1) Dismiss any existing tutorial popup or highlight
        if self._tutorial_popup:
            self._tutorial_popup.dismiss()
            self._tutorial_popup = None

        if self.highlight_widget:
            self.remove_widget(self.highlight_widget)
            self.highlight_widget = None

        # 2) Create or update the semi‐transparent overlay above the betting panel only
        panel_h = self.control_panel.height

        # ── create (or update) a semi-transparent rectangle inside self.track.canvas.before ──
        # ── create (or update) a semi‐transparent overlay above the entire track ──

        if not self._tutorial_overlay:
            # ── replace with this ──
            overlay = Widget()
            with overlay.canvas:
                Color(0, 0, 0, 0.6)
                # cover everything except control_panel (which sits at y==0)
                self._tutorial_rect = Rectangle(
                    pos=(0, self.control_panel.height),
                    size=(Window.width, Window.height - self.control_panel.height)
                )

            def _resize_overlay(*_):
                self._tutorial_rect.pos = (0, self.control_panel.height)
                self._tutorial_rect.size = (Window.width, Window.height - self.control_panel.height)

            Window.bind(size=_resize_overlay)
            self.control_panel.bind(size=_resize_overlay)

            self.add_widget(overlay)
            # put control_panel back on top:
            self.remove_widget(self.control_panel)
            self.add_widget(self.control_panel)
            self._tutorial_overlay = overlay


        else:
            # update the overlay to cover everything above the control_panel
            self._tutorial_rect.pos = (0, self.control_panel.height)
            self._tutorial_rect.size = (Window.width, Window.height - self.control_panel.height)

        # 3) Decide which step text and which widget(s) to highlight
        steps = {
            1: "Welcome! In this game, you bet on\nsix horses. Choose your horse and\nsee who wins!\n",
            2: "“Balance” shows your current money\navailable to bet.",
            3: "Use the “Bet Amount” field to set\nhow much you want to wager.",
            4: "Click the “Deposit” button to add\nmore funds to your balance.",
            5: "Press one of the six horse buttons\nto place your bet on that horse."
        }
        step_text = steps.get(self._tutorial_step, "")

        highlight_map = {
            2: [self.balance_label],
            3: [self.bet_input],
            4: [self.deposit_btn],  # make sure you have stored self.deposit_btn in _build_controls
            5: self.horse_buttons  # make sure you have a list self.horse_buttons in _build_controls
        }

        # 4) Draw a red border around the target widget(s), if needed
        # 4) Draw a red border on top of the target widget(s), if needed
        if self._tutorial_step in (2, 3, 4, 5):
            targets = highlight_map[self._tutorial_step]
            min_x = min(w.x for w in targets)
            min_y = min(w.y for w in targets)
            max_x = max(w.x + w.width for w in targets)
            max_y = max(w.y + w.height for w in targets)
            w_box = max_x - min_x
            h_box = max_y - min_y

            # create a Widget purely to hold the red Line
            hw = Widget()

            # Draw the Line under hw.canvas.after so it appears ABOVE the widget being highlighted
            with hw.canvas.after:
                Color(1, 0, 0, 1)  # bright red
                ln = Line(rectangle=(min_x, min_y, w_box, h_box), width=2)

            def _sync_red_border(*_):
                nx = min(w.x for w in targets)
                ny = min(w.y for w in targets)
                mx = max(w.x + w.width for w in targets)
                my = max(w.y + w.height for w in targets)
                ln.rectangle = (nx, ny, mx - nx, my - ny)

            for w in targets:
                w.bind(pos=_sync_red_border, size=_sync_red_border)

            self.highlight_widget = hw
            # Make sure the highlight Widget is above the track (and above the hue).
            # In a FloatLayout, the last‐added widget floats on top.
            self.add_widget(self.highlight_widget)

        # 5) Build the centered popup UI for this step
        content = BoxLayout(orientation="vertical", padding=15, spacing=10)

        text_lbl = Label(
            text=step_text,
            color=(0, 0, 0, 1),
            font_size="16sp",
            font_name="Arcade",
            size_hint=(1, 0.6),
            halign="left",
            valign="middle"
        )
        content.add_widget(text_lbl)

        btn_row = BoxLayout(size_hint=(1, 0.4), spacing=20)
        prev_btn = Button(
            text="Previous",
            size_hint=(0.1, 1),
            font_size="18sp",
            font_name="Arcade",
            background_normal="assets/images/texture10.png",
            background_down="assets/images/texture12.png",
            color=(1, 1, 1, 1)
        )
        # Add a black border to the PREVIOUS button
        with prev_btn.canvas.after:
            Color(0, 0, 0, 1)
            prev_outline = Line(rectangle=(0, 0, 0, 0), width=2)

        def update_prev_border(*args):
            prev_outline.rectangle = (*prev_btn.pos, *prev_btn.size)

        prev_btn.bind(pos=update_prev_border, size=update_prev_border)

        next_btn = Button(
            text="Next",
            size_hint=(0.1, 1),
            font_size="18sp",
            font_name="Arcade",
            background_normal="assets/images/texture10.png",
            background_down="assets/images/texture12.png",
            color=(1, 1, 1, 1)
        )

        # Add a black border to the NEXT button
        with next_btn.canvas.after:
            Color(0, 0, 0, 1)
            next_outline = Line(rectangle=(0, 0, 0, 0), width=2)

        def update_next_border(*args):
            next_outline.rectangle = (*next_btn.pos, *next_btn.size)

        next_btn.bind(pos=update_next_border, size=update_next_border)

        cancel_btn = Button(
            text="Cancel",
            size_hint=(0.1, 1),
            font_size="18sp",
            font_name="Arcade",
            background_normal="assets/images/texture10.png",
            background_down="assets/images/texture12.png",
            color=(1, 1, 1, 1)
        )

        # Add a black border to the CANCEL button
        with cancel_btn.canvas.after:
            Color(0, 0, 0, 1)
            cancel_outline = Line(rectangle=(0, 0, 0, 0), width=2)

        def update_cancel_border(*args):
            cancel_outline.rectangle = (*cancel_btn.pos, *cancel_btn.size)

        cancel_btn.bind(pos=update_cancel_border, size=update_cancel_border)

        prev_btn.disabled = (self._tutorial_step == 1)
        next_btn.disabled = (self._tutorial_step == len(steps))

        btn_row.add_widget(prev_btn)
        btn_row.add_widget(next_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        self._tutorial_popup = Popup(
            title=f"TUTORIAL - {self._tutorial_step}/{len(steps)}",
            title_font="assets/fonts/arcade.ttf",
            title_size="24sp",
            title_align="center",
            title_color=(1, 1, 1, 1),
            content=content,
            size_hint=(None, None),
            size=(670, 350),
            background="assets/images/texture5.png",
            overlay_color=(0, 0, 0, 0),  # ← disable the Popup’s own dimming
            border=(0, 0, 0, 0),
            separator_height=0,
            auto_dismiss=False
        )

        prev_btn.bind(on_release=lambda *_: self._step_previous())
        next_btn.bind(on_release=lambda *_: self._step_next())
        cancel_btn.bind(on_release=lambda *_: self._end_tutorial())

        self._tutorial_popup.open()

    def _step_previous(self):
        if self._tutorial_step > 1:
            self._tutorial_step -= 1
            self._show_tutorial_step()

    def _step_next(self):
        max_step = 5
        if self._tutorial_step < max_step:
            self._tutorial_step += 1
            self._show_tutorial_step()

    def _end_tutorial(self):
        if self._tutorial_popup:
            self._tutorial_popup.dismiss()
            self._tutorial_popup = None

        if self._tutorial_overlay:
            self.remove_widget(self._tutorial_overlay)
            self._tutorial_overlay = None
            self._tutorial_rect = None

        if self.highlight_widget:
            self.remove_widget(self.highlight_widget)
            self.highlight_widget = None



