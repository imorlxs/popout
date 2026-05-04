# =================================
#             IMPORTS
# =================================

import math
import random
from src.game.board import SYMBOLS, PLAYER1, PLAYER2, COLS

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
#           MCTS CLASSES
# =================================


# MCTS NODE
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


# =================================
#         MCTS PLAYER v1
# =================================


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
