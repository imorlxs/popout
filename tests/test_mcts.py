"""
Unit tests for the MCTS algorithm.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from src.game.board import Board, PLAYER1, PLAYER2, ROWS, COLS
from src.game.popout import PopOutGame
from src.game.player import RandomPlayer
from src.mcts.node import MCTSNode
from src.mcts.mcts import MCTS


class _GameProxy:
    """Minimal game proxy for MCTS tests."""
    def __init__(self, board, current_player):
        self.board = board
        self.current_player = current_player

    def get_legal_moves(self):
        return self.board.get_legal_moves(self.current_player)


class TestMCTSNode:
    def test_uct_unvisited_returns_inf(self):
        parent = MCTSNode(state_tuple=(), current_player=PLAYER1,
                          untried_moves=[])
        parent.visits = 10
        child = MCTSNode(state_tuple=(), current_player=PLAYER2,
                         parent=parent, untried_moves=[])
        assert child.uct_value() == float('inf')

    def test_uct_value_computable(self):
        parent = MCTSNode(state_tuple=(), current_player=PLAYER1,
                          untried_moves=[])
        parent.visits = 10
        child = MCTSNode(state_tuple=(), current_player=PLAYER2,
                         parent=parent, untried_moves=[])
        child.visits = 5
        child.wins = 3
        val = child.uct_value(exploration_constant=1.0)
        assert val > 0

    def test_is_fully_expanded_no_untried(self):
        node = MCTSNode(state_tuple=(), current_player=PLAYER1,
                        untried_moves=[])
        assert node.is_fully_expanded() is True

    def test_is_fully_expanded_with_max_children(self):
        node = MCTSNode(state_tuple=(), current_player=PLAYER1,
                        untried_moves=[('drop', 0), ('drop', 1)])
        # Add 2 children, max_children=2
        node.children = [
            MCTSNode((), PLAYER2),
            MCTSNode((), PLAYER2),
        ]
        assert node.is_fully_expanded(max_children=2) is True

    def test_most_visited_child(self):
        parent = MCTSNode(state_tuple=(), current_player=PLAYER1,
                          untried_moves=[])
        c1 = MCTSNode(state_tuple=(), current_player=PLAYER2,
                      move=('drop', 0), parent=parent)
        c2 = MCTSNode(state_tuple=(), current_player=PLAYER2,
                      move=('drop', 1), parent=parent)
        c1.visits = 10
        c2.visits = 5
        parent.children = [c1, c2]
        assert parent.most_visited_child() is c1


class TestMCTS:
    def _empty_game(self):
        board = Board()
        return _GameProxy(board, PLAYER1)

    def test_returns_legal_move(self):
        game = self._empty_game()
        mcts = MCTS(iterations=50)
        move = mcts.search(game)
        legal = game.get_legal_moves()
        assert move in legal

    def test_blocks_immediate_win(self):
        """MCTS should block an opponent who has 3 in a row."""
        board = Board()
        # Give PLAYER2 three in a row (columns 0-2) at the bottom
        for col in range(3):
            board.drop(col, PLAYER2)
        game = _GameProxy(board.copy(), PLAYER1)
        mcts = MCTS(iterations=1000, rollout_policy='heuristic')
        move = mcts.search(game)
        # PLAYER1 must drop at column 3 to block
        assert move == ('drop', 3)

    def test_takes_winning_move(self):
        """MCTS should take an immediate win."""
        board = Board()
        # PLAYER1 has three in a row at columns 0-2
        for col in range(3):
            board.drop(col, PLAYER1)
        game = _GameProxy(board.copy(), PLAYER1)
        mcts = MCTS(iterations=300)
        move = mcts.search(game)
        assert move == ('drop', 3)

    def test_heuristic_rollout(self):
        game = self._empty_game()
        mcts = MCTS(iterations=50, rollout_policy='heuristic')
        move = mcts.search(game)
        assert move in game.get_legal_moves()

    def test_max_children(self):
        game = self._empty_game()
        mcts = MCTS(iterations=50, max_children=3)
        move = mcts.search(game)
        assert move in game.get_legal_moves()

    def test_full_game_computer_vs_computer(self):
        """A game between two MCTS players should terminate."""
        p1 = RandomPlayer(seed=1)
        p2 = RandomPlayer(seed=2)
        game = PopOutGame(p1, p2)
        result = game.play(verbose=False)
        assert result in ('player1', 'player2', 'draw')
