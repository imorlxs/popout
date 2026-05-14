# =================================
#             IMPORTS
# =================================

import math
from src.decision_tree.id3 import ID3
from src.decision_tree.tree import DecisionNode

# =================================
#        DECISION NODE TESTS
# =================================


class TestDecisionNode:

    def test_leaf_node(self):
        """Test a leaf node is correctly identified."""
        node = DecisionNode(label="drop_3")
        assert node.is_leaf is True

    def test_internal_node(self):
        """Test an internal node is not a leaf."""
        node = DecisionNode(attribute=0, threshold=0.5)
        assert node.is_leaf is False

    def test_node_children_empty_by_default(self):
        """Test a new node has no children."""
        node = DecisionNode(attribute=0, threshold=0.5)
        assert node.children == {}


# =================================
#           ID3 TESTS
# =================================


class TestID3Fit:

    def _simple_dataset(self):
        """3 features, 3 classes, linearly separable."""
        X = [
            [0, 0, 0],
            [0, 0, 0],
            [1, 0, 0],
            [1, 0, 0],
            [2, 0, 0],
            [2, 0, 0],
        ]
        y = ["drop_3", "drop_3", "drop_5", "drop_5", "pop_0", "pop_0"]
        return X, y

    def test_fit_returns_self(self):
        """Test fit returns the ID3 instance."""
        X, y = self._simple_dataset()
        tree = ID3(numerical_attributes=[0, 1, 2])
        result = tree.fit(X, y)
        assert result is tree

    def test_fit_builds_root(self):
        """Test fit builds a root node."""
        X, y = self._simple_dataset()
        tree = ID3(numerical_attributes=[0, 1, 2])
        tree.fit(X, y)
        assert tree.root is not None

    def test_fit_root_is_not_leaf(self):
        """Test root is not a leaf for non-trivial dataset."""
        X, y = self._simple_dataset()
        tree = ID3(numerical_attributes=[0, 1, 2], min_samples=1)
        tree.fit(X, y)
        assert tree.root.is_leaf is False


class TestID3Predict:

    def _train_simple(self):
        X = [
            [0, 0, 0],
            [0, 0, 0],
            [1, 0, 0],
            [1, 0, 0],
            [2, 0, 0],
            [2, 0, 0],
        ]
        y = ["drop_3", "drop_3", "drop_5", "drop_5", "pop_0", "pop_0"]
        tree = ID3(numerical_attributes=[0, 1, 2], min_samples=1)
        tree.fit(X, y)
        return tree

    def test_predict_known_class_0(self):
        """Test prediction for value 0."""
        tree = self._train_simple()
        assert tree.predict([0, 0, 0]) == "drop_3"

    def test_predict_known_class_1(self):
        """Test prediction for value 1."""
        tree = self._train_simple()
        assert tree.predict([1, 0, 0]) == "drop_5"

    def test_predict_known_class_2(self):
        """Test prediction for value 2."""
        tree = self._train_simple()
        assert tree.predict([2, 0, 0]) == "pop_0"

    def test_predict_returns_string(self):
        """Test prediction returns a string."""
        tree = self._train_simple()
        result = tree.predict([0, 0, 0])
        assert isinstance(result, str)


class TestID3StoppingCriteria:

    def test_min_samples_creates_leaf(self):
        """Test tree stops when samples < min_samples."""
        X = [[0], [1], [2]]
        y = ["a", "b", "c"]
        tree = ID3(numerical_attributes=[0], min_samples=10)
        tree.fit(X, y)
        assert tree.root.is_leaf is True

    def test_max_depth_creates_leaf(self):
        """Test tree stops at max_depth."""
        X = [[0], [1], [2], [0], [1], [2]]
        y = ["a", "b", "c", "a", "b", "c"]
        tree = ID3(numerical_attributes=[0], min_samples=1, max_depth=0)
        tree.fit(X, y)
        assert tree.root.is_leaf is True

    def test_pure_node_creates_leaf(self):
        """Test tree stops when all labels are the same."""
        X = [[0, 0], [1, 0], [2, 0]]
        y = ["drop_3", "drop_3", "drop_3"]
        tree = ID3(numerical_attributes=[0, 1], min_samples=1)
        tree.fit(X, y)
        assert tree.root.is_leaf is True
        assert tree.root.label == "drop_3"

    def test_zero_gain_creates_leaf(self):
        """Test tree stops when best gain is 0."""
        X = [[0], [0], [0]]
        y = ["a", "b", "a"]
        tree = ID3(numerical_attributes=[0], min_samples=1)
        tree.fit(X, y)
        assert tree.root.is_leaf is True


class TestID3Entropy:

    def test_entropy_pure(self):
        """Test entropy of a pure set is 0."""
        tree = ID3()
        assert tree._entropy(["a", "a", "a"]) == 0.0

    def test_entropy_binary_equal(self):
        """Test entropy of equal binary split is 1.0."""
        tree = ID3()
        assert abs(tree._entropy(["a", "b"]) - 1.0) < 1e-9

    def test_entropy_three_classes(self):
        """Test entropy of three equal classes."""
        tree = ID3()
        result = tree._entropy(["a", "b", "c"])
        assert abs(result - math.log2(3)) < 1e-9


class TestID3NumericalGain:

    def test_numerical_gain_perfect_split(self):
        """Test gain is positive for a perfect split."""
        tree = ID3(numerical_attributes=[0])
        X = [[0], [0], [1], [1]]
        y = ["a", "a", "b", "b"]
        gain, threshold = tree._numerical_gain(X, y, 0)
        assert gain > 0
        assert threshold == 0.5

    def test_numerical_gain_single_value(self):
        """Test gain is 0 when all values are the same."""
        tree = ID3(numerical_attributes=[0])
        X = [[1], [1], [1]]
        y = ["a", "b", "a"]
        gain, threshold = tree._numerical_gain(X, y, 0)
        assert gain == 0
        assert threshold is None


class TestID3PrintTree:

    def test_print_tree_runs_without_error(self, capsys):
        """Test print_tree executes without raising exceptions."""
        X = [[0, 0], [1, 0], [2, 0], [0, 1], [1, 1], [2, 1]]
        y = ["a", "b", "c", "a", "b", "c"]
        tree = ID3(numerical_attributes=[0, 1], min_samples=1)
        tree.fit(X, y)
        tree.print_tree()
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_print_tree_with_attribute_names(self, capsys):
        """Test print_tree uses attribute names when provided."""
        X = [[0], [1], [2], [0], [1], [2]]
        y = ["a", "b", "c", "a", "b", "c"]
        tree = ID3(numerical_attributes=[0], attribute_names=["cell_0"], min_samples=1)
        tree.fit(X, y)
        tree.print_tree()
        captured = capsys.readouterr()
        assert "cell_0" in captured.out
