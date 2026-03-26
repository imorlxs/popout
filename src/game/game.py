# =================================
#             IMPORTS
# =================================

from src.game.board import SYMBOLS, Board, PLAYER1, PLAYER2

# =================================
#          GAME CLASSES
# =================================


class Game:

    def __init__(self, player1, player2):

        self.board = Board()
        self.player1 = player1
        self.player2 = player2
        self.turn = PLAYER1

    def switch_turn(self):

        if self.turn == PLAYER1:
            self.turn = PLAYER2

        elif self.turn == PLAYER2:
            self.turn = PLAYER1

        else:
            raise ValueError(f"TURN: {self.turn}")

    def get_actual_player(self):

        if self.turn == PLAYER1:
            return self.player1

        elif self.turn == PLAYER2:
            return self.player2

        else:
            raise ValueError(f" INVALID PLAYER OBJECT: {self.turn}")

    def play(self):

        print("=== PopOut Game Start ===")
        print(self.board)

        # While there is no winner and the board is not full
        while not self.board.get_winner() and not self.board.is_full():

            actual_player = self.get_actual_player()
            move_type, col = actual_player.get_move(self.board)

            # Execute move and check if it was valid
            if move_type == "drop":
                valid = self.board.drop(col, actual_player.player_id)

            elif move_type == "pop":
                valid = self.board.pop(col, actual_player.player_id)

            else:
                raise ValueError(f"Invalid move type: {move_type}")

            if not valid:
                print("Move could not be executed, try again")
                continue

            print(self.board)
            self.switch_turn()

        # End of game
        winner = self.board.get_winner()

        if winner:
            print(f"\n Player {SYMBOLS[winner]} wins!")
        else:
            print("\n It's a draw!")
