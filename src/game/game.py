# =================================
#             IMPORTS
# =================================

from src.game.board import SYMBOLS, Board

# =================================
#          GAME CLASSES
# =================================

PLAYER1_TURN = 1
PLAYER2_TURN = 2


class Game:

    # Constructor
    def __init__(self, player1, player2):
        self.board = Board()
        self.player1 = player1
        self.player2 = player2
        self.turn = PLAYER1_TURN

    # Cambio de turno
    def switch_turn(self):

        if self.turn == PLAYER1_TURN:
            self.turn = PLAYER2_TURN
        else:
            self.turn = PLAYER1_TURN

    # Devuelve el jugador actual -> Player()
    def get_actual_player(self, turn):

        if turn == PLAYER1_TURN:
            return self.player1
        else:
            return self.player2

    def play(self):

        # Mostrar tablero
        print("=== PopOut Game Start ===")
        print(self.board)

        # Mientras no haya ganador o el tablero est elleno
        while not self.board.get_winner() and not self.board.is_full():

            # Pedir movimiento al jugador actual
            actual_player = self.get_actual_player(self.turn)
            move_type, col = actual_player.get_move(self.board)

            # Ejecutar movimiento
            if move_type == "drop":
                self.board.drop(col, actual_player.player_id)
            else:
                self.board.pop(col, actual_player.player_id)

            # Mostrar tablero actualizado
            print(self.board)

            # Cambiar turno
            self.switch_turn()

        # Fin de partida
        winner = self.board.get_winner()

        if winner:
            print(f"\nPlayer {SYMBOLS[winner]} wins!")
        else:
            print("\nIt's a draw!")
