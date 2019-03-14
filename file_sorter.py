"""FileSorter

Automatically sort a bunch of files into fitting directories.

"""

import logging
import os
import re
import shutil
import sys


def cached_property(function):
    from functools import lru_cache
    return property(lru_cache(maxsize=1)(function))


class FileSorterError(Exception):
    """A generic error in a FileSorter object."""
    pass


class Candidate:
    """A candidate for a target directory."""

    def __init__(self, root, name, score=None):
        self.root = root
        self.name = name
        self.score = score

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
        return len(element) > 2


class Action:
    """A source file along with the possible targets."""

    def __init__(self, source, source_root, candidates=None):
        self.source = source
        self.root = source_root
        self.candidates = candidates or []

    def __iter__(self):
        """Loop over the candidates in order defined by self.score."""
        return sorted(
                self.candidates,
                key=self.score,
        )

    def score(self, candidate):
        """Score the candidates.  Suitable as a sorting key."""
        return (
            -candidate.score,
            -candidate.ratio,
            candidate.name,
        )


class FileSorter:
    """Sort a set of files into a set of directories.

    The possible targets are scored by the similarity of the names to
    the source file name.

    """

    def __init__(self, source=None, rules=None):
        """Arguments:

        - source (optional): a default argument for
          self.calculate_actions if omitted
        - rules (optional): a dict with custom rules mapping regexps
          to target absolute paths

        """
        self.source_root = source
        self.rules = rules or {}
        self.actions = []

    def _get_targets(self, target_root):
        """Get all the target directories in a root."""
        targets = os.listdir(target_root)
        for target in targets:
            if os.path.isdir(os.path.join(target_root, target)):
                yield target

    def _get_files(self, source_root):
        """Get all the files to be sorted in a root."""
        files = os.listdir(source_root)
        for file in files:
            if os.path.isfile(os.path.join(source_root, file)):
                yield file

    def calculate_actions(self, target_root, source_root=None):
        """Add a target and source root and rate the candidates.

        May be called multiple times with various roots.

        If source_root is omitted, self.source_root is used instead
        (if passed, error otherwise).

        """
        if source_root is None:
            source_root = self.source_root
        if source_root is None:
            logging.getLogger('FileSorter').error("Source root is not set.")
            raise FileSorterError()

        candidates = []
        for target in self._get_targets(target_root):
            candidates.append(Candidate(
                name=target,
                root=target_root,
            ))

        for file in self._get_files(source_root):
            action = Action(
                source=file,
                source_root=source_root,
            )

            for candidate in candidates:
                score = 0
                for word in candidate.elements:
                    if word.lower() in file.lower():
                        score += 1
                if score > 0:
                    candidate.score = score
                    action.candidates.append(candidate)

            for rule, target in self.rules.items():
                if rule in file:
                    action.candidates.append(Candidate(
                        name=target,
                        root='/',
                        score=9999,
                    ))
            if action.candidates:
                self.actions.append(action)

    def perform_actions(self):
        """Perform the queued actions."""
        for action in self.actions:
            self.consider_action(action)

    def consider_action(self, action):
        """Consider each candidate in the scoring order and move the source.

        By default move to the top rated candidate.  Override
        self.execute_action to change this behavior.

        """
        for candidate in action.candidates:
            if self.execute_action(action, candidate):
                return

    def execute_action(self, action, candidate):
        """Move the source file to the target.

        May be overriden.  If returns True, move to the next source
        file.  If returns False, it'll be called again with the next
        candidate.

        """
        source_path = os.path.join(action.root, action.source)
        target_path = os.path.join(candidate.root, candidate.name)
        logging.getLogger('FileSorter').info(
            'Moving "%s" into "%s"',
            source_path,
            target_path,
        )
        shutil.move(source_path, target_path)
        return True


class InteractiveFileSorter(FileSorter):
    """A FileSorter variant that interactively asks the user about candidates."""

    def consider_action(self, action):
        print("\nCurrent file:", action.source)
        return super().consider_action(action)

    def execute_action(self, action, candidate):
        while True:
            print("Proposed target:", candidate.name)
            choice = input(
                'Move? (score: {score}, ratio: {ratio:.2f}) '
                '[ (y)es/(s)kip/(N)o ] '.format(
                    score=candidate.score,
                    ratio=candidate.ratio,
                )
            ).lower()
            if choice in {'y'}:
                print(
                    'Moving "{}"... '.format(action.source),
                    end="",
                    flush=True,
                )
                ret = super().execute_action(action, candidate)
                print("DONE!")
                return ret
            elif choice in {'s'}:
                return True
            elif choice in {'n', ''}:
                return False
            elif choice in {'q'}:
                sys.exit(0)
            else:
                print("Unknown choice:", choice)
