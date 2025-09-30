# Command Executor

A tool for executing SSH commands with both graphical and console interfaces

## Key Features

- **Host Grouping**: Hosts are automatically grouped by first character with natural sorting
- **Centralized Configuration**: All settings are managed in config.py
- **Security Protection**: Built-in dangerous command detection and confirmation dialogs
- **Command Logging**: Automatic audit logging of all SSH operations
- **--help Support**: Full command-line argument support with help
- **Prefix Filtering**: Filter hosts by prefix pattern
- **Checkboxes**: Select individual hosts or entire groups
- **GUI Version**: Graphical interface with dialogs and confirmations
- **CLI Version**: Console interface with interactive security prompts
- **Auto Fallback**: GUI → CLI when tkinter is unavailable
- **Batch Execution**: Commands on multiple hosts simultaneously
- **Host Information**: View SSH configuration for each host
- **Connection Testing**: Check host availability and connectivity

## Security Features

- **Dangerous Command Detection**: Automatically blocks potentially destructive commands
  - `rm -rf`, `dd if=`, `mkfs`, `format`, `chmod 777`, etc.
- **Confirmation Dialogs**: Interactive confirmation for system-level commands
  - `sudo`, `systemctl`, `service`, `mount`, `umount`, etc.
- **Audit Logging**: Complete logging of all command executions
  - Location: `~/.ssh/command_executor_logs/`
  - Format: `ssh_commands_YYYY-MM-DD.log`
- **Configurable Security Policies**: Centralized security rules in config.py

## GUI Capabilities

<img width="1011" height="731" alt="Screenshot 2025-09-30 131604" src="https://github.com/user-attachments/assets/8bcc702e-f26d-4da0-8888-9edc4394cb35" />

- Checkboxes for selecting hosts and groups
- Alphabetical host grouping with natural sorting
- Prefix filtering with clear button
- "Select All" / "Deselect All" buttons
- "Expand All" / "Collapse All" group buttons
- Context menu (right-click)
- Host information dialog (double-click)

  <img width="409" height="331" alt="image" src="https://github.com/user-attachments/assets/f92d9bc5-2598-4331-a375-688ca68d71ba" />

- Command execution with sudo option
- Detailed/brief output modes
- Security confirmation dialogs

  <img width="310" height="348" alt="image" src="https://github.com/user-attachments/assets/3b58cc67-cd7d-4c8d-8630-ff4330fc8736" />

  <img width="366" height="427" alt="image" src="https://github.com/user-attachments/assets/ef38698c-50c8-430a-a641-8f970e692998" />

  <img width="304" height="340" alt="image" src="https://github.com/user-attachments/assets/67ed7c9b-ecd8-4402-8ad5-d281f9c74a84" />

- Dangerous command blocking with explanations

## Usage

### Basic Commands

```bash
# Automatic interface selection (GUI or CLI)
python3 app/main.py

# Force GUI mode
python3 app/main.py --gui

# Force CLI mode
python3 app/main.py --cli

# Complete help for all parameters
python3 app/main.py --help

# Launch via shell script (auto-detects GUI/CLI)
./run.sh
```

### Commands with Parameters

```bash
# Filter hosts by prefix
python3 app/main.py --prefix web
python3 app/main.py -p prod

# Use different SSH config
python3 app/main.py --config ~/.ssh/production

# Timeout settings
python3 app/main.py --timeout 60 --connect-timeout 5

# Verbose output and debugging
python3 app/main.py --verbose --debug

# Combined commands
python3 app/main.py --gui --prefix f --verbose
python3 app/main.py --cli --config ~/.ssh/test --debug
```

### Diagnostic Commands

```bash
# Check SSH configuration
python3 app/main.py --test-config

# Show all available hosts
python3 app/main.py --list-hosts

# Show hosts with prefix
python3 app/main.py --list-hosts --prefix web

# Application version
python3 app/main.py --version
```

## How to Use

### GUI Version

1. Run `python3 app/main.py` or `python3 app/main.py --gui`
2. Enter prefix in "Prefix" field (or leave empty for all hosts)
3. Click "Load" or "Clear"
4. Select hosts using checkboxes (individual hosts or entire groups)
5. Enter command to execute
6. Configure options: sudo, verbose output
7. Click "Execute Command"
8. Review security warnings and confirmations if prompted

### CLI Version

1. Run `python3 app/main.py --cli`
2. Enter prefix when prompted (or Enter for all hosts)
3. Select action from menu
4. Follow instructions for command execution
5. Confirm security prompts when presented

### Host Management

- **Host Checkboxes**: Click checkbox to select/deselect host
- **Group Checkboxes**: Click to select/deselect entire group
- **Double Click**: Shows host information dialog
- **Right Click**: Context menu with additional actions
- **Group Folding**: "Expand All" / "Collapse All" buttons

## Configuration

All settings are located in `config.py`:

- **GUI Settings**: window sizes, fonts, colors
- **SSH Parameters**: timeouts, configuration paths
- **Security Policies**: dangerous commands, confirmation requirements
- **Logging Settings**: audit log location and format
- **Interface Symbols**: checkboxes, icons
- **Messages**: notification texts
- **Default Values**: initial settings

To modify settings, edit the corresponding values in `config.py`.

## Security Configuration

Security policies can be customized in `config.py`:

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

## Project Architecture

- `main.py` - Main entry point with command-line argument support
- `config.py` - Centralized configuration for all settings
- `cli_args.py` - Command-line argument processing
- `command_executor_gui_app.py` - GUI implementation with security dialogs
- `command_executor_cli_app.py` - CLI implementation with security prompts
- `ssh_config_parser.py` - SSH configuration parser with grouping
- `ssh_executor.py` - SSH command execution with logging and security checks
- `run.sh` - Automatic launch script
- `README.md` - Usage documentation
- `SECURITY_IMPROVEMENTS.md` - Security features documentation

## Example Use Cases

```bash
# Quick start
python3 app/main.py

# Work with specific hosts
python3 app/main.py --prefix web --gui

# Debug problems
python3 app/main.py --debug --test-config

# Batch operations with security
python3 app/main.py --cli --prefix prod --verbose
```

## Security Examples

### Dangerous Command (Blocked)

```bash
Command: rm -rf /
Result: BLOCKED - "Command contains potentially dangerous pattern: 'rm -rf'"
```

### System Command (Requires Confirmation)

```bash
Command: sudo systemctl restart nginx
GUI: Shows confirmation dialog with host list
CLI: Prompts "Continue execution? (y/N)"
```

## Requirements

- Python 3.6+
- tkinter (for GUI, usually included with Python)
- SSH client (openssh-client)
- Access to ~/.ssh/config or specified configuration file
