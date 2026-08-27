#!/usr/bin/env python3
"""
Randomly select a question type for an MCQ probe trial.

Usage:
    python select_question_type.py [--exclude type1,type2,...]

Output: 'mcq', 'msq', or 'ordering' on stdout
Exit: 0 on success, 1 on error

Pass type names to exclude from the draw (e.g. to keep a non-procedural
concept from ever drawing 'ordering'). An unknown type name is an error.
Excluding every type is an error.
"""

import argparse
import random
import sys

TYPES = ["mcq", "msq", "ordering"]


def select(exclude):
    excluded_set = set(exclude)
    available = [t for t in TYPES if t not in excluded_set]

    if not available:
        print("error: no question types available", file=sys.stderr)
        sys.exit(1)

    return random.choice(available)


def main():
    parser = argparse.ArgumentParser(
        description="Select a question type for an MCQ probe trial."
    )
    parser.add_argument(
        "--exclude",
        type=str,
        default="",
        help="Comma-delimited list of type names to exclude from the draw.",
    )
    args = parser.parse_args()

    exclude = []
    if args.exclude:
        exclude = [t.strip().lower() for t in args.exclude.split(",") if t.strip()]

    valid = set(TYPES)
    for name in exclude:
        if name not in valid:
            print(f"error: unknown type '{name}'", file=sys.stderr)
            sys.exit(1)

    print(select(exclude))
    return 0


if __name__ == "__main__":
    sys.exit(main())
