#!/usr/bin/env python3

# Выполнение SSH команд и тестирование подключений.

import subprocess
from typing import Dict, Any, Optional

from config import Config

class SSHExecutor:
    # Класс для выполнения SSH команд
    
    def __init__(
        self,
        ssh_config_path: Optional[str] = None,
        *,
        connect_timeout: Optional[int] = None,
        command_timeout: Optional[int] = None,
        batch_mode: Optional[bool] = None,
        strict_host_key_checking: Optional[bool] = None
    ):
        """
        Args:
            ssh_config_path: Путь к SSH config файлу. По умолчанию ~/.ssh/config.
            connect_timeout: Тайм-аут подключения SSH.
            command_timeout: Тайм-аут выполнения команды.
            batch_mode: Признак использования BatchMode.
            strict_host_key_checking: Флаг StrictHostKeyChecking.
        """

        self.ssh_config_path = Config.get_ssh_config_path(ssh_config_path)
        self.connect_timeout = connect_timeout if connect_timeout is not None else Config.SSH_CONNECT_TIMEOUT
        self.command_timeout = command_timeout if command_timeout is not None else Config.SSH_COMMAND_TIMEOUT
        self.batch_mode = Config.SSH_BATCH_MODE if batch_mode is None else batch_mode
        self.strict_host_key_checking = (
            Config.SSH_STRICT_HOST_KEY_CHECKING if strict_host_key_checking is None else strict_host_key_checking
        )
        
    def execute_command(self, hostname: str, command: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        # Выполняем команду на удаленном хосте
        # Args:
        #   hostname: Имя хоста из SSH конфигурации
        #   command: Команда для выполнения
        #   timeout: Тайм-аут выполнения в секундах
        # Returns:
        #   Словарь с результатами выполнения
        effective_timeout = timeout if timeout is not None else self.command_timeout

        try:
            # Формируем SSH команду
            ssh_cmd = [
                'ssh',
                '-F', self.ssh_config_path,
                '-o', f'ConnectTimeout={self.connect_timeout}'
            ]

            if self.batch_mode:
                ssh_cmd.extend(['-o', 'BatchMode=yes'])
            else:
                ssh_cmd.extend(['-o', 'BatchMode=no'])

            ssh_cmd.extend([
                '-o', f'StrictHostKeyChecking={"yes" if self.strict_host_key_checking else "no"}',
                hostname,
                command
            ])

            process = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                timeout=effective_timeout,
                encoding='utf-8',
                errors='replace'
            )
            
            return {
                'success': process.returncode == 0,
                'output': process.stdout.strip() if process.stdout else '',
                'error': process.stderr.strip() if process.stderr else '',
                'return_code': process.returncode,
                'hostname': hostname,
                'command': command
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': f'Тайм-аут выполнения команды ({effective_timeout}с)',
                'return_code': -1,
                'hostname': hostname,
                'command': command
            }
        
        except FileNotFoundError:
            return {
                'success': False,
                'output': '',
                'error': 'SSH клиент не найден. Убедитесь, что OpenSSH установлен.',
                'return_code': -1,
                'hostname': hostname,
                'command': command
            }
        
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': f'Неожиданная ошибка: {str(e)}',
                'return_code': -1,
                'hostname': hostname,
                'command': command
            }
    
    def execute_command_batch(self, hostnames: list, command: str, timeout: Optional[int] = None) -> Dict[str, Dict[str, Any]]:
        # Выполняем команду на нескольких хостах
        # Args:
        #   hostnames: Список имен хостов
        #   command: Команда для выполнения
        #   timeout: Тайм-аут выполнения в секундах
        # Returns:
        #   Словарь с результатами для каждого хоста
        results = {}
        
        for hostname in hostnames:
            results[hostname] = self.execute_command(hostname, command, timeout)
            
        return results
    
    def test_connection(self, hostname: str) -> Dict[str, Any]:
        # Тест подключения к хосту
        # Args:
        #   hostname: Имя хоста
        # Returns:
        #   Результат тестирования подключения
        return self.execute_command(
            hostname,
            'echo "SSH connection test successful"',
            timeout=self.connect_timeout
        )
    
    def get_host_info(self, hostname: str) -> Dict[str, Any]:
        # Базовуя информация о хосте
        # Args:
        #   hostname: Имя хоста
        # Returns:
        #   Информация о хосте
        commands = {
            'hostname': 'hostname',
            'uptime': 'uptime',
            'os': 'uname -a',
            'whoami': 'whoami'
        }
        
        results = {}
        for key, cmd in commands.items():
            result = self.execute_command(hostname, cmd, timeout=self.command_timeout)
            results[key] = result['output'] if result['success'] else f"Ошибка: {result['error']}"
            
        return results

def test_ssh_executor():    
    from config import Config
    
    if Config.TEST_SETTINGS['enable_debug_output']:
        print(f"{Config.get_cli_symbol('rocket')} Тестирование SSH Executor...")
        
        # Создаем экземпляр
        executor = SSHExecutor()
        
        test_hosts = ['localhost']  # Замените на реальные хосты из вашего конфига
        
        for host in test_hosts:
            print(f"\n{Config.get_cli_symbol('search')} Тестирование хоста: {host}")
            
            # Тест подключения
            result = executor.test_connection(host)
            if result['success']:
                print(f"{Config.get_cli_symbol('success')} Подключение успешно: {result['output']}")
                
                # Получаем информацию о хосте
                info = executor.get_host_info(host)
                print(f"{Config.get_cli_symbol('computer')} Информация о хосте:")
                for key, value in info.items():
                    print(f"  {key}: {value}")
                    
            else:
                print(f"{Config.get_cli_symbol('error')} Ошибка подключения: {result['error']}")

if __name__ == "__main__":
    test_ssh_executor()