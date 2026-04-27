# =================================
#             IMPORTS
# =================================

import math
import random
from src.game.board import SYMBOLS, PLAYER1, PLAYER2

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

    def get_move(self, board):
        raise NotImplementedError


# =================================
#          HUMAN PLAYER
# =================================


class HumanPlayer(Player):

    def __init__(self, player_id):
        super().__init__(player_id)

    def get_move(self, board):

        possible_moves = board.get_possible_moves(self.player_id)

        print(f"\n Possible moves for PLAYER-{self.symbol}: {possible_moves}")

        while True:

            move_type = input("Enter move type (drop/pop): ").strip().lower()
            col_str = input("Enter column [0-6]: ").strip()

            if not col_str.isdigit():
                print("INVALID INPUT: column must be a number")
                continue

            col = int(col_str)

            if move_type not in ("drop", "pop"):
                print("INVALID MOVE TYPE: must be 'drop' or 'pop'.")
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

        print(f"\n RandomPlayer-{self.symbol} plays: {move}")

        return move


# =================================
#           MCTS CLASES
# =================================


# MCTS NODE
class MCTS_Node:

    def __init__(self, board, player_id, move=None, parent=None):

        self.board = board
        self.player_id = player_id
        self.move = move  # Move that led to this node
        self.parent = parent  # Parent node

        self.wins = 0
        self.visits = 0
        self.children = []  # Expanded children list
        self.untried_moves = board.get_possible_moves(player_id)

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def is_terminal(self):
        return self.board.get_winner() != 0 or self.board.is_full()

    # Calculate UCT score for the node ( UCT = wins/visits + √2{exploration_param} * √(log(father_visits) / own_visits) )
    def uct_score(self, exploration=math.sqrt(2)):

        # Si visits = 0 devuelvo infinito para forzar que se visite al menos una vez
        if self.visits == 0:
            return float("inf")

        exploitation = self.wins / self.visits

        exploration_term = exploration * math.sqrt(
            math.log(self.parent.visits) / self.visits
        )

        return exploitation + exploration_term

    # Return the child with the highest UCT score
    def best_child(self, exploration=math.sqrt(2)):

        # exploration parameter that balances between exploring
        # unknown nodes and exploiting nodes with high win rates

        best_node = None
        best_score = -1

        for child in self.children:
            score = child.uct_score(exploration)

            if best_node is None or score > best_score:
                best_score = score
                best_node = child

        return best_node

    # Expand one untried move and return the new child node
    def expand(self):

        move = self.untried_moves.pop()
        new_board = self.board.copy()
        move_type, col = move

        if move_type == "drop":
            new_board.drop(col, self.player_id)
        else:
            new_board.pop(col, self.player_id)
            # Añadir elsif error

        opponent = PLAYER2 if self.player_id == PLAYER1 else PLAYER1

        child = MCTS_Node(board=new_board, player_id=opponent, move=move, parent=self)

        self.children.append(child)

        return child


# MCTS PLAYER
class MCTSPlayer(Player):

    def __init__(self, player_id, iterations=100):
        super().__init__(player_id)
        self.iterations = iterations

    # Select next move to do by simulating using random moves
    def get_move(self, board):

        root = MCTS_Node(board=board.copy(), player_id=self.player_id)

        for _ in range(self.iterations):
            node = self._select_next_node(root)

            if not node.is_terminal():
                node = node.expand()

            result = self._simulate(node)
            self._backpropagate(node, result)

        best_node = None

        for child in root.children:

            if best_node is None or child.visits > best_node.visits:
                best_node = child

        print(f"\n MCTSPlayer-{self.symbol} plays: {best_node.move}")

        return best_node.move

    # Select the most promising node using UCT
    def _select_next_node(self, node):

        while not node.is_terminal():

            if not node.is_fully_expanded():
                return node

            node = node.best_child()

        return node

    # Simulate a random game from node and return the winner
    def _simulate(self, node):

        sim_board = node.board.copy()
        current_player = node.player_id

        while not sim_board.get_winner() and not sim_board.is_full():

            moves = sim_board.get_possible_moves(current_player)
            move_type, col = random.choice(moves)

            if move_type == "drop":
                sim_board.drop(col, current_player)
            else:
                sim_board.pop(col, current_player)
                # elsif error

            current_player = PLAYER2 if current_player == PLAYER1 else PLAYER1

        return sim_board.get_winner()

    # Propagate the result up the tree
    def _backpropagate(self, node, result):

        while node is not None:

            node.visits += 1

            if result == self.player_id:
                node.wins += 1

            node = node.parent


# tree reuse
class MCTSPlayerV2(Player):
    def __init__(self, player_id, iterations=100):
        super().__init__(player_id)
        self.iterations = iterations
        self.root = None

    def get_move(self, board):

        root = self._find_or_create_root(board)

        for _ in range(self.iterations):
            node = self._select_next_node(root)

            if not node.is_terminal():
                node = node.expand()

            result = self._simulate(node)
            self._backpropagate(node, result)

        best_node = None

        for child in root.children:

            if best_node is None or child.visits > best_node.visits:
                best_node = child

        print(f"\n MCTSPlayer-{self.symbol} plays: {best_node.move}")

        self.root = best_node
        self.root.parent = None
        return best_node.move

    def _find_or_create_root(self, board):

        current_board_tuple = board.to_tuple()

        if self.root is not None:
            # Search among the children of self.root (opponent's replies)
            for child in self.root.children:
                if child.board.to_tuple() == current_board_tuple:
                    child.parent = None
                    return child

        # No match found — create a fresh root
        return MCTS_Node(board=board.copy(), player_id=self.player_id)

    # Select the most promising node using UCT
    def _select_next_node(self, node):

        while not node.is_terminal():

            if not node.is_fully_expanded():
                return node

            node = node.best_child()

        return node

    # Simulate a random game from node and return the winner
    def _simulate(self, node):

        sim_board = node.board.copy()
        current_player = node.player_id

        while not sim_board.get_winner() and not sim_board.is_full():

            moves = sim_board.get_possible_moves(current_player)
            move_type, col = random.choice(moves)

            if move_type == "drop":
                sim_board.drop(col, current_player)
            else:
                sim_board.pop(col, current_player)
                # elsif error

            current_player = PLAYER2 if current_player == PLAYER1 else PLAYER1

        return sim_board.get_winner()

    # Propagate the result up the tree
    def _backpropagate(self, node, result):

        while node is not None:

            node.visits += 1

            if result == self.player_id:
                node.wins += 1

            node = node.parent


# better simulation - check win moves
class MCTSPlayerV3(Player):

    def __init__(self, player_id, iterations=100):
        super().__init__(player_id)
        self.iterations = iterations

    # Select next move to do by simulating using random moves
    def get_move(self, board):

        root = MCTS_Node(board=board.copy(), player_id=self.player_id)

        for _ in range(self.iterations):
            node = self._select_next_node(root)

            if not node.is_terminal():
                node = node.expand()

            result = self._simulate(node)
            self._backpropagate(node, result)

        best_node = None

        for child in root.children:

            if best_node is None or child.visits > best_node.visits:
                best_node = child

        print(f"\n MCTSPlayer-{self.symbol} plays: {best_node.move}")

        return best_node.move

    # Select the most promising node using UCT
    def _select_next_node(self, node):

        while not node.is_terminal():

            if not node.is_fully_expanded():
                return node

            node = node.best_child()

        return node

    def _pick_smart_move(self, board, current_player):
        opponent = PLAYER2 if current_player == PLAYER1 else PLAYER1
        moves = board.get_possible_moves(current_player)

        # 1. Check if current player can win immediately
        for move in moves:
            test_board = board.copy()
            move_type, col = move
            if move_type == "drop":
                test_board.drop(col, current_player)
            else:
                test_board.pop(col, current_player)
            if test_board.get_winner() == current_player:
                return move

        # 2. Check if opponent can win next turn and block them
        opponent_moves = board.get_possible_moves(opponent)
        for move in opponent_moves:
            test_board = board.copy()
            move_type, col = move
            if move_type == "drop":
                test_board.drop(col, opponent)
            else:
                test_board.pop(col, opponent)
            if test_board.get_winner() == opponent:
                # Play the same move as ourselves to block
                if (move_type, col) in moves:
                    return move

        # 3. No immediate win or block needed — play randomly
        return random.choice(moves)

    # Simulate a random game from node and return the winner
    def _simulate(self, node):

        sim_board = node.board.copy()
        current_player = node.player_id

        while not sim_board.get_winner() and not sim_board.is_full():

            move_type, col = self._pick_smart_move(sim_board, current_player)

            if move_type == "drop":
                sim_board.drop(col, current_player)
            else:
                sim_board.pop(col, current_player)
                # elsif error

            current_player = PLAYER2 if current_player == PLAYER1 else PLAYER1

        return sim_board.get_winner()

    # Propagate the result up the tree
    def _backpropagate(self, node, result):

        while node is not None:

            node.visits += 1

            if result == self.player_id:
                node.wins += 1

            node = node.parent
