#!/usr/bin/env python3

# Command Executor CLI Arguments

import argparse
import sys

from config import Config


def create_parser():
    # Command line argument parser
    parser = argparse.ArgumentParser(
        prog="command-executor",
        description=Config.APP_DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,  # Disable standard help
        epilog=f"""
Usage examples:
  {sys.argv[0]}                    # Automatic GUI/CLI selection
  {sys.argv[0]} --gui              # Force GUI startup
  {sys.argv[0]} --cli              # Force CLI startup
  {sys.argv[0]} --prefix web       # Filter hosts by prefix
  {sys.argv[0]} --config custom    # Use different SSH config
  {sys.argv[0]} --delay 5          # Add 5 second delay between hosts
  {sys.argv[0]} --version          # Show version

Project files:
    main.py                        - Entry point (auto-select GUI/CLI)
    command_executor_gui_app.py    - GUI implementation
    command_executor_cli_app.py    - CLI implementation
    config.py                      - Configuration settings
    ssh_config_parser.py           - SSH configuration parser
    ssh_executor.py                - SSH command execution

{Config.APP_NAME} v{Config.APP_VERSION}
        """.strip(),
    )

    # Add custom help option
    parser.add_argument("-h", "--help", action="help", help="Show help")

    # Main operating modes
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--gui", action="store_true", help="Force GUI version startup"
    )
    mode_group.add_argument(
        "--cli", action="store_true", help="Force CLI version startup"
    )

    # SSH settings
    parser.add_argument(
        "--config",
        "-c",
        metavar="PATH",
        default=Config.DEFAULT_SSH_CONFIG_PATH,
        help=f"Path to SSH config file (default: {Config.DEFAULT_SSH_CONFIG_PATH})",
    )

    # Filtering
    parser.add_argument(
        "--prefix",
        "-p",
        metavar="PREFIX",
        default="",
        help="Prefix for filtering hosts (default: all hosts)",
    )

    # Execution settings
    parser.add_argument(
        "--timeout",
        "-t",
        type=int,
        metavar="SECONDS",
        default=Config.SSH_COMMAND_TIMEOUT,
        help=f"Command execution timeout in seconds (default: {Config.SSH_COMMAND_TIMEOUT})",
    )

    parser.add_argument(
        "--connect-timeout",
        type=int,
        metavar="SECONDS",
        default=Config.SSH_CONNECT_TIMEOUT,
        help=f"SSH connection timeout in seconds (default: {Config.SSH_CONNECT_TIMEOUT})",
    )

    parser.add_argument(
        "--delay",
        type=int,
        metavar="SECONDS",
        default=0,
        help="Delay in seconds between executing commands on hosts (0-600, default: 0)",
    )

    # Debug and information
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output (enabled by default in the GUI)",
    )

    parser.add_argument("--debug", "-d", action="store_true", help="Debug mode")

    parser.add_argument(
        "--version",
        action="version",
        version=f"{Config.APP_NAME} v{Config.APP_VERSION}",
        help="Show program version",
    )

    # Testing
    parser.add_argument(
        "--test-config", action="store_true", help="Check SSH configuration"
    )

    parser.add_argument("--list-hosts", action="store_true", help="Show host list")

    return parser


def parse_args(args=None):
    # Parse command-line arguments
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Argument validation
    try:
        if parsed_args.prefix:
            parsed_args.prefix = Config.validate_prefix(parsed_args.prefix)
    except ValueError as e:
        parser.error(f"Prefix error: {e}")

    if parsed_args.timeout <= 0:
        parser.error("Timeout must be a positive integer")

    if parsed_args.connect_timeout <= 0:
        parser.error("Connection timeout must be a positive integer")

    return parsed_args


if __name__ == "__main__":
    from config import Config

    if Config.TEST_SETTINGS["enable_debug_output"]:
        # Argument parser self-test
        args = parse_args()
        print(f"{Config.get_cli_symbol('wrench')} Parsed arguments:")
        for key, value in vars(args).items():
            print(f"  {key}: {value}")
