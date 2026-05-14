# =================================
#         MCTS PLAYER v1
# =================================

import random

from .node import MCTSNode
from ..game.board import PLAYER1, PLAYER2
from ..game.player import Player


class MCTSPlayer(Player):

    def __init__(self, player_id, iterations=10000):
        super().__init__(player_id)
        self.iterations = iterations

    def wants_to_claim_draw(self, _board):
        # Reaching a 3-fold repetition means MCTS isn't finding a win;
        # claiming the draw is preferable to looping indefinitely.
        return True

    def get_move(self, board):

        root = self._build_root(board)

        for _ in range(self.iterations):
            node = self._select_next_node(root)

            if not node.is_terminal():
                node = node.expand()

            result = self._simulate(node)
            self._backpropagate(node, result)

        best_node = self._select_final_move(root)

        print(f"\n {self.__class__.__name__}-{self.symbol} plays: {best_node.move}")

        self._after_search(best_node)
        return best_node.move

    def _build_root(self, board):
        return MCTSNode(board=board.copy(), player_id=self.player_id)

    def _after_search(self, _best_node):
        # Hook for subclasses that need to act on the chosen node (e.g. tree reuse).
        pass

    def _select_final_move(self, root):
        return max(root.children, key=lambda c: c.visits)

    def _select_next_node(self, node):

        while not node.is_terminal():

            if not node.is_fully_expanded():
                return node

            node = node.best_child()

        return node

    def _simulate(self, node):

        # The expanded node may itself be a terminal draw (declared via the
        # ("draw", -1) move). Honor that without rolling out.
        if node.move is not None and node.move[0] == "draw":
            return 0

        sim_board = node.board.copy()
        current_player = node.player_id

        for _ in range(200):
            winner = sim_board.get_winner()
            if winner:
                return winner

            moves = sim_board.get_possible_moves(current_player)
            if not moves:
                return 0

            move_type, col = self._pick_sim_move(sim_board, current_player, moves)

            if move_type == "draw":
                return 0
            if move_type == "drop":
                sim_board.drop(col, current_player)
            else:
                sim_board.pop(col, current_player)

            current_player = PLAYER2 if current_player == PLAYER1 else PLAYER1

        return sim_board.get_winner()

    def _pick_sim_move(self, _sim_board, _current_player, moves):
        return random.choice(moves)

    def _backpropagate(self, node, result):

        while node is not None:

            node.visits += 1

            # FIX: count wins for the player who MADE the move leading to this node,
            # which is the opponent of node.player_id (who is about to move here).
            # This makes UCT correct at both friendly and opponent nodes.
            mover = PLAYER2 if node.player_id == PLAYER1 else PLAYER1
            if result == mover:
                node.wins += 1

            node = node.parent



# =================================
#     MCTS PLAYER v2 — tree reuse
# =================================


class MCTSPlayerV2(MCTSPlayer):
    """Identical to MCTSPlayer but reuses the search tree between turns."""

    def __init__(self, player_id, iterations=10000):
        super().__init__(player_id, iterations)
        self.root = None

    def _build_root(self, board):
        return self._find_or_create_root(board)

    def _after_search(self, best_node):
        self.root = best_node
        self.root.parent = None

    def _find_or_create_root(self, board):

        current_board_tuple = board.to_tuple()

        if self.root is not None:
            for child in self.root.children:
                if child.board.to_tuple() == current_board_tuple:
                    child.parent = None
                    return child

        return MCTSNode(board=board.copy(), player_id=self.player_id)


# =================================
#  MCTS PLAYER v3 — smart simulation
# =================================


class MCTSPlayerV3(MCTSPlayer):
    """Identical to MCTSPlayer but uses a win/block heuristic during rollouts."""

    def _pick_sim_move(self, sim_board, current_player, _moves):
        return self._pick_smart_move(sim_board, current_player)

    def _pick_smart_move(self, board, current_player):
        opponent = PLAYER2 if current_player == PLAYER1 else PLAYER1
        moves = board.get_possible_moves(current_player)

        # 1. Take an immediate win (draw can't win, skip it)
        for move in moves:
            move_type, col = move
            if move_type == "draw":
                continue
            test_board = board.copy()
            if move_type == "drop":
                test_board.drop(col, current_player)
            else:
                test_board.pop(col, current_player)
            if test_board.get_winner() == current_player:
                return move

        # 2. Block opponent's winning DROP moves only.
        # FIX: pop blocking is removed — you cannot pop the opponent's piece
        # from the bottom row since can_pop checks for your own piece there.
        opponent_moves = board.get_possible_moves(opponent)
        for move in opponent_moves:
            move_type, col = move
            if move_type != "drop":
                continue
            test_board = board.copy()
            test_board.drop(col, opponent)
            if test_board.get_winner() == opponent:
                block = ("drop", col)
                if block in moves:
                    return block

        # 3. No immediate win or block needed — play randomly
        return random.choice(moves)


# =================================
#  MCTS PLAYER v4 — max-wins selection
# =================================


class MCTSPlayerV4(MCTSPlayer):
    """Identical to MCTSPlayer but selects the final move by win count
    (winrate * visits = wins) instead of visit count."""

    def _select_final_move(self, root):
        return max(root.children, key=lambda c: c.wins)


# =================================
#  MCTS PLAYER v5 — tree reuse + max-wins selection
# =================================


class MCTSPlayerV5(MCTSPlayerV2):
    """Tree reuse (V2) with max-wins final selection instead of max-visits."""

    def _select_final_move(self, root):
        return max(root.children, key=lambda c: c.wins)


# =================================
#  MCTS PLAYER v6 — smart simulation + max-wins selection
# =================================


class MCTSPlayerV6(MCTSPlayerV3):
    """Smart simulation (V3) with max-wins final selection instead of max-visits."""

    def _select_final_move(self, root):
        return max(root.children, key=lambda c: c.wins)

