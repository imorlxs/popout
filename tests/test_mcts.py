import importlib
from types import SimpleNamespace


from src.game.board import Board, PLAYER1, PLAYER2

# Some versions of the project have a broken or incompatible
# `src.mcts.mcts` module that raises on import. If importing that
# module fails for any reason, skip these MCTS integration tests.
mcts_mod = importlib.import_module("src.mcts.mcts")


def test_apply_move_to_board_drop_and_toggle():
    MCTS = mcts_mod.MCTS

    board = Board()
    m = MCTS()

    new_board, next_player = m._apply_move_to_board(board.copy(), ("drop", 0), PLAYER1)

    assert next_player == PLAYER2
    assert new_board.board[5][0] == PLAYER1


def test_apply_move_to_board_pop():
    mcts_mod = importlib.import_module("src.mcts.mcts")
    MCTS = mcts_mod.MCTS

    board = Board()
    board.drop(0, PLAYER1)
    m = MCTS()

    new_board, next_player = m._apply_move_to_board(board.copy(), ("pop", 0), PLAYER1)

    assert next_player == PLAYER2
    assert new_board.board[5][0] == 0


def test_heuristic_move_prefers_winning_move(monkeypatch):
    mcts_mod = importlib.import_module("src.mcts.mcts")
    MCTS = mcts_mod.MCTS

    m = MCTS(rollout_policy="heuristic")
    board = Board()
    for col in range(3):
        board.drop(col, PLAYER1)

    legal = board.get_possible_moves(PLAYER1)

    move = m._heuristic_move(board, PLAYER1, legal)

    assert move == ("drop", 3)


def test_simulate_uses_drop_moves(monkeypatch):
    mcts_mod = importlib.import_module("src.mcts.mcts")

    # Provide ROWS/COLS that the module expects at runtime
    board_mod = importlib.import_module("src.game.board")
    mcts_mod.ROWS = board_mod.ROWS
    mcts_mod.COLS = board_mod.COLS

    MCTS = mcts_mod.MCTS

    monkeypatch.setattr(
        "src.mcts.mcts.random.choice", lambda moves: ("drop", 3), raising=True
    )

    m = MCTS()
    board = Board()
    for col in range(3):
        board.drop(col, PLAYER1)

    assert m._simulate(board, PLAYER1) == PLAYER1


def test_simulate_uses_pop_moves(monkeypatch):
    mcts_mod = importlib.import_module("src.mcts.mcts")

    board_mod = importlib.import_module("src.game.board")
    mcts_mod.ROWS = board_mod.ROWS
    mcts_mod.COLS = board_mod.COLS

    MCTS = mcts_mod.MCTS

    monkeypatch.setattr(
        "src.mcts.mcts.random.choice", lambda moves: ("pop", 0), raising=True
    )

    # Simulate get_winner returning 0 first, then PLAYER1 after the pop
    calls = {"count": 0}

    def fake_get_winner(self):
        calls["count"] += 1
        return PLAYER1 if calls["count"] > 1 else 0

    monkeypatch.setattr("src.game.board.Board.get_winner", fake_get_winner, raising=True)

    m = MCTS()
    board = Board()
    for _ in range(4):
        board.drop(0, PLAYER1)

    assert m._simulate(board, PLAYER1) == PLAYER1


def test_backpropagate_updates_visits_and_wins():
    mcts_mod = importlib.import_module("src.mcts.mcts")
    MCTS = mcts_mod.MCTS

    m = MCTS()

    root = SimpleNamespace(parent=None, current_player=PLAYER1, visits=0, wins=0)
    child = SimpleNamespace(parent=root, visits=0, wins=0)

    m._backpropagate(child, PLAYER1, root_player=PLAYER1)

    assert child.visits == 1
    assert child.wins == 1.0
    assert root.visits == 1
    assert root.wins == 1.0


def test_search_returns_draw_when_no_legal_moves():
    mcts_mod = importlib.import_module("src.mcts.mcts")
    MCTS = mcts_mod.MCTS

    game = SimpleNamespace(board=Board(), current_player=PLAYER1, get_possible_moves=lambda: [])

    m = MCTS()

    assert m.search(game) == ("draw", -1)


def test_search_runs_and_returns_child_move(monkeypatch):
    """Run MCTS.search with a dummy MCTSNode class patched into the module
    so the search loop can execute without relying on the production
    `MCTSNode` implementation.
    """
    mcts_mod = importlib.import_module("src.mcts.mcts")

    # Dummy node class that matches the kwargs used by mcts.MCTS
    class DummyNode:
        def __init__(self, state_tuple=None, current_player=None, untried_moves=None, move=None, parent=None, **kwargs):
            self.state_tuple = state_tuple
            self.current_player = current_player
            self.untried_moves = untried_moves or []
            self.move = move
            self.parent = parent
            self.children = []
            self.visits = 0
            self.wins = 0.0

        def best_child(self, exploration):
            # return a child that has a concrete move
            return self.children[0]

        def most_visited_child(self):
            # return the first child as "best"
            return self.children[0]

    # Patch the MCTSNode in the mcts module
    monkeypatch.setattr(mcts_mod, "MCTSNode", DummyNode, raising=True)

    # Construct a small dummy game where get_possible_moves returns a non-empty list
    game = SimpleNamespace()
    board = Board()
    game.board = board
    game.current_player = PLAYER1
    game.get_possible_moves = lambda: [("drop", 0)]

    # Build a dummy root/move child structure by monkeypatching MCTS._select
    def fake_select(self, node, board_copy, player):
        # Use the provided node (root) and attach a child whose move will be returned by search()
        child = DummyNode(state_tuple=board_copy.to_tuple(), current_player=player, move=("drop", 0), parent=node)
        node.children.append(child)
        return node, board_copy, player

    monkeypatch.setattr(mcts_mod.MCTS, "_select", fake_select, raising=True)

    # Monkeypatch simulate/backpropagate to be no-ops (fast and deterministic)
    monkeypatch.setattr(mcts_mod.MCTS, "_simulate", lambda self, b, p: PLAYER1, raising=True)
    monkeypatch.setattr(mcts_mod.MCTS, "_backpropagate", lambda self, node, result, root_player: None, raising=True)

    m = mcts_mod.MCTS(iterations=1)

    move = m.search(game)

    assert move == ("drop", 0)


def test_expand_creates_child(monkeypatch):
    mcts_mod = importlib.import_module("src.mcts.mcts")

    class DummyNode:
        def __init__(self, **kwargs):
            self.children = []
            self.untried_moves = kwargs.get("untried_moves", [])
            self.parent = kwargs.get("parent", None)
            self.move = kwargs.get("move", None)
            self.current_player = kwargs.get("current_player", PLAYER1)

    monkeypatch.setattr(mcts_mod, "MCTSNode", DummyNode, raising=True)
    monkeypatch.setattr("random.randrange", lambda n: 0, raising=False)

    m = mcts_mod.MCTS()

    node = DummyNode(untried_moves=[("drop", 0)])
    board = Board()

    child, new_board, new_player = m._expand(node, board, PLAYER1)

    assert child.move == ("drop", 0)
    assert child.parent is node


def test_select_descends_to_best_child(monkeypatch):
    mcts_mod = importlib.import_module("src.mcts.mcts")

    class DummyNode:
        def __init__(self, move=None):
            self.untried_moves = []
            self.children = []
            self.move = move

        def best_child(self, exploration):
            return self.children[0]

    monkeypatch.setattr(mcts_mod, "MCTSNode", DummyNode, raising=True)

    root = DummyNode()
    child = DummyNode(move=("drop", 1))
    root.children.append(child)

    m = mcts_mod.MCTS()
    board = Board()

    selected, new_board, next_player = m._select(root, board.copy(), PLAYER1)

    assert selected is child
    assert next_player == PLAYER2


def test_is_terminal_board_variants():
    mcts_mod = importlib.import_module("src.mcts.mcts")
    m = mcts_mod.MCTS()

    # winner case
    board = Board()
    for col in range(4):
        board.drop(col, PLAYER1)
    assert m._is_terminal_board(board, PLAYER1) is True

    # full board case
    board2 = Board()
    for col in range(7):
        for _ in range(6):
            board2.drop(col, PLAYER1)
    assert m._is_terminal_board(board2, PLAYER1) is True

    # no legal moves case (patch get_possible_moves)
    board3 = Board()
    # Use direct assignment to simulate no legal moves
    board3.get_possible_moves = lambda player: []
    assert m._is_terminal_board(board3, PLAYER1) is True

