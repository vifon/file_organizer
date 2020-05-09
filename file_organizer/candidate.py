import re

from .helpers import cached_property


class Candidate:
    """A candidate for a target directory."""

    def __init__(self, root, name, score=None, length_threshold=3):
        self.root = root
        self.name = name
        self.score = score
        self.length_threshold = length_threshold

    @cached_property
    def elements(self):
        """The target name split into elements."""
        return set(filter(self.consider_element, self.split_name()))

    @property
    def ratio(self):
        """A secondary estimate of the target fitness."""
        return self.score / len(self.elements)

    def split_name(self):
        """Split the name into individual elements."""
        return re.findall(r'\w+', self.name)

    def consider_element(self, element):
        """Whether an element should be ignored or not.

        By default let's skip very short words.

        """
        return len(element) >= self.length_threshold

    def score(self):
        """Score the candidate.  Suitable as a sorting key."""
        return (
            -self.score,
            -self.ratio,
            self.name,
        )

    def __key(self):
        return (self.root, self.name, self.score)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return self.__key() == other.__key()

    def __lt__(self, other):
        return self.__key() < other.__key()

    def __repr__(self):
        return '<Candidate "{}">'.format(self.name)
