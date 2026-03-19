"""
Player classes for the PopOut game.

HumanPlayer        – reads moves from stdin.
MCTSPlayer         – uses MCTS/UCT to choose a move.
DecisionTreePlayer – uses a trained ID3 decision tree to choose a move.
RandomPlayer       – selects a random legal move (useful for testing).
"""

import random


class HumanPlayer:
    """Interactive player that reads moves from standard input."""

    def choose_move(self, game):
        """
        Ask the human player for a move.

        Returns (move_type, col) where move_type is 'drop', 'pop', or 'draw'
        and col is 0-indexed (displayed as 1-indexed to the user).
        """
        legal = game.get_legal_moves()
        has_draw = any(mt == 'draw' for mt, _ in legal)

        while True:
            try:
                move_input = input(
                    "Enter move type (drop/pop" + ("/draw" if has_draw else "") + "): "
                ).strip().lower()

                if move_input == 'draw' and has_draw:
                    return ('draw', -1)

                if move_input not in ('drop', 'pop'):
                    print("Invalid move type. Please enter 'drop' or 'pop'.")
                    continue

                col_input = int(input("Enter column (1-7): ").strip())
                col = col_input - 1  # convert to 0-indexed

                if (move_input, col) in legal:
                    return (move_input, col)
                else:
                    print(f"Move ({move_input}, column {col_input}) is not legal. Try again.")

            except (ValueError, EOFError):
                print("Invalid input. Please enter a valid move.")


class RandomPlayer:
    """Player that selects a random legal move. Useful as a baseline."""

    def __init__(self, seed: int = None):
        self.rng = random.Random(seed)

    def choose_move(self, game):
        legal = game.get_legal_moves()
        return self.rng.choice(legal)


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

    def __init__(self, iterations: int = 1000, exploration_constant: float = 1.414,
                 max_children: int = None, rollout_policy: str = 'random'):
        self.iterations = iterations
        self.exploration_constant = exploration_constant
        self.max_children = max_children
        self.rollout_policy = rollout_policy

    def choose_move(self, game):
        from ..mcts import MCTS
        mcts = MCTS(
            iterations=self.iterations,
            exploration_constant=self.exploration_constant,
            max_children=self.max_children,
            rollout_policy=self.rollout_policy,
        )
        return mcts.search(game)


class DecisionTreePlayer:
    """
    Player that uses a trained ID3 decision tree to choose a move.

    Parameters
    ----------
    tree : ID3DecisionTree
        A trained decision tree instance.
    fallback : player object, optional
        Player used when the tree cannot produce a legal move.
        Defaults to RandomPlayer.
    """

    def __init__(self, tree, fallback=None):
        self.tree = tree
        self.fallback = fallback or RandomPlayer()

    def choose_move(self, game):
        # Encode the board as a feature vector
        features = game.board.to_flat_list()
        features.append(game.current_player)

        try:
            prediction = self.tree.predict(features)
            # prediction is expected to be (move_type, col) or a string 'type_col'
            if isinstance(prediction, str) and '_' in prediction:
                parts = prediction.split('_')
                move_type = parts[0]
                col = int(parts[1])
                move = (move_type, col)
            else:
                move = prediction

            legal = game.get_legal_moves()
            if move in legal:
                return move
        except Exception:
            pass

        # Fallback if tree predicts an illegal move
        return self.fallback.choose_move(game)
