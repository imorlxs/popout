# =================================
#             IMPORTS
# =================================

import math
from collections import Counter


class DecisionNode:

    def __init__(self, attribute=None, threshold=None, label=None, is_numerical=False):
        self.attribute = attribute
        self.threshold = threshold
        self.label = label
        self.is_numerical = is_numerical
        self.children = {}

    @property
    def is_leaf(self):
        return self.label is not None


class ID3:

    # Decision tree learner using the ID3 algorithm with information gain.
    # Supports both categorical and numerical attributes.
    # Numerical attributes are split with the best binary threshold found by exhaustive search.

    def __init__(
        self,
        numerical_attributes=None,
        attribute_names=None,
        min_samples=10,
        max_depth=10,
    ):
        self.root = None
        self.numerical_attributes = set(numerical_attributes or [])
        self.attribute_names = attribute_names
        self.min_samples = min_samples
        self.max_depth = max_depth

    # =================================
    #         PUBLIC INTERFACE
    # =================================

    def fit(self, X, y):

        # Build the decision tree from training examples X and labels y

        attributes = list(range(len(X[0])))
        self.root = self._build(X, y, attributes, depth=0)

        return self

    def predict(self, x):

        # Predict the class label for a single example

        return self._traverse(self.root, x)

    # =================================
    #          TREE BUILDING
    # =================================

    def _build(self, X, y, attributes, depth):

        if len(y) < self.min_samples or len(set(y)) == 1:
            return DecisionNode(label=self._majority(y))

        if not attributes or (self.max_depth is not None and depth >= self.max_depth):
            return DecisionNode(label=self._majority(y))

        best_attr, best_gain, best_threshold = self._best_split(X, y, attributes)

        if best_gain <= 0:
            return DecisionNode(label=self._majority(y))

        is_numerical = best_attr in self.numerical_attributes

        node = DecisionNode(
            attribute=best_attr,
            threshold=best_threshold,
            is_numerical=is_numerical,
        )

        if is_numerical:

            # Binary split — attribute stays available for further splits at different thresholds

            left_X, left_y, right_X, right_y = self._split_numerical(
                X, y, best_attr, best_threshold
            )

            node.children["<="] = self._build(left_X, left_y, attributes, depth + 1)
            node.children[">"] = self._build(right_X, right_y, attributes, depth + 1)

        else:

            remaining = [a for a in attributes if a != best_attr]

            for val in set(x[best_attr] for x in X):

                subset_X = [X[i] for i, x in enumerate(X) if x[best_attr] == val]
                subset_y = [y[i] for i, x in enumerate(X) if x[best_attr] == val]

                node.children[val] = self._build(
                    subset_X, subset_y, remaining, depth + 1
                )

        return node

    def _best_split(self, X, y, attributes):

        best_attr, best_gain, best_threshold = None, -1, None

        for attr in attributes:

            if attr in self.numerical_attributes:
                gain, threshold = self._numerical_gain(X, y, attr)

            else:
                gain, threshold = self._categorical_gain(X, y, attr), None

            if gain > best_gain:
                best_attr, best_gain, best_threshold = attr, gain, threshold

        return best_attr, best_gain, best_threshold

    # =================================
    #         INFORMATION GAIN
    # =================================

    def _entropy(self, y):

        total = len(y)

        return -sum(
            (c / total) * math.log2(c / total) for c in Counter(y).values() if c > 0
        )

    def _categorical_gain(self, X, y, attr):

        total = len(y)
        weighted = 0.0

        for val in set(x[attr] for x in X):

            subset_y = [y[i] for i, x in enumerate(X) if x[attr] == val]
            weighted += (len(subset_y) / total) * self._entropy(subset_y)

        return self._entropy(y) - weighted

    def _numerical_gain(self, X, y, attr):

        values = sorted(set(x[attr] for x in X))

        if len(values) == 1:
            return 0, None

        base = self._entropy(y)
        total = len(y)
        best_gain, best_threshold = -1, None

        for i in range(len(values) - 1):

            threshold = (values[i] + values[i + 1]) / 2
            left_y = [y[j] for j, x in enumerate(X) if x[attr] <= threshold]
            right_y = [y[j] for j, x in enumerate(X) if x[attr] > threshold]

            weighted = (len(left_y) / total) * self._entropy(left_y) + (
                len(right_y) / total
            ) * self._entropy(right_y)

            gain = base - weighted

            if gain > best_gain:
                best_gain, best_threshold = gain, threshold

        return best_gain, best_threshold

    # =================================
    #          PREDICTION
    # =================================

    def _traverse(self, node, x):

        if node.is_leaf:
            return node.label

        if node.is_numerical:
            key = "<=" if x[node.attribute] <= node.threshold else ">"
            return self._traverse(node.children[key], x)

        val = x[node.attribute]

        if val not in node.children:
            return None

        return self._traverse(node.children[val], x)

    # =================================
    #          HELPERS
    # =================================

    def _majority(self, y):
        return Counter(y).most_common(1)[0][0]

    def _split_numerical(self, X, y, attr, threshold):

        left_X, left_y, right_X, right_y = [], [], [], []

        for i, x in enumerate(X):

            if x[attr] <= threshold:
                left_X.append(x)
                left_y.append(y[i])

            else:
                right_X.append(x)
                right_y.append(y[i])

        return left_X, left_y, right_X, right_y

    # =================================
    #          VISUAL DISPLAY
    # =================================

    def print_tree(self, node=None, prefix="", branch=""):

        if node is None:
            node = self.root

        if node.is_leaf:
            print(f"{prefix}{branch}-> [{node.label}]")
            return
        name = (
            self.attribute_names[node.attribute]
            if self.attribute_names
            else f"attr_{node.attribute}"
        )

        if node.is_numerical:
            print(f"{prefix}{branch}{name} <= {node.threshold:.3f}?")
            self.print_tree(node.children["<="], prefix + "    ", "YES: ")
            self.print_tree(node.children[">"], prefix + "    ", "NO:  ")

        else:
            print(f"{prefix}{branch}{name}?")
            for val, child in node.children.items():
                self.print_tree(child, prefix + "    ", f"={val}: ")


# Two types of Decision trees depending on dataset


# Use this one for the notebook, is the iris csv version
class IrisID3(ID3):
    # ID3 pre-configured for the Iris dataset (4 continuous features, 3 classes)

    def __init__(self):
        super().__init__(
            numerical_attributes=list(range(4)),
            min_samples=2,
            max_depth=10,
        )


class PopOutID3(ID3):
    # ID3 pre-configured for PopOut board states (42 discrete cells: 0, 1, 2)

    def __init__(self):
        super().__init__(
            numerical_attributes=list(range(42)),
            min_samples=5,
            max_depth=15,
        )
