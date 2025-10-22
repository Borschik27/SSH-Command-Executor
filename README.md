# SSH Command Executor

A tool for executing SSH commands with both graphical and console interfaces

## Key Features

- **Host Grouping**: Automatic host grouping by first character with natural sorting
- **Centralized Configuration**: All settings managed in config.py
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
- **Stop Button (GUI)**: Interrupt command execution on remaining hosts
- **Delay Between Hosts**: Configurable pause between host executions (0-600 seconds)
- **Multiline Commands**: Support for heredoc and complex commands
- **EOF Support**: Heredoc templates for passing multiline text

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

- Checkboxes for selecting hosts and groups
- Alphabetical host grouping with natural sorting
- Prefix filtering with clear button
- "Select All" / "Deselect All" buttons
- "Expand All" / "Collapse All" group buttons
- Context menu (right-click)
- Host information dialog (double-click)
- Command execution with sudo option
- Verbose/brief output modes
- Security confirmation dialogs
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

# Full help for all parameters
python3 app/main.py --help

# Run via shell script (auto-detect GUI/CLI)
./run.sh
```

You can also run the application in Windows using PowerShell:

1. Install Python 3.6+ from [python.org](https://www.python.org/downloads/)
2. Execute PowerShell commands:

```powershell
# Running in Windows (PowerShell)
PS > cd "$env:USERPROFILE\path\to\project"
PS > py -3.11 .\app\main.py --config "$env:USERPROFILE\path\to\config" --gui
```

> Replace `-3.11` with the version flag matching your local Python installation.

### Commands with Parameters

```bash
# Filter hosts by prefix
python3 app/main.py --prefix web
python3 app/main.py -p prod

# Use different SSH config
python3 app/main.py --config ~/.ssh/production

# Timeout settings
python3 app/main.py --timeout 60 --connect-timeout 5

# Delay between hosts
python3 app/main.py --delay 10

# Debug mode
python3 app/main.py --debug

# Check SSH configuration
python3 app/main.py --test-config

# List hosts
python3 app/main.py --list-hosts

# Version information
python3 app/main.py --version
```

### GUI Usage

1. Run `python3 app/main.py --gui`
2. Enter a prefix to filter hosts (or leave empty)
3. Select hosts using checkboxes
4. Enter command in the text field
5. Configure options (sudo, verbose, delay)
6. Click "Execute Command" or press Ctrl+Enter
7. Use "Stop" button to interrupt execution

### CLI Usage

1. Run `python3 app/main.py --cli`
2. Enter prefix when prompted (or Enter for all hosts)
3. Select an action from the menu
4. Follow instructions to execute command
5. Confirm security prompts as needed

## Configuration

All settings are located in `config.py`:

- **GUI Settings**: window sizes, fonts, colors
- **SSH Parameters**: timeouts, configuration paths
- **Security Policies**: dangerous commands, confirmation requirements
- **Logging Settings**: audit log location and format
- **Interface Symbols**: checkboxes, icons
- **Messages**: notification texts
- **Default Values**: initial settings

To change settings, edit the corresponding values in `config.py`.

## Security Configuration

Security policies can be configured in `config.py`:

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

### Application Modules

- `main.py` - Main entry point with command-line argument support
- `config.py` - Centralized configuration of all settings
- `cli_args.py` - Command-line argument processing
- `command_executor_gui_app.py` - GUI implementation with security dialogs
- `command_executor_cli_app.py` - CLI implementation with security prompts
- `ssh_config_parser.py` - SSH configuration parser with grouping
- `ssh_executor.py` - SSH command execution with logging and security checks
- `run.sh` - Automatic startup script

### Testing

```bash
# Run all tests
python3 -m unittest discover tests/ -v

# Run individual test
python3 tests/test_config.py
python3 tests/test_config_security.py
python3 tests/test_parse_host_range.py
python3 tests/test_ssh_config_parser.py
```

**Total: 23 tests, all passing successfully**

## Usage Examples

```bash
# Quick start
python3 app/main.py

# Work with specific hosts
python3 app/main.py --prefix web --gui

# Debug issues
python3 app/main.py --debug --test-config

# Batch operations with security
python3 app/main.py --cli --prefix prod --verbose

# Check host availability
python3 app/main.py --cli --prefix db
# Select action: 3. Test connection
```

## Security Examples

### Dangerous Command (blocked)

```bash
Command: rm -rf /
Result: BLOCKED - "Command contains potentially dangerous pattern: 'rm -rf'"
```

### System Command (requires confirmation)

```bash
Command: sudo systemctl restart nginx
GUI: Shows confirmation dialog with host list
CLI: Prompts "Continue execution? (y/N)"
```

## SSH Configuration Format

The application reads standard `~/.ssh/config`:

```
# Server group 'web'
Host web1
    HostName 192.168.1.10
    User admin
    Port 22
    IdentityFile ~/.ssh/web_key

Host web2
    HostName 192.168.1.11
    User admin

# Server group 'db'
Host db1
    HostName 192.168.2.10
    User dbadmin

# Pattern hosts (ignored by application)
Host *.internal
    User root
```

**Features:**

- Hosts are grouped by first character/digit
- Pattern hosts (with `*`) are excluded from the list
- Natural sorting is supported (host1, host2, host10)
- All SSH config parameters are considered when connecting

## Logging

All executed commands are written to log:

```
Path: ~/.ssh/command_executor_logs/ssh_commands_YYYY-MM-DD.log

Format:
2025-10-22 14:30:15 | user | host1 (192.168.1.10) | ls -la | SUCCESS
2025-10-22 14:31:20 | user | host2 (192.168.1.11) | sudo systemctl status nginx | SUCCESS
2025-10-22 14:32:45 | user | host3 (192.168.1.12) | cat /etc/hostname | FAILED: Connection timeout
```

## Troubleshooting

### Issue: GUI not starting

```bash
# Error: ModuleNotFoundError: No module named 'tkinter'

# Solution for Debian/Ubuntu:
sudo apt install python3-tk

# Solution for CentOS/RHEL:
sudo yum install python3-tkinter

# Verification:
python3 -c "import tkinter; print('OK')"
```

### Issue: Command execution timeout

```bash
# Error: Command executing time out (60s)

# Solution 1: Increase timeout via CLI
python3 app/main.py --cli --timeout 120

# Solution 2: Change in config.py
SSH_COMMAND_TIMEOUT = 120  # 2 minutes
```

### Issue: Host not connecting

```bash
# Check availability
python3 app/main.py --cli
# Select: 3. Test connection

# Check SSH configuration
python3 app/main.py --test-config

# Manual SSH check
ssh -v hostname
```

### Issue: Permission denied

```bash
# Create SSH key
ssh-keygen -t rsa -b 4096

# Copy key to server
ssh-copy-id user@host

# Check permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
chmod 600 ~/.ssh/config
```

## System Requirements

- Python 3.6 or higher
- tkinter (for GUI, usually included with Python)
- SSH client (openssh-client)
- Access to ~/.ssh/config or specified configuration file

## Installation

```bash
# Clone repository
git clone <repository-url>
cd linux-bash-ssh

# Install dependencies (if needed)
# For Debian/Ubuntu:
sudo apt update
sudo apt install python3 python3-tk openssh-client

# For CentOS/RHEL:
sudo yum install python3 python3-tkinter openssh-clients

# Verify installation
python3 --version
python3 app/main.py --help
```

## Keyboard Shortcuts (GUI)

- `Ctrl+Enter` - Execute command
- `Ctrl+C` - Copy selected text
- `Ctrl+Shift+C` - Copy all output
- `Ctrl+A` - Select all text
- `Escape` - Clear prefix filter
- `F5` - Refresh host list

## Multiline Commands

### Simple heredoc

```bash
cat << EOF > /tmp/config.txt
Setting1=Value1
Setting2=Value2
EOF
```

### Heredoc in GUI

1. Click "Heredoc" button
2. Modify content as needed
3. Click "Execute Command"

### Heredoc in CLI

```bash
>> Enter command to execute:
(Enter empty line to finish, or type single line and press Enter)
> cat << EOF > /tmp/test.txt
> line 1
> line 2
> EOF

Continue multiline input? (y/N): n
```

## Advanced Examples

### Check OS version on all servers

```bash
python3 app/main.py --cli --prefix prod
# Select: 1. Execute command on hosts
# Hosts: 1-10 (all)
# Command: cat /etc/os-release
```

### Update packages with delay

```bash
python3 app/main.py --gui --prefix web --timeout 300 --delay 30
# Command: sudo apt update && sudo apt upgrade -y
# Enable option: Use sudo
# Delay: 30 seconds between hosts
```

### Mass service restart

```bash
python3 app/main.py --cli --prefix app --delay 60
# Command: sudo systemctl restart myapp
# Delay 60 seconds ensures gradual restart
```

### Collect information from servers

```bash
python3 app/main.py --cli
# Command:
cat << 'EOF'
echo "=== System Info ==="
hostname
uptime
df -h /
free -h
EOF
```

## Development and Contributing

### Code Structure

- All settings in `config.py` - easy to modify
- Modular architecture - each file handles its own task
- Full test coverage of critical functions
- Clear function and variable names
- Comments in English

### Running Tests

```bash
# All tests
python3 -m unittest discover tests/ -v

# Specific module
python3 tests/test_config_security.py -v

# With verbose output
python3 -m unittest tests.test_config.TestConfig.test_ssh_settings -v
```

### Adding New Dangerous Commands

Edit `app/config.py`:

```python
SECURITY = {
    "dangerous_commands": [
        "rm -rf",
        "dd if=",
        "my-dangerous-command",  # Add your command
    ],
    # ...
}
```

### Adding New Commands Requiring Confirmation

```python
SECURITY = {
    # ...
    "require_confirmation": [
        "sudo",
        "systemctl",
        "my-sensitive-command",  # Add your command
    ]
}
```

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

![Screenshot of the GUI main window](https://github.com/user-attachments/assets/8bcc702e-f26d-4da0-8888-9edc4394cb35)

- Checkboxes for selecting hosts and groups
- Alphabetical host grouping with natural sorting
- Prefix filtering with clear button
- "Select All" / "Deselect All" buttons
- "Expand All" / "Collapse All" group buttons
- Context menu (right-click)
- Host information dialog (double-click)

![Screenshot of the host info dialog](https://github.com/user-attachments/assets/f92d9bc5-2598-4331-a375-688ca68d71ba)

- Command execution with sudo option
- Detailed/brief output modes
- Security confirmation dialogs
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

You can also run the application on Windows using PowerShell:

1. Install Python 3.6+ from [python.org](https://www.python.org/downloads/)
2. Run PowerShell commands:

```powershell
# Start in Windows (PowerShell)
PS > cd "$env:USERPROFILE\path\to\project"
PS > py -3.11 .\app\main.py --config "$env:USERPROFILE\path\to\config" --gui
```

> Replace `-3.11` with the version flag that matches your local Python installation.

### Commands with Parameters

```bash
# Filter hosts by prefix
python3 app/main.py --prefix web
python3 app/main.py -p prod

# Use different SSH config
python3 app/main.py --config ~/.ssh/production

# Timeout settings
python3 app/main.py --timeout 60 --connect-timeout 5

# Add delay between hosts (in seconds, 0-600)
python3 app/main.py --delay 5

# Verbose output and debugging
python3 app/main.py --verbose --debug
```

## New Features

### Stop Button (GUI Only)

The **Stop** button allows you to interrupt command execution on remaining hosts:

- Located next to the Execute button in the control panel
- Disabled by default, enabled during command execution
- Commands already running on the current host will complete
- Results show how many hosts were completed before stopping
- Status indicator shows "Stopping execution..." when pressed

**Use cases:**

- Detected issues and need to stop before affecting more hosts
- Gradual rollouts where you want to observe results
- Emergency stop during problematic deployments

### Delay Between Hosts

Control the pause between executing commands on different hosts:

**GUI:**

- Spinbox field in options panel: "Delay (sec)"
- Range: 0-600 seconds (10 minutes)
- Default: 0 (no delay)

**CLI:**

- Use `--delay` argument: `python3 app/main.py --delay 5`
- Displays "Waiting X seconds before next host..." message

**Use cases:**

- Rate limiting to prevent overwhelming target hosts
- Staggered deployments for gradual rollouts
- Network congestion avoidance
- Observing results before proceeding to next host

**Example:**

```bash
# Execute with 10 second delay between hosts
python3 app/main.py --cli --delay 10
```

### Combined Commands

```bash
# GUI with prefix and verbose output
python3 app/main.py --gui --prefix f --verbose

# CLI with custom config and debug
python3 app/main.py --cli --config ~/.ssh/test --debug

# CLI with delay and prefix filter
python3 app/main.py --cli --prefix prod --delay 5
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
- `tests/` - Automated tests for critical helpers such as host range parsing

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
