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
        # Rule 3: track (board, side-to-move) occurrences for threefold repetition.
        self.state_counts = {}

    def _state_key(self):
        return (self.board.to_tuple(), self.turn)

    def _record_state(self):
        key = self._state_key()
        self.state_counts[key] = self.state_counts.get(key, 0) + 1

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
        self._record_state()

        drawn = False
        while not self.board.get_winner() and not drawn:

            actual_player = self.get_actual_player()

            # Rule 2: a full board with no pops available is an automatic draw.
            possible_moves = self.board.get_possible_moves(actual_player.player_id)
            if not possible_moves:
                break

            # Rule 3: if the current state has occurred 3+ times, the side
            # to move may claim a draw before playing.
            if self.state_counts[self._state_key()] >= 3:
                if actual_player.wants_to_claim_draw(self.board):
                    drawn = True
                    print(
                        f"\n PLAYER-{SYMBOLS[self.turn]} claims draw by "
                        "threefold repetition."
                    )
                    break

            move_type, col = actual_player.get_move(self.board)

            if move_type == "draw":
                drawn = True
                break

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
            self._record_state()

        winner = self.board.get_winner()

        if winner:
            print(f"\n Player {SYMBOLS[winner]} wins!")
        else:
            print("\n It's a draw!")
