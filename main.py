# =================================
#             IMPORTS
# =================================

from src.game.player import HumanPlayer
from src.game.game import Game

# =================================
#              MAIN
# =================================


player1 = HumanPlayer(1)
player2 = HumanPlayer(2)

game = Game(player1, player2)
game.play()