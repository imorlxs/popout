"""
ID3 Decision Tree implementation.

Supports:
  - Categorical and continuous (numerical) attributes.
  - Entropy-based information gain as the splitting criterion.
  - Automatic discretisation of continuous features (finds optimal threshold
    that maximises information gain).
  - Pruning via a max_depth parameter.

Note: scikit-learn is NOT used here per assignment requirements.
"""

import math
from collections import Counter

from .tree import DecisionTreeNode


class ID3DecisionTree:
    """
    Decision Tree learned with the ID3 (Information Gain) procedure.

    Parameters
    ----------
    max_depth : int or None
        Maximum depth of the tree. None = no limit.
    min_samples_split : int
        Minimum number of samples required to split an internal node.
    continuous_features : list[int] or None
        Indices of features that are continuous (numerical). For these,
        the best binary threshold is searched automatically.
        If None, all features are treated as categorical.
    feature_names : list[str] or None
        Optional names for features (used for display).
    """

    def __init__(self, max_depth=None, min_samples_split: int = 2,
                 continuous_features=None, feature_names=None):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.continuous_features = set(continuous_features) if continuous_features else set()
        self.feature_names = feature_names
        self.root = None

    # ------------------------------------------------------------------
    # Fitting
    # ------------------------------------------------------------------
    def fit(self, X: list, y: list):
        """
        Build the decision tree from training data.

        Parameters
        ----------
        X : list of lists
            Feature matrix (n_samples × n_features).
        y : list
            Target labels (n_samples,).
        """
        if not X or not y:
            raise ValueError("Training data cannot be empty.")
        n_features = len(X[0])
        available_attributes = list(range(n_features))
        self.root = self._build(X, y, available_attributes, depth=0)
        return self

    def _build(self, X, y, attributes, depth):
        # All labels the same → leaf
        label_counts = Counter(y)
        if len(label_counts) == 1:
            return DecisionTreeNode(label=y[0])

        # No attributes left or max depth reached → majority leaf
        if not attributes or (self.max_depth is not None and depth >= self.max_depth):
            return DecisionTreeNode(label=label_counts.most_common(1)[0][0])

        # Too few samples → majority leaf
        if len(X) < self.min_samples_split:
            return DecisionTreeNode(label=label_counts.most_common(1)[0][0])

        # Select best attribute
        best_attr, best_threshold, best_gain = self._best_split(X, y, attributes)

        if best_gain <= 0:
            return DecisionTreeNode(label=label_counts.most_common(1)[0][0])

        node = DecisionTreeNode(attribute=best_attr, threshold=best_threshold)

        if best_threshold is not None:
            # Binary split for continuous attribute
            left_X, left_y, right_X, right_y = self._split_continuous(
                X, y, best_attr, best_threshold
            )
            remaining = [a for a in attributes if a != best_attr]

            for branch_value, sub_X, sub_y in [(True, left_X, left_y),
                                                (False, right_X, right_y)]:
                if not sub_X:
                    child = DecisionTreeNode(
                        label=label_counts.most_common(1)[0][0]
                    )
                else:
                    child = self._build(sub_X, sub_y, remaining, depth + 1)
                node.add_child(branch_value, child)
        else:
            # Categorical attribute
            values = set(row[best_attr] for row in X)
            remaining = [a for a in attributes if a != best_attr]
            for value in values:
                sub_X = [row for row in X if row[best_attr] == value]
                sub_y = [y[i] for i, row in enumerate(X) if row[best_attr] == value]
                if not sub_X:
                    child = DecisionTreeNode(
                        label=label_counts.most_common(1)[0][0]
                    )
                else:
                    child = self._build(sub_X, sub_y, remaining, depth + 1)
                node.add_child(value, child)

        return node

    # ------------------------------------------------------------------
    # Best attribute selection
    # ------------------------------------------------------------------
    def _best_split(self, X, y, attributes):
        """Return (best_attr, best_threshold, best_gain)."""
        base_entropy = self._entropy(y)
        best_attr = None
        best_threshold = None
        best_gain = -1

        for attr in attributes:
            if attr in self.continuous_features:
                threshold, gain = self._best_continuous_split(X, y, attr, base_entropy)
            else:
                threshold = None
                gain = self._information_gain(X, y, attr, base_entropy)

            if gain > best_gain:
                best_gain = gain
                best_attr = attr
                best_threshold = threshold

        return best_attr, best_threshold, best_gain

    def _best_continuous_split(self, X, y, attr, base_entropy):
        """Find the threshold for a continuous attribute that maximises IG."""
        values = sorted(set(row[attr] for row in X))
        best_threshold = None
        best_gain = -1

        # Candidate thresholds: midpoints between consecutive unique values
        thresholds = [(values[i] + values[i + 1]) / 2.0
                      for i in range(len(values) - 1)]

        for threshold in thresholds:
            left_y = [y[i] for i, row in enumerate(X) if row[attr] <= threshold]
            right_y = [y[i] for i, row in enumerate(X) if row[attr] > threshold]
            if not left_y or not right_y:
                continue
            n = len(y)
            gain = base_entropy - (
                len(left_y) / n * self._entropy(left_y) +
                len(right_y) / n * self._entropy(right_y)
            )
            if gain > best_gain:
                best_gain = gain
                best_threshold = threshold

        return best_threshold, best_gain

    def _information_gain(self, X, y, attr, base_entropy) -> float:
        """Compute information gain for a categorical attribute."""
        n = len(y)
        values = set(row[attr] for row in X)
        weighted_entropy = 0.0
        for value in values:
            subset_y = [y[i] for i, row in enumerate(X) if row[attr] == value]
            if subset_y:
                weighted_entropy += len(subset_y) / n * self._entropy(subset_y)
        return base_entropy - weighted_entropy

    # ------------------------------------------------------------------
    # Entropy
    # ------------------------------------------------------------------
    @staticmethod
    def _entropy(y) -> float:
        """Compute Shannon entropy of label list y."""
        n = len(y)
        if n == 0:
            return 0.0
        counts = Counter(y)
        entropy = 0.0
        for count in counts.values():
            p = count / n
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy

    # ------------------------------------------------------------------
    # Continuous split helper
    # ------------------------------------------------------------------
    @staticmethod
    def _split_continuous(X, y, attr, threshold):
        left_X, left_y, right_X, right_y = [], [], [], []
        for i, row in enumerate(X):
            if row[attr] <= threshold:
                left_X.append(row)
                left_y.append(y[i])
            else:
                right_X.append(row)
                right_y.append(y[i])
        return left_X, left_y, right_X, right_y

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------
    def predict(self, x):
        """
        Predict the class label for a single sample x.

        Parameters
        ----------
        x : list
            Feature vector (must have the same length as training features).

        Returns
        -------
        label : any
            The predicted class label.
        """
        if self.root is None:
            raise RuntimeError("Tree has not been fitted yet. Call fit() first.")
        return self._traverse(self.root, x)

    def predict_batch(self, X: list) -> list:
        """Predict labels for a list of samples."""
        return [self.predict(x) for x in X]

    def _traverse(self, node: DecisionTreeNode, x):
        if node.is_leaf:
            return node.label

        attr = node.attribute
        if node.threshold is not None:
            branch_value = x[attr] <= node.threshold
        else:
            branch_value = x[attr]

        if branch_value not in node.children:
            # Unseen value at prediction time → pick most common child
            if node.children:
                child = next(iter(node.children.values()))
                return self._traverse(child, x)
            return None

        return self._traverse(node.children[branch_value], x)

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------
    def display(self):
        """Print the decision tree structure."""
        if self.root is None:
            print("(empty tree)")
        else:
            self.root.display(feature_names=self.feature_names)

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------
    def evaluate(self, X: list, y: list) -> dict:
        """
        Evaluate accuracy on a test set.

        Returns
        -------
        dict with keys 'accuracy', 'correct', 'total'.
        """
        predictions = self.predict_batch(X)
        correct = sum(p == t for p, t in zip(predictions, y))
        total = len(y)
        return {
            'accuracy': correct / total if total > 0 else 0.0,
            'correct': correct,
            'total': total,
        }