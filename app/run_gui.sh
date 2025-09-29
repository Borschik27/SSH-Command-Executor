#!/bin/bash

cd "$(dirname "$0")"

echo "Command Executor"

if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python3 не найден"
    echo "Установите Python3 для работы приложения"
    exit 1
fi

if [[ ! -f "main.py" ]]; then
    echo "Ошибка: main.py не найден"
    echo "Запустите скрипт из директории проекта"
    exit 1
fi

echo "Python3 найден"
echo "Проверка доступности GUI..."

python3 app/main.py

echo "Command Executor завершил работу."