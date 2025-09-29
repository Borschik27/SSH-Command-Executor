#!/usr/bin/env python3

# Command Executor CLI Arguments

import argparse
import sys
from config import Config

def create_parser():
    # Парсер аргументов командной строки
    parser = argparse.ArgumentParser(
        prog='command-executor',
        description=Config.APP_DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,  # Отключаем стандартную помощь
        epilog=f"""
Примеры использования:
  {sys.argv[0]}                    # Автоматический выбор GUI/CLI
  {sys.argv[0]} --gui              # Принудительный запуск GUI
  {sys.argv[0]} --cli              # Принудительный запуск CLI
  {sys.argv[0]} --prefix web       # Фильтр хостов по префиксу
  {sys.argv[0]} --config custom    # Использовать другой SSH config
  {sys.argv[0]} --version          # Показать версию

Файлы проекта:
    main.py                        - Точка входа (авто-выбор GUI/CLI)
    command_executor_gui_app.py    - Реализация GUI
    command_executor_cli_app.py    - Реализация CLI
    config.py                      - Конфигурационные настройки
    ssh_config_parser.py           - Парсер SSH конфигурации
    ssh_executor.py                - Выполнение SSH команд

{Config.APP_NAME} v{Config.APP_VERSION}
        """.strip()
    )
    
    # Добавляем кастомную опцию помощи
    parser.add_argument(
        '-h', '--help',
        action='help',
        help='Помощь'
    )
    
    # Основные режимы работы
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--gui', 
        action='store_true',
        help='Принудительный запуск GUI версии'
    )
    mode_group.add_argument(
        '--cli', 
        action='store_true',
        help='Принудительный запуск CLI версии'
    )
    
    # Настройки SSH
    parser.add_argument(
        '--config', '-c',
        metavar='PATH',
        default=Config.DEFAULT_SSH_CONFIG_PATH,
        help=f'Путь к SSH config файлу (по умолчанию: {Config.DEFAULT_SSH_CONFIG_PATH})'
    )
    
    # Фильтрация
    parser.add_argument(
        '--prefix', '-p',
        metavar='PREFIX',
        default='',
        help='Префикс для фильтрации хостов (по умолчанию: все хосты)'
    )
    
    # Настройки выполнения
    parser.add_argument(
        '--timeout', '-t',
        type=int,
        metavar='SECONDS',
        default=Config.SSH_COMMAND_TIMEOUT,
        help=f'Тайм-аут выполнения команд в секундах (по умолчанию: {Config.SSH_COMMAND_TIMEOUT})'
    )
    
    parser.add_argument(
        '--connect-timeout',
        type=int,
        metavar='SECONDS', 
        default=Config.SSH_CONNECT_TIMEOUT,
        help=f'Тайм-аут подключения SSH в секундах (по умолчанию: {Config.SSH_CONNECT_TIMEOUT})'
    )
    
    # Отладка и информация
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Подробный вывод (включено по умолчанию в GUI)'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Режим отладки'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'{Config.APP_NAME} v{Config.APP_VERSION}',
        help='Показать версию программы'
    )
    
    # Тестирование
    parser.add_argument(
        '--test-config',
        action='store_true',
        help='Проверить SSH конфигурацию'
    )
    
    parser.add_argument(
        '--list-hosts',
        action='store_true', 
        help='Показать список хостов'
    )
    
    return parser

def parse_args(args=None):
    # Парсит аргументы командной строки
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    # Валидация аргументов
    try:
        if parsed_args.prefix:
            parsed_args.prefix = Config.validate_prefix(parsed_args.prefix)
    except ValueError as e:
        parser.error(f"Ошибка в префиксе: {e}")
    
    if parsed_args.timeout <= 0:
        parser.error("Тайм-аут должен быть положительным числом")
    
    if parsed_args.connect_timeout <= 0:
        parser.error("Тайм-аут подключения должен быть положительным числом")
    
    return parsed_args

def show_usage_examples():
    # Показывает примеры использования
    print(f"""
{Config.APP_NAME} v{Config.APP_VERSION} - Примеры использования:

ОСНОВНЫЕ КОМАНДЫ:
  python3 main.py                      # Автоматический выбор интерфейса
  python3 main.py --gui                # Графический интерфейс
  python3 main.py --cli                # Консольный интерфейс

ФИЛЬТРАЦИЯ ХОСТОВ:
  python3 main.py --prefix web         # Только хосты начинающиеся с 'web'
  python3 main.py --prefix prod        # Только хосты начинающиеся с 'prod'
  python3 main.py -p db                # Сокращенная форма префикса

НАСТРОЙКИ SSH:
  python3 main.py --config ~/.ssh/prod # Использовать другой SSH config
  python3 main.py --timeout 60         # Тайм-аут команд 60 секунд
  python3 main.py --connect-timeout 5  # Тайм-аут подключения 5 секунд

ДИАГНОСТИКА:
  python3 main.py --test-config        # Проверить SSH конфигурацию
  python3 main.py --list-hosts         # Показать все доступные хосты
  python3 main.py --debug              # Режим отладки
  python3 main.py --verbose            # Подробный вывод

КОМБИНАЦИИ:
  python3 main.py --cli --prefix web --verbose
  python3 main.py --gui --config ~/.ssh/test --debug

ФАЙЛЫ ПРОЕКТА:
    main.py                        - Главный файл с авто-выбором интерфейса
    command_executor_gui_app.py    - Реализация GUI (tkinter)
    command_executor_cli_app.py    - Реализация CLI (консоль)
    config.py                      - Настройки и конфигурация
    ssh_config_parser.py           - Парсер SSH конфигурации
    ssh_executor.py                - Выполнение SSH команд
    run_gui.sh                     - Скрипт запуска
    """.strip())

if __name__ == "__main__":
    from config import Config
    
    if Config.TEST_SETTINGS['enable_debug_output']:
        # Тест парсера аргументов
        args = parse_args()
        print(f"{Config.get_cli_symbol('wrench')} Разобранные аргументы:")
        for key, value in vars(args).items():
            print(f"  {key}: {value}")