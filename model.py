"""
File: model.py

Description:
    Defines the core data models for the Horse Race Betting Game, including
    representations of horses, bets, and overall game state logic.

Version: 1.0
Author: Robbe de Guytenaer, Bernardo José Willis Lozano
"""

import random
from typing import List, Optional


class HorseModel:
    """
    Represents a single horse in the race.

    Attributes:
        number (int): Unique identifier for the horse.
        position (float): Current horizontal position of the horse on the track.
        speed (float): Current speed of the horse.
    """

    def __init__(self, number: int) -> None:
        """
        Initialize a HorseModel instance.

        Args:
            number (int): The horse's unique number.
        """
        self.number: int = number
        self.position: float = 0.0
        self.speed: float = 0.0


class Bet:
    """
    Represents a user's bet on a horse.

    Attributes:
        horse_number (int): The number of the horse the user bets on.
        amount (float): The amount wagered.
    """

    def __init__(self, horse_number: int, amount: float) -> None:
        """
        Initialize a Bet instance.

        Args:
            horse_number (int): The selected horse's number.
            amount (float): The wagered amount.
        """
        self.horse_number: int = horse_number
        self.amount: float = amount


class GameState:
    """
    Manages the state and logic of the betting game, including player balance,
    current bet, race setup, and resolution.

    Attributes:
        balance (float): The player's current balance.
        bet (Optional[Bet]): The active bet, if any.
        winner (Optional[int]): The winning horse number after a race.
        horses (List[HorseModel]): The list of horses in the race.
    """

    def __init__(self, balance: float) -> None:
        """
        Initialize the game state with a starting balance and six horses.

        Args:
            balance (float): Starting player balance.
        """
        self.balance: float = balance
        self.bet: Optional[Bet] = None
        self.winner: Optional[int] = None
        self.horses: List[HorseModel] = [HorseModel(i + 1) for i in range(6)]

    def place_bet(self, horse_number: int, amount: float) -> None:
        """
        Place a bet on a specific horse.

        Args:
            horse_number (int): The number of the horse to bet on.
            amount (float): The amount to wager.

        Raises:
            ValueError: If the amount is not positive or exceeds the current balance.
        """
        if amount <= 0:
            raise ValueError("Enter a valid amount")
        if amount > self.balance:
            raise ValueError("Not enough money in balance")
        self.bet = Bet(horse_number, amount)

    def setup_race(self) -> None:
        """
        Prepare the race by resetting the winner, initializing each horse's
        starting position, and assigning a random starting speed.
        """
        self.winner = None
        start_x = 100.0
        for horse in self.horses:
            horse.position = start_x
            horse.speed = random.uniform(1.0, 3.0)

    def setup_race_speeds(self) -> None:
        """
        Reset the winner and assign a new random speed to each horse without
        changing positions.
        """
        self.winner = None
        for horse in self.horses:
            horse.speed = random.uniform(1.0, 3.0)

    def update_speeds(self) -> None:
        """
        Apply a small random fluctuation to each horse's speed and clamp it
        between minimum and maximum thresholds.
        """
        for horse in self.horses:
            horse.speed += random.uniform(-0.2, 0.2)
            horse.speed = max(0.5, min(horse.speed, 4.0))

    def resolve_race(self) -> None:
        """
        Adjust the player's balance based on the race outcome and the active bet.
        If the bet matches the winner, the player wins payout equal to bet
        amount times number of horses; otherwise, the bet amount is lost.
        """
        if self.bet is None or self.winner is None:
            return

        if self.bet.horse_number == self.winner:
            payout = self.bet.amount * len(self.horses)
            self.balance += payout
        else:
            self.balance -= self.bet.amount

    def reset(self) -> None:
        """
        Clear the active bet, winner, and reset all horses' positions and speeds
        to zero.
        """
        self.bet = None
        self.winner = None
        for horse in self.horses:
            horse.position = 0.0
            horse.speed = 0.0

    def deposit_money(self, amount: float) -> None:
        """
        Increase the player's balance by the specified amount, enforcing a
        maximum deposit limit.

        Args:
            amount (float): The amount to deposit.

        Raises:
            ValueError: If the amount is not positive or exceeds the maximum limit.
        """
        MAX_DEPOSIT = 1000.0
        if amount <= 0:
            raise ValueError("Enter a valid amount")
        if amount > MAX_DEPOSIT:
            raise ValueError(f"Cannot deposit more than ${MAX_DEPOSIT}")
        self.balance += amount
