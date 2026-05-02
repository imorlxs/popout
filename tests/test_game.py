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


class TestRule3Repetition:
    """Tests for Rule 3 — threefold repetition."""

    def test_state_counts_initial_after_play_records_starting_state(self):
        """Recording begins at game start with the initial position."""
        p1 = Player(PLAYER1)
        p2 = Player(PLAYER2)
        game = Game(p1, p2)

        assert game.state_counts == {}
        game._record_state()
        assert game.state_counts[(game.board.to_tuple(), PLAYER1)] == 1

    def test_state_counts_distinguishes_side_to_move(self):
        """The same board with different side-to-move counts separately."""
        p1 = Player(PLAYER1)
        p2 = Player(PLAYER2)
        game = Game(p1, p2)

        game._record_state()
        game.switch_turn()
        game._record_state()

        snap = game.board.to_tuple()
        assert game.state_counts[(snap, PLAYER1)] == 1
        assert game.state_counts[(snap, PLAYER2)] == 1

    def test_player_default_does_not_claim_draw(self):
        """Base Player does not claim draws."""
        p = Player(PLAYER1)
        from src.game.board import Board
        assert p.wants_to_claim_draw(Board()) is False

    def test_play_ends_when_player_claims_repetition(self, monkeypatch, capsys):
        """Once the state repeats 3 times, a claiming player ends the game."""
        from src.game.player import RandomPlayer

        class ClaimingPlayer(RandomPlayer):
            def wants_to_claim_draw(self, _board):
                return True

        p1 = ClaimingPlayer(PLAYER1)
        p2 = ClaimingPlayer(PLAYER2)
        game = Game(p1, p2)

        # Pre-seed the state count so the very first turn already has 3
        # occurrences of (initial board, PLAYER1 to move).
        game.state_counts[(game.board.to_tuple(), PLAYER1)] = 2
        game.play()

        captured = capsys.readouterr()
        assert "threefold repetition" in captured.out
        assert "It's a draw!" in captured.out
