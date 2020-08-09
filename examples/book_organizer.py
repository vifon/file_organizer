#!/usr/bin/env python3

from file_organizer import InteractiveFileOrganizer
import argparse
import os


SOURCE_ROOTS = [
    os.path.join(os.environ['HOME'], "dl"),
]
TARGET_ROOTS = [
    os.path.join(os.environ['HOME'], "dl/books"),
]

RULES = {
    "Tolkien":
    os.path.join(os.environ['HOME'], "dl/books/others"),
}

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-t',
        '--threshold',
        default=3,
        type=int,
        help="Minimum word length to consider in candidates.",
    )
    args = parser.parse_args()

    organizer = InteractiveFileOrganizer(
        sources=SOURCE_ROOTS,
        rules=RULES,
        length_threshold=args.threshold,
    )
    for target in TARGET_ROOTS:
        organizer.calculate_actions(target)
    organizer.run()


if __name__ == '__main__':
    from sys import argv
    main(argv)
