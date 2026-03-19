"""
PopOut game controller.

Manages game flow, enforces the three special PopOut rules:
  1. Simultaneous four-in-rows after a pop → mover wins.
  2. Full board → moving player may declare a draw instead of popping.
  3. Same board state repeated 3 times → either player may declare draw.
"""

from .board import Board, PLAYER1, PLAYER2, EMPTY


class PopOutGame:
    """
    Controls a PopOut game session between two players.

    Parameters
    ----------
    player1 : player object
        Must implement ``choose_move(game)`` → (move_type, col).
    player2 : player object
        Must implement ``choose_move(game)`` → (move_type, col).
    """

    def __init__(self, player1, player2):
        self.board = Board()
        self.players = {PLAYER1: player1, PLAYER2: player2}
        self.current_player = PLAYER1
        self.history = []          # list of board tuples for repetition check
        self.move_count = 0
        self.game_over = False
        self.winner = None         # PLAYER1, PLAYER2, or None (draw)

    # ------------------------------------------------------------------
    # Turn helpers
    # ------------------------------------------------------------------
    def other_player(self, player: int) -> int:
        return PLAYER2 if player == PLAYER1 else PLAYER1

    def _record_state(self):
        self.history.append(self.board.to_tuple())

    def _state_repeated(self) -> bool:
        """Return True if the current board state has appeared 3 times."""
        current = self.board.to_tuple()
        return self.history.count(current) >= 3

    # ------------------------------------------------------------------
    # Apply a move and check all win / draw conditions
    # ------------------------------------------------------------------
    def apply_move(self, move_type: str, col: int) -> str:
        """
        Apply (move_type, col) for the current player.

        Returns a status string:
          'win'  – current player wins
          'draw' – game is drawn
          'ok'   – game continues
          'invalid' – move was illegal
        """
        player = self.current_player
        board = self.board

        if move_type == 'drop':
            if not board.drop(col, player):
                return 'invalid'

            winner = board.get_winner()
            if winner:
                self.game_over = True
                self.winner = winner
                return 'win'

        elif move_type == 'pop':
            # Rule 2: if board is full, the mover may choose draw instead
            if board.is_full():
                # The player object can signal 'draw' by returning
                # move_type == 'draw'; we handle it here for completeness.
                pass

            if not board.pop(col, player):
                return 'invalid'

            # Rule 1: check both players after a pop move
            p1_wins = self._has_four(PLAYER1)
            p2_wins = self._has_four(PLAYER2)
            if p1_wins or p2_wins:
                self.game_over = True
                # Simultaneous → the player who popped wins
                self.winner = player
                return 'win'

        elif move_type == 'draw':
            # Player explicitly declares a draw (Rule 2 / Rule 3)
            self.game_over = True
            self.winner = None
            return 'draw'

        else:
            return 'invalid'

        # Rule 3: repetition check
        self._record_state()
        if self._state_repeated():
            # Either player *may* declare draw; we auto-declare here
            self.game_over = True
            self.winner = None
            return 'draw'

        # Board full and no move declared draw yet → offer draw handled by
        # the player choosing 'draw' move next turn (Rule 2).
        self.move_count += 1
        self.current_player = self.other_player(player)
        return 'ok'

    def _has_four(self, player: int) -> bool:
        """Return True if player currently has four in a row on the board."""
        return self.board.get_winner() == player

    # ------------------------------------------------------------------
    # Legal moves for the current player
    # ------------------------------------------------------------------
    def get_legal_moves(self):
        moves = self.board.get_legal_moves(self.current_player)
        # Rule 2: if board is full, add draw option
        if self.board.is_full():
            moves.append(('draw', -1))
        return moves

    # ------------------------------------------------------------------
    # Main game loop
    # ------------------------------------------------------------------
    def play(self, verbose: bool = True) -> str:
        """
        Run the full game loop.

        Returns 'player1', 'player2', or 'draw'.
        """
        while not self.game_over:
            if verbose:
                print(self.board)
                player_symbol = 'X' if self.current_player == PLAYER1 else 'O'
                print(f"\nIt is now {player_symbol}'s turn.")

            player_obj = self.players[self.current_player]
            move_type, col = player_obj.choose_move(self)

            if verbose:
                if move_type == 'draw':
                    print(f"{player_symbol} declares a draw.")
                else:
                    print(f"{player_symbol} plays {move_type} on column {col + 1}.")

            status = self.apply_move(move_type, col)

            if status == 'invalid':
                if verbose:
                    print("Invalid move! Please try again.")
                continue

        if verbose:
            print("\nFinal board:")
            print(self.board)
            if self.winner is None:
                print("\nGame over – it's a draw!")
            else:
                symbol = 'X' if self.winner == PLAYER1 else 'O'
                print(f"\nGame over – {symbol} wins!")

        if self.winner == PLAYER1:
            return 'player1'
        if self.winner == PLAYER2:
            return 'player2'
        return 'draw'

    # ------------------------------------------------------------------
    # String representation
    # ------------------------------------------------------------------
    def __str__(self) -> str:
        return str(self.board)
