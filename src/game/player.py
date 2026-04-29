# =================================
#             IMPORTS
# =================================

from src.game.board import SYMBOLS, PLAYER1, PLAYER2

# =================================
#          PLAYER CLASSES
# =================================


class Player:

    def __init__(self, player_id):

        if player_id not in (PLAYER1, PLAYER2):
            raise ValueError(
                f"player_id must be {PLAYER1} or {PLAYER2}, got {player_id}"
            )

        self.player_id = player_id
        self.symbol = SYMBOLS[player_id]
        self.debug = false

    def set_debug_mode(self):
        self.debug = True

    def get_move(self, board):
        raise NotImplementedError


class HumanPlayer(Player):

    def __init__(self, player_id):
        super().__init__(player_id)

    def get_move(self, board):

        possible_moves = board.get_possible_moves(self.player_id)

        if self.debug:
            print(f"\nPossible moves for PLAYER-{self.symbol}: {possible_moves}")

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
