from itertools import groupby
import sys

from . import file_organizer


class InteractiveFileOrganizer(file_organizer.FileOrganizer):
    """A FileOrganizer variant that interactively asks the user about candidates."""

    def perform_actions(self):
        self.queue = []
        self.accept_all = False
        super().perform_actions()
        if not self.queue:
            return
        print("\n\nQueued actions:")

        def grouped_actions():
            """Group the actions queue by target directory."""
            def key(x):
                action, candidate = x
                return candidate
            return groupby(sorted(self.queue, key=key), key=key)

        for candidate, group in grouped_actions(self.queue):
            print()
            for action, _ in group:
                print('-', action.source)
            print('->', candidate.name)
        while True:
            choice = input('\nPerform? [ (Y)es/(n)o ] ').lower()
            if choice in {'y', 'n', 'q', ''}:
                break
        if choice in {'y'}:
            for candidate, group in grouped_actions(self.queue):
                for action, _ in group:
                    print(
                        'Moving "{}"... '.format(action.source),
                        end="",
                        flush=True,
                    )
                    if super().execute_action(action, candidate):
                        print("DONE!")
                    else:
                        print("ERROR!")


    def consider_action(self, action):
        if not self.accept_all:
            print("\nCurrent file:", action.source)
        return super().consider_action(action)

    def execute_action(self, action, candidate):
        while True:
            if self.accept_all:
                choice = 'y'
            else:
                print("Proposed target:", candidate.name)
                choice = input(
                    'Move? (score: {score}, ratio: {ratio:.2f}) '
                    '[ (y)es/(s)kip/(N)o/(a)ll ] '.format(
                        score=candidate.score,
                        ratio=candidate.ratio,
                    )
                ).lower()
            if choice in {'y'}:
                self.queue.append((action, candidate))
                return True
            elif choice in {'s'}:
                return True
            elif choice in {'n', ''}:
                return False
            elif choice in {'a'}:
                self.accept_all = True
            elif choice in {'q'}:
                sys.exit(0)
            else:
                print("Unknown choice:", choice)
