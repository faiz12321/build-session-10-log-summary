"""Makes a made-up log called sample/app.log. It holds invented lines only, plus a few lines that are
deliberately badly formed, like a real log that has been edited or cut.

Run only in a new empty lesson folder: python make_sample.py
Setup refuses any existing sample path and exclusively creates a new fictional log.
"""
import sys
import stat
from pathlib import Path

LINES = """2026-10-15 08:58:10 INFO Server started
2026-10-15 09:01:44 INFO Request /home took 12 ms
2026-10-15 09:12:03 ERROR Disk almost full
2026-10-15 09:12:09 WARNING Retrying upload
2026-10-15 09:40:55 ERROR Upload failed

2026-10-15 10:05:01 INFO Request /about took 9 ms
error: connection lost
2026-10-15 10:07:30 CRITICAL Database not reachable
2026-10-15 10:07:31 ERROR Request /home failed
2026-10-15 10:30:00 DEBUG Cache cleared
2026-02-30 10:31:00 INFO Impossible date
2026-10-15 11:02:12 INFO Server stopped
"""


def make(folder):
    folder = Path(folder).absolute()
    if '..' in folder.parts:
        raise OSError('Parent-traversal paths are unsupported.')
    for parent in reversed(folder.parents):
        info = parent.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise OSError('Linked/reparse-point parents are unsupported.')

    folder.mkdir()
    path = folder / "app.log"
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(LINES)
    return path


if __name__ == "__main__":
    try:
        make(Path(__file__).absolute().parent / "sample")
    except FileExistsError:
        raise SystemExit("Stopped: sample already exists. Nothing was replaced or deleted.")
    print("Made sample/app.log")
    sys.exit(0)
