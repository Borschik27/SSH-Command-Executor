import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

# Ensure the application modules are importable when running tests directly
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
APP_DIR = PROJECT_ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from app.command_executor_cli_app import parse_host_range  # noqa: E402


class ParseHostRangeTests(unittest.TestCase):
    def test_single_numbers_are_parsed(self):
        result = parse_host_range("1, 5, 3", hosts_count=10)
        self.assertEqual(result, [1, 3, 5])

    def test_standard_range_is_expanded(self):
        result = parse_host_range("2-4", hosts_count=10)
        self.assertEqual(result, [2, 3, 4])

    def test_reversed_range_is_normalized(self):
        result = parse_host_range("5-3", hosts_count=10)
        self.assertEqual(result, [3, 4, 5])

    def test_invalid_entries_are_ignored_with_message(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            result = parse_host_range("1,foo,0,11,2-abc,3", hosts_count=5)

        # Only valid numbers within range should remain
        self.assertEqual(result, [1, 3])

        output = buffer.getvalue()
        self.assertIn("Invalid host number: foo", output)
        self.assertIn("Invalid range: 2-abc", output)

    def test_duplicates_and_overlaps_are_deduplicated(self):
        result = parse_host_range("1,3-5,2-4,5,3", hosts_count=10)

        # Numbers should be unique and sorted even with overlapping segments
        self.assertEqual(result, [1, 2, 3, 4, 5])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
