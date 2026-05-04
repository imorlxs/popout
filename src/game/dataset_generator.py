# =================================
#             IMPORTS
# =================================

import csv
import os
from src.game.board import Board, PLAYER1, PLAYER2
from src.game.player import MCTSPlayer

# =================================
#         DATASET GENERATOR
# =================================

OUTPUT_PATH = "data/dataset.csv"
NUM_GAMES = 200
MCTS_ITERATIONS = 100


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

        current_player = other_player
        other_player = current_player

    return samples


def generate_dataset(num_games=NUM_GAMES, output_path=OUTPUT_PATH):

    # Simulate num_games games and save (state, move_type, col) to CSV.

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    player1 = MCTSPlayer(PLAYER1, iterations=MCTS_ITERATIONS)
    player2 = MCTSPlayer(PLAYER2, iterations=MCTS_ITERATIONS)

    # CSV header: 42 cells (6x7 board) + move_type + col
    header = [f"cell_{i}" for i in range(42)] + ["move_type", "col"]

    total_samples = 0

    with open(output_path, "w", newline="") as f:

        writer = csv.writer(f)
        writer.writerow(header)

        for game_num in range(1, num_games + 1):

            print(f"Simulating game {game_num}/{num_games}...")
            samples = simulate_game(player1, player2)

            for state, move_type, col in samples:

                writer.writerow(state + [move_type, col])
                total_samples += 1

    print(f"\nDataset generated: {total_samples} samples from {num_games} games")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    generate_dataset()
