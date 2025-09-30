#!/usr/bin/env python3

import os


class Config:
    # Main settings
    APP_NAME = "Command Executor"
    APP_VERSION = "0.1"
    APP_DESCRIPTION = (
        "Tool for executing SSH commands with graphical and console interfaces"
    )

    # SSH settings
    DEFAULT_SSH_CONFIG_PATH = os.path.expanduser("~/.ssh/config")
    SSH_CONNECT_TIMEOUT = 10
    SSH_COMMAND_TIMEOUT = 30
    SSH_BATCH_MODE = True
    SSH_STRICT_HOST_KEY_CHECKING = False

    # Logging settings
    LOG_DIR = os.path.expanduser("~/.ssh/command_executor_logs")
    LOG_FILE_PREFIX = "ssh_commands"
    LOG_DATE_FORMAT = "%Y-%m-%d"
    LOG_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
    LOG_ENABLED = True

    # Security settings
    SECURITY = {
        "dangerous_commands": [
            "rm -rf",
            "dd if=",
            "mkfs",
            "format",
            "fdisk",
            "> /dev/",
            "chmod 777",
            "chmod -R 777",
        ],
        "require_confirmation": [
            "sudo",
            "su",
            "passwd",
            "usermod",
            "userdel",
            "systemctl",
            "service",
            "mount",
            "umount",
            "fdisk",
            "parted",
            "crontab",
            "chown",
            "chmod 777",
            "chmod +x",
        ],
    }

    # GUI settings
    GUI_WINDOW_TITLE = f"{APP_NAME} - SSH Command Launcher"
    GUI_WINDOW_GEOMETRY = "1000x700"
    GUI_WINDOW_MIN_WIDTH = 800
    GUI_WINDOW_MIN_HEIGHT = 600

    # Host tree column sizes
    GUI_TREE_HOST_COLUMN_WIDTH = 250
    GUI_TREE_HOST_COLUMN_MIN_WIDTH = 200
    GUI_TREE_CHECKBOX_COLUMN_WIDTH = 30
    GUI_TREE_CHECKBOX_COLUMN_MIN_WIDTH = 30

    # Input field settings
    GUI_PREFIX_ENTRY_WIDTH = 10
    GUI_COMMAND_ENTRY_FONT = ("Consolas", 10)
    GUI_RESULTS_TEXT_FONT = ("Consolas", 9)
    GUI_TITLE_FONT = ("Arial", 16, "bold")
    GUI_INFO_DIALOG_FONT = ("Consolas", 10)
    GUI_INFO_DIALOG_TITLE_FONT = ("Arial", 14, "bold")

    # Padding and spacing
    GUI_MAIN_PADDING = "10"
    GUI_FRAME_PADDING = "5"
    GUI_BUTTON_PADX = (0, 5)
    GUI_CONTROL_PANEL_PADY = (10, 0)

    # Colors and styles
    GUI_COLORS = {
        "selected_host_bg": "#e3f2fd",
        "selected_host_fg": "#1976d2",
        "unselected_host_bg": "white",
        "unselected_host_fg": "black",
        "group_bg": "#f5f5f5",
        "group_fg": "#666666",
        "status_ready": "green",
        "status_working": "orange",
        "status_error": "red",
        "status_info": "blue",
    }

    # CLI settings
    CLI_SEPARATOR_LENGTH = 60
    CLI_HOST_NUMBER_WIDTH = 2
    CLI_HOST_INFO_KEY_WIDTH = 15

    # Interface symbols
    SYMBOLS = {
        "unchecked": "☐",
        "checked": "☑",
        "checkbox_header": "☑",
        "success": "[OK]",
        "error": "[ERROR]",
        "warning": "[!]",
        "info": "[i]",
        "rocket": ">>",
        "computer": "PC",
        "folder": "[+]",
        "target": "*",
        "satellite": ">>",
        "chart": "#",
        "wave": "bye",
        "refresh": "~",
        "search": "?",
        "link": "->",
        "clipboard": "[]",
        "wrench": "cfg",
        "finish": "[DONE]",
        "scroll": "...",
    }

    # Messages
    MESSAGES = {
        "gui_startup": f"{SYMBOLS['rocket']} Starting GUI version of {APP_NAME}...",
        "cli_startup": f"{SYMBOLS['warning']} GUI (tkinter) not available, starting console version...",
        "cli_fallback": f"{SYMBOLS['refresh']} Attempting to start console version...",
        "hosts_not_found": "{warning} No hosts found in {config_path}",
        "hosts_with_prefix_not_found": "{warning} No hosts with prefix '{prefix}' found in {config_path}",
        "hosts_loaded": "{success} Loaded {count} hosts in {groups} groups",
        "hosts_loaded_with_prefix": "{success} Loaded {count} hosts with prefix '{prefix}' in {groups} groups",
        "total_hosts_info": "{chart} Total hosts in configuration: {total}",
        "ready_status": "Ready to work",
        "execution_status": "Executing commands...",
        "testing_connection": "{search} Testing connection to {hostname}...",
        "connection_success": "{success} Connection successful",
        "connection_error": "{error} Connection error",
        "execution_start": "{rocket} Executing command: {command}",
        "execution_hosts": "{satellite} On hosts: {hosts}",
        "execution_finish": "{finish} Execution completed on {count} hosts",
        "goodbye": "Goodbye!",
        "goodbye_cli": "Exit with Ctrl+C",
    }

    # Default settings
    DEFAULTS = {
        "verbose_output": True,
        "sudo_enabled": False,
        "tree_groups_expanded": True,
        "prefix_filter": "",
        "command_history_size": 50,
    }

    # Test settings (used in if __name__ == "__main__" blocks)
    TEST_SETTINGS = {
        "test_prefix": "",  # Prefix for parser testing
        "test_host_limit": 5,  # Maximum hosts to show in tests
        "test_group_limit": 3,  # Maximum hosts in group to show
        "enable_debug_output": True,
        "test_command": 'echo "SSH connection test successful"',
    }

    # Validation
    VALIDATION = {
        "max_prefix_length": 50,
        "max_command_length": 1000,
        "max_hostname_length": 253,  # RFC standard
        "max_concurrent_connections": 50,
    }

    # Host grouping
    GROUPING = {
        "numeric_group_name": "other",
        "special_chars_group_name": "zzz",
        "default_group_sort_priority": 999,
    }

    @classmethod
    def get_ssh_config_path(cls, custom_path=None):
        # Path to SSH configuration
        if custom_path:
            return os.path.expanduser(custom_path)
        return cls.DEFAULT_SSH_CONFIG_PATH

    @classmethod
    def validate_prefix(cls, prefix):
        if len(prefix) > cls.VALIDATION["max_prefix_length"]:
            raise ValueError(
                f"Prefix too long (maximum {cls.VALIDATION['max_prefix_length']} characters)"
            )
        return prefix.strip()

    @classmethod
    def validate_command(cls, command):
        if len(command) > cls.VALIDATION["max_command_length"]:
            raise ValueError(
                f"Command too long (maximum {cls.VALIDATION['max_command_length']} characters)"
            )
        return command.strip()

    @classmethod
    def get_symbol(cls, name, use_emoji=False):
        # Symbol by name
        return cls.SYMBOLS.get(name, "")

    @classmethod
    def get_gui_symbol(cls, name):
        # Symbol for GUI
        return cls.get_symbol(name)

    @classmethod
    def get_cli_symbol(cls, name):
        # Symbol for CLI
        return cls.get_symbol(name)

    @classmethod
    def get_message(cls, name, **kwargs):
        # Message with parameter substitution
        template = cls.MESSAGES.get(name, "")
        if not template:
            return ""

        context = dict(cls.SYMBOLS)
        context.update(
            {
                "config_path": cls.DEFAULT_SSH_CONFIG_PATH,
                "default_path": cls.DEFAULT_SSH_CONFIG_PATH,
                "app_name": cls.APP_NAME,
            }
        )
        context.update(kwargs)

        try:
            return template.format(**context)
        except KeyError:
            return template

    @classmethod
    def get_color(cls, name):
        # Color by name
        return cls.GUI_COLORS.get(name, "black")

    @classmethod
    def get_log_file_path(cls, date_str=None):
        # Path to log file for specified date
        import datetime

        if date_str is None:
            date_str = datetime.datetime.now().strftime(cls.LOG_DATE_FORMAT)

        filename = f"{cls.LOG_FILE_PREFIX}_{date_str}.log"
        return os.path.join(cls.LOG_DIR, filename)

    @classmethod
    def ensure_log_dir(cls):
        # Create log directory if it doesn't exist
        os.makedirs(cls.LOG_DIR, exist_ok=True)

    @classmethod
    def check_dangerous_command(cls, command):
        # Check if command is potentially dangerous
        command_lower = command.lower().strip()

        for dangerous_pattern in cls.SECURITY["dangerous_commands"]:
            if dangerous_pattern.lower() in command_lower:
                return {
                    "is_dangerous": True,
                    "reason": f"Command contains potentially dangerous pattern: '{dangerous_pattern}'",
                }

        return {"is_dangerous": False, "reason": ""}

    @classmethod
    def requires_confirmation(cls, command):
        # Check if command requires confirmation
        command_lower = command.lower().strip()

        for confirm_pattern in cls.SECURITY["require_confirmation"]:
            pattern_lower = confirm_pattern.lower()
            # Check both command start and content
            if (
                command_lower.startswith(pattern_lower)
                or f" {pattern_lower}" in command_lower
                or pattern_lower in command_lower
            ):
                return True

        return False
