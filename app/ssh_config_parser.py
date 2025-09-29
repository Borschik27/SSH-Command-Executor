#!/usr/bin/env python3

import os
import re
from typing import Dict, List, Optional
from pathlib import Path

from config import Config

def natural_sort_key(hostname: str) -> tuple:
    # Создаем ключ для естественной сортировки хостов с группировкой
    # Args:
    #   hostname: Имя хоста
    # Returns:
    #   Кортеж для сортировки (группа, натуральный_ключ)
    if not hostname:
        return ('zzz', '')
    
    first_char = hostname[0].lower()

    numeric_group = Config.GROUPING.get('numeric_group_name', 'other')
    special_group = Config.GROUPING.get('special_chars_group_name', 'zzz')

    # Определяем группу по первому символу
    if first_char.isdigit():
        group = numeric_group
    elif first_char.isalpha():
        group = first_char
    else:
        group = special_group

    # Создаем ключ для сортировки внутри группы
    parts = re.split(r'(\d+)', hostname.lower())
    natural_key = []
    
    for part in parts:
        if part.isdigit():
            natural_key.append(int(part))
        else:
            natural_key.append(part)
    
    return (group, natural_key)

def group_hosts_by_first_char(hosts: List[str]) -> Dict[str, List[str]]:
    # Группируем хосты по первому символу
    # Args:
    #   hosts: Список хостов
    # Returns:
    #   Словарь групп {группа: [хосты]}
    groups = {}
    
    for host in hosts:
        if not host:
            continue
            
        first_char = host[0].lower()
        
        if first_char.isdigit():
            group_name = Config.GROUPING.get('numeric_group_name', 'other')
        elif first_char.isalpha():
            group_name = first_char
        else:
            group_name = Config.GROUPING.get('special_chars_group_name', 'zzz')
            
        if group_name not in groups:
            groups[group_name] = []
        groups[group_name].append(host)
    
    # Сортируем хосты внутри каждой группы
    for group_name in groups:
        groups[group_name].sort(key=lambda x: natural_sort_key(x)[1])
    
    return groups

class SSHConfigParser:    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = os.path.expanduser("~/.ssh/config")
        
        self.config_path = Path(config_path)
        self.hosts = {}
        
    def parse_config(self) -> Dict[str, Dict[str, str]]:
        if not self.config_path.exists():
            print(f"SSH config файл не найден: {self.config_path}")
            return {}
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Ошибка чтения файла {self.config_path}: {e}")
            return {}
            
        self.hosts = self._parse_content(content)
        return self.hosts
    
    def _parse_content(self, content: str) -> Dict[str, Dict[str, str]]:
        hosts: Dict[str, Dict[str, str]] = {}
        current_hosts: List[str] = []
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Пропускаем пустые строки и комментарии
            if not line or line.startswith('#'):
                continue
                
            # Обработка Host директивы
            if line.lower().startswith('host '):
                host_names = line[5:].split()
                current_hosts = host_names
                for alias in host_names:
                    hosts[alias] = {'Host': alias}
                continue
                
            # Обработка других директив
            if current_hosts and ' ' in line:
                parts = line.split(None, 1)
                if len(parts) == 2:
                    key, value = parts
                    key_lower = key.lower()
                    for alias in current_hosts:
                        hosts[alias][key_lower] = value
                    
        return hosts
    
    def get_hosts_with_prefix(self, prefix: str = '') -> List[str]:
        if not self.hosts:
            self.parse_config()
            
        if not prefix:
            # Возвращаем все хосты, если префикс не указан
            hosts = list(self.hosts.keys())
        else:
            hosts = [host for host in self.hosts.keys() 
                    if host.lower().startswith(prefix.lower())]
        
        # Используем улучшенную сортировку
        return sorted(hosts, key=natural_sort_key)
    
    def get_grouped_hosts_with_prefix(self, prefix: str = '') -> Dict[str, List[str]]:
        hosts = self.get_hosts_with_prefix(prefix)
        return group_hosts_by_first_char(hosts)
    
    def get_host_info(self, hostname: str) -> Optional[Dict[str, str]]:
        if not self.hosts:
            self.parse_config()
            
        return self.hosts.get(hostname)
    
    def get_all_hosts(self) -> List[str]:

        if not self.hosts:
            self.parse_config()
            
        return sorted(list(self.hosts.keys()), key=natural_sort_key)

if __name__ == "__main__":
    from config import Config
    
    # Тестирование парсера с использованием параметров из конфигурации
    parser = SSHConfigParser()
    
    # Тест с префиксом из конфигурации
    test_prefix = Config.TEST_SETTINGS['test_prefix']
    test_hosts = parser.get_hosts_with_prefix(test_prefix)
    host_limit = Config.TEST_SETTINGS['test_host_limit']
    
    if Config.TEST_SETTINGS['enable_debug_output']:
        print(f"Хосты с префиксом '{test_prefix}':", 
              test_hosts[:host_limit], 
              f"... (всего {len(test_hosts)})")
    
        # Тест всех хостов с группировкой
        all_groups = parser.get_grouped_hosts_with_prefix('')
        print(f"\nВсе хосты по группам (всего групп: {len(all_groups)}):")
        
        group_limit = Config.TEST_SETTINGS['test_group_limit']
        for group_name in sorted(all_groups.keys()):
            hosts_in_group = all_groups[group_name]
            print(f"Группа '{group_name}': {hosts_in_group[:group_limit]}... ({len(hosts_in_group)} хостов)")
        
        if test_hosts:
            # Показываем информацию о первом хосте
            info = parser.get_host_info(test_hosts[0])
            print(f"\nИнформация о {test_hosts[0]}:", info)