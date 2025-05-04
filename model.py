### model.py
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
        self.horse_speeds = {}
        self.undo_manager = undo_manager

    def place_bet(self, horse_number, amount):
        if amount <= 0 or amount > self.balance:
            raise ValueError("Invalid bet amount")
        self.bet = Bet(horse_number, amount)
        self.undo_manager.record(('bet', self.bet))

    def setup_race(self):
        self.winner = random.randint(1, len(self.horses))
        for horse in self.horses:
            self.horse_speeds[horse.number] = 5 if horse.number == self.winner else random.uniform(1, 3)
            horse.position = 0

    def resolve_race(self):
        if not self.bet:
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
        self.horse_speeds.clear()
        for horse in self.horses:
            horse.position = 0
