import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import Config  # noqa: E402


class ConfigSecurityTests(unittest.TestCase):
    def test_check_dangerous_command_detects_known_pattern(self):
        result = Config.check_dangerous_command("rm -rf /tmp")
        self.assertTrue(result["is_dangerous"])
        self.assertIn("rm -rf", result["reason"])

    def test_check_dangerous_command_allows_safe_command(self):
        result = Config.check_dangerous_command("echo 'hello world'")
        self.assertFalse(result["is_dangerous"])
        self.assertEqual(result["reason"], "")

    def test_requires_confirmation_catches_sensitive_command(self):
        self.assertTrue(Config.requires_confirmation("sudo systemctl restart nginx"))

    def test_requires_confirmation_allows_regular_command(self):
        self.assertFalse(Config.requires_confirmation("ls -la"))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
