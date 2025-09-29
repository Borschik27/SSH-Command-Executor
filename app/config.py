#!/usr/bin/env python3

import os
from pathlib import Path

class Config:    
    # Основные настройки
    APP_NAME = "Command Executor"
    APP_VERSION = "0.1"
    APP_DESCRIPTION = "Инструмент для выполнения SSH команд с графическим и консольным интерфейсами"

    # Настройки SSH
    DEFAULT_SSH_CONFIG_PATH = os.path.expanduser("~/.ssh/config")
    SSH_CONNECT_TIMEOUT = 10
    SSH_COMMAND_TIMEOUT = 30
    SSH_BATCH_MODE = True
    SSH_STRICT_HOST_KEY_CHECKING = False
    
    # GUI настройки
    GUI_WINDOW_TITLE = f"{APP_NAME} - Запуск SSH команд"
    GUI_WINDOW_GEOMETRY = "1000x700"
    GUI_WINDOW_MIN_WIDTH = 800
    GUI_WINDOW_MIN_HEIGHT = 600
    
    # Размеры колонок дерева хостов
    GUI_TREE_HOST_COLUMN_WIDTH = 250
    GUI_TREE_HOST_COLUMN_MIN_WIDTH = 200
    GUI_TREE_CHECKBOX_COLUMN_WIDTH = 30
    GUI_TREE_CHECKBOX_COLUMN_MIN_WIDTH = 30
    
    # Настройки полей ввода
    GUI_PREFIX_ENTRY_WIDTH = 10
    GUI_COMMAND_ENTRY_FONT = ('Consolas', 10)
    GUI_RESULTS_TEXT_FONT = ('Consolas', 9)
    GUI_TITLE_FONT = ('Arial', 16, 'bold')
    GUI_INFO_DIALOG_FONT = ('Consolas', 10)
    GUI_INFO_DIALOG_TITLE_FONT = ('Arial', 14, 'bold')
    
    # Отступы и интервалы
    GUI_MAIN_PADDING = "10"
    GUI_FRAME_PADDING = "5"
    GUI_BUTTON_PADX = (0, 5)
    GUI_CONTROL_PANEL_PADY = (10, 0)
    
    # Цвета и стили
    GUI_COLORS = {
        'selected_host_bg': '#e3f2fd',
        'selected_host_fg': '#1976d2',
        'unselected_host_bg': 'white',
        'unselected_host_fg': 'black',
        'group_bg': '#f5f5f5',
        'group_fg': '#666666',
        'status_ready': 'green',
        'status_working': 'orange',
        'status_error': 'red',
        'status_info': 'blue'
    }
    
    # CLI настройки
    CLI_SEPARATOR_LENGTH = 60
    CLI_HOST_NUMBER_WIDTH = 2
    CLI_HOST_INFO_KEY_WIDTH = 15
    
    # Символы интерфейса
    SYMBOLS = {
        'unchecked': '☐',
        'checked': '☑',
        'checkbox_header': '☑',
        'success': '[OK]',
        'error': '[ERROR]',
        'warning': '[!]',
        'info': '[i]',
        'rocket': '>>',
        'computer': 'PC',
        'folder': '[+]',
        'target': '*',
        'satellite': '>>',
        'chart': '#',
        'wave': 'bye',
        'refresh': '~',
        'search': '?',
        'link': '->',
        'clipboard': '[]',
        'wrench': 'cfg',
        'finish': '[DONE]',
        'scroll': '...'
    }
    
    # Сообщения
    MESSAGES = {
        'gui_startup': f"{SYMBOLS['rocket']} Запуск GUI версии {APP_NAME}...",
        'cli_startup': f"{SYMBOLS['warning']} GUI (tkinter) недоступен, запуск консольной версии...",
        'cli_fallback': f"{SYMBOLS['refresh']} Попытка запуска консольной версии...",
        'hosts_not_found': "{warning} Хосты не найдены в {config_path}",
        'hosts_with_prefix_not_found': "{warning} Хосты с префиксом '{prefix}' не найдены в {config_path}",
        'hosts_loaded': "{success} Загружено {count} хостов в {groups} группах",
        'hosts_loaded_with_prefix': "{success} Загружено {count} хостов с префиксом '{prefix}' в {groups} группах",
        'total_hosts_info': "{chart} Всего хостов в конфигурации: {total}",
        'ready_status': "Готов к работе",
        'execution_status': "Выполнение команд...",
        'testing_connection': "{search} Тестирование подключения к {hostname}...",
        'connection_success': "{success} Подключение успешно",
        'connection_error': "{error} Ошибка подключения",
        'execution_start': "{rocket} Выполнение команды: {command}",
        'execution_hosts': "{satellite} На хостах: {hosts}",
        'execution_finish': "{finish} Выполнение завершено на {count} хостах",
        'goodbye': f"{SYMBOLS['wave']} До свидания!",
        'goodbye_cli': f"{SYMBOLS['wave']} Выход по Ctrl+C"
    }
    
    # Настройки по умолчанию
    DEFAULTS = {
        'verbose_output': True,
        'sudo_enabled': False,
        'tree_groups_expanded': True,
        'prefix_filter': "",
        'command_history_size': 50
    }
    
    # Настройки тестирования (используются в if __name__ == "__main__" блоках)
    TEST_SETTINGS = {
        'test_prefix': '',  # Префикс для тестирования парсера
        'test_host_limit': 5,  # Максимум хостов для показа в тестах
        'test_group_limit': 3,  # Максимум хостов в группе для показа
        'enable_debug_output': True,
        'test_command': 'echo "SSH connection test successful"'
    }
    
    # Валидация
    VALIDATION = {
        'max_prefix_length': 50,
        'max_command_length': 1000,
        'max_hostname_length': 253,  # rfc
        'max_concurrent_connections': 50
    }
    
    # Группировка хостов
    GROUPING = {
        'numeric_group_name': 'other',
        'special_chars_group_name': 'zzz',
        'default_group_sort_priority': 999
    }
    
    @classmethod
    def get_ssh_config_path(cls, custom_path=None):
        # Путь к SSH конфигурации
        if custom_path:
            return os.path.expanduser(custom_path)
        return cls.DEFAULT_SSH_CONFIG_PATH
    
    @classmethod
    def validate_prefix(cls, prefix):
        if len(prefix) > cls.VALIDATION['max_prefix_length']:
            raise ValueError(f"Префикс слишком длинный (максимум {cls.VALIDATION['max_prefix_length']} символов)")
        return prefix.strip()
    
    @classmethod
    def validate_command(cls, command):
        if len(command) > cls.VALIDATION['max_command_length']:
            raise ValueError(f"Команда слишком длинная (максимум {cls.VALIDATION['max_command_length']} символов)")
        return command.strip()
    
    @classmethod
    def get_symbol(cls, name, use_emoji=False):
        # Символ по имени
        return cls.SYMBOLS.get(name, '')
    
    @classmethod
    def get_gui_symbol(cls, name):
        # Символ для GUI
        return cls.get_symbol(name)
    
    @classmethod
    def get_cli_symbol(cls, name):
        # Символ для CLI
        return cls.get_symbol(name)
    
    @classmethod
    def get_message(cls, name, **kwargs):
        # Cообщение с подстановкой параметров
        template = cls.MESSAGES.get(name, '')
        if not template:
            return ''

        context = dict(cls.SYMBOLS)
        context.update({
            'config_path': cls.DEFAULT_SSH_CONFIG_PATH,
            'default_path': cls.DEFAULT_SSH_CONFIG_PATH,
            'app_name': cls.APP_NAME
        })
        context.update(kwargs)

        try:
            return template.format(**context)
        except KeyError:
            return template
    
    @classmethod
    def get_color(cls, name):
        # Цвет по имени
        return cls.GUI_COLORS.get(name, 'black')