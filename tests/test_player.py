# =================================
#             IMPORTS
# =================================

import pytest
from src.game.board import Board, PLAYER1, PLAYER2, SYMBOLS
from src.game.player import Player, HumanPlayer, RandomPlayer

# =================================
#         HUMAN PLAYER TESTS
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



# =================================
#        RANDOM PLAYER TESTS
# =================================

class TestRandomPlayerInit:

    def test_init_player1(self):
        """Test RandomPlayer initializes correctly with PLAYER1."""
        player = RandomPlayer(PLAYER1)
        assert player.player_id == PLAYER1
        assert player.symbol == "X"

    def test_init_player2(self):
        """Test RandomPlayer initializes correctly with PLAYER2."""
        player = RandomPlayer(PLAYER2)
        assert player.player_id == PLAYER2
        assert player.symbol == "O"

    def test_init_invalid_player_id(self):
        """Test RandomPlayer raises ValueError with invalid player_id."""
        with pytest.raises(ValueError):
            RandomPlayer(99)


class TestRandomPlayerGetMove:

    def test_get_move_returns_tuple(self):
        """Test get_move returns a tuple."""
        player = RandomPlayer(PLAYER1)
        board = Board()
        move = player.get_move(board)
        assert isinstance(move, tuple)

    def test_get_move_returns_valid_move(self):
        """Test get_move returns a move that is in possible_moves."""
        player = RandomPlayer(PLAYER1)
        board = Board()
        move = player.get_move(board)
        assert move in board.get_possible_moves(PLAYER1)

    def test_get_move_returns_valid_move_type(self):
        """Test get_move returns a move with a valid move type."""
        player = RandomPlayer(PLAYER1)
        board = Board()
        move_type, col = player.get_move(board)
        assert move_type in ("drop", "pop")

    def test_get_move_returns_valid_column(self):
        """Test get_move returns a move with a valid column."""
        player = RandomPlayer(PLAYER1)
        board = Board()
        move_type, col = player.get_move(board)
        assert 0 <= col <= 6

    def test_get_move_is_random(self):
        """Test get_move does not always return the same move."""
        player = RandomPlayer(PLAYER1)
        board = Board()
        moves = {player.get_move(board) for _ in range(50)}
        assert len(moves) > 1

    def test_get_move_with_almost_full_board(self):
        """Test get_move works when only one drop move is available."""
        player = RandomPlayer(PLAYER1)
        board = Board()
        # Fill all columns except col 0 with PLAYER2 tokens
        # so PLAYER1 has no pop moves available
        for col in range(1, 7):
            for _ in range(6):
                board.drop(col, PLAYER2)
        move = player.get_move(board)
        assert move == ("drop", 0)

    def test_get_move_includes_pop_when_available(self, monkeypatch):
        """Test get_move can return a pop move when available."""
        player = RandomPlayer(PLAYER1)
        board = Board()
        board.drop(0, PLAYER1)
        # Force random.choice to return the pop move
        monkeypatch.setattr("random.choice", lambda moves: ("pop", 0))
        move = player.get_move(board)
        assert move == ("pop", 0)