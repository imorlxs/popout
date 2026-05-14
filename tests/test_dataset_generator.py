# =================================
#             IMPORTS
# =================================

import os
from src.game.board import PLAYER1, PLAYER2
from src.game.player import RandomPlayer
from src.game.dataset_generator import simulate_game, generate_dataset

# =================================
#      DATASET GENERATOR TESTS
# =================================


class TestSimulateGame:

    def test_simulate_game_returns_list(self):
        """Test simulate_game returns a list."""
        p1 = RandomPlayer(PLAYER1)
        p2 = RandomPlayer(PLAYER2)
        samples = simulate_game(p1, p2)
        assert isinstance(samples, list)

    def test_simulate_game_returns_samples(self):
        """Test simulate_game returns at least one sample."""
        p1 = RandomPlayer(PLAYER1)
        p2 = RandomPlayer(PLAYER2)
        samples = simulate_game(p1, p2)
        assert len(samples) > 0

    def test_simulate_game_sample_structure(self):
        """Test each sample has correct structure."""
        p1 = RandomPlayer(PLAYER1)
        p2 = RandomPlayer(PLAYER2)
        samples = simulate_game(p1, p2)
        for state, move_type, col in samples:
            assert len(state) == 42
            assert move_type in ("drop", "pop")
            assert 0 <= col <= 6

    def test_simulate_game_state_values(self):
        """Test board state values are valid (0, 1 or 2)."""
        p1 = RandomPlayer(PLAYER1)
        p2 = RandomPlayer(PLAYER2)
        samples = simulate_game(p1, p2)
        for state, _, _ in samples:
            for cell in state:
                assert cell in (0, 1, 2)


class TestGenerateDataset:

    def test_generate_dataset_creates_file(self, tmp_path):
        """Test generate_dataset creates a CSV file."""
        output = str(tmp_path / "test_dataset.csv")
        generate_dataset(num_games=2, output_path=output, iterations=10)
        assert os.path.exists(output)

    def test_generate_dataset_has_header(self, tmp_path):
        """Test generated CSV has correct header."""
        output = str(tmp_path / "test_dataset.csv")
        generate_dataset(num_games=2, output_path=output, iterations=10)
        with open(output) as f:
            header = f.readline().strip().split(",")
        assert header[0] == "cell_0"
        assert header[41] == "cell_41"
        assert header[42] == "move_type"
        assert header[43] == "col"

    def test_generate_dataset_has_rows(self, tmp_path):
        """Test generated CSV has at least one data row."""
        output = str(tmp_path / "test_dataset.csv")
        generate_dataset(num_games=2, output_path=output, iterations=10)
        with open(output) as f:
            lines = f.readlines()
        assert len(lines) > 1
