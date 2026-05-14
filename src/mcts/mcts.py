# =================================
#         MCTS PLAYER v1
# =================================

import random

from .node import MCTSNode
from ..game.board import Board, PLAYER1, PLAYER2, ROWS, COLS

class MCTS:
    """
    Monte Carlo Tree Search with UCT.

    Parameters
    ----------
    iterations : int
        Total number of simulation iterations.
    exploration_constant : float
        UCT exploration parameter C.
    max_children : int or None
        Maximum children expanded per node; None = expand all.
    rollout_policy : str
        'random' – uniform random rollout (default).
        'heuristic' – prefer winning / blocking moves during rollout.
    """

    def __init__(self, iterations: int = 1000,
                 exploration_constant: float = 1.414,
                 max_children: int = None,
                 rollout_policy: str = 'random'):
        self.iterations = iterations
        self.exploration_constant = exploration_constant
        self.max_children = max_children
        self.rollout_policy = rollout_policy

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def search(self, game) -> tuple:
        """
        Run MCTS from the current game state.

        Parameters
        ----------
        game : PopOutGame
            The current game (not mutated).

        Returns
        -------
        (move_type, col) : tuple
            The best move found.
        """
        board_copy = game.board.copy()
        current_player = game.current_player
        legal_moves = game.get_possible_moves()

        if not legal_moves:
            return ('draw', -1)

        # Build the root node (pass Board and player_id to node implementation)
        root = MCTSNode(
            board=board_copy,
            player_id=current_player,
            untried_moves=list(legal_moves),
        )

        for _ in range(self.iterations):
            # --- Selection ---
            node, board_sim, player_sim = self._select(root, board_copy.copy(), current_player)

            # --- Expansion ---
            if node.untried_moves and not self._is_terminal_board(board_sim, player_sim):
                node, board_sim, player_sim = self._expand(node, board_sim, player_sim)

            # --- Simulation (rollout) ---
            result = self._simulate(board_sim, player_sim)

            # --- Backpropagation ---
            self._backpropagate(node, result, current_player)

        best = root.most_visited_child()
        return best.move

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------
    def _select(self, node: MCTSNode, board: Board, player: int):
        """Traverse the tree using UCT until an unexpanded node is found."""
        while not node.untried_moves and node.children:
            node = node.best_child(self.exploration_constant)
            board, player = self._apply_move_to_board(board, node.move, player)
        return node, board, player

    # ------------------------------------------------------------------
    # Expansion
    # ------------------------------------------------------------------
    def _expand(self, node: MCTSNode, board: Board, player: int):
        """Expand one untried move from node."""
        move = node.untried_moves.pop(random.randrange(len(node.untried_moves)))
        new_board, new_player = self._apply_move_to_board(board.copy(), move, player)
        legal = new_board.get_possible_moves(new_player)
        child = MCTSNode(
            board=new_board,
            player_id=new_player,
            move=move,
            parent=node,
            untried_moves=legal,
        )
        node.children.append(child)
        return child, new_board, new_player

    # ------------------------------------------------------------------
    # Simulation (rollout)
    # ------------------------------------------------------------------
    def _simulate(self, board: Board, player: int) -> int:
        """
        Play a game to completion using the chosen rollout policy.

        Returns
        -------
        winner : int
            PLAYER1, PLAYER2, or 0 (draw).
        """
        board = board.copy()
        current = player
        max_moves = ROWS * COLS * 2  # safety cap

        for _ in range(max_moves):
            winner = board.get_winner()
            if winner:
                return winner
            if board.is_full():
                return 0  # draw

            legal = board.get_possible_moves(current)
            if not legal:
                return 0

            if self.rollout_policy == 'heuristic':
                move = self._heuristic_move(board, current, legal)
            else:
                move = random.choice(legal)

            move_type, col = move
            if move_type == 'drop':
                board.drop(col, current)
            elif move_type == 'pop':
                board.pop(col, current)

            winner = board.get_winner()
            if winner:
                return winner

            current = PLAYER2 if current == PLAYER1 else PLAYER1

        return 0  # draw by move limit

    def _heuristic_move(self, board: Board, player: int, legal: list) -> tuple:
        """
        Simple heuristic rollout: prefer moves that immediately win,
        then moves that block the opponent; otherwise random.
        """
        opponent = PLAYER2 if player == PLAYER1 else PLAYER1

        # Check for winning move
        for move in legal:
            b = board.copy()
            move_type, col = move
            if move_type == 'drop':
                b.drop(col, player)
            else:
                b.pop(col, player)
            if b.get_winner() == player:
                return move

        # Check for blocking move
        for move in legal:
            b = board.copy()
            move_type, col = move
            if move_type == 'drop':
                b.drop(col, player)
            else:
                b.pop(col, player)
            if b.get_winner() == opponent:
                # This move 'accidentally' lets opponent win → skip
                continue
            # Simulate opponent's best response
            for opp_move in b.get_possible_moves(opponent):
                b2 = b.copy()
                omt, oc = opp_move
                if omt == 'drop':
                    b2.drop(oc, opponent)
                else:
                    b2.pop(oc, opponent)
                if b2.get_winner() == opponent:
                    return move  # block this

        return random.choice(legal)

    # ------------------------------------------------------------------
    # Backpropagation
    # ------------------------------------------------------------------
    def _backpropagate(self, node: MCTSNode, result: int, root_player: int):
        """
        Walk back up the tree updating visit counts and wins.

        Wins are accumulated from the perspective of the player who
        moved into each node (i.e., the *parent's* current_player).
        """
        while node is not None:
            node.visits += 1
            if result == 0:
                node.wins += 0.5  # draw
            elif node.parent is not None:
                # The player who made the move to reach this node
                mover = node.parent.current_player
                if result == mover:
                    node.wins += 1.0
            else:
                # Root node: reward from root_player's perspective
                if result == root_player:
                    node.wins += 1.0
            node = node.parent

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _apply_move_to_board(self, board: Board, move: tuple, player: int):
        """Apply move to board and return (new_board, next_player)."""
        move_type, col = move
        if move_type == 'drop':
            board.drop(col, player)
        elif move_type == 'pop':
            board.pop(col, player)
        next_player = PLAYER2 if player == PLAYER1 else PLAYER1
        return board, next_player

    def _is_terminal_board(self, board: Board, player: int) -> bool:
        """Return True if the board is in a terminal state."""
        if board.get_winner():
            return True
        if board.is_full():
            return True
        if not board.get_possible_moves(player):
            return True
        return False



