# =================================
#             IMPORTS
# =================================

import pytest
from src.game.board import EMPTY, PLAYER1, PLAYER2
from src.game.player import Player, HumanPlayer
from src.game.game import Game

# =================================
#           GAME TESTS
# =================================


class TestGameInitialization:
    """Tests for Game initialization."""

    def test_game_init_human_human(self):
        """Test Game initializes correctly with two human players."""
        p1 = HumanPlayer(PLAYER1)
        p2 = HumanPlayer(PLAYER2)
        game = Game(p1, p2)

        assert game.board is not None
        assert game.player1 is p1
        assert game.player2 is p2

    def test_game_starts_with_player1_turn(self):
        """Test Game starts with Player 1 turn."""
        p1 = Player(PLAYER1)
        p2 = Player(PLAYER2)
        game = Game(p1, p2)

        assert game.turn == PLAYER1

    def test_game_board_is_empty(self):
        """Test Game starts with empty board."""
        p1 = Player(PLAYER1)
        p2 = Player(PLAYER2)
        game = Game(p1, p2)

        for row in game.board.board:
            for cell in row:
                assert cell == EMPTY


class TestGameSwitchTurn:
    """Tests for Game.switch_turn method."""

    def test_switch_from_player1_to_player2(self):
        """Test switch_turn changes from Player 1 to Player 2."""
        p1 = Player(PLAYER1)
        p2 = Player(PLAYER2)
        game = Game(p1, p2)

        game.switch_turn()
        assert game.turn == PLAYER2

    def test_switch_from_player2_to_player1(self):
        """Test switch_turn changes from Player 2 to Player 1."""
        p1 = Player(PLAYER1)
        p2 = Player(PLAYER2)
        game = Game(p1, p2)

        game.switch_turn()
        game.switch_turn()
        assert game.turn == PLAYER1

    def test_switch_turn_multiple_times(self):
        """Test switch_turn alternates correctly multiple times."""
        p1 = Player(PLAYER1)
        p2 = Player(PLAYER2)
        game = Game(p1, p2)

        expected = [PLAYER2, PLAYER1, PLAYER2, PLAYER1]
        for expected_turn in expected:
            game.switch_turn()
            assert game.turn == expected_turn

    def test_switch_turn_invalid_raises_value_error(self):
        """Test switch_turn raises ValueError for unexpected turn value."""
        p1 = Player(PLAYER1)
        p2 = Player(PLAYER2)
        game = Game(p1, p2)

        game.turn = 99
        with pytest.raises(ValueError):
            game.switch_turn()


class TestGameGetActualPlayer:
    """Tests for Game.get_actual_player method."""

    def test_get_player1(self):
        """Test get_actual_player returns Player 1 on turn 1."""
        p1 = Player(PLAYER1)
        p2 = Player(PLAYER2)
        game = Game(p1, p2)

        assert game.get_actual_player() is p1

    def test_get_player2(self):
        """Test get_actual_player returns Player 2 on turn 2."""
        p1 = Player(PLAYER1)
        p2 = Player(PLAYER2)
        game = Game(p1, p2)

        game.switch_turn()
        assert game.get_actual_player() is p2

    def test_get_actual_player_after_switch(self):
        """Test get_actual_player returns correct player after switch."""
        p1 = Player(PLAYER1)
        p2 = Player(PLAYER2)
        game = Game(p1, p2)

        game.switch_turn()
        assert game.get_actual_player() is p2

    def test_get_actual_player_invalid_raises_value_error(self):
        """Test get_actual_player raises ValueError for unexpected
        turn value."""
        p1 = Player(PLAYER1)
        p2 = Player(PLAYER2)
        game = Game(p1, p2)
        game.turn = 99

        with pytest.raises(ValueError):
            game.get_actual_player()


class TestGamePlay:
    """Tests for Game.play method simulating a short game."""

    def test_play_player1_wins_horizontal(self, monkeypatch, capsys):
        """Test play detects Player 1 winning horizontally."""
        p1 = HumanPlayer(PLAYER1)
        p2 = HumanPlayer(PLAYER2)
        game = Game(p1, p2)

        moves = iter(
            [
                "drop",
                "0",  # P1
                "drop",
                "0",  # P2
                "drop",
                "1",  # P1
                "drop",
                "1",  # P2
                "drop",
                "2",  # P1
                "drop",
                "2",  # P2
                "drop",
                "3",  # P1 wins
            ]
        )
        monkeypatch.setattr("builtins.input", lambda _: next(moves))

        game.play()

        captured = capsys.readouterr()
        assert "X wins" in captured.out
