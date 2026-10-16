# Summarise a log file

A small read-only Python tool built step by step. Give it a text log and it counts lines per level (DEBUG, INFO, WARNING, ERROR, CRITICAL), counts errors per hour, shows the first few errors, and lists lines it could not read. It only reads the file.

## Run it

    python make_sample.py                     # makes a made-up log in sample/
    python logsummary.py sample/app.log       # summary of that log
    python -m unittest -v                     # 20 temporary-fixture tests

On Windows, if `python` is not found, use `py`.

## Files

- `logsummary.py` - the tool
- `make_sample.py` - makes a made-up log, including a few badly formed lines on purpose
- `test_logsummary.py` - tests

## Setup safety and evidence

Setup refuses any existing sample path and exclusively creates a fictional app.log inside a new folder. It never resets old data. Start in a new empty lesson folder. Four new setup collision/repeat tests compare nested unrelated bytes and modification times. The checker is unchanged. It can follow a source file link; reports reveal excerpts and paths. Invalid UTF-8 bytes are replaced during decoding, not validated. Keep private output private.

Two Windows and two Ubuntu recordings pass all 20 tests. Paired outputs differ only in unittest time and the unique temporary path in the intentionally failing first-version traceback. Displays use first Windows output; versions and test-name rendering can differ. The recorder saves the exact visible first/final file versions inside a unique temporary folder and removes only that recording folder. Setup itself refuses a second run.

## Notes

- It expects lines like `2026-10-15 09:12:03 ERROR Disk almost full`: a date, a time, an upper-case level, then a message. Any other line is counted as unreadable. The first three are shown and the rest are reported as a number. That includes lower-case levels and impossible dates. A real log may use a different format, and then most lines would be unreadable.
- The hour in "Errors per hour" is the hour written in the log. No time zones are handled.
- The counts are only as good as the log. A summary does not tell you why something failed.
- Python documentation used: collections.Counter (https://docs.python.org/3/library/collections.html) and datetime.strptime (https://docs.python.org/3/library/datetime.html).
- Tested only on a small made-up log and small test files, not on real or very large logs. Python 3.10 (Linux) and, by GitHub Actions, Python 3.12 on Windows and Ubuntu. Not tested on a Windows 10 or 11 desktop.
- Educational example, no warranty. Use at your own risk.
- Code is MIT licensed (see LICENSE). Python is a separate project with its own license; this repository does not include it.
