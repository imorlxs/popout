import sys
import types

from src.game.board import PLAYER1
from src.game.player import MCTSPlayer


def test_choose_move_delegates_to_mcts():
    # Inject a lightweight fake `src.mcts.mcts` module so the
    # MCTSPlayer.choose_move import inside the method succeeds.
    # Provide a FakeMCTS implementation on the package `src.mcts` so
    # the relative import `from ..mcts import MCTS` inside
    # `MCTSPlayer.choose_move` resolves successfully.
    import importlib

    class FakeMCTS:
        def __init__(self, *args, **kwargs):
            pass

        def search(self, game):
            return ("drop", 0)

    mcts_pkg = importlib.import_module("src.mcts")
    setattr(mcts_pkg, "MCTS", FakeMCTS)

    try:
        player = MCTSPlayer(PLAYER1)
        result = player.choose_move("fake-game")
        assert result == ("drop", 0)
    finally:
        # Clean up the attribute we added
        delattr(mcts_pkg, "MCTS")
