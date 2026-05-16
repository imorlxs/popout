# =================================
#             IMPORTS
# =================================

import contextlib
import io
import random

from src.game.board import Board, PLAYER1, PLAYER2
from src.game.player import (
    MCTSPlayer,
    MCTSPlayerV2,
    MCTSPlayerV3,
    MCTSPlayerV4,
    MCTSPlayerV5,
    MCTSPlayerV6,
    DecisionTreePlayer,
)
from src.game.decision_tree_player import PopOutID3

# =================================
#         SILENT GAME RUNNER
# =================================

_SUPPRESS = contextlib.redirect_stdout(io.StringIO())


def _play_one_game(player1, player2, max_moves=300):
    """Play one game silently. Returns PLAYER1, PLAYER2, or 0 (draw)."""

    board = Board()
    current, other = player1, player2
    state_counts = {}

    def _record(turn):
        key = (board.to_tuple(), turn)
        state_counts[key] = state_counts.get(key, 0) + 1
        return key

    _record(current.player_id)

    for _ in range(max_moves):

        winner = board.get_winner()
        if winner:
            return winner

        moves = board.get_possible_moves(current.player_id)
        if not moves:
            return 0

        key = (board.to_tuple(), current.player_id)
        if state_counts.get(key, 0) >= 3 and current.wants_to_claim_draw(board):
            return 0

        with contextlib.redirect_stdout(io.StringIO()):
            move_type, col = current.get_move(board)

        if move_type == "draw":
            return 0
        elif move_type == "drop":
            board.drop(col, current.player_id)
        elif move_type == "pop":
            board.pop(col, current.player_id)

        current, other = other, current
        _record(current.player_id)

    return board.get_winner()


# =================================
#         MATCH RUNNER
# =================================


def play_match(player1, player2, num_games=20):
    """
    Play num_games between two already-constructed players.
    Returns dict with p1_wins, draws, p2_wins, p1_winrate.
    Players are reused across games (important for V2 tree reuse).
    """
    w1 = w2 = draws = 0

    for i in range(num_games):
        result = _play_one_game(player1, player2)
        if result == PLAYER1:
            w1 += 1
        elif result == PLAYER2:
            w2 += 1
        else:
            draws += 1
        label = "P1" if result == PLAYER1 else ("P2" if result == PLAYER2 else "Draw")
        print(f"  Game {i + 1}/{num_games}: {label}", flush=True)

    return {
        "p1_wins": w1,
        "draws": draws,
        "p2_wins": w2,
        "p1_winrate": round(w1 / num_games, 3),
        "p2_winrate": round(w2 / num_games, 3),
    }


# =================================
#       MCTS HEAD-TO-HEAD
# =================================

MCTS_CLASSES = [
    MCTSPlayer,
    MCTSPlayerV2,
    MCTSPlayerV3,
    MCTSPlayerV4,
    MCTSPlayerV5,
    MCTSPlayerV6,
]


def evaluate_mcts(num_games=10, iterations=500):
    """
    Round-robin tournament: every MCTS class plays every other class.
    Each ordered pair (P1, P2) plays num_games, so every pair appears twice
    (once with each class as P1) — this neutralises first-player advantage.

    Returns a dict:
        {
            "matchups":      list of per-matchup dicts (p1_name, p2_name, p1_wins, draws, p2_wins),
            "win_matrix":    {row_class: {col_class: wins_when_row_is_p1_vs_col}},
            "totals":        list of dicts ranked by total wins across all games played,
        }
    """
    names = [c.__name__ for c in MCTS_CLASSES]
    matchups = []
    win_matrix = {name: dict.fromkeys(names, 0) for name in names}
    totals = {name: {"wins": 0, "draws": 0, "losses": 0, "games": 0} for name in names}

    for cls1 in MCTS_CLASSES:
        for cls2 in MCTS_CLASSES:
            if cls1 is cls2:
                continue

            n1, n2 = cls1.__name__, cls2.__name__
            print(f"\n{n1} (P1) vs {n2} (P2)")

            p1 = cls1(PLAYER1, iterations=iterations)
            p2 = cls2(PLAYER2, iterations=iterations)
            res = play_match(p1, p2, num_games)

            matchups.append(
                {
                    "p1_name": n1,
                    "p2_name": n2,
                    "p1_wins": res["p1_wins"],
                    "draws": res["draws"],
                    "p2_wins": res["p2_wins"],
                    "p1_winrate": res["p1_winrate"],
                }
            )

            win_matrix[n1][n2] = res["p1_wins"]

            totals[n1]["wins"] += res["p1_wins"]
            totals[n1]["losses"] += res["p2_wins"]
            totals[n1]["draws"] += res["draws"]
            totals[n1]["games"] += num_games

            totals[n2]["wins"] += res["p2_wins"]
            totals[n2]["losses"] += res["p1_wins"]
            totals[n2]["draws"] += res["draws"]
            totals[n2]["games"] += num_games

    ranking = sorted(
        [
            {"player": n, **t, "winrate": round(t["wins"] / t["games"], 3)}
            for n, t in totals.items()
        ],
        key=lambda r: r["winrate"],
        reverse=True,
    )

    return {
        "matchups": matchups,
        "win_matrix": win_matrix,
        "totals": ranking,
    }


# =================================
#     DECISION TREE ACCURACY
# =================================


def evaluate_tree_accuracy(csv_path="data/dataset.csv", test_ratio=0.2, seed=42):
    """
    Train/test split accuracy for PopOutID3.
    Predicts the full label (e.g. 'drop_3') and measures exact-match accuracy.
    Returns a dict with train_size, test_size, accuracy, and the fitted tree.
    """
    import csv as csv_mod

    with open(csv_path, newline="") as f:
        rows = list(csv_mod.DictReader(f))

    rng = random.Random(seed)
    rng.shuffle(rows)
    split = int(len(rows) * (1 - test_ratio))
    train_rows, test_rows = rows[:split], rows[split:]

    def to_Xy(rows):
        X = [[int(r[f"cell_{i}"]) for i in range(42)] for r in rows]
        y = [f"{r['move_type']}_{r['col']}" for r in rows]
        return X, y

    X_train, y_train = to_Xy(train_rows)
    X_test, y_test = to_Xy(test_rows)

    tree = PopOutID3()
    tree.fit(X_train, y_train)

    correct = sum(tree.predict(x) == y for x, y in zip(X_test, y_test))
    accuracy = round(correct / len(y_test), 3)

    return {
        "train_size": len(X_train),
        "test_size": len(X_test),
        "accuracy": accuracy,
        "tree": tree,
    }


# =================================
#   DECISION TREE PLAYER VS MCTS
# =================================


def evaluate_tree_player(csv_path="data/dataset.csv", num_games=20, iterations=1000):
    """
    Pit DecisionTreePlayer against each MCTS variant.
    Returns a list of result dicts.
    """
    opponents = [
        (MCTSPlayer, "vs V1  (random sim)"),
        (MCTSPlayerV3, "vs V3  (smart sim)"),
        (MCTSPlayerV6, "vs V6  (smart sim + max-wins)"),
    ]

    results = []

    for mcts_cls, label in opponents:
        print(f"\nDecisionTreePlayer {label}")
        dt = DecisionTreePlayer(PLAYER1, csv_path=csv_path)
        mcts = mcts_cls(PLAYER2, iterations=iterations)
        res = play_match(dt, mcts, num_games)
        res["matchup"] = f"DecisionTreePlayer {label}"
        results.append(res)

    return results
