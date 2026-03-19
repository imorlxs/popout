"""
Unit tests for the ID3 decision tree.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from src.decision_tree.id3 import ID3DecisionTree
from src.decision_tree.tree import DecisionTreeNode


class TestEntropy:
    def test_pure_set_entropy_is_zero(self):
        tree = ID3DecisionTree()
        assert tree._entropy(['A', 'A', 'A']) == 0.0

    def test_balanced_binary_entropy_is_one(self):
        tree = ID3DecisionTree()
        assert abs(tree._entropy(['A', 'B']) - 1.0) < 1e-9

    def test_empty_entropy_is_zero(self):
        tree = ID3DecisionTree()
        assert tree._entropy([]) == 0.0


class TestInformationGain:
    def test_perfect_split(self):
        # Attribute 0 perfectly separates classes
        X = [[0], [0], [1], [1]]
        y = ['A', 'A', 'B', 'B']
        tree = ID3DecisionTree()
        base = tree._entropy(y)
        gain = tree._information_gain(X, y, 0, base)
        assert abs(gain - 1.0) < 1e-9

    def test_no_split_gain_is_zero(self):
        # Attribute 0 has the same value for all → no gain
        X = [[0], [0], [0], [0]]
        y = ['A', 'A', 'B', 'B']
        tree = ID3DecisionTree()
        base = tree._entropy(y)
        gain = tree._information_gain(X, y, 0, base)
        assert gain == 0.0


class TestID3FitPredict:
    def _simple_data(self):
        # A trivially separable dataset
        X = [
            [0, 0],
            [0, 1],
            [1, 0],
            [1, 1],
        ]
        y = ['neg', 'neg', 'pos', 'pos']
        return X, y

    def test_fit_and_predict(self):
        X, y = self._simple_data()
        tree = ID3DecisionTree()
        tree.fit(X, y)
        for x, label in zip(X, y):
            assert tree.predict(x) == label

    def test_predict_batch(self):
        X, y = self._simple_data()
        tree = ID3DecisionTree()
        tree.fit(X, y)
        predictions = tree.predict_batch(X)
        assert predictions == y

    def test_accuracy_perfect(self):
        X, y = self._simple_data()
        tree = ID3DecisionTree()
        tree.fit(X, y)
        result = tree.evaluate(X, y)
        assert result['accuracy'] == 1.0

    def test_unfitted_raises(self):
        tree = ID3DecisionTree()
        with pytest.raises(RuntimeError):
            tree.predict([0, 0])

    def test_max_depth(self):
        X, y = self._simple_data()
        tree = ID3DecisionTree(max_depth=1)
        tree.fit(X, y)
        # Should still return a valid prediction
        for x in X:
            pred = tree.predict(x)
            assert pred in ('pos', 'neg')

    def test_single_class(self):
        X = [[0], [1], [2]]
        y = ['A', 'A', 'A']
        tree = ID3DecisionTree()
        tree.fit(X, y)
        assert tree.predict([0]) == 'A'
        assert tree.predict([5]) == 'A'

    def test_all_same_features(self):
        X = [[1, 2], [1, 2], [1, 2]]
        y = ['A', 'B', 'A']
        tree = ID3DecisionTree()
        tree.fit(X, y)
        # Should predict majority class
        assert tree.predict([1, 2]) == 'A'


class TestContinuousFeatures:
    def test_continuous_split(self):
        # x < 2.5 → 'low', x >= 2.5 → 'high'
        X = [[1.0], [2.0], [3.0], [4.0]]
        y = ['low', 'low', 'high', 'high']
        tree = ID3DecisionTree(continuous_features=[0])
        tree.fit(X, y)
        assert tree.predict([1.5]) == 'low'
        assert tree.predict([3.5]) == 'high'

    def test_iris_like_data(self):
        # Simplified iris-like data (4 continuous features)
        X = [
            [5.1, 3.5, 1.4, 0.2],
            [4.9, 3.0, 1.4, 0.2],
            [7.0, 3.2, 4.7, 1.4],
            [6.4, 3.2, 4.5, 1.5],
            [6.3, 3.3, 6.0, 2.5],
            [5.8, 2.7, 5.1, 1.9],
        ]
        y = ['setosa', 'setosa', 'versicolor', 'versicolor', 'virginica', 'virginica']
        tree = ID3DecisionTree(continuous_features=[0, 1, 2, 3])
        tree.fit(X, y)
        result = tree.evaluate(X, y)
        assert result['accuracy'] == 1.0


class TestDecisionTreeNode:
    def test_leaf_node(self):
        node = DecisionTreeNode(label='A')
        assert node.is_leaf is True
        assert node.label == 'A'

    def test_internal_node(self):
        node = DecisionTreeNode(attribute=0)
        assert node.is_leaf is False

    def test_add_child(self):
        parent = DecisionTreeNode(attribute=0)
        child = DecisionTreeNode(label='B')
        parent.add_child('val1', child)
        assert 'val1' in parent.children
        assert parent.children['val1'] is child

    def test_display_does_not_crash(self):
        parent = DecisionTreeNode(attribute=0)
        child = DecisionTreeNode(label='B')
        parent.add_child('val1', child)
        parent.display(feature_names=['feature_0'])
