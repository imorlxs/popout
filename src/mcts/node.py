"""
MCTS Node used by the Monte Carlo Tree Search algorithm.
"""

import math


class MCTSNode:
    """
    A node in the MCTS game tree.

    Attributes
    ----------
    state_tuple : tuple
        Immutable board snapshot at this node.
    current_player : int
        The player whose turn it is at this node.
    move : tuple or None
        The (move_type, col) that led to this node from its parent.
    parent : MCTSNode or None
    children : list[MCTSNode]
    visits : int
        Number of times this node has been visited.
    wins : float
        Accumulated reward (from the perspective of the player who *made*
        the move that led here, i.e., the parent's current_player).
    untried_moves : list
        Legal moves that have not yet been expanded.
    """

    def __init__(self, state_tuple, current_player, move=None, parent=None,
                 untried_moves=None):
        self.state_tuple = state_tuple
        self.current_player = current_player
        self.move = move
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0.0
        self.untried_moves = list(untried_moves) if untried_moves else []

    # ------------------------------------------------------------------
    # UCT value
    # ------------------------------------------------------------------
    def uct_value(self, exploration_constant: float = 1.414) -> float:
        """
        Compute the UCT (Upper Confidence bound for Trees) value.

        UCT = wins/visits + C * sqrt(ln(parent.visits) / visits)
        """
        if self.visits == 0:
            return float('inf')
        exploitation = self.wins / self.visits
        exploration = exploration_constant * math.sqrt(
            math.log(self.parent.visits) / self.visits
        )
        return exploitation + exploration

    # ------------------------------------------------------------------
    # Tree helpers
    # ------------------------------------------------------------------
    def is_fully_expanded(self, max_children: int = None) -> bool:
        """Return True when all (or max_children) moves have been tried."""
        if not self.untried_moves:
            return True
        if max_children is not None and len(self.children) >= max_children:
            return True
        return False

    def is_terminal(self) -> bool:
        """Return True when there are no untried moves and no children."""
        return not self.untried_moves and not self.children

    def best_child(self, exploration_constant: float = 1.414) -> 'MCTSNode':
        """Return the child with the highest UCT value."""
        return max(self.children, key=lambda c: c.uct_value(exploration_constant))

    def most_visited_child(self) -> 'MCTSNode':
        """Return the child with the most visits (used for final selection)."""
        return max(self.children, key=lambda c: c.visits)

    def __repr__(self) -> str:
        move_str = str(self.move) if self.move else "root"
        return (
            f"MCTSNode(move={move_str}, visits={self.visits}, "
            f"wins={self.wins:.2f}, children={len(self.children)})"
        )
