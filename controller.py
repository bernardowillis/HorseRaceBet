from kivy.clock import Clock
from model import GameState

class GameController:
    """
    Handles all interaction between view and model.
    """
    def __init__(self, model: GameState, view):
        self.model = model
        self.view = view
        self.view.controller = self
        # show initial balance
        self.view.update_balance(self.model.balance)

    def place_bet(self, horse_number, amount):
        try:
            self.model.place_bet(horse_number, amount)
        except ValueError as e:
            # Show “Not enough money in balance” under the panel
            self.view.show_bet_error(str(e))
            raise

        # Capture current horse widget x positions as starting positions
        for horse_widget in self.view.track.horses:
            horse_model = self.model.horses[horse_widget.number - 1]
            horse_model.position = horse_widget.x  # Store absolute start x

        # Hide betting UI
        self.view.control_panel.opacity = 0
        self.view.control_panel.disabled = True

        # Setup race speeds
        self.model.setup_race_speeds()  # adjust to only set speeds, no resetting position

        # Start animation
        self.view.start_race_animation(
            None,
            finish_x=self.view.track.width * 0.9
        )

    def update_speeds_and_positions(self):
        self.model.update_speeds()
        finish_x = self.view.track.width * 0.9

        for horse in self.model.horses:
            horse.position += horse.speed

            if horse.position >= finish_x and self.model.winner is None:
                print(f"there is a winner: {horse.number}")
                self.model.winner = horse.number

                # Determine win/loss before race ends
                bet = self.model.bet
                player_won = (horse.number == bet.horse_number)
                amount = bet.amount
                payout = amount * len(self.model.horses) if player_won else -amount

                # Pass win/loss info to the view
                self.view.show_result(horse.number, player_won, abs(payout))

                # Combine dismiss + resolve + reset in one scheduled action
                def finish_race(dt):
                    self.view.result_popup.dismiss()
                    self.model.resolve_race()
                    self.view.update_balance(self.model.balance)
                    self._reset()

                Clock.schedule_once(finish_race, 2)

    def _reset(self):
        # Stop the animation loop
        Clock.unschedule(self.view.event)

        # Reset game state and visuals
        self.model.reset()
        self.view.reset_track()

    # ───────────────────────────────────────────────────────
    # NEW: Deposit Money
    # ───────────────────────────────────────────────────────
    def deposit_money(self, amount):
        try:
            self.model.deposit_money(amount)
        except ValueError as e:
            # inform view of the error (e.g. show a warning popup)
            self.view.show_deposit_error(str(e))
            return
        # update balance in view
        self.view.update_balance(self.model.balance)
        # optionally close the deposit popup (view will handle this)
        self.view.dismiss_deposit_popup()

