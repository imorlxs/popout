# =================================
#             IMPORTS
# =================================

import pytest
from src.game.board import Board, PLAYER1, PLAYER2, SYMBOLS
from src.game.player import Player, HumanPlayer

# =================================
#         PLAYER TESTS
# =================================



class TestPlayerInitialization:
    """Tests for Player base class initialization."""

    def test_player1_init(self):
        """Test Player 1 initializes correctly."""
        player = Player(PLAYER1)
        assert player.player_id == PLAYER1

    def test_player2_init(self):
        """Test Player 2 initializes correctly."""
        player = Player(PLAYER2)
        assert player.player_id == PLAYER2

    def test_player1_symbol(self):
        """Test Player 1 has correct symbol."""
        player = Player(PLAYER1)
        assert player.symbol == SYMBOLS[PLAYER1]

    def test_player2_symbol(self):
        """Test Player 2 has correct symbol."""
        player = Player(PLAYER2)
        assert player.symbol == SYMBOLS[PLAYER2]

    def test_invalid_player_id_raises_value_error(self):
        """Test Player raises ValueError for invalid player_id."""
        with pytest.raises(ValueError):
            Player(99)

    def test_get_move_raises_not_implemented(self):
        """Test base Player.get_move raises NotImplementedError."""
        player = Player(PLAYER1)
        board = Board()
        with pytest.raises(NotImplementedError):
            player.get_move(board)


class TestHumanPlayerInitialization:
    """Tests for HumanPlayer initialization."""

    def test_human_player1_init(self):
        """Test HumanPlayer 1 initializes correctly."""
        player = HumanPlayer(PLAYER1)
        assert player.player_id == PLAYER1
        assert player.symbol == SYMBOLS[PLAYER1]

    def test_human_player2_init(self):
        """Test HumanPlayer 2 initializes correctly."""
        player = HumanPlayer(PLAYER2)
        assert player.player_id == PLAYER2
        assert player.symbol == SYMBOLS[PLAYER2]

    def test_human_player_is_player(self):
        """Test HumanPlayer is instance of Player."""
        player = HumanPlayer(PLAYER1)
        assert isinstance(player, Player)

    def test_human_player_get_move_returns_tuple(self, monkeypatch):
        """Test HumanPlayer.get_move returns a valid (move_type, col) tuple."""
        player = HumanPlayer(PLAYER1)
        board = Board()

        inputs = iter(["drop", "0"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        move = player.get_move(board)

        assert isinstance(move, tuple)
        assert len(move) == 2
        assert move[0] in ["drop", "pop"]
        assert isinstance(move[1], int)

    def test_human_player_get_move_invalid_column_then_valid(self, monkeypatch):
        """Test HumanPlayer.get_move retries when column input is not a number."""
        player = HumanPlayer(PLAYER1)
        board = Board()

        inputs = iter(["drop", "asdfdf", "drop", "0"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        move = player.get_move(board)
        assert move == ("drop", 0)

    def test_human_player_get_move_invalid_move_type_then_valid(self, monkeypatch):
        """Test HumanPlayer.get_move retries when move type is invalid."""
        player = HumanPlayer(PLAYER1)
        board = Board()

        inputs = iter(["jsdfjdsjf", "0", "drop", "0"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        move = player.get_move(board)
        assert move == ("drop", 0)
