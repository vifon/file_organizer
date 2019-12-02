from .candidate import Candidate


class Action:
    """A source file along with the possible targets."""

    def __init__(self, source, source_root, candidates=None):
        self.source = source
        self.root = source_root
        self.candidates = candidates or set()

    def __iter__(self):
        """Loop over the candidates in order defined by self.score."""
        return iter(sorted(
            self.candidates,
            key=Candidate.score,
        ))
