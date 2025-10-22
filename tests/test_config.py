#!/usr/bin/env python3
"""
Tests for Config module
Validates all settings and configuration values
"""

import sys
import os
import re
import unittest
from pathlib import Path

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from config import Config
from tests.config_test import (
    TEST_CONFIG_CHECKS,
    TEST_EXPECTED_SYMBOLS,
    TEST_EXPECTED_COLORS,
    TEST_DANGEROUS_COMMANDS,
    TEST_SAFE_COMMANDS,
    TEST_CONFIRMATION_COMMANDS,
    TEST_NO_CONFIRMATION_COMMANDS,
)


class TestConfig(unittest.TestCase):
    """Tests for Config class"""

    def test_app_info(self):
        """Check main application information"""
        checks = TEST_CONFIG_CHECKS["app_info"]
        
        # Check application name
        self.assertIsInstance(Config.APP_NAME, str)
        self.assertGreater(len(Config.APP_NAME), 0)
        
        # Check version (must match format X.Y.Z)
        self.assertIsInstance(Config.APP_VERSION, str)
        version_pattern = re.compile(checks["version_format"])
        self.assertIsNotNone(
            version_pattern.match(Config.APP_VERSION),
            f"Version '{Config.APP_VERSION}' doesn't match format {checks['version_format']}"
        )
        
        # Check description
        self.assertIsInstance(Config.APP_DESCRIPTION, str)
        self.assertGreaterEqual(
            len(Config.APP_DESCRIPTION),
            checks["description_min_length"],
            f"Description too short (min {checks['description_min_length']} chars)"
        )
        
        print(f"✓ APP_NAME: {Config.APP_NAME}")
        print(f"✓ APP_VERSION: {Config.APP_VERSION}")

    def test_ssh_settings(self):
        """Check SSH settings"""
        checks = TEST_CONFIG_CHECKS["ssh_settings"]
        
        # Check timeout values
        self.assertIsInstance(Config.SSH_CONNECT_TIMEOUT, int)
        self.assertGreaterEqual(
            Config.SSH_CONNECT_TIMEOUT,
            checks["connect_timeout_min"],
            f"Connect timeout too small (min {checks['connect_timeout_min']}s)"
        )
        
        self.assertIsInstance(Config.SSH_COMMAND_TIMEOUT, int)
        self.assertGreaterEqual(
            Config.SSH_COMMAND_TIMEOUT,
            checks["command_timeout_min"],
            f"Command timeout too small (min {checks['command_timeout_min']}s)"
        )
        
        # Check that command timeout is greater than connect timeout
        self.assertGreater(
            Config.SSH_COMMAND_TIMEOUT,
            Config.SSH_CONNECT_TIMEOUT,
            "Command timeout must be greater than connect timeout"
        )
        
        # Check boolean settings
        self.assertIsInstance(Config.SSH_BATCH_MODE, bool)
        self.assertIsInstance(Config.SSH_STRICT_HOST_KEY_CHECKING, bool)
        
        print(f"✓ SSH_CONNECT_TIMEOUT: {Config.SSH_CONNECT_TIMEOUT}s")
        print(f"✓ SSH_COMMAND_TIMEOUT: {Config.SSH_COMMAND_TIMEOUT}s")

    def test_gui_timing_settings(self):
        """Check GUI timing settings"""
        checks = TEST_CONFIG_CHECKS["gui_timing"]
        
        self.assertIsInstance(Config.GUI_STATUS_MESSAGE_DURATION, int)
        self.assertGreaterEqual(
            Config.GUI_STATUS_MESSAGE_DURATION,
            checks["status_message_duration_min"],
            f"Status message duration too small (min {checks['status_message_duration_min']}ms)"
        )
        
        self.assertIsInstance(Config.GUI_THREAD_UPDATE_INTERVAL, int)
        self.assertGreaterEqual(
            Config.GUI_THREAD_UPDATE_INTERVAL,
            checks["thread_update_interval_min"],
            f"Thread update interval invalid (min {checks['thread_update_interval_min']}ms)"
        )
        
        print(f"✓ GUI_STATUS_MESSAGE_DURATION: {Config.GUI_STATUS_MESSAGE_DURATION}ms")
        print(f"✓ GUI_THREAD_UPDATE_INTERVAL: {Config.GUI_THREAD_UPDATE_INTERVAL}ms")

    def test_logging_settings(self):
        """Check logging settings"""
        checks = TEST_CONFIG_CHECKS["logging"]
        
        # Check paths
        self.assertIsInstance(Config.LOG_DIR, str)
        if checks["log_dir_must_exist"]:
            self.assertTrue(Config.LOG_DIR.startswith(os.path.expanduser("~")))
        
        # Check prefix and formats
        if checks["log_file_prefix_required"]:
            self.assertIsInstance(Config.LOG_FILE_PREFIX, str)
            self.assertGreater(len(Config.LOG_FILE_PREFIX), 0)
        
        if checks["date_format_required"]:
            self.assertIsInstance(Config.LOG_DATE_FORMAT, str)
            self.assertIsInstance(Config.LOG_TIMESTAMP_FORMAT, str)
        
        self.assertIsInstance(Config.LOG_ENABLED, bool)
        
        print(f"✓ LOG_DIR: {Config.LOG_DIR}")
        print(f"✓ LOG_ENABLED: {Config.LOG_ENABLED}")

    def test_security_settings(self):
        """Check security settings"""
        checks = TEST_CONFIG_CHECKS["security"]
        
        # Check that SECURITY is a dict
        self.assertIsInstance(Config.SECURITY, dict)
        
        # Check for required keys
        self.assertIn("dangerous_commands", Config.SECURITY)
        self.assertIn("require_confirmation", Config.SECURITY)
        
        # Check that they are lists
        self.assertIsInstance(Config.SECURITY["dangerous_commands"], list)
        self.assertIsInstance(Config.SECURITY["require_confirmation"], list)
        
        # Check that lists are not empty and meet minimum requirements
        self.assertGreaterEqual(
            len(Config.SECURITY["dangerous_commands"]),
            checks["dangerous_commands_min_count"],
            f"Too few dangerous commands (min {checks['dangerous_commands_min_count']})"
        )
        self.assertGreaterEqual(
            len(Config.SECURITY["require_confirmation"]),
            checks["require_confirmation_min_count"],
            f"Too few confirmation commands (min {checks['require_confirmation_min_count']})"
        )
        
        print(f"✓ Dangerous commands: {len(Config.SECURITY['dangerous_commands'])}")
        print(f"✓ Require confirmation: {len(Config.SECURITY['require_confirmation'])}")

    def test_gui_settings(self):
        """Check GUI settings"""
        checks = TEST_CONFIG_CHECKS["gui_dimensions"]
        
        # Check window dimensions
        self.assertIsInstance(Config.GUI_WINDOW_GEOMETRY, str)
        self.assertIn("x", Config.GUI_WINDOW_GEOMETRY)
        
        self.assertIsInstance(Config.GUI_WINDOW_MIN_WIDTH, int)
        self.assertGreaterEqual(
            Config.GUI_WINDOW_MIN_WIDTH,
            checks["min_width"],
            f"Window width too small (min {checks['min_width']})"
        )
        
        self.assertIsInstance(Config.GUI_WINDOW_MIN_HEIGHT, int)
        self.assertGreaterEqual(
            Config.GUI_WINDOW_MIN_HEIGHT,
            checks["min_height"],
            f"Window height too small (min {checks['min_height']})"
        )
        
        # Check colors
        self.assertIsInstance(Config.GUI_COLORS, dict)
        for color_key in TEST_EXPECTED_COLORS:
            self.assertIn(
                color_key,
                Config.GUI_COLORS,
                f"Color '{color_key}' not found in GUI_COLORS"
            )
        
        print(f"✓ GUI_WINDOW_GEOMETRY: {Config.GUI_WINDOW_GEOMETRY}")
        print(f"✓ GUI colors defined: {len(Config.GUI_COLORS)}")

    def test_cli_settings(self):
        """Check CLI settings"""
        checks = TEST_CONFIG_CHECKS["cli"]
        
        self.assertIsInstance(Config.CLI_SEPARATOR_LENGTH, int)
        self.assertGreaterEqual(
            Config.CLI_SEPARATOR_LENGTH,
            checks["separator_length_min"],
            f"Separator too short (min {checks['separator_length_min']})"
        )
        
        print(f"✓ CLI_SEPARATOR_LENGTH: {Config.CLI_SEPARATOR_LENGTH}")

    def test_symbols(self):
        """Check interface symbols"""
        self.assertIsInstance(Config.SYMBOLS, dict)
        self.assertGreater(len(Config.SYMBOLS), 0)
        
        # Check key symbols from test config
        for symbol in TEST_EXPECTED_SYMBOLS:
            self.assertIn(
                symbol,
                Config.SYMBOLS,
                f"Symbol '{symbol}' not found in Config.SYMBOLS"
            )
            self.assertIsInstance(Config.SYMBOLS[symbol], str)
        
        print(f"✓ Symbols defined: {len(Config.SYMBOLS)}")

    def test_methods_check_dangerous_command(self):
        """Test check_dangerous_command method with data from config_test.py"""
        # Dangerous commands from test config
        for cmd in TEST_DANGEROUS_COMMANDS:
            with self.subTest(command=cmd):
                result = Config.check_dangerous_command(cmd)
                self.assertIsInstance(result, dict)
                self.assertIn("is_dangerous", result)
                self.assertTrue(
                    result["is_dangerous"],
                    f"Command '{cmd}' should be detected as dangerous"
                )
                self.assertIn("reason", result)
                print(f"✓ Dangerous detected: '{cmd[:40]}...'")
        
        # Safe commands from test config
        for cmd in TEST_SAFE_COMMANDS:
            with self.subTest(command=cmd):
                result = Config.check_dangerous_command(cmd)
                self.assertFalse(
                    result["is_dangerous"],
                    f"Command '{cmd}' should be safe"
                )
                print(f"✓ Safe detected: '{cmd}'")

    def test_methods_requires_confirmation(self):
        """Test requires_confirmation method with data from config_test.py"""
        # Commands requiring confirmation
        for cmd in TEST_CONFIRMATION_COMMANDS:
            with self.subTest(command=cmd):
                result = Config.requires_confirmation(cmd)
                self.assertTrue(
                    result,
                    f"Command '{cmd}' should require confirmation"
                )
                print(f"✓ Confirmation required: '{cmd}'")
        
        # Regular commands
        for cmd in TEST_NO_CONFIRMATION_COMMANDS:
            with self.subTest(command=cmd):
                result = Config.requires_confirmation(cmd)
                self.assertFalse(
                    result,
                    f"Command '{cmd}' should not require confirmation"
                )
                print(f"✓ No confirmation needed: '{cmd}'")

    def test_methods_get_color(self):
        """Test get_color method"""
        colors = ["status_ready", "status_error", "status_info"]
        for color_key in colors:
            color = Config.get_color(color_key)
            self.assertIsInstance(color, str)
            self.assertGreater(len(color), 0)
            print(f"✓ Color '{color_key}': {color}")

    def test_methods_get_symbol(self):
        """Test get_symbol method"""
        symbols = ["success", "error", "info"]
        for symbol_key in symbols:
            symbol = Config.get_symbol(symbol_key)
            self.assertIsInstance(symbol, str)
            print(f"✓ Symbol '{symbol_key}': {symbol}")

    def test_log_file_path_generation(self):
        """Test log file path generation"""
        # Test with specific date
        log_path = Config.get_log_file_path("2024-10-22")
        self.assertIsInstance(log_path, str)
        self.assertIn("2024-10-22", log_path)
        self.assertTrue(log_path.endswith(".log"))
        print(f"✓ Log file path: {log_path}")
        
        # Test without date (current date)
        log_path_today = Config.get_log_file_path()
        self.assertIsInstance(log_path_today, str)
        self.assertTrue(log_path_today.endswith(".log"))
        print(f"✓ Today's log file: {log_path_today}")


def run_tests():
    """Run all tests"""
    print("=" * 70)
    print("CONFIG MODULE TESTING")
    print("=" * 70)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestConfig)
    
    # Run with verbose=2
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Success: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
