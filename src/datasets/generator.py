"""
Dataset generator for the PopOut game.

Generates (state, move) pairs by running MCTS-guided self-play games.
The board state is encoded as a flat list of cell values plus the current
player indicator (42 board cells + 1 player cell = 43 features).
The target label is a string 'movetype_col' (e.g. 'drop_3', 'pop_1').
"""

import random
from ..game.board import Board, PLAYER1, PLAYER2, ROWS, COLS
from ..game.popout import PopOutGame
from ..game.player import RandomPlayer
from ..mcts.mcts import MCTS


class PopOutDatasetGenerator:
    """
    Generates a labelled dataset of (board_state, best_move) pairs.

    Parameters
    ----------
    mcts_iterations : int
        MCTS iterations used to determine the best move per state.
    exploration_constant : float
        UCT exploration constant for MCTS.
    rollout_policy : str
        'random' or 'heuristic' rollout policy for MCTS.
    seed : int or None
        Random seed for reproducibility.
    """

    def __init__(self, mcts_iterations: int = 200,
                 exploration_constant: float = 1.414,
                 rollout_policy: str = 'random',
                 seed: int = 42):
        self.mcts_iterations = mcts_iterations
        self.exploration_constant = exploration_constant
        self.rollout_policy = rollout_policy
        self.rng = random.Random(seed)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate(self, n_games: int = 50) -> tuple:
        """
        Run n_games self-play games and collect (state, move) pairs.

        Returns
        -------
        X : list of lists
            Feature vectors (43 values each).
        y : list of str
            Labels of the form 'movetype_col'.
        feature_names : list of str
            Names for each feature.
        """
        X, y = [], []

        mcts = MCTS(
            iterations=self.mcts_iterations,
            exploration_constant=self.exploration_constant,
            rollout_policy=self.rollout_policy,
        )

        for game_idx in range(n_games):
            board = Board()
            current_player = PLAYER1
            history = []
            move_count = 0
            max_moves = ROWS * COLS * 3

            while move_count < max_moves:
                # Check terminal conditions
                winner = board.get_winner()
                if winner:
                    break
                if board.is_full():
                    break

                legal = board.get_legal_moves(current_player)
                if not legal:
                    break

                # Build a lightweight game-like object for MCTS
                game_proxy = _GameProxy(board.copy(), current_player)
                move = mcts.search(game_proxy)

                # Record this (state, move) pair
                features = board.to_flat_list() + [current_player]
                label = f"{move[0]}_{move[1]}"
                X.append(features)
                y.append(label)

                # Apply the move
                move_type, col = move
                if move_type == 'drop':
                    board.drop(col, current_player)
                elif move_type == 'pop':
                    board.pop(col, current_player)
                else:
                    break

                # Detect repetition
                state = board.to_tuple()
                if history.count(state) >= 3:
                    break
                history.append(state)

                current_player = PLAYER2 if current_player == PLAYER1 else PLAYER1
                move_count += 1

        feature_names = [
            f"cell_{r}_{c}" for r in range(ROWS) for c in range(COLS)
        ] + ["current_player"]

        return X, y, feature_names

    # ------------------------------------------------------------------
    # Iris dataset helper
    # ------------------------------------------------------------------
    @staticmethod
    def load_iris(filepath: str) -> tuple:
        """
        Load the Iris CSV dataset.

        Expected columns (in order):
          sepal_length, sepal_width, petal_length, petal_width, class

        Returns
        -------
        X : list of lists (float values)
        y : list of str (class labels)
        feature_names : list of str
        """
        X, y = [], []
        feature_names = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']

        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split(',')
                if len(parts) < 5:
                    continue
                # Skip header row if present
                try:
                    values = [float(p) for p in parts[:4]]
                except ValueError:
                    continue  # header or malformed row
                label = parts[4].strip()
                X.append(values)
                y.append(label)

        return X, y, feature_names


class _GameProxy:
    """Lightweight game-state proxy used by MCTS during dataset generation."""

    def __init__(self, board: Board, current_player: int):
        self.board = board
        self.current_player = current_player

    def get_legal_moves(self):
        moves = self.board.get_legal_moves(self.current_player)
        if self.board.is_full():
            moves.append(('draw', -1))
        return moves
