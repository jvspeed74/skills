#!/usr/bin/env python3
"""
Select the correct-answer position for an MCQ trial, balanced across the batch.

Usage:
    python select_answer_position.py [--assigned A,B,...]

Output: one position label (A, B, C, or D) on stdout
Exit: 0 on success, 1 on error

Pass the positions already assigned to earlier MCQ slots in this batch, in
assignment order. The draw is uniform over the least-used positions, so counts
across a batch's MCQ slots never differ by more than 1 while the order stays
unpredictable. Omit --assigned for the batch's first MCQ slot.

MCQ only. Ordering and Matching have no assignable correct-answer position --
their label-and-shuffle is a within-trial property, already gated by their own
internal-validation checklists. MSQ's correct set is constrained by content
rather than freely assignable and is out of scope here.

Interface note: the two sibling selectors take --exclude, a set of values
forbidden outright. Position assignment is a balancing problem, not an
exclusion problem -- with more than 4 MCQ slots every position must recur --
so this script takes --assigned and balances, rather than naming an argument
--exclude that would not exclude.
"""

import argparse
import sys
import random
from collections import Counter

POSITIONS = ["A", "B", "C", "D"]


def select(assigned):
    counts = Counter(assigned)
    fewest = min(counts.get(p, 0) for p in POSITIONS)
    available = [p for p in POSITIONS if counts.get(p, 0) == fewest]

    if not available:
        print("error: no positions available", file=sys.stderr)
        sys.exit(1)

    return random.choice(available)


def main():
    parser = argparse.ArgumentParser(
        description="Select a batch-balanced correct-answer position for an MCQ trial."
    )
    parser.add_argument(
        "--assigned",
        type=str,
        default="",
        help="Comma-delimited list of positions already assigned to this batch's MCQ slots, in assignment order.",
    )
    args = parser.parse_args()

    assigned = []
    if args.assigned:
        assigned = [p.strip().upper() for p in args.assigned.split(",") if p.strip()]

    valid = set(POSITIONS)
    for name in assigned:
        if name not in valid:
            print(f"error: unknown position '{name}'", file=sys.stderr)
            sys.exit(1)

    print(select(assigned))
    return 0


if __name__ == "__main__":
    sys.exit(main())
