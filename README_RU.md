# SSH Command Executor

Инструмент для выполнения SSH команд с графическим и консольным интерфейсами

## Основные возможности

- **Группировка хостов**: Автоматическая группировка хостов по первому символу с естественной сортировкой
- **Централизованная конфигурация**: Все настройки управляются в config.py
- **Защита безопасности**: Встроенное обнаружение опасных команд и диалоги подтверждения
- **Логирование команд**: Автоматический аудит всех SSH операций
- **Поддержка --help**: Полная поддержка аргументов командной строки с помощью
- **Фильтрация по префиксу**: Фильтрация хостов по префиксному шаблону
- **Чекбоксы**: Выбор отдельных хостов или целых групп
- **GUI версия**: Графический интерфейс с диалогами и подтверждениями
- **CLI версия**: Консольный интерфейс с интерактивными запросами безопасности
- **Автоматический переход**: GUI → CLI когда tkinter недоступен
- **Пакетное выполнение**: Команды на нескольких хостах одновременно
- **Информация о хостах**: Просмотр SSH конфигурации для каждого хоста
- **Тестирование подключения**: Проверка доступности и подключения хостов
- **Кнопка Stop (GUI)**: Прерывание выполнения команды на оставшихся хостах
- **Задержка между хостами**: Настраиваемая пауза между выполнением на хостах (0-600 секунд)
- **Многострочные команды**: Поддержка heredoc и сложных команд
- **Поддержка EOF**: Шаблоны heredoc для передачи многострочного текста

## Функции безопасности

- **Обнаружение опасных команд**: Автоматическая блокировка потенциально разрушительных команд
  - `rm -rf`, `dd if=`, `mkfs`, `format`, `chmod 777` и т.д.
- **Диалоги подтверждения**: Интерактивное подтверждение для системных команд
  - `sudo`, `systemctl`, `service`, `mount`, `umount` и т.д.
- **Аудит-логирование**: Полное логирование всех выполнений команд
  - Расположение: `~/.ssh/command_executor_logs/`
  - Формат: `ssh_commands_YYYY-MM-DD.log`
- **Настраиваемые политики безопасности**: Централизованные правила безопасности в config.py

## GUI возможности

- Чекбоксы для выбора хостов и групп
- Алфавитная группировка хостов с естественной сортировкой
- Фильтрация по префиксу с кнопкой очистки
- Кнопки "Select All" / "Deselect All"
- Кнопки "Expand All" / "Collapse All" для групп
- Контекстное меню (правый клик)
- Диалог информации о хосте (двойной клик)
- Выполнение команд с опцией sudo
- Режимы детального/краткого вывода
- Диалоги подтверждения безопасности
- Блокировка опасных команд с объяснениями

## Использование

### Базовые команды

```bash
# Автоматический выбор интерфейса (GUI или CLI)
python3 app/main.py

# Принудительный режим GUI
python3 app/main.py --gui

# Принудительный режим CLI
python3 app/main.py --cli

# Полная справка по всем параметрам
python3 app/main.py --help

# Запуск через shell скрипт (автоопределение GUI/CLI)
./run.sh
```

Вы также можете запустить приложение в Windows используя PowerShell:

1. Установите Python 3.6+ с [python.org](https://www.python.org/downloads/)
2. Выполните команды PowerShell:

```powershell
# Запуск в Windows (PowerShell)
PS > cd "$env:USERPROFILE\path\to\project"
PS > py -3.11 .\app\main.py --config "$env:USERPROFILE\path\to\config" --gui
```

> Замените `-3.11` на флаг версии, соответствующий вашей локальной установке Python.

### Команды с параметрами

```bash
# Фильтрация хостов по префиксу
python3 app/main.py --prefix web
python3 app/main.py -p prod

# Использование другого SSH конфига
python3 app/main.py --config ~/.ssh/production

# Настройки таймаута
python3 app/main.py --timeout 60 --connect-timeout 5

# Задержка между хостами
python3 app/main.py --delay 10

# Режим отладки
python3 app/main.py --debug

# Проверка SSH конфигурации
python3 app/main.py --test-config

# Список хостов
python3 app/main.py --list-hosts

# Информация о версии
python3 app/main.py --version
```

### Использование GUI

1. Запустите `python3 app/main.py --gui`
2. Введите префикс для фильтрации хостов (или оставьте пустым)
3. Выберите хосты через чекбоксы
4. Введите команду в текстовое поле
5. Настройте опции (sudo, verbose, delay)
6. Нажмите "Execute Command" или Ctrl+Enter
7. Используйте кнопку "Stop" для прерывания выполнения

### Использование CLI

1. Запустите `python3 app/main.py --cli`
2. Введите префикс при запросе (или Enter для всех хостов)
3. Выберите действие из меню
4. Следуйте инструкциям для выполнения команды
5. Подтвердите запросы безопасности при необходимости

### Управление хостами

- **Чекбоксы хостов**: Клик по чекбоксу для выбора/снятия выбора хоста
- **Чекбоксы групп**: Клик для выбора/снятия выбора всей группы
- **Двойной клик**: Показывает диалог информации о хосте
- **Правый клик**: Контекстное меню с дополнительными действиями
- **Сворачивание групп**: Кнопки "Expand All" / "Collapse All"

## Конфигурация

Все настройки находятся в `config.py`:

- **Настройки GUI**: размеры окон, шрифты, цвета
- **Параметры SSH**: таймауты, пути конфигурации
- **Политики безопасности**: опасные команды, требования подтверждения
- **Настройки логирования**: расположение и формат аудит-лога
- **Символы интерфейса**: чекбоксы, иконки
- **Сообщения**: тексты уведомлений
- **Значения по умолчанию**: начальные настройки

Для изменения настроек отредактируйте соответствующие значения в `config.py`.

## Конфигурация безопасности

Политики безопасности можно настроить в `config.py`:

```python
SECURITY = {
    "dangerous_commands": [
        "rm -rf", "dd if=", "mkfs", "format", ...
    ],
    "require_confirmation": [
        "sudo", "systemctl", "service", "mount", ...
    ]
}
```

## Архитектура проекта

```
linux-bash-ssh/
├── app/                                  # Основное приложение
│   ├── main.py                          # Точка входа (157 строк)
│   ├── config.py                        # Конфигурация (299 строк)
│   ├── cli_args.py                      # Обработка аргументов (149 строк)
│   ├── ssh_config_parser.py             # Парсер SSH конфига (212 строк)
│   ├── ssh_executor.py                  # Выполнение SSH команд (263 строки)
│   ├── command_executor_cli_app.py      # CLI интерфейс (455 строк)
│   └── command_executor_gui_app.py      # GUI интерфейс (1226 строк)
├── tests/                                # Тесты (23 теста)
│   ├── __init__.py
│   ├── config_test.py                   # Тестовые данные (175 строк)
│   ├── test_config.py                   # Тесты конфигурации (334 строки)
│   ├── test_config_security.py          # Тесты безопасности (67 строк)
│   ├── test_parse_host_range.py         # Тесты парсинга диапазонов (95 строк)
│   └── test_ssh_config_parser.py        # Тесты парсера SSH (61 строка)
├── README.md                             # Документация (английский)
├── README_RU.md                          # Документация (русский)
├── EOF_USAGE.md                          # Руководство по heredoc
└── run.sh                                # Скрипт запуска
```

### Модули приложения

- `main.py` - Главная точка входа с поддержкой аргументов командной строки
- `config.py` - Централизованная конфигурация всех настроек
- `cli_args.py` - Обработка аргументов командной строки
- `command_executor_gui_app.py` - Реализация GUI с диалогами безопасности
- `command_executor_cli_app.py` - Реализация CLI с запросами безопасности
- `ssh_config_parser.py` - Парсер SSH конфигурации с группировкой
- `ssh_executor.py` - Выполнение SSH команд с логированием и проверками безопасности
- `run.sh` - Скрипт автоматического запуска

### Тестирование

```bash
# Запуск всех тестов
python3 -m unittest discover tests/ -v

# Запуск отдельного теста
python3 tests/test_config.py
python3 tests/test_config_security.py
python3 tests/test_parse_host_range.py
python3 tests/test_ssh_config_parser.py
```

**Покрытие тестами:**
- `test_config.py`: 13 тестов - проверка конфигурации, настроек, методов
- `test_config_security.py`: 4 теста - проверка безопасности, опасных команд
- `test_parse_host_range.py`: 5 тестов - парсинг диапазонов хостов (1-5, 3,7 и т.д.)
- `test_ssh_config_parser.py`: 1 тест - исключение паттерн-хостов

**Итого: 23 теста, все проходят успешно**

## Примеры использования

```bash
# Быстрый старт
python3 app/main.py

# Работа с конкретными хостами
python3 app/main.py --prefix web --gui

# Отладка проблем
python3 app/main.py --debug --test-config

# Пакетные операции с безопасностью
python3 app/main.py --cli --prefix prod --verbose

# Проверка доступности хостов
python3 app/main.py --cli --prefix db
# Выберите действие: 3. Test connection
```

## Примеры безопасности

### Опасная команда (блокируется)

```bash
Команда: rm -rf /
Результат: ЗАБЛОКИРОВАНА - "Command contains potentially dangerous pattern: 'rm -rf'"
```

### Системная команда (требует подтверждения)

```bash
Команда: sudo systemctl restart nginx
GUI: Показывает диалог подтверждения со списком хостов
CLI: Запрашивает "Continue execution? (y/N)"
```

## Формат SSH конфигурации

Приложение читает стандартный `~/.ssh/config`:

```
# Группа серверов 'web'
Host web1
    HostName 192.168.1.10
    User admin
    Port 22
    IdentityFile ~/.ssh/web_key

Host web2
    HostName 192.168.1.11
    User admin

# Группа серверов 'db'
Host db1
    HostName 192.168.2.10
    User dbadmin

# Паттерн-хосты (игнорируются приложением)
Host *.internal
    User root
```

**Особенности:**
- Хосты группируются по первому символу/цифре
- Паттерн-хосты (с `*`) исключаются из списка
- Поддерживается естественная сортировка (host1, host2, host10)
- Все параметры SSH конфига учитываются при подключении

## Логирование

Все выполненные команды записываются в лог:

```
Путь: ~/.ssh/command_executor_logs/ssh_commands_YYYY-MM-DD.log

Формат:
2025-10-22 14:30:15 | user | host1 (192.168.1.10) | ls -la | SUCCESS
2025-10-22 14:31:20 | user | host2 (192.168.1.11) | sudo systemctl status nginx | SUCCESS
2025-10-22 14:32:45 | user | host3 (192.168.1.12) | cat /etc/hostname | FAILED: Connection timeout
```

## Устранение неполадок

### Проблема: GUI не запускается

```bash
# Ошибка: ModuleNotFoundError: No module named 'tkinter'

# Решение для Debian/Ubuntu:
sudo apt install python3-tk

# Решение для CentOS/RHEL:
sudo yum install python3-tkinter

# Проверка:
python3 -c "import tkinter; print('OK')"
```

### Проблема: Таймаут выполнения команды

```bash
# Ошибка: Command executing time out (60s)

# Решение 1: Увеличить таймаут через CLI
python3 app/main.py --cli --timeout 120

# Решение 2: Изменить в config.py
SSH_COMMAND_TIMEOUT = 120  # 2 минуты
```

### Проблема: Хост не подключается

```bash
# Проверка доступности
python3 app/main.py --cli
# Выберите: 3. Test connection

# Проверка SSH конфигурации
python3 app/main.py --test-config

# Ручная проверка SSH
ssh -v hostname
```

### Проблема: Permission denied

```bash
# Создание SSH ключа
ssh-keygen -t rsa -b 4096

# Копирование ключа на сервер
ssh-copy-id user@host

# Проверка прав доступа
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
chmod 600 ~/.ssh/config
```

## Системные требования

- Python 3.6 или выше
- tkinter (для GUI, обычно включен в Python)
- SSH клиент (openssh-client)
- Доступ к ~/.ssh/config или указанному файлу конфигурации

## Установка

```bash
# Клонирование репозитория
git clone <repository-url>
cd linux-bash-ssh

# Установка зависимостей (если требуется)
# Для Debian/Ubuntu:
sudo apt update
sudo apt install python3 python3-tk openssh-client

# Для CentOS/RHEL:
sudo yum install python3 python3-tkinter openssh-clients

# Проверка установки
python3 --version
python3 app/main.py --help
```

## Горячие клавиши (GUI)

- `Ctrl+Enter` - Выполнить команду
- `Ctrl+C` - Копировать выделенный текст
- `Ctrl+Shift+C` - Копировать весь вывод
- `Ctrl+A` - Выделить весь текст
- `Escape` - Очистить фильтр префикса
- `F5` - Обновить список хостов

## Многострочные команды

### Простой heredoc

```bash
cat << EOF > /tmp/config.txt
Setting1=Value1
Setting2=Value2
EOF
```

### Heredoc в GUI

1. Нажмите кнопку "Heredoc"
2. Измените содержимое по необходимости
3. Нажмите "Execute Command"

### Heredoc в CLI

```bash
>> Enter command to execute:
(Enter empty line to finish, or type single line and press Enter)
> cat << EOF > /tmp/test.txt
> line 1
> line 2
> EOF

Continue multiline input? (y/N): n
```

## Расширенные примеры

### Проверка версии ОС на всех серверах

```bash
python3 app/main.py --cli --prefix prod
# Выберите: 1. Execute command on hosts
# Hosts: 1-10 (все)
# Command: cat /etc/os-release
```

### Обновление пакетов с задержкой

```bash
python3 app/main.py --gui --prefix web --timeout 300 --delay 30
# Команда: sudo apt update && sudo apt upgrade -y
# Включить опцию: Use sudo
# Delay: 30 секунд между хостами
```

### Массовый перезапуск сервисов

```bash
python3 app/main.py --cli --prefix app --delay 60
# Команда: sudo systemctl restart myapp
# Delay 60 секунд обеспечивает постепенный перезапуск
```

### Сбор информации с серверов

```bash
python3 app/main.py --cli
# Команда:
cat << 'EOF'
echo "=== System Info ==="
hostname
uptime
df -h /
free -h
EOF
```

## Разработка и вклад

### Структура кода

- Все настройки в `config.py` - легко изменять
- Модульная архитектура - каждый файл отвечает за свою задачу
- Полное тестовое покрытие критических функций
- Понятные имена функций и переменных
- Комментарии на английском языке

### Запуск тестов

```bash
# Все тесты
python3 -m unittest discover tests/ -v

# Конкретный модуль
python3 tests/test_config_security.py -v

# С подробным выводом
python3 -m unittest tests.test_config.TestConfig.test_ssh_settings -v
```

### Добавление новых опасных команд

Отредактируйте `app/config.py`:

```python
SECURITY = {
    "dangerous_commands": [
        "rm -rf",
        "dd if=",
        "my-dangerous-command",  # Добавьте свою команду
    ],
    # ...
}
```

### Добавление новых команд требующих подтверждения

```python
SECURITY = {
    # ...
    "require_confirmation": [
        "sudo",
        "systemctl",
        "my-sensitive-command",  # Добавьте свою команду
    ]
}
```

## Лицензия и авторство

Проект: SSH Command Executor
Версия: 0.1
Автор: [Ваше имя]
Репозиторий: <repository-url>

## Контакты и поддержка

- **Issues**: <repository-url>/issues
- **Документация**: README.md (English), README_RU.md (Russian)
- **Руководство по EOF**: EOF_USAGE.md

---

**Дата обновления документации**: 22 октября 2025
**Версия приложения**: 0.1
**Строк кода**: ~3500 (приложение + тесты)
**Тестов**: 23 (все проходят)
