#!/usr/bin/env python3

import sys
import os
from config import Config
from cli_args import parse_args, show_usage_examples

def test_ssh_config(config_path):
    # Тест SSH конфигурации
    try:
        from ssh_config_parser import SSHConfigParser
        
        print(f"{Config.get_symbol('search')} Проверка SSH конфигурации: {config_path}")
        
        if not os.path.exists(config_path):
            print(f"{Config.get_symbol('error')} Файл не найден: {config_path}")
            return False
            
        parser = SSHConfigParser(config_path)
        hosts = parser.get_all_hosts()
        
        if not hosts:
            print(f"{Config.get_symbol('warning')} Хосты не найдены в конфигурации")
            return False
            
        print(f"{Config.get_symbol('success')} Найдено {len(hosts)} хостов")
        
        # Показываем группировку
        groups = parser.get_grouped_hosts_with_prefix("")
        print(f"{Config.get_symbol('folder')} Группы хостов:")
        for group_name in sorted(groups.keys()):
            print(f"  {group_name}: {len(groups[group_name])} хостов")
            
        return True
        
    except Exception as e:
        print(f"{Config.get_symbol('error')} Ошибка проверки конфигурации: {e}")
        return False

def list_hosts(config_path, prefix=""):
    # Список хостов
    try:
        from ssh_config_parser import SSHConfigParser
        
        parser = SSHConfigParser(config_path)
        groups = parser.get_grouped_hosts_with_prefix(prefix)
        
        if not groups:
            if prefix:
                print(f"{Config.get_symbol('warning')} Хосты с префиксом '{prefix}' не найдены")
            else:
                print(f"{Config.get_symbol('warning')} Хосты не найдены")
            return
            
        total_hosts = sum(len(hosts) for hosts in groups.values())
        
        if prefix:
            print(f"{Config.get_symbol('satellite')} Хосты с префиксом '{prefix}' ({total_hosts} найдено):")
        else:
            print(f"{Config.get_symbol('satellite')} Все хосты ({total_hosts} найдено):")
            
        for group_name in sorted(groups.keys()):
            hosts_in_group = groups[group_name]
            print(f"\n{Config.get_symbol('folder')} Группа '{group_name}' ({len(hosts_in_group)} хостов):")
            
            for host in hosts_in_group:
                host_info = parser.get_host_info(host)
                if host_info and 'hostname' in host_info:
                    print(f"  {host} ({host_info['hostname']})")
                else:
                    print(f"  {host}")
                    
    except Exception as e:
        print(f"{Config.get_symbol('error')} Ошибка получения списка хостов: {e}")

def start_gui(args):
    # GUI
    try:
        import tkinter as tk
        from command_executor_gui_app import CommandExecutorApp

        print(Config.get_message('gui_startup'))

        root = tk.Tk()
        app = CommandExecutorApp(root, args)
        root.mainloop()
        
    except ImportError:
        print(Config.get_message('cli_startup'))
        start_cli(args)
    except Exception as e:
        if args.debug:
            import traceback
            traceback.print_exc()
        print(f"{Config.get_symbol('error')} Ошибка запуска GUI версии: {str(e)}")
        print(Config.get_message('cli_fallback'))
        start_cli(args)

def start_cli(args):
    # CLI
    try:
        from command_executor_cli_app import main as cli_main
        cli_main(args)
    except Exception as e:
        if args.debug:
            import traceback
            traceback.print_exc()
        print(f"{Config.get_symbol('error')} Ошибка запуска консольной версии: {str(e)}")
        sys.exit(1)

def main():
    args = parse_args()
    
    if args.debug:
        print(f"{Config.get_symbol('wrench')} Режим отладки активен")
        print(f"Аргументы: {vars(args)}")
    
    # Специальные команды
    if args.test_config:
        success = test_ssh_config(args.config)
        sys.exit(0 if success else 1)
        
    if args.list_hosts:
        list_hosts(args.config, args.prefix)
        sys.exit(0)
    
    # Выбор интерфейса
    if args.gui:
        start_gui(args)
    elif args.cli:
        start_cli(args)
    else:
        # Автоматический выбор
        start_gui(args)

if __name__ == "__main__":
    main()