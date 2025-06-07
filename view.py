"""
File: view.py

Description:
    Defines the graphical user interface for the Horse Race Betting Game using Kivy.
    Includes the RaceTrack and HorseSprite widgets for rendering the race,
    and the GameView class for assembling controls, handling user input,
    managing audio, popups, animations, and localization.

Version: 1.0
Author: Robbe de Guytenaer, Bernardo José Willis Lozano
"""

from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, Line, Ellipse, InstructionGroup
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.core.text import LabelBase

LabelBase.register(name="Arcade", fn_regular="assets/fonts/arcade.ttf")


class RaceTrack(Widget):
    """
    Widget that draws the race track background, start and finish lines,
    and positions HorseSprite instances.
    """

    def __init__(self, **kwargs):
        """
        Initialize the RaceTrack, load background images and prepare the finish line widget.
        """
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.grass_top = Rectangle(source="assets/images/grass1.png")
            self.grass_bottom = Rectangle(source="assets/images/grass2.png")
            self.track_bg = Rectangle(source="assets/images/racetrack.png")
            Color(0.55, 0.27, 0.07, 0.1)
            self.start_line = Line(points=[0, 0, 0, 0], width=6)

        self.finish_line_image = Image(
            source="assets/images/finish_line_1.png",
            allow_stretch=True,
            keep_ratio=False,
        )
        self.add_widget(self.finish_line_image)
        self.bind(pos=self._update_layout, size=self._update_layout)
        self.horses = []
        self.bind(size=lambda *_: Clock.schedule_once(self._setup, 0))

    def _update_layout(self, *args) -> None:
        """
        Recalculate positions and sizes of grass, track, and start/finish lines
        whenever the widget's size or position changes.
        """
        x, y, w, h = self.x, self.y, self.width, self.height
        grass_height = h * 0.05
        bottom_height = h * 0.20

        self.grass_top.pos = (x, y + h - grass_height)
        self.grass_top.size = (w, grass_height)
        self.grass_bottom.pos = (x, y)
        self.grass_bottom.size = (w, bottom_height)
        self.track_bg.pos = (x, y + bottom_height)
        self.track_bg.size = (w, h - bottom_height - grass_height)

        finish_x = x + w * 0.9
        track_y = y + bottom_height
        track_h = h - bottom_height - grass_height
        self.finish_line_image.size = (60, track_h)
        self.finish_line_image.pos = (finish_x, track_y)

        start_x = x + w * 0.1 + 85
        self.start_line.points = [
            start_x, track_y,
            start_x, track_y + track_h
        ]

    def _setup(self, dt=None) -> None:
        """
        Create HorseSprite instances, position them evenly along the track,
        and add them as children of this widget.
        """
        for child in self.horses:
            self.remove_widget(child)
        self.horses = []

        num_horses = 6
        sample = HorseSprite(1)
        horse_h = sample.height
        bottom_margin = self.height * 0.22
        visible_h = self.height - bottom_margin
        spacing = (visible_h - num_horses * horse_h) / (num_horses + 1)
        start_x = self.width * 0.1

        for i in range(num_horses):
            y = bottom_margin + spacing * (i + 1) + horse_h * i
            sprite = HorseSprite(i + 1)
            sprite.pos = (start_x, y)
            self.horses.append(sprite)
            self.add_widget(sprite)


class HorseSprite(Widget):
    """
    Widget representing a single horse, with static and animated images,
    a numeric label, and optional highlight overlay.
    """

    def __init__(self, number: int, **kwargs):
        """
        Initialize the HorseSprite with a horse number, size, image sources,
        and label.
        """
        super().__init__(**kwargs)
        self.number = number
        self.size = (100, 100)
        self.static_source = f"assets/images/horses/horse{number}.png"
        self.animated_source = f"assets/images/horses/horserun{number}.gif"
        self.running = False
        self._highlight_group = None

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
            size=self.size,
            color=(1, 1, 1, 1),
            font_size="20sp",
            font_name="Arcade",
            bold=True
        )
        self.add_widget(self.label)
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *args) -> None:
        """
        Synchronize child image and label positions and highlight overlay
        when this widget moves or resizes.
        """
        self.image.pos = self.pos
        self.image.size = self.size
        self.label.center_x = self.center_x - 18
        self.label.center_y = self.center_y

        if self._highlight_group:
            padding = 8
            self._highlight_ellipse.pos = (self.x - padding, self.y - padding)
            self._highlight_ellipse.size = (self.width + padding*2, self.height + padding*2)

    def set_running(self, running: bool) -> None:
        """
        Switch between static and animated image based on running state.

        Args:
            running (bool): True to show running animation, False for static image.
        """
        if running == self.running:
            return
        self.running = running
        if running:
            self.image.source = self.animated_source
            self.image.anim_delay = 0.05
        else:
            self.image.source = self.static_source
            self.image.anim_delay = -1
        self.image.reload()

    def highlight(self) -> None:
        """
        Add a translucent ellipse behind the sprite to indicate selection.
        """
        if self._highlight_group:
            return
        padding = 8
        group = InstructionGroup()
        group.add(Color(1, 1, 0, 0.3))
        ellipse = Ellipse(
            pos=(self.x - padding, self.y - padding),
            size=(self.width + padding*2, self.height + padding*2)
        )
        group.add(ellipse)
        self._highlight_group = group
        self._highlight_ellipse = ellipse
        self.canvas.before.add(group)
        self.bind(pos=self._sync, size=self._sync)

    def unhighlight(self) -> None:
        """
        Remove the highlight overlay from the sprite.
        """
        if not self._highlight_group:
            return
        try:
            self.canvas.before.remove(self._highlight_group)
        except Exception:
            pass
        self.unbind(pos=self._sync, size=self._sync)
        self._highlight_group = None
        self._highlight_ellipse = None


class GameView(FloatLayout):
    """
    Main application view: assembles the race track, control panels, settings,
    tutorial, popups, and manages all user interactions and animations.
    """

    def __init__(self, lang_mgr, **kwargs):
        """
        Initialize GameView with language manager for localization,
        load audio assets, create track and controls, and schedule initial text updates.

        Args:
            lang_mgr (LanguageManager): Manager for localized strings.
        """
        super().__init__(**kwargs)
        self.lang = lang_mgr

        # References to dynamic UI elements
        self.bet_amount_label = None
        self.deposit_btn = None
        self.settings_popup = None
        self.lang_popup = None
        self._deposit_popup = None
        self.result_popup = None
        self._tutorial_popup = None
        self._tutorial_overlay = None
        self.highlight_widget = None

        # Load audio assets
        def _load(path, *, loop=False, vol=1.0):
            snd = SoundLoader.load(path)
            if snd:
                snd.loop = loop
                snd.volume = vol
                snd._orig_vol = vol
            return snd

        self.click_snd = _load("assets/sounds/click.mp3", vol=0.8)
        self.pop_snd = _load("assets/sounds/popup.mp3", vol=1.0)
        self.pistol_snd = _load("assets/sounds/starterpistol.mp3", vol=0.8)
        self.win_snd = _load("assets/sounds/win.mp3", vol=0.9)
        self.disappointed_snd = _load("assets/sounds/disappointed.mp3", vol=0.5)
        self.whip_snd = _load("assets/sounds/whip.mp3", vol=1.0)
        self.bg_music = _load("assets/sounds/music.mp3", loop=True, vol=0.2)
        self.bg_horse = _load("assets/sounds/horsebackground.mp3", loop=True, vol=0.5)
        self.gallop_snd = _load("assets/sounds/horsegallop.mp3", loop=True, vol=0.4)

        if self.bg_music:
            self.bg_music.play()
        if self.bg_horse:
            self.bg_horse.play()

        self._gallop_event = None
        self._pistol_event = None
        self.music_muted = False
        self.sounds_muted = False
        self._race_active = False
        self._selected_horse = None

        # Create and add the track
        self.track = RaceTrack(size_hint=(1, 1))
        self.add_widget(self.track)

        # Build control panels and auxiliary UI
        self._build_controls()
        self._build_settings_button()
        self._build_tutorial_button()

        # Error and status labels
        self.bet_error_label = Label(
            text="", color=(1, 0, 0, 1), font_size="18sp",
            font_name="Arcade", size_hint=(None, None), size=(400, 30),
            opacity=0, halign="center", valign="middle"
        )
        self._bet_error_added = False
        self._bet_error_timer = None

        self.deposit_error_label = Label(
            text="", color=(1, 0, 0, 1), font_size="18sp",
            font_name="Arcade", size_hint=(None, None), size=(500, 30),
            opacity=0, halign="center", valign="middle"
        )

        self.leading_label = Label(
            text="", color=(1, 1, 1, 1), font_size="20sp",
            font_name="Arcade", size_hint=(0.5, None), height=30,
            opacity=0, halign="center", valign="middle",
            pos_hint={"center_x": 0.5, "y": 0.08}
        )
        self.add_widget(self.leading_label)

        Clock.schedule_once(lambda dt: self.update_ui_texts(), 0)

    def _play_click(self) -> None:
        """
        Play click sound if sounds are enabled.
        """
        if self.click_snd and not self.sounds_muted:
            self.click_snd.stop()
            self.click_snd.play()

    def on_touch_down(self, touch) -> bool:
        """
        Play whip sound on touch during an active race and propagate event.

        Args:
            touch: Touch event object.

        Returns:
            bool: Result of super().on_touch_down.
        """
        if self._race_active and self.whip_snd and not self.sounds_muted:
            self.whip_snd.stop()
            self.whip_snd.play()
        return super().on_touch_down(touch)

    def _add_border(self, widget, rgba=(0, 0, 0, 1), width=2) -> None:
        """
        Draw a border around a widget.

        Args:
            widget: The widget to decorate.
            rgba (tuple): RGBA color for the border.
            width (int): Border width.
        """
        with widget.canvas.after:
            Color(*rgba)
            ln = Line(
                rectangle=(widget.x, widget.y, widget.width, widget.height),
                width=width, joint="miter"
            )
        widget.bind(
            pos=lambda *_: self._sync_line(ln, widget),
            size=lambda *_: self._sync_line(ln, widget)
        )

    @staticmethod
    def _sync_line(line, w) -> None:
        """
        Synchronize a border line's rectangle to widget geometry.

        Args:
            line: The Line instruction.
            w: The widget being bordered.
        """
        line.rectangle = (w.x, w.y, w.width, w.height)

    def _build_settings_button(self) -> None:
        """
        Create and position the settings gear button.
        """
        gear = Button(
            text="", size_hint=(None, None), size=(45, 45),
            pos_hint={"right": .04, "top": 0.28},
            background_normal="assets/images/settings.png",
            background_down="assets/images/settings2.png",
            border=(0, 0, 0, 0), background_color=(1, 1, 1, 1)
        )
        gear.bind(on_release=lambda *_: self._show_settings_popup())
        self.add_widget(gear)

    def _toggle_music(self, btn: Button) -> None:
        """
        Mute or unmute background music and update button appearance and text.

        Args:
            btn (Button): The toggle button instance.
        """
        self.music_muted = not self.music_muted
        btn.text = (
            self.lang.get("unmute_music") if self.music_muted
            else self.lang.get("mute_music")
        )
        if self.music_muted:
            btn.background_normal = "assets/images/texture13.png"
            btn.background_down = "assets/images/texture14.png"
        else:
            btn.background_normal = "assets/images/texture10.png"
            btn.background_down = "assets/images/texture12.png"
        for snd in (self.bg_music, self.bg_horse, self.gallop_snd):
            if snd:
                snd.volume = 0 if self.music_muted else snd._orig_vol

    def _toggle_sounds(self, btn: Button) -> None:
        """
        Mute or unmute sound effects and update button appearance and text.

        Args:
            btn (Button): The toggle button instance.
        """
        self.sounds_muted = not self.sounds_muted
        btn.text = (
            self.lang.get("unmute_sounds") if self.sounds_muted
            else self.lang.get("mute_sounds")
        )
        if self.sounds_muted:
            btn.background_normal = "assets/images/texture13.png"
            btn.background_down = "assets/images/texture14.png"
        else:
            btn.background_normal = "assets/images/texture10.png"
            btn.background_down = "assets/images/texture12.png"
        for snd in (self.click_snd, self.pop_snd, self.pistol_snd, self.win_snd):
            if snd:
                snd.volume = 0 if self.sounds_muted else snd._orig_vol

    def _show_settings_popup(self) -> None:
        """
        Display the settings popup allowing toggling music, sounds, and language.
        """
        if self.pop_snd and not self.sounds_muted:
            self.pop_snd.stop(); self.pop_snd.play()

        root = FloatLayout()

        music_btn = Button(
            text=(self.lang.get("unmute_music") if self.music_muted else self.lang.get("mute_music")),
            font_size="22sp", font_name="Arcade",
            size_hint=(0.8, 0.18), pos_hint={"center_x": 0.5, "center_y": 0.85},
            background_normal="assets/images/texture10.png",
            background_down="assets/images/texture12.png",
            border=(0, 0, 0, 0)
        )
        sounds_btn = Button(
            text=(self.lang.get("unmute_sounds") if self.sounds_muted else self.lang.get("mute_sounds")),
            font_size="22sp", font_name="Arcade",
            size_hint=(0.8, 0.18), pos_hint={"center_x": 0.5, "center_y": 0.62},
            background_normal="assets/images/texture10.png",
            background_down="assets/images/texture12.png",
            border=(0, 0, 0, 0)
        )
        language_btn = Button(
            text=self.lang.get("language"),
            font_size="22sp", font_name="Arcade",
            size_hint=(0.8, 0.18), pos_hint={"center_x": 0.5, "center_y": 0.39},
            background_normal="assets/images/texture10.png",
            background_down="assets/images/texture12.png",
            border=(0, 0, 0, 0)
        )
        close_btn = Button(
            text=self.lang.get("close"),
            font_size="22sp", font_name="Arcade",
            size_hint=(0.8, 0.18), pos_hint={"center_x": 0.5, "center_y": 0.16},
            background_normal="assets/images/texture10.png",
            background_down="assets/images/texture12.png",
            border=(0, 0, 0, 0)
        )

        for btn in (music_btn, sounds_btn, language_btn, close_btn):
            self._add_border(btn)
            root.add_widget(btn)

        music_btn.bind(on_release=lambda *_: (self._play_click(), self._toggle_music(music_btn)))
        sounds_btn.bind(on_release=lambda *_: (self._play_click(), self._toggle_sounds(sounds_btn)))
        language_btn.bind(on_release=lambda *_: (self._play_click(), self._change_language()))
        close_btn.bind(on_release=lambda *_: (self._play_click(), self.settings_popup.dismiss()))

        self.settings_popup = Popup(
            title=self.lang.get("settings_title"),
            title_font="assets/fonts/arcade.ttf",
            title_size="26sp",
            title_align="center",
            title_color=(1, 1, 1, 1),
            content=root,
            size_hint=(None, None),
            size=(500, 450),
            background="assets/images/texture5.png",
            border=(0, 0, 0, 0),
            separator_height=0,
            auto_dismiss=False,
        )

        with self.settings_popup.canvas.after:
            Color(0, 0, 0, 1)
            outline = Line(
                rectangle=(
                    self.settings_popup.x,
                    self.settings_popup.y,
                    self.settings_popup.width,
                    self.settings_popup.height
                ),
                width=2
            )

        def _upd_sp(*_):
            outline.rectangle = (
                self.settings_popup.x,
                self.settings_popup.y,
                self.settings_popup.width,
                self.settings_popup.height
            )

        self.settings_popup.bind(pos=_upd_sp, size=_upd_sp)
        self.settings_popup.open()

    def _change_language(self) -> None:
        """
        Close settings popup and open the language selection popup.
        """
        if self.settings_popup:
            self.settings_popup.dismiss()
        self._show_language_popup()

    def _show_language_popup(self) -> None:
        """
        Display a popup to select the application's language.
        """
        if self.pop_snd and not self.sounds_muted:
            self.pop_snd.stop(); self.pop_snd.play()

        root = FloatLayout()
        btn_kwargs = dict(
            font_size="22sp", font_name="Arcade",
            size_hint=(0.8, 0.18),
            background_normal="assets/images/texture10.png",
            background_down="assets/images/texture12.png",
            border=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )

        def make_lang_btn(code, label, pos_y):
            btn = Button(text=label, pos_hint={"center_x": 0.5, "center_y": pos_y}, **btn_kwargs)
            self._add_border(btn)
            btn.bind(on_release=lambda *_: (
                self._play_click(),
                self.lang.load(code),
                self.update_ui_texts(),
                self.lang_popup.dismiss(),
                self._show_settings_popup()
            ))
            root.add_widget(btn)

        make_lang_btn("en", "English", 0.75)
        make_lang_btn("es", "Español", 0.55)
        make_lang_btn("sv", "Svenska", 0.35)

        cancel_btn = Button(text=self.lang.get("cancel"), pos_hint={"center_x": 0.5, "center_y": 0.15}, **btn_kwargs)
        self._add_border(cancel_btn)
        cancel_btn.bind(on_release=lambda *_: (
            self._play_click(),
            self.lang_popup.dismiss(),
            self._show_settings_popup()
        ))
        root.add_widget(cancel_btn)

        self.lang_popup = Popup(
            title=self.lang.get("language"),
            title_font="assets/fonts/arcade.ttf",
            title_size="26sp",
            title_align="center",
            title_color=(1, 1, 1, 1),
            content=root,
            size_hint=(None, None),
            size=(500, 450),
            background="assets/images/texture5.png",
            border=(0, 0, 0, 0),
            separator_height=0,
            auto_dismiss=False,
        )

        with self.lang_popup.canvas.after:
            Color(0, 0, 0, 1)
            outline = Line(
                rectangle=(
                    self.lang_popup.x,
                    self.lang_popup.y,
                    self.lang_popup.width,
                    self.lang_popup.height
                ),
                width=2
            )

        def _upd_lp(*_):
            outline.rectangle = (
                self.lang_popup.x,
                self.lang_popup.y,
                self.lang_popup.width,
                self.lang_popup.height
            )

        self.lang_popup.bind(pos=_upd_lp, size=_upd_lp)
        self.lang_popup.open()

    def _build_controls(self) -> None:
        """
        Build the betting and deposit control panel with inputs, buttons, and balance display.
        """
        self.control_panel = BoxLayout(orientation="vertical", size_hint=(1, 0.2), pos_hint={"x": 0, "y": 0})
        with self.control_panel.canvas.before:
            self.bg_rect = Rectangle(source="assets/images/texture1.png",
                                     pos=self.control_panel.pos, size=self.control_panel.size)
        self.control_panel.bind(
            pos=lambda *a: setattr(self.bg_rect, "pos", self.control_panel.pos),
            size=lambda *a: setattr(self.bg_rect, "size", self.control_panel.size)
        )
        self._add_border(self.control_panel, (0, 0, 0, 1), 2)

        top_row = BoxLayout(size_hint=(1, 0.4))
        self.bet_amount_label = Label(
            text=self.lang.get("bet_amount"),
            color=(0, 0, 0, 1),
            font_size="25sp",
            font_name="Arcade"
        )
        top_row.add_widget(self.bet_amount_label)

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

        def adjust_padding(_, __):
            off = (self.bet_input.height - self.bet_input.line_height) / 2
            self.bet_input.padding = [0, max(0, off), 0, max(0, off)]

        adjust_padding(None, None)
        self.bet_input.bind(size=adjust_padding, font_size=adjust_padding)
        top_row.add_widget(self.bet_input)
        self._add_border(self.bet_input, (0, 0, 0, 1), 2)

        self.balance_label = Label(text="", color=(0, 0, 0, 1), font_size="25sp", font_name="Arcade")
        top_row.add_widget(self.balance_label)

        self.deposit_btn = Button(
            text=self.lang.get("deposit"),
            color=(0, 0, 0, 1),
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            font_size="24sp",
            font_name="Arcade"
        )
        self.deposit_btn.bind(on_release=lambda *_: self.show_deposit_popup())
        top_row.add_widget(self.deposit_btn)
        self._add_border(self.deposit_btn, (0, 0, 0, 1), 2)

        self.control_panel.add_widget(top_row)

        horse_row = BoxLayout(size_hint=(1, 0.5))
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
            btn.bind(on_release=lambda inst: (self._play_click(), self._on_bet(inst)))
            self._add_border(btn, (0, 0, 0, 1), 2)
            horse_row.add_widget(btn)
            self.horse_buttons.append(btn)

        self.control_panel.add_widget(horse_row)
        self.add_widget(self.control_panel)

    def _on_bet(self, instance: Button) -> None:
        """
        Handle horse selection and initiate bet placement via controller.

        Args:
            instance (Button): The horse button that was pressed.
        """
        if self.click_snd and not self.sounds_muted:
            self.click_snd.stop(); self.click_snd.play()
        if self.pistol_snd and not self.sounds_muted:
            if self._pistol_event:
                Clock.unschedule(self._pistol_event)
            self._pistol_event = Clock.schedule_once(
                lambda _dt: (self.pistol_snd.stop(), self.pistol_snd.play()), 0.01
            )

        horse_number = int(instance.text)
        amount = int(self.bet_input.text)
        self._selected_horse = horse_number

        for sprite in self.track.horses:
            if sprite.number == horse_number:
                sprite.highlight()
            else:
                sprite.unhighlight()

        try:
            self.controller.place_bet(horse_number, amount)
        except Exception:
            pass

    def update_balance(self, balance: float) -> None:
        """
        Update the balance display label.

        Args:
            balance (float): The new balance to display.
        """
        self.balance_label.text = f"{self.lang.get('balance')}: ${balance}"

    def start_race_animation(self, horse_speeds, finish_x: float) -> None:
        """
        Begin the race animation loop, play gallop sound, and show leading horse.

        Args:
            horse_speeds: Unused placeholder (speeds stored in model).
            finish_x (float): X-coordinate of the finish line.
        """
        if hasattr(self, "tutorial_btn"):
            self.tutorial_btn.opacity = 0
            self.tutorial_btn.disabled = True

        self._race_active = True
        if self.gallop_snd and not self.music_muted:
            if self._gallop_event:
                Clock.unschedule(self._gallop_event)
            self._gallop_event = Clock.schedule_once(
                lambda _dt: (self.gallop_snd.stop(), self.gallop_snd.play()), 0.5
            )

        for sprite in self.track.horses:
            sprite.set_running(True)

        self.leading_label.opacity = 1
        self.finish_x = finish_x
        self.event = Clock.schedule_interval(self._animate, 1 / 60)

    def _animate(self, dt) -> None:
        """
        Called on each frame: update model, move sprites, and update leading label.

        Args:
            dt: Time since last frame.
        """
        self.controller.update_speeds_and_positions()
        for sprite in self.track.horses:
            pos = self.controller.model.horses[sprite.number - 1].position
            sprite.x = self.track.x + pos

        leader = max(
            self.track.horses,
            key=lambda spr: self.controller.model.horses[spr.number - 1].position
        ).number
        self.leading_label.text = f"{self.lang.get('leading_horse')} {leader}"

    def reset_track(self) -> None:
        """
        Stop sounds and animation, reset track and control panel to initial state.
        """
        if self.gallop_snd:
            self.gallop_snd.stop()
        if self._gallop_event:
            Clock.unschedule(self._gallop_event)
            self._gallop_event = None

        self.track._setup()
        self.control_panel.opacity = 1
        self.control_panel.disabled = False
        self.leading_label.opacity = 0
        self.leading_label.text = ""
        if hasattr(self, "tutorial_btn"):
            self.tutorial_btn.opacity = 1
            self.tutorial_btn.disabled = False

        self._race_active = False
        for sprite in self.track.horses:
            sprite.unhighlight()
        self._selected_horse = None

    def show_result(self, winner: int, player_won: bool, payout: float) -> None:
        """
        Display a popup showing race results and payout or loss.

        Args:
            winner (int): Winning horse number.
            player_won (bool): True if player's horse won.
            payout (float): Amount won or lost.
        """
        title = self.lang.get("race_result")
        line1 = self.lang.get("horse_wins").format(winner)
        if player_won:
            if self.win_snd and not self.sounds_muted:
                self.win_snd.stop(); self.win_snd.play()
            line2 = self.lang.get("you_won").format(payout)
        else:
            if self.disappointed_snd and not self.sounds_muted:
                self.disappointed_snd.stop(); self.disappointed_snd.play()
            line2 = self.lang.get("you_lost").format(payout)

        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        content.add_widget(Label(text=line1, font_size="22sp", font_name="Arcade", color=(0, 0, 0, 1)))
        content.add_widget(Label(
            text=line2,
            font_size="18sp",
            font_name="Arcade",
            color=(0, 0.35, 0, 1) if player_won else (0.55, 0, 0, 1)
        ))

        self.result_popup = Popup(
            title=title,
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

        with self.result_popup.canvas.after:
            Color(0, 0, 0, 1)
            outline = Line(
                rectangle=(
                    self.result_popup.x,
                    self.result_popup.y,
                    self.result_popup.width,
                    self.result_popup.height
                ),
                width=2
            )

        def _upd_res(*_):
            outline.rectangle = (
                self.result_popup.x,
                self.result_popup.y,
                self.result_popup.width,
                self.result_popup.height
            )

        self.result_popup.bind(pos=_upd_res, size=_upd_res)
        self.result_popup.open()

    def show_bet_error(self, msg: str) -> None:
        """
        Show a temporary error label below the control panel for invalid bets.

        Args:
            msg (str): Error message to display.
        """
        if not self._bet_error_added:
            Window.add_widget(self.bet_error_label)
            self._bet_error_added = True

        self.bet_error_label.text = msg
        self.bet_error_label.opacity = 1
        cp_x, cp_y = self.control_panel.pos
        cp_w, cp_h = self.control_panel.size
        lw, lh = self.bet_error_label.size
        self.bet_error_label.pos = (cp_x + (cp_w - lw)/2, cp_y + cp_h + 15)

        if self._bet_error_timer:
            Clock.unschedule(self._bet_error_timer)
        self._bet_error_timer = Clock.schedule_once(self._hide_bet_error, 2)

    def _hide_bet_error(self, dt) -> None:
        """
        Hide the bet error label.
        """
        self.bet_error_label.opacity = 0
        self.bet_error_label.text = ""

    def show_deposit_popup(self) -> None:
        """
        Display a popup allowing the user to enter an amount to deposit.
        """
        if self.pop_snd and not self.sounds_muted:
            self.pop_snd.stop(); self.pop_snd.play()

        content = BoxLayout(orientation="vertical", padding=15, spacing=15)
        content.add_widget(Label(
            text=self.lang.get("enter_deposit"),
            color=(0, 0, 0, 1),
            font_size="20sp",
            font_name="Arcade",
            size_hint=(1, 0.2),
            halign="center",
            valign="middle"
        ))

        self.deposit_input = TextInput(
            text="10",
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

        def adjust(_, __):
            off = (self.deposit_input.height - self.deposit_input.line_height)/2
            self.deposit_input.padding = [10, max(off, 0), 10, max(off, 0)]

        adjust(None, None)
        self.deposit_input.bind(size=adjust, font_size=adjust)
        content.add_widget(self.deposit_input)

        row = BoxLayout(size_hint=(1, 0.3), spacing=20)
        add_btn = Button(
            text=self.lang.get("add"),
            color=(1, 1, 1, 1),
            background_normal="assets/images/texture10.png",
            background_down="assets/images/texture12.png",
            font_size="20sp",
            font_name="Arcade",
            size_hint=(0.45, 1)
        )
        with add_btn.canvas.after:
            Color(0, 0, 0, 1)
            ao = Line(rectangle=(0, 0, 0, 0), width=2)

        def _ua(*_):
            ao.rectangle = (*add_btn.pos, *add_btn.size)

        add_btn.bind(pos=_ua, size=_ua)

        cancel_btn = Button(
            text=self.lang.get("cancel"),
            color=(1, 1, 1, 1),
            background_normal="assets/images/texture10.png",
            background_down="assets/images/texture12.png",
            font_size="20sp",
            font_name="Arcade",
            size_hint=(0.45, 1)
        )
        with cancel_btn.canvas.after:
            Color(0, 0, 0, 1)
            co = Line(rectangle=(0, 0, 0, 0), width=2)

        def _uc(*_):
            co.rectangle = (*cancel_btn.pos, *cancel_btn.size)

        cancel_btn.bind(pos=_uc, size=_uc)

        row.add_widget(add_btn)
        row.add_widget(cancel_btn)
        content.add_widget(row)

        self._deposit_popup = Popup(
            title=self.lang.get("deposit"),
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

        add_btn.bind(on_release=lambda *_: (self._play_click(), self._on_deposit_add()))
        cancel_btn.bind(on_release=lambda *_: (self._play_click(), self._on_deposit_cancel()))

        with self._deposit_popup.canvas.after:
            Color(0, 0, 0, 1)
            outline = Line(
                rectangle=(
                    self._deposit_popup.x,
                    self._deposit_popup.y,
                    self._deposit_popup.width,
                    self._deposit_popup.height
                ),
                width=2
            )

        def _ud(*_):
            outline.rectangle = (
                self._deposit_popup.x,
                self._deposit_popup.y,
                self._deposit_popup.width,
                self._deposit_popup.height
            )

        self._deposit_popup.bind(pos=_ud, size=_ud)
        self._deposit_popup.open()

    def _on_deposit_add(self) -> None:
        """
        Validate and send deposit amount to controller.
        """
        try:
            amount = int(self.deposit_input.text)
        except ValueError:
            self.show_deposit_error(self.lang.get("invalid_amount"))
            return
        self.controller.deposit_money(amount)

    def _on_deposit_cancel(self) -> None:
        """
        Close the deposit popup without action.
        """
        if self._deposit_popup:
            self._deposit_popup.dismiss()
            self._deposit_popup = None

    def dismiss_deposit_popup(self) -> None:
        """
        Close the deposit popup if open.
        """
        if self._deposit_popup:
            self._deposit_popup.dismiss()
            self._deposit_popup = None

    def show_deposit_error(self, msg: str) -> None:
        """
        Show a temporary error label near the deposit popup.

        Args:
            msg (str): Error message to display.
        """
        if not hasattr(self, "_error_added"):
            Window.add_widget(self.deposit_error_label)
            self._error_added = True

        self.deposit_error_label.text = msg
        self.deposit_error_label.opacity = 1

        if self._deposit_popup:
            px, py = self._deposit_popup.pos
            pw, ph = self._deposit_popup.size
            lw, lh = self.deposit_error_label.size
            self.deposit_error_label.pos = (px + (pw - lw)/2, py - (lh + 15))

        if hasattr(self, "_deposit_error_timer") and self._deposit_error_timer:
            Clock.unschedule(self._deposit_error_timer)
        self._deposit_error_timer = Clock.schedule_once(self._hide_deposit_error, 2)

    def _hide_deposit_error(self, dt) -> None:
        """
        Hide the deposit error label.
        """
        self.deposit_error_label.opacity = 0
        self.deposit_error_label.text = ""

    def _build_tutorial_button(self) -> None:
        """
        Create and position the tutorial help button.
        """
        self.tutorial_btn = Button(
            text="", size_hint=(None, None), size=(45, 45),
            pos_hint={"right": .04, "top": 0.34},
            background_normal="assets/images/tutorial1.png",
            background_down="assets/images/tutorial2.png",
            border=(0, 0, 0, 0), background_color=(1, 1, 1, 1)
        )

        def _on_tut(*_):
            if self.pop_snd and not self.sounds_muted:
                self.pop_snd.stop(); self.pop_snd.play()
            self._start_tutorial()

        self.tutorial_btn.bind(on_release=_on_tut)
        self.add_widget(self.tutorial_btn)

    def _start_tutorial(self) -> None:
        """
        Begin tutorial sequence at step 1.
        """
        self._tutorial_step = 1
        self._show_tutorial_step()

    def _show_tutorial_step(self) -> None:
        """
        Display the current tutorial popup and highlight relevant widgets.
        """
        # Dismiss previous overlays
        if self._tutorial_popup:
            self._tutorial_popup.dismiss()
            self._tutorial_popup = None
        if self.highlight_widget:
            self.remove_widget(self.highlight_widget)
            self.highlight_widget = None

        # Create or update overlay darkening the background
        if not self._tutorial_overlay:
            overlay = Widget()
            with overlay.canvas:
                Color(0, 0, 0, 0.7)
                self._tutorial_rect = Rectangle(
                    pos=(0, self.control_panel.height),
                    size=(Window.width, Window.height - self.control_panel.height)
                )
            def _ro(*_):
                self._tutorial_rect.pos = (0, self.control_panel.height)
                self._tutorial_rect.size = (Window.width, Window.height - self.control_panel.height)
            Window.bind(size=_ro)
            self.control_panel.bind(size=_ro)
            self.add_widget(overlay)
            self._tutorial_overlay = overlay
        else:
            self._tutorial_rect.pos = (0, self.control_panel.height)
            self._tutorial_rect.size = (Window.width, Window.height - self.control_panel.height)

        # Define tutorial texts
        steps = {
            1: self.lang.get("tutorial_step1"),
            2: self.lang.get("tutorial_step2"),
            3: self.lang.get("tutorial_step3"),
            4: self.lang.get("tutorial_step4"),
            5: self.lang.get("tutorial_step5"),
        }
        text = steps.get(self._tutorial_step, "")

        # Optionally highlight controls
        highlight_map = {
            2: [self.balance_label],
            3: [self.bet_input],
            4: [self.deposit_btn],
            5: self.horse_buttons
        }
        if self._tutorial_step in highlight_map:
            targets = highlight_map[self._tutorial_step]
            min_x = min(w.x for w in targets)
            min_y = min(w.y for w in targets)
            max_x = max(w.x + w.width for w in targets)
            max_y = max(w.y + w.height for w in targets)
            hw = Widget()
            with hw.canvas.after:
                Color(1, 0, 0, 1)
                ln = Line(rectangle=(min_x, min_y, max_x-min_x, max_y-min_y), width=2)
            def _sr(*_):
                nx = min(w.x for w in targets)
                ny = min(w.y for w in targets)
                mx = max(w.x + w.width for w in targets)
                my = max(w.y + w.height for w in targets)
                ln.rectangle = (nx, ny, mx-nx, my-ny)
            for w in targets:
                w.bind(pos=_sr, size=_sr)
            self.highlight_widget = hw
            self.add_widget(self.highlight_widget)

        # Build popup content
        content = BoxLayout(orientation="vertical", padding=15, spacing=10)
        content.add_widget(Label(
            text=text, color=(0, 0, 0, 1),
            font_size="16sp", font_name="Arcade",
            size_hint=(1, 0.6), halign="left", valign="middle"
        ))

        btn_row = BoxLayout(size_hint=(1, 0.4), spacing=20)
        prev_btn = Button(
            text=self.lang.get("previous"),
            size_hint=(0.1,1),
            font_size="18sp", font_name="Arcade",
            background_normal="assets/images/texture10.png",
            background_down="assets/images/texture12.png",
            color=(1,1,1,1)
        )
        with prev_btn.canvas.after:
            Color(0,0,0,1)
            po = Line(rectangle=(0,0,0,0), width=2)
        def _up(*_):
            po.rectangle = (*prev_btn.pos, *prev_btn.size)
        prev_btn.bind(pos=_up, size=_up)
        prev_btn.disabled = (self._tutorial_step == 1)
        prev_btn.bind(on_release=lambda *_: (self._play_click(), self._step_previous()))

        next_btn = Button(
            text=self.lang.get("next"),
            size_hint=(0.1,1),
            font_size="18sp", font_name="Arcade",
            background_normal="assets/images/texture10.png",
            background_down="assets/images/texture12.png",
            color=(1,1,1,1)
        )
        with next_btn.canvas.after:
            Color(0,0,0,1)
            no = Line(rectangle=(0,0,0,0), width=2)
        def _un(*_):
            no.rectangle = (*next_btn.pos, *next_btn.size)
        next_btn.bind(pos=_un, size=_un)
        next_btn.disabled = (self._tutorial_step == len(steps))
        next_btn.bind(on_release=lambda *_: (self._play_click(), self._step_next()))

        cancel_btn = Button(
            text=self.lang.get("cancel"),
            size_hint=(0.1,1),
            font_size="18sp", font_name="Arcade",
            background_normal="assets/images/texture10.png",
            background_down="assets/images/texture12.png",
            color=(1,1,1,1)
        )
        with cancel_btn.canvas.after:
            Color(0,0,0,1)
            co = Line(rectangle=(0,0,0,0), width=2)
        def _uc(*_):
            co.rectangle = (*cancel_btn.pos, *cancel_btn.size)
        cancel_btn.bind(pos=_uc, size=_uc)
        cancel_btn.bind(on_release=lambda *_: (self._play_click(), self._end_tutorial()))

        btn_row.add_widget(prev_btn)
        btn_row.add_widget(next_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        self._tutorial_popup = Popup(
            title=f"{self.lang.get('tutorial')} - {self._tutorial_step}/{len(steps)}",
            title_font="assets/fonts/arcade.ttf",
            title_size="24sp",
            title_align="center",
            title_color=(1,1,1,1),
            content=content,
            size_hint=(None,None),
            size=(670,350),
            background="assets/images/texture5.png",
            overlay_color=(0,0,0,0),
            border=(0,0,0,0),
            separator_height=0,
            auto_dismiss=False
        )

        with self._tutorial_popup.canvas.after:
            Color(0,0,0,1)
            outline = Line(
                rectangle=(
                    self._tutorial_popup.x,
                    self._tutorial_popup.y,
                    self._tutorial_popup.width,
                    self._tutorial_popup.height
                ),
                width=2
            )
        self._tutorial_popup.bind(
            pos=lambda *_: setattr(outline, 'rectangle', 
                                   (self._tutorial_popup.x, self._tutorial_popup.y,
                                    self._tutorial_popup.width, self._tutorial_popup.height)),
            size=lambda *_: setattr(outline, 'rectangle', 
                                    (self._tutorial_popup.x, self._tutorial_popup.y,
                                     self._tutorial_popup.width, self._tutorial_popup.height))
        )
        self._tutorial_popup.open()

    def _step_previous(self) -> None:
        """
        Move to the previous tutorial step.
        """
        if self._tutorial_step > 1:
            self._tutorial_step -= 1
            self._show_tutorial_step()

    def _step_next(self) -> None:
        """
        Move to the next tutorial step.
        """
        steps = 5
        if self._tutorial_step < steps:
            self._tutorial_step += 1
            self._show_tutorial_step()

    def _end_tutorial(self) -> None:
        """
        End the tutorial, dismiss popups and overlays.
        """
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

    def update_ui_texts(self) -> None:
        """
        Refresh all UI text elements when the language changes.
        """
        self.bet_amount_label.text = self.lang.get("bet_amount")
        self.deposit_btn.text = self.lang.get("deposit")
        try:
            bal = self.controller.model.balance
        except Exception:
            bal = 0
        self.update_balance(bal)

        if self._deposit_popup:
            self._deposit_popup.dismiss()
            self.show_deposit_popup()

        if self._tutorial_popup:
            self._show_tutorial_step()
