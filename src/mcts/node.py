"""
MCTS Node used by the Monte Carlo Tree Search algorithm.
"""

import math

from ..game.board import COLS, PLAYER1, PLAYER2


class MCTSNode:

    def __init__(
        self, board, player_id, move=None, parent=None, exploration=math.sqrt(2)
    ):

        self.board = board
        self.player_id = player_id
        self.move = move
        self.parent = parent

        self.wins = 0
        self.visits = 0
        self.children = []
        self.untried_moves = board.get_possible_moves(player_id)
        self.exploration = exploration

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def is_terminal(self):
        # A "draw" move ends the game; the resulting node is terminal.
        if self.move is not None and self.move[0] == "draw":
            return True
        if self.board.get_winner() != 0:
            return True
        if self.board.is_full():
            return not any(
                self.board.can_pop(col, self.player_id) for col in range(COLS)
            )
        return False

    def uct_score(self):

        if self.visits == 0:
            return float("inf")

        exploitation = self.wins / self.visits

        exploration_term = self.exploration * math.sqrt(
            math.log(self.parent.visits) / self.visits
        )

        return exploitation + exploration_term

    def best_child(self):

        best_node = None
        best_score = -1

        for child in self.children:
            # FIX: uct_score() takes no arguments; exploration is stored on the node
            score = child.uct_score()

            if best_node is None or score > best_score:
                best_score = score
                best_node = child

        return best_node

    def expand(self):

        move = self.untried_moves.pop()
        new_board = self.board.copy()
        move_type, col = move

        if move_type == "drop":
            new_board.drop(col, self.player_id)
        elif move_type == "pop":
            new_board.pop(col, self.player_id)
        # "draw" leaves the board unchanged; the child node is a terminal draw.

        opponent = PLAYER2 if self.player_id == PLAYER1 else PLAYER1

        child = MCTSNode(board=new_board, player_id=opponent, move=move, parent=self)

        self.children.append(child)

        return child
