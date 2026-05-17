# =================================
#             IMPORTS
# =================================

import csv
import itertools
import os
import concurrent.futures
import random
from src.game.board import Board
from src.game.player import (
    MCTSPlayer,
    MCTSPlayerV2,
    MCTSPlayerV3,
    MCTSPlayerV4,
    MCTSPlayerV5,
    MCTSPlayerV6,
)

# =================================
#         DATASET GENERATOR
# =================================

OUTPUT_PATH = "data/dataset.csv"
NUM_GAMES = 100
MCTS_ITERATIONS = 5000

PLAYER_CLASSES = [
    MCTSPlayer,
    MCTSPlayerV2,
    MCTSPlayerV3,
    MCTSPlayerV4,
    MCTSPlayerV5,
    MCTSPlayerV6,
]


def _simulate_game_task(cls1_name, cls2_name, iterations):

    # Worker function run in subprocess: import player classes by name
    from src.game.player import PLAYER1, PLAYER2

    mod = __import__("src.game.player", fromlist=[cls1_name, cls2_name])
    cls1 = getattr(mod, cls1_name)
    cls2 = getattr(mod, cls2_name)

    # Seed randomness in worker to reduce identical rollouts
    random.seed()

    player1 = cls1(PLAYER1, iterations=iterations)
    player2 = cls2(PLAYER2, iterations=iterations)

    return simulate_game(player1, player2)


def simulate_game(player1, player2):

    # Simulate a full game between two MCTS players.
    # Returns a list of (state, move) pairs from both players movements.

    board = Board()
    current_player = player1
    other_player = player2
    samples = []

    while not board.get_winner() and not board.is_full():

        state = board.to_flat_list()
        current_id = current_player.player_id
        move = current_player.get_move(board)
        move_type, col = move

        if move_type == "drop":
            success = board.drop(col, current_player.player_id)
        elif move_type == "pop":
            success = board.pop(col, current_player.player_id)
        else:
            break

        if not success:
            break

        # Only save samples from player1's perspective
        # if current_player is player1:
        #     samples.append((state, move_type, col))

        # Samples from both players (include current player id)
        samples.append((state, current_id, move_type, col))

        current_player, other_player = other_player, current_player

    return samples


def generate_dataset(
    num_games=NUM_GAMES, output_path=OUTPUT_PATH, iterations=MCTS_ITERATIONS
):

    # Simulate num_games games and save (state, move_type, col) to CSV.
    # Each game cycles through all MCTS player class combinations so the
    # dataset captures diverse strategies.

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # CSV header: 42 cells (6x7 board) + current_player + move_type + col + label
    header = [f"cell_{i}" for i in range(42)] + [
        "current_player",
        "move_type",
        "col",
        "label",
    ]

    total_samples = 0
    # Use self-play (same class vs same class) to generate dataset from
    # MCTS self-play. Cycle through classes repeatedly.
    pair_cycle = itertools.cycle([(cls, cls) for cls in PLAYER_CLASSES])

    with open(output_path, "w", newline="") as f:

        writer = csv.writer(f)
        writer.writerow(header)

        # Build task list (class names) for each game so workers can import classes
        games = []
        for game_num in range(1, num_games + 1):
            cls1, cls2 = next(pair_cycle)
            games.append((game_num, cls1.__name__, cls2.__name__))

        # Run games in parallel using processes and write results as they arrive
        with concurrent.futures.ProcessPoolExecutor() as executor:

            future_to_meta = {
                executor.submit(_simulate_game_task, c1, c2, iterations): (num, c1, c2)
                for num, c1, c2 in games
            }

            for future in concurrent.futures.as_completed(future_to_meta):

                game_num, c1, c2 = future_to_meta[future]

                try:
                    samples = future.result()
                    print(
                        f"Game {game_num}/{num_games}: {c1} vs {c2}... done ({len(samples)} samples)"
                    )

                    for item in samples:
                        # each item is (state, current_id, move_type, col)
                        state, current_id, move_type, col = item
                        label = f"{move_type}_{col}"
                        writer.writerow(state + [current_id, move_type, col, label])
                        total_samples += 1

                except Exception as e:
                    print(f"Game {game_num} ({c1} vs {c2}) failed: {e}")

    print(f"\nDataset generated: {total_samples} samples from {num_games} games")
    print(f"Saved to: {output_path}")


def load_iris(filepath: str) -> tuple:
    """
    Load the Iris CSV dataset.

    Expected columns (in order):
      sepal_length, sepal_width, petal_length, petal_width, class

    Returns
    -------
    X : list of lists (float values)
    y : list of str (class labels)
    feature_names : list of str
    """
    X, y = [], []
    feature_names = ["sepal_length", "sepal_width", "petal_length", "petal_width"]

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 5:
                continue

            # Handle files that include an index column (6 cols: idx, sepal, sw, pl, pw, class)
            if len(parts) >= 6:
                # try parse columns 1..4 as floats and last as label
                try:
                    values = [float(p) for p in parts[1:5]]
                    label = parts[5]
                except ValueError:
                    # skip header/malformed
                    continue
            else:
                # standard format: sepal_length,sepal_width,petal_length,petal_width,class
                try:
                    values = [float(p) for p in parts[:4]]
                    label = parts[4]
                except ValueError:
                    continue

            X.append(values)
            y.append(label)

    return X, y, feature_names


def load_popout(filepath: str) -> tuple:
    """
    Load a PopOut dataset CSV produced by `generate_dataset()`.

    Expects a header with columns:
    cell_0..cell_41, current_player, label

    Returns
    -------
    X : list of lists (numeric features) -- 42 board cells followed by current_player
    y : list of str (labels in the form 'move_type_col', e.g. 'drop_3')
    feature_names : list of str
    """

    X, y = [], []
    cell_cols = [f"cell_{i}" for i in range(42)]
    feature_names = cell_cols + ["current_player"]

    with open(filepath, "r", newline="") as f:
        reader = csv.DictReader(f)

        # Validate header presence
        cols = reader.fieldnames or []

        has_cells = all(c in cols for c in cell_cols)
        if not has_cells:
            raise ValueError(f"Missing board cell columns in {filepath}")

        has_current = "current_player" in cols

        for row in reader:
            try:
                cells = [int(row[c]) for c in cell_cols]
            except Exception:
                # skip malformed rows
                continue

            if has_current:
                try:
                    cur = int(row["current_player"])
                except Exception:
                    cur = 0
            else:
                cur = 0

            # determine label: prefer explicit 'label' column, otherwise combine move_type+col
            label = None
            if "label" in cols and row.get("label"):
                label = row.get("label")

            if label is None:
                continue

            X.append(cells + [cur])
            y.append(label)

    return X, y, feature_names


if __name__ == "__main__":
    generate_dataset()
