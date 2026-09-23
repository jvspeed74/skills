#!/usr/bin/env python3
"""
Randomly select a question type for an MCQ probe trial.

Usage:
    python select_question_type.py

Output: 'mcq' or 'msq' on stdout
Exit: 0 on success
"""

import random
import sys

TYPES = ["mcq", "msq"]


def main():
    print(random.choice(TYPES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
