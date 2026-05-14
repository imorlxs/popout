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
