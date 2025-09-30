#!/bin/bash

cd "$(dirname "$0")" || exit

echo "Command Executor"

if ! command -v python3 &>/dev/null; then
	echo "Error: Python3 not found"
	echo "Please install Python3 to run the application"
	exit 1
fi

if [[ ! -f "app/main.py" ]]; then
	echo "Error: main.py not found"
	echo "Run the script from the project directory"
	exit 1
fi

echo "Python3 found"
echo "Checking GUI availability..."

python3 app/main.py

echo "Command Executor finished."
