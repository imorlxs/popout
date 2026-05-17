from src.decision_tree.id3 import ID3DecisionTree
from src.decision_tree.tree import DecisionTreeNode


def test_unseen_categorical_value_uses_node_majority_label():
    tree = ID3DecisionTree()
    root = DecisionTreeNode(attribute=0, majority_label="majority")
    root.add_child("minority_branch", DecisionTreeNode(label="minority"))
    root.add_child("majority_branch", DecisionTreeNode(label="majority"))
    tree.root = root

    assert tree.predict(["unseen"]) == "majority"


def test_fit_stores_majority_label_for_unseen_fallback():
    X = [["red"], ["red"], ["blue"]]
    y = ["majority", "majority", "minority"]

    tree = ID3DecisionTree().fit(X, y)

    assert tree.root.majority_label == "majority"
    assert tree.predict(["green"]) == "majority"
