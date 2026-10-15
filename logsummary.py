"""Summarise a log file: lines per level, and errors per hour. It only reads the file.

Usage:  python logsummary.py FILE
A readable line looks like:  2026-10-15 09:12:03 ERROR Disk almost full
Other lines are counted and the first few are shown, so nothing is silently skipped.
"""
import sys
from collections import Counter
from datetime import datetime

LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
SHOW = 3


def parse(text):
    """Return (timestamp text, level, message) or None if the line is not readable."""
    parts = text.split(" ", 3)
    if len(parts) < 3:
        return None
    stamp = parts[0] + " " + parts[1]
    try:
        datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
    if parts[2] not in LEVELS:
        return None
    return stamp, parts[2], parts[3] if len(parts) > 3 else ""


def summarise(lines):
    levels = Counter()
    errors_by_hour = Counter()
    first_errors = []
    unreadable = []
    total = 0
    for number, line in enumerate(lines, start=1):
        text = line.rstrip("\r\n")
        if not text.strip():
            continue
        total += 1
        found = parse(text)
        if found is None:
            unreadable.append((number, text))
            continue
        stamp, level, message = found
        levels[level] += 1
        if level in ("ERROR", "CRITICAL"):
            errors_by_hour[stamp[:13] + ":00"] += 1
            if len(first_errors) < SHOW:
                first_errors.append((number, message))
    return total, levels, errors_by_hour, first_errors, unreadable


def main(argv):
    if len(argv) != 2:
        print("Usage: python logsummary.py FILE")
        return 2
    try:
        with open(argv[1], encoding="utf-8", errors="replace") as handle:
            total, levels, by_hour, first_errors, unreadable = summarise(handle)
    except OSError as error:
        print(f"Could not read {argv[1]}: {error.strerror}")
        return 2
    print(f"File: {argv[1]}")
    print(f"Lines with text: {total}")
    for level in LEVELS:
        print(f"  {level:<8} {levels[level]}")
    print(f"Unreadable lines: {len(unreadable)}")
    for number, text in unreadable[:SHOW]:
        print(f"  line {number}: {text[:60]!r}")
    if by_hour:
        print("Errors per hour (ERROR and CRITICAL):")
        for hour in sorted(by_hour):
            print(f"  {hour}  {by_hour[hour]}")
    if first_errors:
        print("First errors:")
        for number, message in first_errors:
            print(f"  line {number}: {message[:60]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
