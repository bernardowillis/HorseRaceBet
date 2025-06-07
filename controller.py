"""
File: controller.py

Description:
    Defines the GameController class, which mediates between the GameState model
    and the GameView, handling user actions, updating game logic, and orchestrating
    animations and view updates.

Version: 1.0
Author: Robbe de Guytenaer, Bernardo José Willis Lozano
"""

from kivy.clock import Clock
from model import GameState


class GameController:
    """
    Controller for the Horse Race Betting Game.
    Manages interactions between the game state (model) and the user interface (view).
    """

    def __init__(self, model: GameState, view) -> None:
        """
        Initialize the controller with a model and view, bind controller to view,
        and display the initial balance.

        Args:
            model (GameState): The game state instance.
            view: The GameView instance.
        """
        self.model = model
        self.view = view
        self.view.controller = self

        # Display starting balance
        self.view.update_balance(self.model.balance)

    def place_bet(self, horse_number: int, amount: float) -> None:
        """
        Handle user placing a bet: validate and store the bet in the model, capture
        horses' starting positions, hide betting controls, initialize race speeds,
        and start the race animation.

        Args:
            horse_number (int): Number of the horse being bet on.
            amount (float): Amount of money wagered.

        Raises:
            ValueError: If the bet is invalid (e.g., insufficient balance).
        """
        try:
            self.model.place_bet(horse_number, amount)
        except ValueError as e:
            self.view.show_bet_error(str(e))
            raise

        # Record each horse widget's x-coordinate as its starting position
        for horse_widget in self.view.track.horses:
            horse_model = self.model.horses[horse_widget.number - 1]
            horse_model.position = horse_widget.x

        # Disable betting UI
        self.view.control_panel.opacity = 0
        self.view.control_panel.disabled = True

        # Assign new random speeds without resetting positions
        self.model.setup_race_speeds()

        # Launch the race animation to 90% of track width
        self.view.start_race_animation(
            None,
            finish_x=self.view.track.width * 0.9
        )

    def update_speeds_and_positions(self) -> None:
        """
        Called repeatedly during the race animation loop. Updates horse speeds,
        advances positions, detects the winner, and schedules race completion.
        """
        self.model.update_speeds()
        finish_x = self.view.track.width * 0.9

        for horse in self.model.horses:
            horse.position += horse.speed

            if horse.position >= finish_x and self.model.winner is None:
                # First horse to cross finish line is the winner
                self.model.winner = horse.number

                # Determine if the player won and calculate payout or loss
                bet = self.model.bet
                player_won = (horse.number == bet.horse_number)
                payout = bet.amount * len(self.model.horses) if player_won else -bet.amount

                # Display race result in the view
                self.view.show_result(horse.number, player_won, abs(payout))

                # After a short delay, finalize the race and reset
                def finish_race(dt):
                    self.view.result_popup.dismiss()
                    self.model.resolve_race()
                    self.view.update_balance(self.model.balance)
                    self._reset()

                Clock.schedule_once(finish_race, 2)

    def _reset(self) -> None:
        """
        Internal method to stop the animation loop, reset the game state,
        and refresh the track visuals for a new race.
        """
        Clock.unschedule(self.view.event)
        self.model.reset()
        self.view.reset_track()

    def deposit_money(self, amount: float) -> None:
        """
        Handle user depositing additional funds: validate deposit amount,
        update the model and view balance, and close the deposit dialog.

        Args:
            amount (float): The amount to deposit.
        """
        try:
            self.model.deposit_money(amount)
        except ValueError as e:
            self.view.show_deposit_error(str(e))
            return

        self.view.update_balance(self.model.balance)
        self.view.dismiss_deposit_popup()
