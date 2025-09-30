#!/usr/bin/env python3

import re
from pathlib import Path
from typing import Dict, List, Optional

from config import Config


def _is_pattern_host(alias: str) -> bool:
    if not alias:
        return True
    return alias == "*" or any(char in alias for char in "*?")


def natural_sort_key(hostname: str) -> tuple:
    # Create key for natural host sorting with grouping
    # Args:
    #   hostname: Host alias
    # Returns:
    #   Tuple for sorting (group, natural_key)
    if not hostname:
        return ("zzz", "")

    first_char = hostname[0].lower()

    numeric_group = Config.GROUPING.get("numeric_group_name", "other")
    special_group = Config.GROUPING.get("special_chars_group_name", "zzz")

    # Determine group by first character
    if first_char.isdigit():
        group = numeric_group
    elif first_char.isalpha():
        group = first_char
    else:
        group = special_group

    # Build key for sorting within the group
    parts = re.split(r"(\d+)", hostname.lower())
    natural_key = []

    for part in parts:
        if part.isdigit():
            natural_key.append(int(part))
        else:
            natural_key.append(part)

    return (group, natural_key)


def group_hosts_by_first_char(hosts: List[str]) -> Dict[str, List[str]]:
    # Group hosts by their first character
    # Args:
    #   hosts: List of host aliases
    # Returns:
    #   Dictionary of groups {group: [hosts]}
    groups = {}

    for host in hosts:
        if not host:
            continue

        first_char = host[0].lower()

        if first_char.isdigit():
            group_name = Config.GROUPING.get("numeric_group_name", "other")
        elif first_char.isalpha():
            group_name = first_char
        else:
            group_name = Config.GROUPING.get("special_chars_group_name", "zzz")

        if group_name not in groups:
            groups[group_name] = []
        groups[group_name].append(host)

    # Sort hosts inside each group
    for group_name in groups:
        groups[group_name].sort(key=lambda x: natural_sort_key(x)[1])

    return groups


class SSHConfigParser:
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            from config import Config

            config_path = Config.DEFAULT_SSH_CONFIG_PATH

        self.config_path = Path(config_path)
        self.hosts = {}

    def parse_config(self) -> Dict[str, Dict[str, str]]:
        if not self.config_path.exists():
            print(f"SSH config file not found: {self.config_path}")
            return {}

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file {self.config_path}: {e}")
            return {}

        self.hosts = self._parse_content(content)
        return self.hosts

    def _parse_content(self, content: str) -> Dict[str, Dict[str, str]]:
        hosts: Dict[str, Dict[str, str]] = {}
        current_hosts: List[str] = []

        for line in content.split("\n"):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Process Host directives
            if line.lower().startswith("host "):
                host_names = line[5:].split()
                current_hosts = host_names
                for alias in host_names:
                    hosts[alias] = {"Host": alias}
                continue

            # Process other directives
            if current_hosts and " " in line:
                parts = line.split(None, 1)
                if len(parts) == 2:
                    key, value = parts
                    key_lower = key.lower()
                    for alias in current_hosts:
                        hosts[alias][key_lower] = value

        return hosts

    def get_hosts_with_prefix(self, prefix: str = "") -> List[str]:
        if not self.hosts:
            self.parse_config()

        if not prefix:
            hosts = list(self.hosts.keys())
        else:
            hosts = [
                host
                for host in self.hosts.keys()
                if host.lower().startswith(prefix.lower())
            ]

        hosts = [host for host in hosts if not _is_pattern_host(host)]
        return sorted(hosts, key=natural_sort_key)

    def get_grouped_hosts_with_prefix(self, prefix: str = "") -> Dict[str, List[str]]:
        hosts = self.get_hosts_with_prefix(prefix)
        return group_hosts_by_first_char(hosts)

    def get_host_info(self, hostname: str) -> Optional[Dict[str, str]]:
        if not self.hosts:
            self.parse_config()

        return self.hosts.get(hostname)

    def get_all_hosts(self) -> List[str]:

        if not self.hosts:
            self.parse_config()

        return sorted(
            [host for host in self.hosts.keys() if not _is_pattern_host(host)],
            key=natural_sort_key,
        )


if __name__ == "__main__":
    from config import Config

    # Testing parser with configuration parameters
    parser = SSHConfigParser()

    # Test hosts with configured prefix
    test_prefix = Config.TEST_SETTINGS["test_prefix"]
    test_hosts = parser.get_hosts_with_prefix(test_prefix)
    host_limit = Config.TEST_SETTINGS["test_host_limit"]

    if Config.TEST_SETTINGS["enable_debug_output"]:
        print(
            f"Hosts with prefix '{test_prefix}':",
            test_hosts[:host_limit],
            f"... (total {len(test_hosts)})",
        )

        # Test all hosts with grouping
        all_groups = parser.get_grouped_hosts_with_prefix("")
        print(f"\nAll hosts by groups (total groups: {len(all_groups)}):")

        group_limit = Config.TEST_SETTINGS["test_group_limit"]
        for group_name in sorted(all_groups.keys()):
            hosts_in_group = all_groups[group_name]
            print(
                f"Group '{group_name}': {hosts_in_group[:group_limit]}... ({len(hosts_in_group)} hosts)"
            )

        if test_hosts:
            # Show information about the first host
            info = parser.get_host_info(test_hosts[0])
            print(f"\nInformation about {test_hosts[0]}:", info)
