"""
Board representation and core logic for the PopOut game.

The board is stored as a 2D list: board[row][col]
where row 0 is the TOP of the board and row ROWS-1 is the BOTTOM.
Player tokens are represented as 1 (X) and 2 (O). Empty cells are 0.
"""

ROWS = 6
COLS = 7
EMPTY = 0
PLAYER1 = 1
PLAYER2 = 2
SYMBOLS = {EMPTY: "-", PLAYER1: "X", PLAYER2: "O"}


class Board:
    """Represents a PopOut game board."""

    def __init__(self):
        raise NotImplementedError("Board logic is not implemented yet.")

    def copy(self):
        raise NotImplementedError("Board logic is not implemented yet.")

    # ------------------------------------------------------------------
    # Drop move: place a disc in column col from the top
    # ------------------------------------------------------------------
    def can_drop(self, col: int) -> bool:
        """Return True if column col has at least one empty cell."""
        raise NotImplementedError("Board logic is not implemented yet.")

    def drop(self, col: int, player: int) -> bool:
        """
        Drop player's disc into column col.
        Returns True on success, False if the column is full.
        """
        raise NotImplementedError("Board logic is not implemented yet.")

    # ------------------------------------------------------------------
    # Pop move: remove a disc from the bottom of a column
    # ------------------------------------------------------------------
    def can_pop(self, col: int, player: int) -> bool:
        """Return True if column col's bottom cell contains player's disc."""
        raise NotImplementedError("Board logic is not implemented yet.")

    def pop(self, col: int, player: int) -> bool:
        """
        Remove the bottom disc of column col (must belong to player).
        Every disc above it shifts down by one row.
        Returns True on success, False otherwise.
        """
        raise NotImplementedError("Board logic is not implemented yet.")

    # ------------------------------------------------------------------
    # Win / draw detection
    # ------------------------------------------------------------------
    def _check_line(self, cells) -> int:
        """
        Given a list of cell values, return the player who has 4 in a row,
        or 0 if neither does.
        """
        raise NotImplementedError("Board logic is not implemented yet.")

    def get_winner(self) -> int:
        """
        Return PLAYER1, PLAYER2, or 0 (no winner yet).
        Checks all horizontal, vertical, and diagonal lines.
        """
        raise NotImplementedError("Board logic is not implemented yet.")

    def is_full(self) -> bool:
        """Return True if every cell on the board is occupied."""
        raise NotImplementedError("Board logic is not implemented yet.")

    # ------------------------------------------------------------------
    # Possible moves
    # ------------------------------------------------------------------
    def get_possible_moves(self, player: int):
        """
        Return a list of (move_type, col) tuples for the given player.
        move_type is 'drop' or 'pop'.
        """
        raise NotImplementedError("Board logic is not implemented yet.")

    # ------------------------------------------------------------------
    # Board state encoding (for repetition detection / dataset)
    # ------------------------------------------------------------------
    def to_tuple(self):
        """Return an immutable representation of the board state."""
        raise NotImplementedError("Board logic is not implemented yet.")

    def to_flat_list(self):
        """Return a flat list of cell values (row-major order)."""
        raise NotImplementedError("Board logic is not implemented yet.")

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------
    def __str__(self) -> str:
        """Return the string representation of the board"""
        raise NotImplementedError("Board logic is not implemented yet.")
