"""
Unit tests for the PopOut game board logic.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from src.game.board import Board, PLAYER1, PLAYER2, EMPTY, ROWS, COLS


class TestBoardDrop:
    def test_drop_in_empty_column(self):
        board = Board()
        assert board.drop(0, PLAYER1) is True
        assert board.grid[ROWS - 1][0] == PLAYER1

    def test_drop_fills_bottom_first(self):
        board = Board()
        board.drop(0, PLAYER1)
        board.drop(0, PLAYER2)
        assert board.grid[ROWS - 1][0] == PLAYER1
        assert board.grid[ROWS - 2][0] == PLAYER2

    def test_drop_full_column_returns_false(self):
        board = Board()
        for _ in range(ROWS):
            board.drop(0, PLAYER1)
        assert board.drop(0, PLAYER2) is False

    def test_can_drop_empty_column(self):
        board = Board()
        assert board.can_drop(0) is True

    def test_can_drop_full_column(self):
        board = Board()
        for _ in range(ROWS):
            board.drop(0, PLAYER1)
        assert board.can_drop(0) is False

    def test_drop_invalid_column(self):
        board = Board()
        assert board.drop(-1, PLAYER1) is False
        assert board.drop(COLS, PLAYER1) is False


class TestBoardPop:
    def test_pop_bottom_disc(self):
        board = Board()
        board.drop(0, PLAYER1)
        board.drop(0, PLAYER2)
        assert board.can_pop(0, PLAYER1) is True
        assert board.pop(0, PLAYER1) is True
        # After pop: bottom row should have PLAYER2 (shifted down)
        assert board.grid[ROWS - 1][0] == PLAYER2
        assert board.grid[ROWS - 2][0] == EMPTY

    def test_pop_wrong_player(self):
        board = Board()
        board.drop(0, PLAYER1)
        assert board.can_pop(0, PLAYER2) is False
        assert board.pop(0, PLAYER2) is False

    def test_pop_empty_column(self):
        board = Board()
        assert board.pop(0, PLAYER1) is False

    def test_pop_shifts_discs_down(self):
        board = Board()
        # Stack P1, P2, P1 in column 0 (bottom to top: P1, P2, P1)
        board.drop(0, PLAYER1)
        board.drop(0, PLAYER2)
        board.drop(0, PLAYER1)
        board.pop(0, PLAYER1)
        # Bottom should now be P2
        assert board.grid[ROWS - 1][0] == PLAYER2


class TestBoardWinner:
    def test_horizontal_win(self):
        board = Board()
        for col in range(4):
            board.drop(col, PLAYER1)
        assert board.get_winner() == PLAYER1

    def test_vertical_win(self):
        board = Board()
        for _ in range(4):
            board.drop(0, PLAYER1)
        assert board.get_winner() == PLAYER1

    def test_diagonal_win_tlbr(self):
        board = Board()
        # Build a diagonal for PLAYER1
        # row5,col0 | row4,col1 | row3,col2 | row2,col3
        board.grid[5][0] = PLAYER1
        board.grid[4][1] = PLAYER1
        board.grid[3][2] = PLAYER1
        board.grid[2][3] = PLAYER1
        assert board.get_winner() == PLAYER1

    def test_no_winner_empty_board(self):
        board = Board()
        assert board.get_winner() == 0

    def test_no_winner_three_in_row(self):
        board = Board()
        for col in range(3):
            board.drop(col, PLAYER1)
        assert board.get_winner() == 0


class TestBoardLegalMoves:
    def test_empty_board_has_drop_moves_only(self):
        board = Board()
        moves = board.get_legal_moves(PLAYER1)
        assert all(mt == 'drop' for mt, _ in moves)
        assert len(moves) == COLS

    def test_pop_move_available_when_bottom_occupied(self):
        board = Board()
        board.drop(0, PLAYER1)
        moves = board.get_legal_moves(PLAYER1)
        assert ('pop', 0) in moves

    def test_full_column_no_drop(self):
        board = Board()
        for _ in range(ROWS):
            board.drop(0, PLAYER1)
        moves = board.get_legal_moves(PLAYER1)
        drop_cols = [col for mt, col in moves if mt == 'drop']
        assert 0 not in drop_cols


class TestBoardIsFull:
    def test_empty_board_not_full(self):
        board = Board()
        assert board.is_full() is False

    def test_full_board(self):
        board = Board()
        for col in range(COLS):
            for _ in range(ROWS):
                board.drop(col, PLAYER1)
        assert board.is_full() is True


class TestBoardCopy:
    def test_copy_is_independent(self):
        board = Board()
        board.drop(0, PLAYER1)
        copy = board.copy()
        copy.drop(0, PLAYER2)
        # Original should not be affected
        assert board.grid[ROWS - 2][0] == EMPTY

    def test_to_tuple_is_hashable(self):
        board = Board()
        t = board.to_tuple()
        assert isinstance(t, tuple)
        d = {t: 1}
        assert d[t] == 1
