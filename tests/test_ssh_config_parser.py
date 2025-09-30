import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
APP_DIR = PROJECT_ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from app.ssh_config_parser import SSHConfigParser  # noqa: E402


class SSHConfigParserFilteringTests(unittest.TestCase):
    def _make_config(self, content: str) -> Path:
        temp = tempfile.NamedTemporaryFile("w", delete=False)
        temp.write(content)
        temp.flush()
        temp.close()
        self.addCleanup(lambda: Path(temp.name).unlink(missing_ok=True))
        return Path(temp.name)

    def test_pattern_hosts_are_excluded_from_results(self):
        config_content = """
Host *
  User default

Host web-*
  User deploy

Host app-production
  HostName prod.example.com

Host db01 db02
  HostName db.internal
"""
        config_path = self._make_config(config_content)

        parser = SSHConfigParser(str(config_path))
        hosts = parser.get_hosts_with_prefix("")

        self.assertIn("app-production", hosts)
        self.assertIn("db01", hosts)
        self.assertIn("db02", hosts)
        self.assertNotIn("*", hosts)
        self.assertNotIn("web-*", hosts)

        all_hosts = parser.get_all_hosts()
        self.assertEqual(sorted(hosts), sorted(all_hosts))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
