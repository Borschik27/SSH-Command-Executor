#!/usr/bin/env python3
# Компонент консольного интерфейса Command Executor.

from typing import Dict, List

from config import Config
from ssh_config_parser import SSHConfigParser
from ssh_executor import SSHExecutor


def main(args=None):
    # Точка входа CLI-версии.
    prefix = args.prefix if args and hasattr(args, "prefix") else ""
    raw_config_path = args.config if args and hasattr(args, "config") else None
    config_path = Config.get_ssh_config_path(raw_config_path)
    timeout = args.timeout if args and hasattr(args, "timeout") else Config.SSH_COMMAND_TIMEOUT
    connect_timeout = (
        args.connect_timeout if args and hasattr(args, "connect_timeout") else Config.SSH_CONNECT_TIMEOUT
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

    print(f"\n{Config.get_cli_symbol('folder')} Доступные группы хостов:")
    all_groups = parser.get_grouped_hosts_with_prefix("")
    if all_groups:
        for group_name in sorted(all_groups.keys()):
            hosts_count = len(all_groups[group_name])
            print(f"{Config.get_cli_symbol('folder')} Группа '{group_name}' ({hosts_count} хостов)")
    else:
        print(f"{Config.get_cli_symbol('error')} Группы не найдены")

    if not prefix:
        print("\nНастройка фильтра хостов")
        prefix = input("Введите префикс хостов (Enter для всех хостов): ").strip()
    else:
        print(f"\nИспользуется префикс из аргументов: '{prefix}'")

    print(f"\n{Config.get_cli_symbol('satellite')} Загрузка хостов...")
    groups = parser.get_grouped_hosts_with_prefix(prefix)

    if not groups:
        if prefix:
            print(Config.get_message("hosts_with_prefix_not_found", prefix=prefix, config_path=config_path))
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
        print(f"{Config.get_cli_symbol('folder')} Группа '{group_name}' ({len(hosts_in_group)} хостов)")
        for host in hosts_in_group:
            host_index[index] = host
            index += 1

    print(Config.get_message("total_hosts_info", total=len(parser.get_all_hosts())))
    print("\n" + separator)

    while True:
        print("\nВыберите действие:")
        print("1. Выполнить команду на выбранных хостах")
        print("2. Показать информацию о хосте")
        print("3. Тестировать подключение")
        print("4. Показать список хостов")
        print("0. Выход")

        try:
            choice = input("\nВведите номер действия: ").strip()

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
                print(f"{Config.get_cli_symbol('error')} Неверный выбор. Попробуйте еще раз.")

        except KeyboardInterrupt:
            print(f"\n\n{Config.get_cli_symbol('wave')} Выход по Ctrl+C")
            break
        except Exception as exc:  # pragma: no cover - защита от неожиданных ошибок CLI
            print(f"{Config.get_cli_symbol('error')} Ошибка: {exc}")


def parse_host_range(user_input, hosts_list):
    # Парсит диапазон номеров хостов из пользовательского ввода.
    hosts: List[int] = []
    max_hosts = len(hosts_list)

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
                print(f"{Config.get_cli_symbol('error')} Неверный диапазон: {part}")
        else:
            try:
                hosts.append(int(part))
            except ValueError:
                print(f"{Config.get_cli_symbol('error')} Неверный номер хоста: {part}")

    valid_hosts = [h for h in hosts if 1 <= h <= max_hosts]
    return sorted(set(valid_hosts))


def execute_command_on_hosts(host_index: Dict[int, str], executor: SSHExecutor) -> None:
    print(f"\n{Config.get_cli_symbol('rocket')} Выполнение команды на хостах")
    print("-" * 40)

    if not host_index:
        print(f"{Config.get_cli_symbol('error')} Нет доступных хостов")
        return

    print(f"Доступно хостов: 1-{len(host_index)}")
    host_input = input("Введите номера хостов (например: 1,3,5-8): ").strip()

    if not host_input:
        print(f"{Config.get_cli_symbol('error')} Не выбраны хосты")
        return

    selected_numbers = parse_host_range(host_input, len(host_index))
    if not selected_numbers:
        print(f"{Config.get_cli_symbol('error')} Некорректные номера хостов")
        return

    selected_hosts = [host_index[i] for i in selected_numbers]

    print(f"{Config.get_cli_symbol('success')} Выбрано хостов: {len(selected_hosts)}")
    for idx, host in enumerate(selected_hosts, 1):
        print(f"  {idx}. {host}")

    command = input("\nВведите команду для выполнения: ").strip()
    if not command:
        print(f"{Config.get_cli_symbol('error')} Команда не введена")
        return

    use_sudo = input("Использовать sudo? (y/N): ").strip().lower() == "y"
    if use_sudo and not command.startswith("sudo "):
        command = f"sudo {command}"

    print(f"\n{Config.get_cli_symbol('target')} Выполнение команды: {command}")
    print(f"{Config.get_cli_symbol('satellite')} На хостах: {', '.join(selected_hosts)}")
    print("=" * Config.CLI_SEPARATOR_LENGTH)

    for idx, host in enumerate(selected_hosts, 1):
        print(f"\n[{idx}/{len(selected_hosts)}] 🖥️  {host}")
        print("-" * 30)
        try:
            result = executor.execute_command(host, command)
            if result["success"]:
                print(f"{Config.get_cli_symbol('success')} Успешно (код возврата: {result['return_code']})")
                if result["output"]:
                    print("Вывод:")
                    print(result["output"])
                if result["error"]:
                    print("Предупреждения:")
                    print(result["error"])
            else:
                print(f"{Config.get_cli_symbol('error')} Ошибка (код возврата: {result['return_code']})")
                if result["error"]:
                    print("Ошибка:")
                    print(result["error"])
        except Exception as exc:  # pragma: no cover - защита от неожиданных ошибок выполнения
            print(f"{Config.get_cli_symbol('error')} Исключение: {exc}")

    print(Config.get_message("execution_finish", count=len(selected_hosts)))


def show_host_info(host_index: Dict[int, str], parser: SSHConfigParser) -> None:
    print(f"\n{Config.get_cli_symbol('clipboard')} Информация о хосте")
    print("-" * 30)

    try:
        host_num = int(input(f"Введите номер хоста (1-{len(host_index)}): "))
    except ValueError:
        print(f"{Config.get_cli_symbol('error')} Введите корректный номер")
        return

    if host_num not in host_index:
        print(f"{Config.get_cli_symbol('error')} Неверный номер хоста")
        return

    hostname = host_index[host_num]
    info = parser.get_host_info(hostname)

    print(f"\n{Config.get_cli_symbol('computer')} Хост: {hostname}")
    print("=" * 40)

    if info:
        for key, value in info.items():
            print(f"{key:15s}: {value}")
    else:
        print("Информация о хосте не найдена")


def test_host_connection(host_index: Dict[int, str], executor: SSHExecutor) -> None:
    print("\nТест подключения")
    print("-" * 25)

    try:
        host_num = int(input(f"Введите номер хоста (1-{len(host_index)}): "))
    except ValueError:
        print(f"{Config.get_cli_symbol('error')} Введите корректный номер")
        return

    if host_num not in host_index:
        print(f"{Config.get_cli_symbol('error')} Неверный номер хоста")
        return

    hostname = host_index[host_num]
    print(f"{Config.get_cli_symbol('search')} Тестирование подключения к {hostname}...")

    result = executor.test_connection(hostname)
    if result["success"]:
        print(f"{Config.get_cli_symbol('success')} Подключение успешно")
        if result["output"]:
            print(f"Ответ: {result['output']}")
    else:
        print(f"{Config.get_cli_symbol('error')} Ошибка подключения")
        if result["error"]:
            print(f"Ошибка: {result['error']}")


def show_hosts_list(host_index: Dict[int, str], parser: SSHConfigParser) -> None:
    print(f"\n{Config.get_cli_symbol('clipboard')} Полный список хостов")
    print("=" * 50)

    groups = parser.get_grouped_hosts_with_prefix("")
    for group_name in sorted(groups.keys()):
        hosts_in_group = groups[group_name]
        print(f"\n{Config.get_cli_symbol('folder')} Группа '{group_name}' ({len(hosts_in_group)} хостов):")

        for host in hosts_in_group:
            host_num = next((num for num, indexed_host in host_index.items() if indexed_host == host), None)
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
