import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path

import logsummary
import make_sample


def lines(text):
    return text.splitlines(keepends=True)


class ParseTests(unittest.TestCase):
    def test_readable_line(self):
        self.assertEqual(
            logsummary.parse("2026-10-15 09:12:03 ERROR Disk almost full"),
            ("2026-10-15 09:12:03", "ERROR", "Disk almost full"),
        )

    def test_level_without_message_is_readable(self):
        self.assertEqual(logsummary.parse("2026-10-15 09:12:03 INFO")[1:], ("INFO", ""))

    def test_lowercase_level_is_not_readable(self):
        self.assertIsNone(logsummary.parse("2026-10-15 09:12:03 error Disk almost full"))

    def test_impossible_date_is_not_readable(self):
        self.assertIsNone(logsummary.parse("2026-02-30 09:12:03 INFO Hello"))
        self.assertIsNone(logsummary.parse("2026-10-15 25:00:00 INFO Hello"))

    def test_short_and_odd_lines_are_not_readable(self):
        for text in ("", "hello", "2026-10-15 09:12:03", "error: connection lost"):
            self.assertIsNone(logsummary.parse(text), text)


class SummariseTests(unittest.TestCase):
    def test_counts_levels_and_ignores_blank_lines(self):
        total, levels, _, _, bad = logsummary.summarise(lines(
            "2026-10-15 09:00:00 INFO a\n\n   \n2026-10-15 09:00:01 INFO b\n2026-10-15 09:00:02 WARNING c\n"))
        self.assertEqual((total, levels["INFO"], levels["WARNING"], bad), (3, 2, 1, []))

    def test_errors_grouped_by_hour_include_critical(self):
        _, _, by_hour, _, _ = logsummary.summarise(lines(
            "2026-10-15 09:01:00 ERROR a\n2026-10-15 09:59:59 CRITICAL b\n2026-10-15 10:00:00 ERROR c\n"
            "2026-10-16 09:00:00 ERROR d\n2026-10-15 09:30:00 WARNING e\n"))
        self.assertEqual(dict(by_hour), {"2026-10-15 09:00": 2, "2026-10-15 10:00": 1, "2026-10-16 09:00": 1})

    def test_first_errors_are_limited_and_numbered(self):
        text = "".join(f"2026-10-15 09:00:0{i} ERROR problem {i}\n" for i in range(6))
        _, _, _, first, _ = logsummary.summarise(lines(text))
        self.assertEqual(first, [(1, "problem 0"), (2, "problem 1"), (3, "problem 2")])

    def test_unreadable_lines_are_kept_with_line_numbers(self):
        total, levels, _, _, bad = logsummary.summarise(lines(
            "2026-10-15 09:00:00 INFO a\nnot a log line\n2026-10-15 09:00:01 INFO b\n"))
        self.assertEqual((total, sum(levels.values()), bad), (3, 2, [(2, "not a log line")]))

    def test_windows_line_endings(self):
        total, levels, _, _, bad = logsummary.summarise(lines("2026-10-15 09:00:00 ERROR a\r\n2026-10-15 09:00:01 INFO b\r\n"))
        self.assertEqual((total, levels["ERROR"], bad), (2, 1, []))


class MainTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def run_main(self, args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = logsummary.main(["logsummary.py"] + args)
        return code, buf.getvalue()

    def test_sample_log_summary(self):
        path = make_sample.make(self.dir)
        code, out = self.run_main([str(path)])
        self.assertEqual(code, 0)
        for expected in ("Lines with text: 12", "ERROR    3", "CRITICAL 1", "Unreadable lines: 2",
                         "2026-10-15 09:00  2", "2026-10-15 10:00  2", "line 8: 'error: connection lost'"):
            self.assertIn(expected, out)

    def test_empty_file(self):
        path = self.dir / "empty.log"
        path.write_text("")
        code, out = self.run_main([str(path)])
        self.assertEqual(code, 0)
        self.assertIn("Lines with text: 0", out)
        self.assertNotIn("Errors per hour", out)

    def test_missing_file_and_folder_and_no_argument(self):
        self.assertEqual(self.run_main([str(self.dir / "nothing.log")])[0], 2)
        self.assertEqual(self.run_main([str(self.dir)])[0], 2)
        self.assertEqual(self.run_main([])[0], 2)

    def test_bytes_that_are_not_text_do_not_crash(self):
        path = self.dir / "odd.log"
        path.write_bytes(b"2026-10-15 09:00:00 ERROR caf\xe9 broke\n\xff\xfe\n")
        code, out = self.run_main([str(path)])
        self.assertEqual(code, 0)
        self.assertIn("ERROR    1", out)
        self.assertIn("Unreadable lines: 1", out)

    def test_file_not_changed(self):
        path = make_sample.make(self.dir)
        before = (path.read_bytes(), os.stat(path).st_mtime_ns)
        self.run_main([str(path)])
        self.assertEqual((path.read_bytes(), os.stat(path).st_mtime_ns), before)


if __name__ == "__main__":
    unittest.main()
