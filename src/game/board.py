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
        self.board = [[EMPTY] * COLS for _ in range(ROWS)]

    def copy(self) -> "Board":
        """Return a deep copy of the board."""
        new_board = Board()
        new_board.board = [row[:] for row in self.board]
        return new_board

    # ------------------------------------------------------------------
    # Drop move: place a disc in column col from the top
    # ------------------------------------------------------------------
    def can_drop(self, col: int) -> bool:
        """Return True if column col has at least one empty cell."""
        return 0 <= col < COLS and self.board[0][col] == EMPTY

    def drop(self, col: int, player: int) -> bool:
        """
        Drop player's disc into column col.
        Returns True on success, False if the column is full.
        """
        if player not in (PLAYER1, PLAYER2):
            raise ValueError("player must be PLAYER1 or PLAYER2")

        if not self.can_drop(col):
            return False
        # Find the lowest empty row in the column
        for row in range(ROWS - 1, -1, -1):
            if self.board[row][col] == EMPTY:
                self.board[row][col] = player
                return True
        return False

    # ------------------------------------------------------------------
    # Pop move: remove a disc from the bottom of a column
    # ------------------------------------------------------------------
    def can_pop(self, col: int, player: int) -> bool:
        """Return True if column col's bottom cell contains player's disc."""
        return 0 <= col < COLS and self.board[ROWS - 1][col] == player

    def pop(self, col: int, player: int) -> bool:
        """
        Remove the bottom disc of column col (must belong to player).
        Every disc above it shifts down by one row.
        Returns True on success, False otherwise.
        """
        if not self.can_pop(col, player):
            return False
        # Shift all discs down (remove bottom, shift rest down)
        for row in range(ROWS - 1, 0, -1):
            self.board[row][col] = self.board[row - 1][col]
        self.board[0][col] = EMPTY
        return True

    # ------------------------------------------------------------------
    # Win / draw detection
    # ------------------------------------------------------------------
    def _check_line(self, cells: list[int]) -> int:
        """
        Given a list of cell values, return the player who has 4 in a row,
        or 0 if neither does.
        """
        for player in (PLAYER1, PLAYER2):
            count = 0
            for cell in cells:
                if cell == player:
                    count += 1
                    if count >= 4:
                        return player
                else:
                    count = 0
        return 0

    def get_winner(self) -> int:
        """
        Return PLAYER1, PLAYER2, or 0 (no winner yet).
        Checks all horizontal, vertical, and diagonal lines.
        """
        # Horizontal
        for row in range(ROWS):
            w = self._check_line(self.board[row])
            if w:
                return w

        # Vertical
        for col in range(COLS):
            w = self._check_line([self.board[row][col] for row in range(ROWS)])
            if w:
                return w

        # Diagonal (top-left to bottom-right)
        for row in range(ROWS - 3):
            for col in range(COLS - 3):
                w = self._check_line([self.board[row + k][col + k] for k in range(4)])
                if w:
                    return w

        # Diagonal (top-right to bottom-left)
        for row in range(ROWS - 3):
            for col in range(3, COLS):
                w = self._check_line([self.board[row + k][col - k] for k in range(4)])
                if w:
                    return w

        return 0

    def is_full(self) -> bool:
        """Return True if every cell on the board is occupied."""
        return all(self.board[0][col] != EMPTY for col in range(COLS))

    # ------------------------------------------------------------------
    # Possible moves
    # ------------------------------------------------------------------
    def get_possible_moves(self, player: int) -> list[tuple[str, int]]:
        """
        Return a list of (move_type, col) tuples for the given player.
        move_type is 'drop', 'pop', or 'draw'.

        Rule 2: when the board is full, the player to move may choose to end
        the game as a draw instead of popping. The ('draw', -1) option is
        included only when the board is full and at least one pop is legal.
        """
        moves = []
        for col in range(COLS):
            if self.can_drop(col):
                moves.append(("drop", col))
        for col in range(COLS):
            if self.can_pop(col, player):
                moves.append(("pop", col))
        if self.is_full() and any(m[0] == "pop" for m in moves):
            moves.append(("draw", -1))
        return moves

    # ------------------------------------------------------------------
    # Board state encoding (for repetition detection / dataset)
    # ------------------------------------------------------------------
    def to_tuple(self):
        """Return an immutable representation of the board state."""
        return tuple(tuple(row) for row in self.board)

    def to_flat_list(self):
        """Return a flat list of cell values (row-major order)."""
        return [cell for row in self.board for cell in row]

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------
    def __str__(self) -> str:
        """Return the string representation of the board"""
        lines = []
        for row in self.board:
            lines.append("".join(SYMBOLS[cell] for cell in row))
        return "\n".join(lines)
