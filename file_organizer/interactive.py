import sys

from . import file_organizer


class InteractiveFileOrganizer(file_organizer.FileOrganizer):
    """A FileOrganizer variant that interactively asks the user about candidates."""

    def choose_actions(self):
        self.action_for_all = None
        super().choose_actions()

    def enqueue_action(self, action, candidate):
        if self.action_for_all is None:
            print("\nCurrent file:", action.source)

        while True:
            if self.action_for_all == 'accept':
                choice = 'y'
            elif self.action_for_all == 'skip':
                choice = 's'
            else:
                print("Proposed target:", candidate.name)
                choice = input(
                    'Move? (score: {score}, ratio: {ratio:.2f}) '
                    '[ (y)es/(s)kip/(N)o/(a)ll/s(k)ip all ] '.format(
                        score=candidate.score,
                        ratio=candidate.ratio,
                    )
                ).lower()
            if choice in {'y'}:
                self.queue.append((action, candidate))
                return True
            elif choice in {'s'}:
                return True
            elif choice in {'k'}:
                self.action_for_all = 'skip'
            elif choice in {'n', ''}:
                return False
            elif choice in {'a'}:
                self.action_for_all = 'accept'
            elif choice in {'q'}:
                sys.exit(0)
            else:
                print("Unknown choice:", choice)

    def execute_actions(self):
        if not self.queue:
            return
        print("\n\nQueued actions:")

        for candidate, group in self.grouped_queue():
            print()
            for action, _ in group:
                print('-', action.source)
            print('->', candidate.name)
        while True:
            choice = input('\nPerform? [ (Y)es/(n)o ] ').lower()
            if choice in {'y', 'n', 'q', ''}:
                break
        if choice in {'y'}:
            super().execute_actions()

    def execute_action_group(self, candidate, group):
        # It's needed multiple times, a plain generator won't do.
        group = list(group)
        *source_paths, last_path = [action.source for action, _ in group]

        print("Moving: ")
        for path in source_paths:
            print('  "{}" and…'.format(path))

        print(
            '  "{}"… '.format(last_path),
            end="",
            flush=True,
        )

        try:
            super().execute_action_group(candidate, group)
        except Exception as e:
            print("ERROR!")
            raise e
        else:
            print("DONE!")
