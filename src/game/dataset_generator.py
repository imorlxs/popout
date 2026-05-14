# =================================
#             IMPORTS
# =================================

import csv
import itertools
import os
from src.game.board import Board, PLAYER1, PLAYER2
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
NUM_GAMES = 200
MCTS_ITERATIONS = 5000

PLAYER_CLASSES = [
    MCTSPlayer,
    MCTSPlayerV2,
    MCTSPlayerV3,
    MCTSPlayerV4,
    MCTSPlayerV5,
    MCTSPlayerV6,
]


def simulate_game(player1, player2):

    # Simulate a full game between two MCTS players.
    # Returns a list of (state, move) pairs from both players movements.

    board = Board()
    current_player = player1
    other_player = player2
    samples = []

    while not board.get_winner() and not board.is_full():

        state = board.to_flat_list()
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

        # Samples from both players
        samples.append((state, move_type, col))

        current_player, other_player = other_player, current_player

    return samples


def generate_dataset(
    num_games=NUM_GAMES, output_path=OUTPUT_PATH, iterations=MCTS_ITERATIONS
):

    # Simulate num_games games and save (state, move_type, col) to CSV.
    # Each game cycles through all MCTS player class combinations so the
    # dataset captures diverse strategies.

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # CSV header: 42 cells (6x7 board) + move_type + col
    header = [f"cell_{i}" for i in range(42)] + ["move_type", "col"]

    total_samples = 0
    # Cycle through every ordered pair of player classes so all matchups and
    # PLAYER1/PLAYER2 role assignments are covered across games.
    pair_cycle = itertools.cycle(itertools.permutations(PLAYER_CLASSES, 2))

    with open(output_path, "w", newline="") as f:

        writer = csv.writer(f)
        writer.writerow(header)

        for game_num in range(1, num_games + 1):

            cls1, cls2 = next(pair_cycle)

            player1 = cls1(PLAYER1, iterations=iterations)
            player2 = cls2(PLAYER2, iterations=iterations)

            print(
                f"Game {game_num}/{num_games}: "
                f"{cls1.__name__} vs {cls2.__name__}..."
            )
            samples = simulate_game(player1, player2)

            for state, move_type, col in samples:

                writer.writerow(state + [move_type, col])
                total_samples += 1

    print(f"\nDataset generated: {total_samples} samples from {num_games} games")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    generate_dataset()
