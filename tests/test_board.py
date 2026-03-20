"""
Comprehensive tests for the Board class in PopOut game.

Tests cover board initialization, piece placement/removal, win detection,
and board state management.
"""

import pytest
from src.game.board import Board, ROWS, COLS, EMPTY, PLAYER1, PLAYER2


class TestBoardInitialization:
    """Tests for Board initialization."""

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_init_creates_board(self):
        """Test that __init__ creates a valid board."""
        board = Board()
        assert board is not None

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_init_board_all_empty(self):
        """Test that initialized board has all empty cells."""
        board = Board()
        # Check that all cells are empty (0)
        for row in board.board:
            for cell in row:
                assert cell == EMPTY

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_init_board_dimensions(self):
        """Test that board has correct dimensions."""
        board = Board()
        assert len(board.board) == ROWS
        for row in board.board:
            assert len(row) == COLS


class TestBoardCopy:
    """Tests for Board.copy() method."""
    @pytest.mark.xfail(raises=NotImplementedError)
    def test_copy_creates_independent_board(self):
        """Test that copy creates an independent board instance."""
        board1 = Board()
        board1.drop(0, PLAYER1)
        board2 = board1.copy()
        
        # Modify board2
        board2.drop(1, PLAYER2)
        
        # board1 should be unchanged
        assert board1.board[ROWS - 1][0] == PLAYER1
        assert board1.board[ROWS - 1][1] == EMPTY

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_copy_preserves_state(self):
        """Test that copy preserves the current board state."""
        board1 = Board()
        board1.drop(0, PLAYER1)
        board1.drop(0, PLAYER2)
        board1.drop(1, PLAYER1)
        
        board2 = board1.copy()
        
        assert board2.board == board1.board
        assert board2 is not board1  # Should be different objects


class TestDropMove:
    """Tests for drop and can_drop methods."""

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_can_drop_empty_column(self):
        """Test can_drop returns True for empty column."""
        board = Board()
        assert board.can_drop(0) is True
        assert board.can_drop(COLS - 1) is True

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_drop_single_piece(self):
        """Test dropping a single piece into empty column."""
        board = Board()
        result = board.drop(0, PLAYER1)
        assert result is True
        assert board.board[ROWS - 1][0] == PLAYER1

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_drop_stacks_pieces(self):
        """Test that pieces stack on top of each other."""
        board = Board()
        board.drop(0, PLAYER1)
        board.drop(0, PLAYER2)
        
        assert board.board[ROWS - 1][0] == PLAYER1
        assert board.board[ROWS - 2][0] == PLAYER2

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_drop_fills_column(self):
        """Test dropping pieces until column is full."""
        board = Board()
        for i in range(ROWS):
            assert board.can_drop(0) is True
            result = board.drop(0, PLAYER1 if i % 2 == 0 else PLAYER2)
            assert result is True

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_can_drop_full_column_returns_false(self):
        """Test can_drop returns False for full column."""
        board = Board()
        # Fill column 0
        for i in range(ROWS):
            board.drop(0, PLAYER1)
        
        assert board.can_drop(0) is False

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_drop_full_column_returns_false(self):
        """Test drop returns False when column is full."""
        board = Board()
        # Fill column 0
        for i in range(ROWS):
            board.drop(0, PLAYER1)
        
        assert board.drop(0, PLAYER2) is False

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_drop_multiple_columns(self):
        """Test dropping pieces into multiple columns."""
        board = Board()
        for col in range(COLS):
            board.drop(col, PLAYER1)
        
        for col in range(COLS):
            assert board.board[ROWS - 1][col] == PLAYER1

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_drop_invalid_column_index(self):
        """Test drop with invalid column index."""
        board = Board()
        # Behavior depends on implementation, but should handle gracefully
        result = board.drop(-1, PLAYER1)
        # Either returns False or raises exception
        if result is not False:
            pytest.fail("Expected drop to return False or raise exception for invalid column")


class TestPopMove:
    """Tests for pop and can_pop methods."""

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_can_pop_empty_column_returns_false(self):
        """Test can_pop returns False for empty column."""
        board = Board()
        assert board.can_pop(0, PLAYER1) is False

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_can_pop_wrong_player_returns_false(self):
        """Test can_pop returns False if bottom piece doesn't belong to player."""
        board = Board()
        board.drop(0, PLAYER1)
        assert board.can_pop(0, PLAYER2) is False

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_can_pop_correct_player_returns_true(self):
        """Test can_pop returns True for correct player."""
        board = Board()
        board.drop(0, PLAYER1)
        assert board.can_pop(0, PLAYER1) is True

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_pop_removes_bottom_piece(self):
        """Test that pop removes the bottom piece."""
        board = Board()
        board.drop(0, PLAYER1)
        board.pop(0, PLAYER1)
        assert board.board[ROWS - 1][0] == EMPTY

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_pop_shifts_pieces_down(self):
        """Test that pop shifts pieces down."""
        board = Board()
        board.drop(0, PLAYER1)
        board.drop(0, PLAYER2)
        board.drop(0, PLAYER1)
        
        board.pop(0, PLAYER1)
        
        # After popping bottom PLAYER1, PLAYER2 should be at bottom
        assert board.board[ROWS - 1][0] == PLAYER2
        assert board.board[ROWS - 2][0] == PLAYER1
        assert board.board[ROWS - 3][0] == EMPTY

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_pop_wrong_player_returns_false(self):
        """Test pop returns False with wrong player."""
        board = Board()
        board.drop(0, PLAYER1)
        result = board.pop(0, PLAYER2)
        assert result is False

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_pop_empty_column_returns_false(self):
        """Test pop returns False on empty column."""
        board = Board()
        result = board.pop(0, PLAYER1)
        assert result is False

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_pop_multiple_pieces_sequence(self):
        """Test popping multiple pieces in sequence."""
        board = Board()
        board.drop(0, PLAYER1)
        board.drop(0, PLAYER2)
        board.drop(0, PLAYER1)
        
        assert board.pop(0, PLAYER1) is True
        assert board.pop(0, PLAYER2) is True
        assert board.pop(0, PLAYER1) is True
        assert board.board[ROWS - 1][0] == EMPTY


class TestWinDetection:
    """Tests for get_winner and _check_line methods."""

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_check_line_four_in_row(self):
        """Test _check_line detects four in a row."""
        board = Board()
        line = [PLAYER1, PLAYER1, PLAYER1, PLAYER1]
        assert board._check_line(line) == PLAYER1

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_check_line_player2_wins(self):
        """Test _check_line detects player 2 win."""
        board = Board()
        line = [EMPTY, PLAYER2, PLAYER2, PLAYER2, PLAYER2, EMPTY]
        assert board._check_line(line) == PLAYER2

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_check_line_no_winner(self):
        """Test _check_line returns 0 for no winner."""
        board = Board()
        line = [PLAYER1, PLAYER2, PLAYER1, PLAYER2]
        assert board._check_line(line) == 0

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_check_line_three_in_row(self):
        """Test _check_line doesn't count three in a row."""
        board = Board()
        line = [PLAYER1, PLAYER1, PLAYER1, PLAYER2]
        assert board._check_line(line) == 0

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_horizontal_win(self):
        """Test detecting horizontal win."""
        board = Board()
        # Create a horizontal line of Player1 pieces
        for col in range(4):
            board.drop(col, PLAYER1)
        
        assert board.get_winner() == PLAYER1

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_vertical_win(self):
        """Test detecting vertical win."""
        board = Board()
        # Stack 4 pieces in same column
        for _ in range(4):
            board.drop(0, PLAYER1)
        
        assert board.get_winner() == PLAYER1

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_diagonal_win_ascending(self):
        """Test detecting diagonal win (ascending)."""
        board = Board()

        #   - - - - - - -
        #   - - - - - - -
        #   - - - - X - -
        #   - - - X O - -
        #   - - X O O - -
        #   - X O O O - -
        board.drop(1, PLAYER1)
        
        board.drop(2, PLAYER2)
        board.drop(2, PLAYER1) 
        
        board.drop(3, PLAYER2)
        board.drop(3, PLAYER2)
        board.drop(3, PLAYER1) 
        
        board.drop(4, PLAYER2)
        board.drop(4, PLAYER2)
        board.drop(4, PLAYER2)
        board.drop(4, PLAYER1) 
        
        assert board.get_winner() == PLAYER1

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_diagonal_win_descending(self):
        """Test detecting diagonal win (descending)."""
        board = Board()
        #   - - - - - - -
        #   - - - - - - -
        #   - - X - - - -
        #   - - O X - - -
        #   - - O O X - -
        #   - - O O O X -

        board.drop(2, PLAYER2)
        board.drop(2, PLAYER2)
        board.drop(2, PLAYER2)
        board.drop(2, PLAYER1)
        board.drop(2, PLAYER1)
        
        board.drop(3, PLAYER2)
        board.drop(3, PLAYER2)
        board.drop(3, PLAYER1) 

        board.drop(4, PLAYER2)
        board.drop(4, PLAYER1) 
        
        board.drop(5, PLAYER1)
        
        assert board.get_winner() == PLAYER1

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_no_winner_empty_board(self):
        """Test no winner on empty board."""
        board = Board()
        assert board.get_winner() == 0

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_no_winner_partial_board(self):
        """Test no winner with partial board."""
        board = Board()
        board.drop(0, PLAYER1)
        board.drop(1, PLAYER2)
        board.drop(2, PLAYER1)
        assert board.get_winner() == 0


class TestBoardFull:
    """Tests for is_full method."""

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_empty_board_not_full(self):
        """Test empty board is not full."""
        board = Board()
        assert board.is_full() is False

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_partially_filled_board_not_full(self):
        """Test partially filled board is not full."""
        board = Board()
        for col in range(COLS):
            board.drop(col, PLAYER1)
        assert board.is_full() is False

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_completely_filled_board_is_full(self):
        """Test completely filled board is full."""
        board = Board()
        # Fill all cells
        for col in range(COLS):
            for _ in range(ROWS):
                board.drop(col, PLAYER1)
        assert board.is_full() is True

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_full_board_alternates(self):
        """Test full board with alternating players."""
        board = Board()
        # Fill board with alternating players
        for col in range(COLS):
            for i in range(ROWS):
                player = PLAYER1 if i % 2 == 0 else PLAYER2
                board.drop(col, player)
        assert board.is_full() is True


class TestPossibleMoves:
    """Tests for get_possible_moves method."""

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_possible_moves_empty_board(self):
        """Test possible moves on empty board."""
        board = Board()
        moves = board.get_possible_moves(PLAYER1)
        
        # All columns should allow drop moves
        drop_moves = [move for move in moves if move[0] == 'drop']
        assert len(drop_moves) >= COLS

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_possible_moves_include_drops(self):
        """Test that possible moves include drop moves."""
        board = Board()
        board.drop(0, PLAYER1)
        moves = board.get_possible_moves(PLAYER1)
        
        # Should have drop option for column 0 (not full yet)
        assert any(move[0] == 'drop' and move[1] == 0 for move in moves)

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_possible_moves_include_pops(self):
        """Test that possible moves include pop moves when applicable."""
        board = Board()
        board.drop(0, PLAYER1)
        moves = board.get_possible_moves(PLAYER1)
        
        # Should have pop option for column 0
        assert any(move[0] == 'pop' and move[1] == 0 for move in moves)

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_possible_moves_no_pop_for_other_player(self):
        """Test no pop move if bottom piece belongs to other player."""
        board = Board()
        board.drop(0, PLAYER2)
        moves = board.get_possible_moves(PLAYER1)
        
        # Should not have pop option for column 0
        pop_moves = [move for move in moves if move[0] == 'pop' and move[1] == 0]
        assert len(pop_moves) == 0

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_possible_moves_full_column_no_drop(self):
        """Test no drop move for full column."""
        board = Board()
        # Fill column 0
        for _ in range(ROWS):
            board.drop(0, PLAYER1)
        
        moves = board.get_possible_moves(PLAYER1)
        drop_moves = [move for move in moves if move[0] == 'drop' and move[1] == 0]
        assert len(drop_moves) == 0

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_possible_moves_returns_tuples(self):
        """Test that get_possible_moves returns list of tuples."""
        board = Board()
        moves = board.get_possible_moves(PLAYER1)
        
        assert isinstance(moves, list)
        for move in moves:
            assert isinstance(move, tuple)
            assert len(move) == 2
            assert move[0] in ['drop', 'pop']
            assert isinstance(move[1], int)


class TestBoardStateEncoding:
    """Tests for to_tuple and to_flat_list methods."""

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_to_tuple_immutable(self):
        """Test that to_tuple returns an immutable structure."""
        board = Board()
        board.drop(0, PLAYER1)
        board_tuple = board.to_tuple()
        
        # Should be immutable (tuple)
        assert isinstance(board_tuple, tuple)

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_to_tuple_represents_state(self):
        """Test that to_tuple represents board state."""
        board1 = Board()
        board1.drop(0, PLAYER1)
        board1.drop(1, PLAYER2)
        
        board2 = Board()
        board2.drop(0, PLAYER1)
        board2.drop(1, PLAYER2)
        
        assert board1.to_tuple() == board2.to_tuple()

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_to_tuple_different_states(self):
        """Test that different states produce different tuples."""
        board1 = Board()
        board1.drop(0, PLAYER1)
        
        board2 = Board()
        board2.drop(0, PLAYER2)
        
        assert board1.to_tuple() != board2.to_tuple()

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_to_flat_list_length(self):
        """Test that to_flat_list has correct length."""
        board = Board()
        flat = board.to_flat_list()
        
        assert len(flat) == ROWS * COLS

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_to_flat_list_empty_board(self):
        """Test to_flat_list for empty board."""
        board = Board()
        flat = board.to_flat_list()
        
        assert all(cell == EMPTY for cell in flat)

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_to_flat_list_represents_state(self):
        """Test that to_flat_list represents board state."""
        board = Board()
        board.drop(0, PLAYER1)
        board.drop(1, PLAYER2)
        
        flat = board.to_flat_list()
        
        # Bottom row should have pieces in columns 0 and 1
        bottom_row_flat = flat[-COLS:]
        assert bottom_row_flat[0] == PLAYER1
        assert bottom_row_flat[1] == PLAYER2

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_to_flat_list_row_major_order(self):
        """Test that to_flat_list uses row-major order."""
        board = Board()
        board.drop(0, PLAYER1)
        
        flat = board.to_flat_list()
        
        # Last element of flat list should be bottom-right cell
        assert flat[-1] == EMPTY  # Bottom right is empty


class TestBoardDisplay:
    """Tests for __str__ method."""

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_str_returns_string(self):
        """Test that __str__ returns a string."""
        board = Board()
        result = board.__str__()
        assert isinstance(result, str)

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_str_empty_board(self):
        """Test string representation of empty board."""
        board = Board()
        board_str = str(board)
        
        # Should contain representation of empty cells
        assert '-' in board_str or 'E' in board_str or '0' in board_str

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_str_with_pieces(self):
        """Test string representation with pieces."""
        board = Board()
        board.drop(0, PLAYER1)
        board.drop(1, PLAYER2)
        
        board_str = str(board)
        
        # Should contain both piece representations
        assert 'X' in board_str or '1' in board_str
        assert 'O' in board_str or '2' in board_str

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_str_multiple_lines(self):
        """Test that string representation has multiple lines."""
        board = Board()
        board.drop(0, PLAYER1)
        
        board_str = str(board)
        lines = board_str.strip().split('\n')
        
        # Should have ROWS lines
        assert len(lines) == ROWS

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_str_correct_width(self):
        """Test that each line has correct width."""
        board = Board()
        board_str = str(board)
        lines = board_str.strip().split('\n')
        
        # Each line should represent COLS columns
        for line in lines:
            # Account for spacing/separators
            cells = line.split()
            assert len(cells) == COLS or len(line) >= COLS
