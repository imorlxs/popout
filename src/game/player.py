# =================================
#             IMPORTS
# =================================

import random
from types import SimpleNamespace
from .board import SYMBOLS, PLAYER1, PLAYER2
from ..mcts.mcts import MCTS


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
#          MCTS PLAYER
# =================================

class MCTSPlayer:
    """
    Player that uses Monte Carlo Tree Search (UCT) to choose a move.

    Parameters
    ----------
    iterations : int
        Number of MCTS simulation iterations per move.
    exploration_constant : float
        UCT exploration constant (c in the UCB1 formula).
    max_children : int or None
        Maximum children to expand per node. None means expand all.
    """

    def __init__(self, player_id, iterations: int = 1000, exploration_constant: float = 1.414,
                 max_children: int = None, rollout_policy: str = 'random'):
        self.player_id = player_id
        self.iterations = iterations
        self.exploration_constant = exploration_constant
        self.max_children = max_children
        self.rollout_policy = rollout_policy

    def get_move(self, game):
        # Accept either a Game-like object or a Board instance for compatibility
        mcts = MCTS(
            iterations=self.iterations,
            exploration_constant=self.exploration_constant,
            max_children=self.max_children,
            rollout_policy=self.rollout_policy,
        )

        # If a full game object is provided (has board/current_player/get_possible_moves), use it.
        if hasattr(game, "board") and hasattr(game, "current_player") and hasattr(game, "get_possible_moves"):
            return mcts.search(game)

        # Otherwise assume a Board was passed (Game.play passes only the board).
        board = game
        wrapper = SimpleNamespace(
            board=board,
            current_player=self.player_id,
            get_possible_moves=lambda: board.get_possible_moves(self.player_id),
        )
        return mcts.search(wrapper)

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
