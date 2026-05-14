# =================================
#             IMPORTS
# =================================

import math
import random
import pandas as pd
from .board import SYMBOLS, PLAYER1, PLAYER2, COLS

# =================================
#          PLAYER CLASSES
# =================================


class Player:

    def __init__(self, player_id):

        if player_id not in (PLAYER1, PLAYER2):
            raise ValueError(
                f" player_id must be {PLAYER1} or {PLAYER2}, got {player_id}"
            )

        self.player_id = player_id
        self.symbol = SYMBOLS[player_id]
        self.debug = False

    def set_debug_mode(self, enabled: bool = True):
        self.debug = enabled

    def get_move(self, board):
        raise NotImplementedError

    def wants_to_claim_draw(self, _board):
        """Rule 3: called only when the current state has occurred 3+ times.
        Default: do not claim. Subclasses may override to claim or prompt."""
        return False


# =================================
#          HUMAN PLAYER
# =================================


class HumanPlayer(Player):

    def __init__(self, player_id):
        super().__init__(player_id)

    def wants_to_claim_draw(self, _board):
        while True:
            ans = (
                input(
                    f"PLAYER-{self.symbol}: state has repeated 3 times. "
                    "Claim draw? (y/n): "
                )
                .strip()
                .lower()
            )
            if ans in ("y", "yes"):
                return True
            if ans in ("n", "no"):
                return False
            print("Please enter y or n.")

    def get_move(self, board):

        possible_moves = board.get_possible_moves(self.player_id)

        if self.debug:
            print(f"\nPossible moves for PLAYER-{self.symbol}: {possible_moves}")

        can_draw = ("draw", -1) in possible_moves

        while True:

            prompt = (
                "Enter move type (drop/pop/draw): "
                if can_draw
                else "Enter move type (drop/pop): "
            )
            move_type = input(prompt).strip().lower()

            if move_type == "draw":
                if can_draw:
                    return ("draw", -1)
                print("Cannot declare draw right now.")
                continue

            col_str = input("Enter column [0-6]: ").strip()

            if not col_str.isdigit():
                print("INVALID INPUT: column must be a number")
                continue

            col = int(col_str)

            if move_type not in ("drop", "pop"):
                valid = "'drop', 'pop', or 'draw'." if can_draw else "'drop' or 'pop'."
                print(f"INVALID MOVE TYPE: must be {valid}")
                continue

            if (move_type, col) in possible_moves:
                return move_type, col
            else:
                print("INVALID MOVE, try again.")


# =================================
#          RANDOM PLAYER
# =================================


class RandomPlayer(Player):

    def __init__(self, player_id):
        super().__init__(player_id)

    def get_move(self, board):

        possible_moves = board.get_possible_moves(self.player_id)
        move = random.choice(possible_moves)

        if self.debug:
            print(f"\n RandomPlayer-{self.symbol} plays: {move}")

        return move


# =================================
#      DECISSION TREE PLAYER
# =================================


class DecisionTreePlayer(Player):

    def __init__(self, player_id, csv_path="data/dataset.csv"):
        super().__init__(player_id)
        self.tree = self._train(csv_path)

    def get_move(self, board):

        state = board.to_flat_list()
        prediction = self.tree.predict(state)
        possible_moves = board.get_possible_moves(self.player_id)

        if prediction is not None:

            parts = prediction.rsplit("_", 1)

            if len(parts) == 2:

                move_type, col_str = parts

                if col_str.isdigit():

                    move = (move_type, int(col_str))

                    if move in possible_moves:

                        print(f"\n DecisionTreePlayer-{self.symbol} plays: {move}")

                        return move

        # Fallback if prediction is invalid or not in possible moves
        move = random.choice(possible_moves)

        print(f"\n DecisionTreePlayer-{self.symbol} fallback plays: {move}")

        return move


# Re-export MCTS classes and node for convenience
from ..mcts.node import MCTSNode
from ..mcts.mcts import (
    MCTSPlayer,
    MCTSPlayerV2,
    MCTSPlayerV3,
    MCTSPlayerV4,
    MCTSPlayerV5,
    MCTSPlayerV6,
)

__all__ = [
    "Player",
    "HumanPlayer",
    "RandomPlayer",
    "DecisionTreePlayer",
    "MCTSNode",
    "MCTSPlayer",
    "MCTSPlayerV2",
    "MCTSPlayerV3",
    "MCTSPlayerV4",
    "MCTSPlayerV5",
    "MCTSPlayerV6",
]
