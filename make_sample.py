"""Makes a made-up log called sample/app.log. It holds invented lines only, plus a few lines that are
deliberately badly formed, like a real log that has been edited or cut.

Run: python make_sample.py
"""
import sys
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
    folder = Path(folder)
    folder.mkdir(exist_ok=True)
    path = folder / "app.log"
    path.write_text(LINES, encoding="utf-8", newline="\n")
    return path


if __name__ == "__main__":
    make(Path(__file__).resolve().parent / "sample")
    print("Made sample/app.log")
    sys.exit(0)
