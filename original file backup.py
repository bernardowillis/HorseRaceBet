import random

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


class Separator(Widget):
    """
    A simple widget to visually separate two areas.
    Draws a thin black rectangle.
    """
    def __init__(self, **kwargs):
        super(Separator, self).__init__(**kwargs)
        with self.canvas:
            Color(0, 0, 0, 1)  # black
            self.line = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_line, size=self.update_line)

    def update_line(self, *args):
        self.line.pos = self.pos
        self.line.size = self.size


class Horse(Widget):
    """
    A simple widget representing a horse.
    The horse is drawn as a circle with a number in its center.
    """
    def __init__(self, number, **kwargs):
        super(Horse, self).__init__(**kwargs)
        self.number = number
        # Set a fixed size (the circle's diameter)
        self.size = (50, 50)
        # Draw the circle representing the horse.
        with self.canvas:
            Color(0.8, 0.3, 0.3, 1)  # a reddish color
            self.ellipse = Ellipse(pos=self.pos, size=self.size)
        # Update the ellipse when the widget moves.
        self.bind(pos=self.update_graphics)
        # Create a label to show the horse's number (centered on the circle)
        self.label = Label(text=str(self.number), color=(0, 0, 0, 1))
        self.add_widget(self.label)
        self.bind(pos=self.update_label, size=self.update_label)

    def update_graphics(self, *args):
        self.ellipse.pos = self.pos

    def update_label(self, *args):
        # Center the label on the horse widget.
        self.label.center = self.center


class RaceTrack(Widget):
    """
    The RaceTrack widget displays the track for the horses.
    It draws the white background and the finish line,
    and positions the horse widgets.
    """
    def __init__(self, **kwargs):
        super(RaceTrack, self).__init__(**kwargs)
        # Draw the white background for the track.
        with self.canvas:
            Color(1, 1, 1, 1)  # white background
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)
        # Draw the finish line (using canvas.after so it's on top).
        self.bind(pos=self.draw_finish_line, size=self.draw_finish_line)

        # Create and add 6 horse widgets.
        self.horses = []
        for i in range(6):
            horse = Horse(number=i + 1)
            self.horses.append(horse)
            self.add_widget(horse)
        # Set the finish line's x-coordinate to 90% of the track width.
        self.finish_line_x = self.width * 0.9

        # Position the horses when the widget size is available.
        self.bind(size=self.setup)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def draw_finish_line(self, *args):
        self.canvas.after.clear()
        with self.canvas.after:
            Color(0, 0, 0, 1)  # black finish line
            Line(points=[self.width * 0.9, 0, self.width * 0.9, self.height], width=2)
        self.finish_line_x = self.width * 0.9

    def setup(self, *args):
        """
        Positions the horses at the starting line, spacing them evenly.
        """
        start_x = self.width * 0.1  # starting x position (10% of track width)
        spacing = self.height / (len(self.horses) + 1)
        for idx, horse in enumerate(self.horses):
            # Evenly space horses vertically.
            horse.pos = (start_x, self.height - (idx + 1) * spacing - horse.height / 2)


class HorseRaceGame(App):
    """
    Main application class combining the race track with betting controls.
    Implements the race and betting logic.
    """
    def build(self):
        # Set an initial balance.
        self.balance = 100
        self.bet_horse = None
        self.bet_amount = 0
        self.race_in_progress = False
        self.winner = None

        # Root layout: a vertical BoxLayout.
        root = BoxLayout(orientation='vertical')

        # Create the RaceTrack widget.
        # Use a size_hint so that the track occupies roughly 65% of the vertical space.
        self.track = RaceTrack(size_hint_y=5)
        root.add_widget(self.track)

        # Add a separator to divide the race track and the betting board.
        separator = Separator(size_hint_y=None, height=4)  # a thin black line
        root.add_widget(separator)

        # Create the control panel for betting (occupies roughly 35% of vertical space).
        control_panel = BoxLayout(orientation='vertical', size_hint_y=0.35)

        # Top row for bet amount input and balance display.
        top_controls = BoxLayout(size_hint_y=1)
        top_controls.add_widget(Label(text="Bet Amount:"))
        self.bet_input = TextInput(text='10', multiline=False, input_filter='int')
        top_controls.add_widget(self.bet_input)
        self.balance_label = Label(text="Balance: $" + str(self.balance))
        top_controls.add_widget(self.balance_label)
        control_panel.add_widget(top_controls)

        # Lower row: One button per horse to place a bet.
        button_row = BoxLayout()
        for i in range(6):
            btn = Button(text="Horse " + str(i + 1))
            btn.bind(on_press=self.place_bet)
            button_row.add_widget(btn)
        control_panel.add_widget(button_row)

        root.add_widget(control_panel)
        return root

    def place_bet(self, instance):
        """
        Called when a horse button is pressed.
        Validates the bet and starts the race if valid.
        """
        if self.race_in_progress:
            return  # Do nothing if a race is already running

        try:
            bet = int(self.bet_input.text)
        except ValueError:
            print("Invalid bet amount.")
            return
        if bet <= 0:
            print("Enter a positive bet amount.")
            return
        if bet > self.balance:
            print("Insufficient balance.")
            return
        self.bet_amount = bet

        # Determine the chosen horse from the button text.
        horse_str = instance.text.split(" ")[1]
        self.bet_horse = int(horse_str)
        print("Bet placed on horse", self.bet_horse, "with amount", self.bet_amount)

        # Start the race.
        self.start_race()

    def start_race(self):
        """
        Chooses a winning horse at random and assigns speeds.
        Then schedules the update of the race animation.
        """
        self.race_in_progress = True
        # Randomly select the winning horse (each with 1/6 chance).
        self.winner = random.randint(1, 6)
        print("Winning horse (preselected):", self.winner)

        # Assign speeds: the winning horse gets a faster speed.
        self.horse_speeds = {}
        for horse in self.track.horses:
            if horse.number == self.winner:
                self.horse_speeds[horse.number] = 5  # faster speed for the winning horse
            else:
                self.horse_speeds[horse.number] = random.uniform(1, 3)

        # Schedule the race animation update.
        self.event = Clock.schedule_interval(self.update_race, 1 / 60)

    def update_race(self, dt):
        """
        Updates each horse's position based on its speed.
        Ends the race when a horse reaches the finish line.
        """
        finished = False
        for horse in self.track.horses:
            speed = self.horse_speeds[horse.number]
            new_x = horse.x + speed
            # Stop the horse at the finish line.
            if new_x + horse.width >= self.track.finish_line_x:
                new_x = self.track.finish_line_x - horse.width
                finished = True
            horse.x = new_x
        if finished:
            Clock.unschedule(self.event)
            self.race_in_progress = False
            self.show_result()
            # Reset race after a short delay.
            Clock.schedule_once(self.reset_race, 2)

    def show_result(self):
        """
        Updates the player's balance based on the race outcome.
        """
        if self.bet_horse == self.winner:
            win_amount = self.bet_amount * 6
            self.balance += win_amount
            print("You win! Amount won:", win_amount)
        else:
            self.balance -= self.bet_amount
            print("You lose!")
        self.balance_label.text = "Balance: $" + str(self.balance)
        print("The winning horse was", self.winner)

    def reset_race(self, dt):
        """
        Resets the horses to the starting positions.
        """
        self.track.setup()


if __name__ == '__main__':
    HorseRaceGame().run()
