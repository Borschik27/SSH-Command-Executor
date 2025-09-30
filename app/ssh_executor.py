#!/usr/bin/env python3

import subprocess
from typing import Any, Dict, Optional

from config import Config


class SSHExecutor:
    # Class for executing SSH commands

    def __init__(
        self,
        ssh_config_path: Optional[str] = None,
        *,
        connect_timeout: Optional[int] = None,
        command_timeout: Optional[int] = None,
        batch_mode: Optional[bool] = None,
        strict_host_key_checking: Optional[bool] = None,
    ):
        # Args:
        #     ssh_config_path: Path to SSH config file. Default ~/.ssh/config.
        #     connect_timeout: SSH connection timeout.
        #     command_timeout: Command execution timeout.
        #     batch_mode: BatchMode usage flag.
        #     strict_host_key_checking: StrictHostKeyChecking flag.

        self.ssh_config_path = Config.get_ssh_config_path(ssh_config_path)
        self.connect_timeout = (
            connect_timeout
            if connect_timeout is not None
            else Config.SSH_CONNECT_TIMEOUT
        )
        self.command_timeout = (
            command_timeout
            if command_timeout is not None
            else Config.SSH_COMMAND_TIMEOUT
        )
        self.batch_mode = Config.SSH_BATCH_MODE if batch_mode is None else batch_mode
        self.strict_host_key_checking = (
            Config.SSH_STRICT_HOST_KEY_CHECKING
            if strict_host_key_checking is None
            else strict_host_key_checking
        )

    def execute_command(
        self, hostname: str, command: str, timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        # Execute a command on a remote host
        # Args:
        #   hostname: Host alias from the SSH configuration
        #   command: Command to execute
        #   timeout: Command timeout in seconds
        # Returns:
        #   Dictionary with command execution results
        effective_timeout = timeout if timeout is not None else self.command_timeout

        try:
            # Build SSH command
            ssh_cmd = [
                "ssh",
                "-F",
                self.ssh_config_path,
                "-o",
                f"ConnectTimeout={self.connect_timeout}",
            ]

            if self.batch_mode:
                ssh_cmd.extend(["-o", "BatchMode=yes"])
            else:
                ssh_cmd.extend(["-o", "BatchMode=no"])

            ssh_cmd.extend(
                [
                    "-o",
                    f'StrictHostKeyChecking={"yes" if self.strict_host_key_checking else "no"}',
                    hostname,
                    command,
                ]
            )

            process = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                timeout=effective_timeout,
                encoding="utf-8",
                errors="replace",
            )

            result = {
                "success": process.returncode == 0,
                "output": process.stdout.strip() if process.stdout else "",
                "error": process.stderr.strip() if process.stderr else "",
                "return_code": process.returncode,
                "hostname": hostname,
                "command": command,
            }
            self._log_command(hostname, command, result)
            return result

        except subprocess.TimeoutExpired:
            result = {
                "success": False,
                "output": "",
                "error": f"Command execution timeout ({effective_timeout}s)",
                "return_code": -1,
                "hostname": hostname,
                "command": command,
            }
            self._log_command(hostname, command, result)
            return result

        except FileNotFoundError:
            result = {
                "success": False,
                "output": "",
                "error": "SSH client not found. Make sure OpenSSH is installed.",
                "return_code": -1,
                "hostname": hostname,
                "command": command,
            }
            self._log_command(hostname, command, result)
            return result

        except Exception as e:
            result = {
                "success": False,
                "output": "",
                "error": f"Unexpected error: {str(e)}",
                "return_code": -1,
                "hostname": hostname,
                "command": command,
            }
            self._log_command(hostname, command, result)
            return result

    def _log_command(self, hostname: str, command: str, result: Dict[str, Any]) -> None:
        # Log executed command using configuration settings
        if not Config.LOG_ENABLED:
            return

        try:
            import datetime

            # Ensure log directory exists
            Config.ensure_log_dir()

            # Resolve log file path
            log_file = Config.get_log_file_path()

            # Compose log entry
            timestamp = datetime.datetime.now().strftime(Config.LOG_TIMESTAMP_FORMAT)
            log_entry = (
                f"[{timestamp}] HOST: {hostname} | "
                f"CMD: {command} | "
                f"SUCCESS: {result['success']} | "
                f"RC: {result['return_code']}"
            )

            # Append to log file
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")

        except Exception:  # nosec
            # If logging fails, continue without interrupting execution
            pass

    def execute_command_batch(
        self, hostnames: list, command: str, timeout: Optional[int] = None
    ) -> Dict[str, Dict[str, Any]]:
        # Execute a command on multiple hosts
        # Args:
        #   hostnames: List of host aliases
        #   command: Command to execute
        #   timeout: Command timeout in seconds
        # Returns:
        #   Dictionary with results for each host
        results = {}

        for hostname in hostnames:
            results[hostname] = self.execute_command(hostname, command, timeout)

        return results

    def test_connection(self, hostname: str) -> Dict[str, Any]:
        # Test connectivity to a host
        # Args:
        #   hostname: Host alias
        # Returns:
        #   Result of the connectivity test
        return self.execute_command(
            hostname,
            'echo "SSH connection test successful"',
            timeout=self.connect_timeout,
        )

    def get_host_info(self, hostname: str) -> Dict[str, Any]:
        # Retrieve basic information about a host
        # Args:
        #   hostname: Host alias
        # Returns:
        #   Host information
        commands = {
            "hostname": "hostname",
            "uptime": "uptime",
            "os": "uname -a",
            "whoami": "whoami",
        }

        results = {}
        for key, cmd in commands.items():
            result = self.execute_command(hostname, cmd, timeout=self.command_timeout)
            results[key] = (
                result["output"] if result["success"] else f"Error: {result['error']}"
            )

        return results


def test_ssh_executor():
    from config import Config

    if Config.TEST_SETTINGS["enable_debug_output"]:
        print(f"{Config.get_cli_symbol('rocket')} Testing SSH Executor...")

        # Create executor instance
        executor = SSHExecutor()

        test_hosts = ["localhost"]  # Replace with real hosts from your configuration

        for host in test_hosts:
            print(f"\n{Config.get_cli_symbol('search')} Testing host: {host}")

            # Test connection
            result = executor.test_connection(host)
            if result["success"]:
                print(
                    f"{Config.get_cli_symbol('success')} Connection successful: {result['output']}"
                )

                # Get host information
                info = executor.get_host_info(host)
                print(f"{Config.get_cli_symbol('computer')} Host information:")
                for key, value in info.items():
                    print(f"  {key}: {value}")

            else:
                print(
                    f"{Config.get_cli_symbol('error')} Connection error: {result['error']}"
                )


if __name__ == "__main__":
    test_ssh_executor()
