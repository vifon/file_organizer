import copy
import logging
import os
import shutil
from itertools import groupby

from .action import Action
from .candidate import Candidate


class FileOrganizerError(Exception):
    """A generic error in a FileOrganizer object."""

    pass


class FileOrganizer:
    """Sort a set of files into a set of directories.

    The possible targets are scored by the similarity of the names to
    the source file name.

    """

    def __init__(self, sources=None, rules=None, length_threshold=3):
        """Arguments:

        - source (optional): a default argument for
          self.calculate_actions if omitted
        - rules (optional): a dict with custom rules mapping regexps
          to target absolute paths

        """
        self.source_roots = sources
        self.rules = rules or {}
        self.actions = {}
        self.length_threshold = length_threshold
        self.queue = []

    def get_targets(self, target_root):
        """Get all the target directories in a root."""
        targets = os.listdir(target_root)
        for target in targets:
            if os.path.isdir(os.path.join(target_root, target)):
                yield target

    def get_files(self, source_root):
        """Get all the files to be sorted in a root."""
        for dirpath, _, filenames in os.walk(source_root):
            for filename in filenames:
                yield os.path.join(dirpath, filename)

    def calculate_actions(self, target_root, source_roots=None):
        """Add a target and source root and rate the candidates.

        May be called multiple times with various roots.

        If source_roots is omitted, self.source_roots is used instead
        (if passed, error otherwise).

        """
        if source_roots is None:
            source_roots = self.source_roots
        if source_roots is None:
            logging.getLogger("FileOrganizer").error("Source root is not set.")
            raise FileOrganizerError()

        candidates = []
        for target in self.get_targets(target_root):
            candidates.append(
                Candidate(
                    name=target,
                    root=target_root,
                    length_threshold=self.length_threshold,
                )
            )

        for source_root in source_roots:
            for filepath in self.get_files(source_root):
                relpath = os.path.relpath(filepath, source_root)
                key = filepath
                if key in self.actions:
                    action = self.actions[key]
                else:
                    action = Action(
                        source=relpath,
                        source_root=source_root,
                    )

                for rule, target in self.rules.items():
                    if rule in relpath:
                        action.candidates.add(
                            Candidate(
                                name=os.path.basename(target),
                                root=os.path.dirname(target),
                                score=9999,
                                length_threshold=self.length_threshold,
                            )
                        )

                for candidate in candidates:
                    score = 0
                    for word in candidate.elements:
                        if word.lower() in relpath.lower():
                            score += 1
                    if score > 0:
                        c = copy.copy(candidate)
                        c.score = score
                        action.candidates.add(c)

                if action.candidates:
                    self.actions[key] = action

    def run(self):
        self.choose_actions()
        self.execute_actions()
        self.cleanup_actions()

    def choose_actions(self):
        """Choose the best candidates for actions and enqueue them."""
        for action in sorted(self.actions.values(), key=lambda x: x.source):
            self.consider_action(action)

    def consider_action(self, action):
        """Consider each candidate in the scoring order and enqueue actions.

        By default move to the top rated candidate.  Override
        self.enqueue_action to change this behavior.

        """
        for candidate in action:
            if self.enqueue_action(action, candidate):
                return

    def enqueue_action(self, action, candidate):
        """Enqueue the source file for moving to the target.

        May be overriden.  If returns True, move on to the next source
        file.  If returns False, it'll be called again with the next
        candidate.

        """
        self.queue.append((action, candidate))
        return True

    def grouped_queue(self):
        """Group the actions queue by target directory."""

        def key(x):
            action, candidate = x
            return candidate

        return groupby(sorted(self.queue, key=key), key=key)

    def cleanup_actions(self):
        """Perform cleanup operations, such as removing empty directories."""

        def key(x):
            action, candidate = x
            return os.path.dirname(action.source)

        for parent, actions in groupby(sorted(self.queue, key=key), key=key):
            if parent == "":
                continue
            root = next(actions)[0].root
            try:
                cwd = os.getcwd()
                os.chdir(root)
                os.removedirs(parent)
            except OSError:
                # The directory is not empty, no big deal.
                pass
            finally:
                os.chdir(cwd)

    def execute_actions(self):
        """Execute the queued actions grouped by the target directory."""
        for candidate, group in self.grouped_queue():
            self.execute_action_group(candidate, group)

    def execute_action_group(self, candidate, group):
        """Execute a group of actions scheduled to the same target."""
        target_path = os.path.join(candidate.root, candidate.name)
        source_paths = []
        for action, _ in group:
            source_path = os.path.join(action.root, action.source)
            source_paths.append(source_path)
            logging.getLogger("FileOrganizer").info(
                'Moving "%s" into "%s"',
                source_path,
                target_path,
            )
        self.move_group(source_paths, target_path)

    def move_group(self, srcs, dst):
        """Move all the files scheduled to the same target.

        Override this method and ignore move_single() to implement
        batch moving.

        """
        for src in srcs:
            self.move_single(src, dst)

    def move_single(self, src, dst):
        """Move each individual file.

        Override this method to implement custom moving logic (for
        example using rsync).

        """
        shutil.move(src, dst)
