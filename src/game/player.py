# =================================
#             IMPORTS
# =================================

from src.game.board import SYMBOLS


# =================================
#          PLAYER CLASSES
# =================================
class Player:

    def __init__(self, player_id):

        self.player_id = player_id
        self.symbol = SYMBOLS[player_id]  # SYMBOLS[1] = 'X', SYMBOLS[2] = 'O'

    # Clase que se implementa en cada tipo de PLAYER
    def get_move(self, board):
        raise NotImplementedError


class HumanPlayer(Player):

    def __init__(self, player_id):
        super().__init__(player_id)  # llama al __init__ de Player

    # Devuelve el movimiento del jugador (si se puede realizar)
    def get_move(self, board):

        possible_moves = board.get_possible_moves(self.player_id)

        print(f"\n Possible moves for PLAYER-{self.symbol} : {possible_moves}")

        while True:

            move_type = input("Enter move type (drop/pop): ").strip().lower()
            col_str = input("Enter column (0-6): ").strip()

            # Compruebo que el input de la columna es un numero
            if col_str.isdigit():
                col = int(col_str)
            else:
                print("INVALID INPUT, please enter a number for the column")
                continue

            if (move_type, col) in possible_moves:
                return move_type, col
            else:
                print("INVALID MOVE")
