#!/usr/bin/env python3
# Console interface component for Command Executor.

from typing import Dict, List

from config import Config
from ssh_config_parser import SSHConfigParser
from ssh_executor import SSHExecutor


def main(args=None):
    # CLI version entry point.
    prefix = args.prefix if args and hasattr(args, "prefix") else ""
    raw_config_path = args.config if args and hasattr(args, "config") else None
    config_path = Config.get_ssh_config_path(raw_config_path)
    timeout = (
        args.timeout
        if args and hasattr(args, "timeout")
        else Config.SSH_COMMAND_TIMEOUT
    )
    connect_timeout = (
        args.connect_timeout
        if args and hasattr(args, "connect_timeout")
        else Config.SSH_CONNECT_TIMEOUT
    )
    debug = args.debug if args and hasattr(args, "debug") else False

    if debug:
        print(
            f"[DEBUG] CLI args: prefix='{prefix}', config='{config_path}', "
            f"timeout={timeout}, connect_timeout={connect_timeout}"
        )

    separator = "=" * Config.CLI_SEPARATOR_LENGTH
    print(separator)
    print(Config.APP_NAME)
    print(separator)

    parser = SSHConfigParser(config_path)
    executor = SSHExecutor(
        ssh_config_path=config_path,
        connect_timeout=connect_timeout,
        command_timeout=timeout,
    )

    print(f"\n{Config.get_cli_symbol('folder')} Available host groups:")
    all_groups = parser.get_grouped_hosts_with_prefix("")
    if all_groups:
        for group_name in sorted(all_groups.keys()):
            hosts_count = len(all_groups[group_name])
            print(
                f"{Config.get_cli_symbol('folder')} Group '{group_name}' ({hosts_count} hosts)"
            )
    else:
        print(f"{Config.get_cli_symbol('error')} Groups not found")

    if not prefix:
        print("\nHost filter configuration")
        prefix = input("Enter host prefix (press Enter for all hosts): ").strip()
    else:
        print(f"\nUsing prefix from arguments: '{prefix}'")

    print(f"\n{Config.get_cli_symbol('satellite')} Loading hosts...")
    groups = parser.get_grouped_hosts_with_prefix(prefix)

    if not groups:
        if prefix:
            print(
                Config.get_message(
                    "hosts_with_prefix_not_found",
                    prefix=prefix,
                    config_path=config_path,
                )
            )
        else:
            print(Config.get_message("hosts_not_found", config_path=config_path))
        return

    total_hosts = sum(len(hosts) for hosts in groups.values())

    if prefix:
        print(
            Config.get_message(
                "hosts_loaded_with_prefix",
                count=total_hosts,
                prefix=prefix,
                groups=len(groups),
                config_path=config_path,
            )
        )
    else:
        print(Config.get_message("hosts_loaded", count=total_hosts, groups=len(groups)))

    host_index: Dict[int, str] = {}
    index = 1
    for group_name in sorted(groups.keys()):
        hosts_in_group = groups[group_name]
        print(
            f"{Config.get_cli_symbol('folder')} Group '{group_name}' ({len(hosts_in_group)} hosts)"
        )
        for host in hosts_in_group:
            host_index[index] = host
            index += 1

    print(Config.get_message("total_hosts_info", total=len(parser.get_all_hosts())))
    print("\n" + separator)

    while True:
        print("\nSelect action:")
        print("1. Execute command on selected hosts")
        print("2. Show host information")
        print("3. Test connection")
        print("4. Show host list")
        print("0. Exit")

        try:
            choice = input("\nEnter action number: ").strip()

            if choice == "0":
                print(Config.get_message("goodbye"))
                break
            if choice == "1":
                execute_command_on_hosts(host_index, executor)
            elif choice == "2":
                show_host_info(host_index, parser)
            elif choice == "3":
                test_host_connection(host_index, executor)
            elif choice == "4":
                show_hosts_list(host_index, parser)
            else:
                print(f"{Config.get_cli_symbol('error')} Invalid choice. Try again.")

        except KeyboardInterrupt:
            print(f"\n\n{Config.get_cli_symbol('wave')} Exit by Ctrl+C")
            break
        except (
            Exception
        ) as exc:  # pragma: no cover - safeguard against unexpected CLI errors
            print(f"{Config.get_cli_symbol('error')} Error: {exc}")


def parse_host_range(user_input: str, hosts_count: int) -> List[int]:
    """Parse a comma-separated list of host numbers such as "1,3,5-8"."""
    hosts: List[int] = []
    max_hosts = hosts_count

    for part in user_input.split(","):
        part = part.strip()
        if not part:
            continue

        if "-" in part:
            try:
                start, end = map(int, part.split("-"))
                if start <= end:
                    hosts.extend(range(start, end + 1))
                else:
                    hosts.extend(range(end, start + 1))
            except ValueError:
                print(f"{Config.get_cli_symbol('error')} Invalid range: {part}")
        else:
            try:
                hosts.append(int(part))
            except ValueError:
                print(f"{Config.get_cli_symbol('error')} Invalid host number: {part}")

    valid_hosts = [h for h in hosts if 1 <= h <= max_hosts]
    return sorted(set(valid_hosts))


def execute_command_on_hosts(host_index: Dict[int, str], executor: SSHExecutor) -> None:
    print(f"\n{Config.get_cli_symbol('rocket')} Execute command on hosts")
    print("-" * 40)

    if not host_index:
        print(f"{Config.get_cli_symbol('error')} No available hosts")
        return

    print(f"Available hosts: 1-{len(host_index)}")
    host_input = input("Enter host numbers (for example: 1,3,5-8): ").strip()

    if not host_input:
        print(f"{Config.get_cli_symbol('error')} No hosts selected")
        return

    selected_numbers = parse_host_range(host_input, len(host_index))
    if not selected_numbers:
        print(f"{Config.get_cli_symbol('error')} Invalid host numbers")
        return

    selected_hosts = [host_index[i] for i in selected_numbers]

    print(f"{Config.get_cli_symbol('success')} Selected hosts: {len(selected_hosts)}")
    for idx, host in enumerate(selected_hosts, 1):
        print(f"  {idx}. {host}")

    command = input("\nEnter command to execute: ").strip()
    if not command:
        print(f"{Config.get_cli_symbol('error')} Command not provided")
        return

    use_sudo = input("Use sudo? (y/N): ").strip().lower() == "y"
    if use_sudo and not command.startswith("sudo "):
        command = f"sudo {command}"

    # Safety check for dangerous commands
    dangerous_result = Config.check_dangerous_command(command)
    if dangerous_result["is_dangerous"]:
        print(
            f"\n{Config.get_cli_symbol('error')} WARNING: Command blocked as potentially dangerous!"
        )
        print(f"Command: {command}")
        print(f"Reason: {dangerous_result['reason']}")
        print("Execution of dangerous commands is prohibited for safety.")
        return

    # Additional confirmation for sensitive commands
    if Config.requires_confirmation(command):
        print(
            f"\n{Config.get_cli_symbol('warning')} NOTICE: Command requires confirmation!"
        )
        print(f"Command: {command}")
        print(f"Hosts: {', '.join(selected_hosts)}")
        confirm = input("Continue execution? (y/N): ").strip().lower()
        if confirm != "y":
            print(f"{Config.get_cli_symbol('info')} Execution cancelled by user")
            return

    print(f"\n{Config.get_cli_symbol('target')} Executing command: {command}")
    print(f"{Config.get_cli_symbol('satellite')} On hosts: {', '.join(selected_hosts)}")
    print("=" * Config.CLI_SEPARATOR_LENGTH)

    for idx, host in enumerate(selected_hosts, 1):
        print(f"\n[{idx}/{len(selected_hosts)}] 🖥️  {host}")
        print("-" * 30)
        try:
            result = executor.execute_command(host, command)
            if result["success"]:
                print(
                    f"{Config.get_cli_symbol('success')} Success (return code: {result['return_code']})"
                )
                if result["output"]:
                    print("Output:")
                    print(result["output"])
                if result["error"]:
                    print("Warnings:")
                    print(result["error"])
            else:
                print(
                    f"{Config.get_cli_symbol('error')} Error (return code: {result['return_code']})"
                )
                if result["error"]:
                    print("Error:")
                    print(result["error"])
        except (
            Exception
        ) as exc:  # pragma: no cover - safeguard against unexpected CLI errors
            print(f"{Config.get_cli_symbol('error')} Exception: {exc}")

    print(Config.get_message("execution_finish", count=len(selected_hosts)))


def show_host_info(host_index: Dict[int, str], parser: SSHConfigParser) -> None:
    print(f"\n{Config.get_cli_symbol('clipboard')} Host information")
    print("-" * 30)

    try:
        host_num = int(input(f"Enter host number (1-{len(host_index)}): "))
    except ValueError:
        print(f"{Config.get_cli_symbol('error')} Enter a valid number")
        return

    if host_num not in host_index:
        print(f"{Config.get_cli_symbol('error')} Invalid host number")
        return

    hostname = host_index[host_num]
    info = parser.get_host_info(hostname)

    print(f"\n{Config.get_cli_symbol('computer')} Host: {hostname}")
    print("=" * 40)

    if info:
        for key, value in info.items():
            print(f"{key:15s}: {value}")
    else:
        print("Host information not found")


def test_host_connection(host_index: Dict[int, str], executor: SSHExecutor) -> None:
    print("\nTest connection")
    print("-" * 25)

    try:
        host_num = int(input(f"Enter host number (1-{len(host_index)}): "))
    except ValueError:
        print(f"{Config.get_cli_symbol('error')} Enter a valid number")
        return

    if host_num not in host_index:
        print(f"{Config.get_cli_symbol('error')} Invalid host number")
        return

    hostname = host_index[host_num]
    print(f"{Config.get_cli_symbol('search')} Testing connection to {hostname}...")

    result = executor.test_connection(hostname)
    if result["success"]:
        print(f"{Config.get_cli_symbol('success')} Connection successful")
        if result["output"]:
            print(f"Response: {result['output']}")
    else:
        print(f"{Config.get_cli_symbol('error')} Connection error")
        if result["error"]:
            print(f"Error: {result['error']}")


def show_hosts_list(host_index: Dict[int, str], parser: SSHConfigParser) -> None:
    print(f"\n{Config.get_cli_symbol('clipboard')} Full host list")
    print("=" * 50)

    groups = parser.get_grouped_hosts_with_prefix("")
    for group_name in sorted(groups.keys()):
        hosts_in_group = groups[group_name]
        print(
            f"\n{Config.get_cli_symbol('folder')} Group '{group_name}' ({len(hosts_in_group)} hosts):"
        )

        for host in hosts_in_group:
            host_num = next(
                (
                    num
                    for num, indexed_host in host_index.items()
                    if indexed_host == host
                ),
                None,
            )
            host_info = parser.get_host_info(host)
            display_info = ""
            if host_info and "hostname" in host_info:
                display_info = f" ({host_info['hostname']})"

            if host_num is not None:
                print(f"  {host_num:2d}. {host}{display_info}")
            else:
                print(f"   -. {host}{display_info}")


if __name__ == "__main__":
    main()
