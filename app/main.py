#!/usr/bin/env python3

import os
import sys

from cli_args import parse_args
from config import Config


def test_ssh_config(config_path):
    # Test SSH configuration
    try:
        from ssh_config_parser import SSHConfigParser

        print(
            f"{Config.get_symbol('search')} Checking SSH configuration: {config_path}"
        )

        if not os.path.exists(config_path):
            print(f"{Config.get_symbol('error')} File not found: {config_path}")
            return False

        parser = SSHConfigParser(config_path)
        hosts = parser.get_all_hosts()

        if not hosts:
            print(f"{Config.get_symbol('warning')} No hosts found in configuration")
            return False

        print(f"{Config.get_symbol('success')} Found {len(hosts)} hosts")

        # Show grouping
        groups = parser.get_grouped_hosts_with_prefix("")
        print(f"{Config.get_symbol('folder')} Host groups:")
        for group_name in sorted(groups.keys()):
            print(f"  {group_name}: {len(groups[group_name])} hosts")

        return True

    except Exception as e:
        print(f"{Config.get_symbol('error')} Configuration check error: {e}")
        return False


def list_hosts(config_path, prefix=""):
    # List hosts
    try:
        from ssh_config_parser import SSHConfigParser

        parser = SSHConfigParser(config_path)
        groups = parser.get_grouped_hosts_with_prefix(prefix)

        if not groups:
            if prefix:
                print(
                    f"{Config.get_symbol('warning')} No hosts found with prefix '{prefix}'"
                )
            else:
                print(f"{Config.get_symbol('warning')} No hosts found")
            return

        total_hosts = sum(len(hosts) for hosts in groups.values())

        if prefix:
            print(
                f"{Config.get_symbol('satellite')} Hosts with prefix '{prefix}' ({total_hosts} found):"
            )
        else:
            print(f"{Config.get_symbol('satellite')} All hosts ({total_hosts} found):")

        for group_name in sorted(groups.keys()):
            hosts_in_group = groups[group_name]
            print(
                f"\n{Config.get_symbol('folder')} Group '{group_name}' ({len(hosts_in_group)} hosts):"
            )

            for host in hosts_in_group:
                host_info = parser.get_host_info(host)
                if host_info and "hostname" in host_info:
                    print(f"  {host} ({host_info['hostname']})")
                else:
                    print(f"  {host}")

    except Exception as e:
        print(f"{Config.get_symbol('error')} Error getting host list: {e}")


def start_gui(args):
    # Start GUI interface
    try:
        import tkinter as tk

        from command_executor_gui_app import CommandExecutorApp

        print(Config.get_message("gui_startup"))

        root = tk.Tk()
        CommandExecutorApp(root, args)
        root.mainloop()

    except ImportError:
        print(Config.get_message("cli_startup"))
        start_cli(args)
    except Exception as e:
        if args.debug:
            import traceback

            traceback.print_exc()
        print(f"{Config.get_symbol('error')} GUI version startup error: {str(e)}")
        print(Config.get_message("cli_fallback"))
        start_cli(args)


def start_cli(args):
    # Start CLI interface
    try:
        from command_executor_cli_app import main as cli_main

        cli_main(args)
    except Exception as e:
        if args.debug:
            import traceback

            traceback.print_exc()
        print(f"{Config.get_symbol('error')} CLI version startup error: {str(e)}")
        sys.exit(1)


def main():
    args = parse_args()

    if args.debug:
        print(f"{Config.get_symbol('wrench')} Debug mode active")
        print(f"Arguments: {vars(args)}")

    # Special commands
    if args.test_config:
        success = test_ssh_config(args.config)
        sys.exit(0 if success else 1)

    if args.list_hosts:
        list_hosts(args.config, args.prefix)
        sys.exit(0)

    # Interface selection
    if args.gui:
        start_gui(args)
    elif args.cli:
        start_cli(args)
    else:
        # Automatic selection
        start_gui(args)


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
