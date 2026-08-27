#!/usr/bin/env python3
"""
Select a single MCQ judgment axis, excluding previously used axes.

Usage:
    python select_mcq_axis.py [--exclude axis1,axis2,...]

Output: one axis name on stdout
Exit: 0 on success, 1 on error

Pass axes in the order they were used. When all 9 axes have been excluded
(N > 9 trials), only the most recently used axis is blocked — the
consecutive-repeat constraint is all that survives.
"""

import argparse
import random
import sys

AXES = [
    "recognition",
    "application",
    "failure-diagnosis",
    "boundary-condition",
    "transfer",
    "time",
    "risk",
    "coupling",
    "observability",
]


def select(exclude_ordered):
    excluded_set = set(exclude_ordered)
    available = [a for a in AXES if a not in excluded_set]

    if not available:
        # All 9 exhausted — relax to only blocking the most recently used axis.
        last_used = exclude_ordered[-1] if exclude_ordered else None
        available = [a for a in AXES if a != last_used]

    if not available:
        print("error: no axes available", file=sys.stderr)
        sys.exit(1)

    return random.choice(available)


def main():
    parser = argparse.ArgumentParser(
        description="Select a non-repeating MCQ judgment axis."
    )
    parser.add_argument(
        "--exclude",
        type=str,
        default="",
        help="Comma-delimited list of axes already used this session, in order used.",
    )
    args = parser.parse_args()

    exclude_ordered = []
    if args.exclude:
        exclude_ordered = [a.strip().lower() for a in args.exclude.split(",") if a.strip()]

    valid = set(AXES)
    for name in exclude_ordered:
        if name not in valid:
            print(f"error: unknown axis '{name}'", file=sys.stderr)
            sys.exit(1)

    print(select(exclude_ordered))
    return 0


if __name__ == "__main__":
    sys.exit(main())
