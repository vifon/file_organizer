import copy
import logging
import os
import shutil

from .action import Action
from .candidate import Candidate


class FileSorterError(Exception):
    """A generic error in a FileSorter object."""
    pass


class FileSorter:
    """Sort a set of files into a set of directories.

    The possible targets are scored by the similarity of the names to
    the source file name.

    """

    def __init__(self, source=None, rules=None, length_threshold=3):
        """Arguments:

        - source (optional): a default argument for
          self.calculate_actions if omitted
        - rules (optional): a dict with custom rules mapping regexps
          to target absolute paths

        """
        self.source_root = source
        self.rules = rules or {}
        self.actions = {}
        self.length_threshold = length_threshold

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
                length_threshold=self.length_threshold,
            ))

        for file in self._get_files(source_root):
            key = os.path.join(source_root, file)
            if key in self.actions:
                action = self.actions[key]
            else:
                action = Action(
                    source=file,
                    source_root=source_root,
                )

            for rule, target in self.rules.items():
                if rule in file:
                    action.candidates.add(Candidate(
                        name=os.path.basename(target),
                        root=os.path.dirname(target),
                        score=9999,
                        length_threshold=self.length_threshold,
                    ))

            for candidate in candidates:
                score = 0
                for word in candidate.elements:
                    if word.lower() in file.lower():
                        score += 1
                if score > 0:
                    c = copy.copy(candidate)
                    c.score = score
                    action.candidates.add(c)

            if action.candidates:
                self.actions[key] = action

    def perform_actions(self):
        """Perform the queued actions."""
        for action in sorted(self.actions.values(), key=lambda x: x.source):
            self.consider_action(action)

    def consider_action(self, action):
        """Consider each candidate in the scoring order and move the source.

        By default move to the top rated candidate.  Override
        self.execute_action to change this behavior.

        """
        for candidate in action:
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