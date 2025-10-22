"""
Test configuration
This file contains test data and settings for unit tests
"""

# Test dangerous commands
TEST_DANGEROUS_COMMANDS = [
    "rm -rf /tmp",
    "dd if=/dev/zero of=/dev/sda",
    "mkfs.ext4 /dev/sda1",
]

# Test safe commands
TEST_SAFE_COMMANDS = [
    "echo 'hello world'",
    "ls -la",
    "cat /etc/hostname",
    "date",
    "whoami",
]

# Commands requiring confirmation
TEST_CONFIRMATION_COMMANDS = [
    "sudo systemctl restart nginx",
    "sudo apt-get update",
    "systemctl stop mysql",
]

# Commands not requiring confirmation
TEST_NO_CONFIRMATION_COMMANDS = [
    "ls -la",
    "echo test",
    "cat file.txt",
]

# Test data for parsing host ranges
TEST_HOST_RANGES = {
    "single_numbers": {
        "input": "1,3,5",
        "expected": [1, 3, 5],
    },
    "standard_range": {
        "input": "1-3",
        "expected": [1, 2, 3],
    },
    "reversed_range": {
        "input": "5-1",
        "expected": [1, 2, 3, 4, 5],
    },
    "duplicates_and_overlaps": {
        "input": "1,1-3,2",
        "expected": [1, 2, 3],
    },
    "invalid_entries": {
        "input": "1,abc,2-4,xyz",
        "expected": [1, 2, 3, 4],
        "should_print_warning": True,
    },
}

# Test data for SSH config parser
TEST_SSH_CONFIG_CONTENT = """
Host test-server-*
    HostName 192.168.1.10
    User testuser
    Port 22

Host production-*
    HostName 10.0.0.5
    User produser
    Port 2222
    
Host *.example.com
    HostName wildcard.example.com
    User wildcarduser

Host specific-host
    HostName 192.168.1.100
    User specificuser
"""

TEST_SSH_CONFIG_EXPECTED_HOSTS = [
    "test-server-*",
    "production-*",
    "*.example.com",
    "specific-host",
]

# Hosts with patterns (should be excluded from results)
TEST_SSH_CONFIG_PATTERN_HOSTS = [
    "test-server-*",
    "production-*",
    "*.example.com",
]

# Hosts without patterns (should be in results)
TEST_SSH_CONFIG_NON_PATTERN_HOSTS = [
    "specific-host",
]

# Settings for Config validation
TEST_CONFIG_CHECKS = {
    "app_info": {
        "name": "SSH Command Executor",
        "version_format": r"^\d+\.\d+(\.\d+)?$",  # Regex for version (0.1 or 1.0.0)
        "description_min_length": 10,
    },
    "ssh_settings": {
        "connect_timeout_min": 1,
        "command_timeout_min": 10,
        "timeout_relationship": "command > connect",  # command_timeout must be greater
    },
    "gui_timing": {
        "status_message_duration_min": 1000,  # Minimum 1 second
        "thread_update_interval_min": 0,  # Can be 0
    },
    "logging": {
        "log_dir_must_exist": True,
        "log_file_prefix_required": True,
        "date_format_required": True,
    },
    "security": {
        "dangerous_commands_min_count": 5,
        "require_confirmation_min_count": 3,
    },
    "gui_dimensions": {
        "min_width": 800,
        "min_height": 600,
    },
    "cli": {
        "separator_length_min": 40,
    },
}

# Expected symbols
TEST_EXPECTED_SYMBOLS = [
    "unchecked",
    "checked",
    "success",
    "error",
    "warning",
    "info",
]

# Expected colors
TEST_EXPECTED_COLORS = [
    "status_ready",
    "status_error",
    "status_info",
    "selected_host_bg",
    "selected_host_fg",
]

# Test messages
TEST_MESSAGES = {
    "dangerous_command_detected": "Command contains dangerous pattern",
    "confirmation_required": "Command requires confirmation",
    "safe_command": "Command is safe to execute",
}

# Settings for validation testing
TEST_VALIDATION = {
    "valid_prefix": "test-",
    "invalid_prefix_too_long": "x" * 100,
    "valid_command": "echo test",
    "invalid_command_too_long": "echo " + "x" * 2000,
}

# Test environment settings
TEST_ENVIRONMENT = {
    "test_timeout": 5,  # Test timeout (seconds)
    "verbose": True,  # Verbose output
    "capture_warnings": True,  # Capture warnings
}
