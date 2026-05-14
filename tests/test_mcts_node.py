import math

import pytest
from src.game.board import Board, PLAYER1, PLAYER2
from src.mcts.node import MCTSNode


class TestMCTSNode:

    def test_init_sets_state_and_moves(self):
        board = Board()
        node = MCTSNode(board=board, player_id=PLAYER1, move=("drop", 0), parent=None)

        assert node.board is board
        assert node.player_id == PLAYER1
        assert node.move == ("drop", 0)
        assert node.parent is None
        assert node.wins == 0
        assert node.visits == 0
        assert node.children == []
        assert node.untried_moves == board.get_possible_moves(PLAYER1)

    def test_is_fully_expanded_uses_untried_moves(self):
        node = MCTSNode(board=Board(), player_id=PLAYER1)
        node.untried_moves = []

        assert node.is_fully_expanded() is True

    def test_is_terminal_detects_winner(self):
        board = Board()
        for col in range(4):
            board.drop(col, PLAYER1)

        node = MCTSNode(board=board, player_id=PLAYER2)

        assert node.is_terminal() is True

    def test_uct_score_returns_inf_for_unvisited_node(self):
        parent = MCTSNode(board=Board(), player_id=PLAYER1)
        parent.visits = 5
        node = MCTSNode(board=Board(), player_id=PLAYER2, parent=parent)

        assert node.uct_score() == float("inf")

    def test_uct_score_matches_formula(self):
        parent = MCTSNode(board=Board(), player_id=PLAYER1)
        parent.visits = 10
        node = MCTSNode(board=Board(), player_id=PLAYER2, parent=parent)
        node.wins = 3
        node.visits = 5

        expected = (3 / 5) + math.sqrt(2) * math.sqrt(math.log(10) / 5)

        assert node.uct_score() == pytest.approx(expected)

    def test_best_child_picks_highest_score(self, monkeypatch):
        node = MCTSNode(board=Board(), player_id=PLAYER1)
        child_a = MCTSNode(
            board=Board(), player_id=PLAYER2, move=("drop", 0), parent=node
        )
        child_b = MCTSNode(
            board=Board(), player_id=PLAYER2, move=("drop", 1), parent=node
        )
        node.children = [child_a, child_b]

        scores = {("drop", 0): 1.0, ("drop", 1): 2.0}
        monkeypatch.setattr(
            MCTSNode,
            "uct_score",
            lambda self: scores[self.move],
        )

        assert node.best_child() is child_b

    def test_expand_handles_drop_moves(self):
        node = MCTSNode(board=Board(), player_id=PLAYER1)
        node.untried_moves = [("drop", 0)]

        child = node.expand()

        assert child.parent is node
        assert child.move == ("drop", 0)
        assert child.player_id == PLAYER2
        assert child.board.board[5][0] == PLAYER1
        assert node.children == [child]

    def test_expand_handles_pop_moves(self):
        board = Board()
        board.drop(0, PLAYER1)
        node = MCTSNode(board=board, player_id=PLAYER1)
        node.untried_moves = [("pop", 0)]

        child = node.expand()

        assert child.parent is node
        assert child.move == ("pop", 0)
        assert child.player_id == PLAYER2
        assert child.board.board[5][0] == 0
        assert node.children == [child]


def test_is_terminal_draw_move():
    board = Board()
    node = MCTSNode(board=board, player_id=PLAYER1, move=("draw", -1), parent=None)
    assert node.is_terminal() is True


def test_is_terminal_full_board_no_pops(monkeypatch):
    board = Board()
    # Fill the board and ensure can_pop returns False for all cols
    for col in range(7):
        for _ in range(6):
            board.drop(col, PLAYER1)

    node = MCTSNode(board=board, player_id=PLAYER1)

    # Force can_pop to return False for all columns
    monkeypatch.setattr(board, "can_pop", lambda c, pid: False)

    assert node.is_terminal() is True


def test_is_terminal_full_board_with_pop(monkeypatch):
    board = Board()
    for col in range(7):
        for _ in range(6):
            board.drop(col, PLAYER1)

    node = MCTSNode(board=board, player_id=PLAYER1)

    # Force can_pop to return True for at least one column
    monkeypatch.setattr(board, "can_pop", lambda c, pid: c == 0)
    # Ensure no winner short-circuits the terminal check
    monkeypatch.setattr(board, "get_winner", lambda: 0)

    assert node.is_terminal() is False
