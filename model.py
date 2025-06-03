from collections import deque
import random

class HorseModel:
    """
    Represents a single horse in the race.
    """
    def __init__(self, number):
        self.number = number
        self.position = 0
        self.speed = 0

class Bet:
    """
    Represents a user's bet.
    """
    def __init__(self, horse_number, amount):
        self.horse_number = horse_number
        self.amount = amount

class UndoRedoManager:
    """
    Manages undo and redo functionality using stacks.
    """
    def __init__(self):
        self.undo_stack = deque()
        self.redo_stack = deque()

    def record(self, action):
        self.undo_stack.append(action)
        self.redo_stack.clear()

    def undo(self):
        if not self.undo_stack:
            return None
        action = self.undo_stack.pop()
        self.redo_stack.append(action)
        return action

    def redo(self):
        if not self.redo_stack:
            return None
        action = self.redo_stack.pop()
        self.undo_stack.append(action)
        return action

class GameState:
    """
    Stores the game state including balance, current bet, and horse states.
    """
    def __init__(self, balance, undo_manager):
        self.balance = balance
        self.bet = None
        self.winner = None
        self.horses = [HorseModel(i+1) for i in range(6)]
        self.undo_manager = undo_manager

    def place_bet(self, horse_number, amount):
        if amount <= 0 or amount > self.balance:
            raise ValueError("Invalid bet amount")
        self.bet = Bet(horse_number, amount)
        self.undo_manager.record(('bet', self.bet))

    def setup_race(self):
        self.winner = None
        start_x = 100  # or get from view/track width * 0.1 if you want it dynamic
        for horse in self.horses:
            horse.position = start_x
            horse.speed = random.uniform(1, 3)

    def setup_race_speeds(self):
        self.winner = None
        for horse in self.horses:
            horse.speed = random.uniform(1, 3)  # or whatever speed logic you want

    def update_speeds(self):
        """
        Dynamically adjust each horse's speed with small random changes.
        Clamp speed between a min and max value.
        """
        for horse in self.horses:
            # Add small random fluctuation to speed
            horse.speed += random.uniform(-0.2, 0.2)
            # Clamp speed limits
            horse.speed = max(0.5, min(horse.speed, 4))

    def resolve_race(self):
        if not self.bet or self.winner is None:
            return
        if self.bet.horse_number == self.winner:
            win_amount = self.bet.amount * len(self.horses)
            self.balance += win_amount
        else:
            self.balance -= self.bet.amount
        self.undo_manager.record(('balance', self.balance))

    def reset(self):
        self.bet = None
        self.winner = None
        for horse in self.horses:
            horse.position = 0
            horse.speed = 0

    # ───────────────────────────────────────────────────────
    # NEW: deposit money (with a maximum limit)
    # ───────────────────────────────────────────────────────
    def deposit_money(self, amount):
        MAX_DEPOSIT = 1000
        if amount <= 0:
            raise ValueError("Enter a valid amount")
        if amount > MAX_DEPOSIT:
            raise ValueError(f"Cannot deposit more than ${MAX_DEPOSIT}")
        # record undo of current balance
        self.undo_manager.record(('balance', self.balance))
        self.balance += amount
