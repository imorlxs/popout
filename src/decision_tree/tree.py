"""
Decision Tree node structure used by the ID3 algorithm.
"""


class DecisionTreeNode:
    """
    A node in an ID3 decision tree.

    Leaf nodes store a class label.
    Internal nodes store an attribute index (and an optional split threshold
    for continuous attributes), plus a dict mapping attribute values to child
    nodes.
    """

    def __init__(self, attribute=None, threshold=None, label=None):
        """
        Parameters
        ----------
        attribute : int or None
            Index of the feature used for splitting (internal node).
        threshold : float or None
            For continuous attributes, the split threshold (value <= threshold
            goes left; value > threshold goes right).
        label : any or None
            Class label for leaf nodes.
        """
        self.attribute = attribute
        self.threshold = threshold
        self.label = label
        self.children = {}  # {attribute_value: DecisionTreeNode}

    @property
    def is_leaf(self) -> bool:
        return self.label is not None

    def add_child(self, value, node: "DecisionTreeNode"):
        self.children[value] = node

    # ------------------------------------------------------------------
    # Pretty-print helpers
    # ------------------------------------------------------------------
    def _to_str(self, indent: int = 0, feature_names: list = None) -> str:
        pad = "  " * indent
        if self.is_leaf:
            return f"{pad}→ {self.label}\n"

        if feature_names and self.attribute < len(feature_names):
            attr_name = feature_names[self.attribute]
        else:
            attr_name = f"feature[{self.attribute}]"

        if self.threshold is not None:
            lines = [f"{pad}[{attr_name} <= {self.threshold:.4f}?]\n"]
        else:
            lines = [f"{pad}[{attr_name}]\n"]

        for value, child in sorted(self.children.items(), key=lambda x: str(x[0])):
            if self.threshold is not None:
                branch_label = "Yes" if value else "No"
            else:
                branch_label = str(value)
            lines.append(f"{pad}  {branch_label}:\n")
            lines.append(child._to_str(indent + 2, feature_names))

        return "".join(lines)

    def display(self, feature_names: list = None):
        """Print the tree to stdout."""
        print(self._to_str(feature_names=feature_names))

    def __repr__(self) -> str:
        if self.is_leaf:
            return f"Leaf({self.label!r})"
        return f"Node(attr={self.attribute}, threshold={self.threshold}, children={list(self.children.keys())})"
