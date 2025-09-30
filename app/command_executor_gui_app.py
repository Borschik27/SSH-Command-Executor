#!/usr/bin/env python3

# GUI application component for Command Executor.

import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from config import Config
from ssh_config_parser import SSHConfigParser
from ssh_executor import SSHExecutor


class CommandExecutorApp:
    def __init__(self, root, args=None):
        self.root = root
        self.args = args or type("Args", (), {})()  # Empty object if args not passed

        # Window configuration from config
        self.root.title(Config.GUI_WINDOW_TITLE)
        self.root.geometry(Config.GUI_WINDOW_GEOMETRY)
        self.root.minsize(Config.GUI_WINDOW_MIN_WIDTH, Config.GUI_WINDOW_MIN_HEIGHT)

        # Component initialization with settings from args
        ssh_config_path = getattr(self.args, "config", Config.DEFAULT_SSH_CONFIG_PATH)
        self.ssh_config_path = ssh_config_path
        self.config_parser = SSHConfigParser(ssh_config_path)
        self.ssh_executor = SSHExecutor(ssh_config_path)
        self.selected_hosts = set()

        # Create interface
        self.create_widgets()
        self.load_hosts()

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding=Config.GUI_MAIN_PADDING)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure stretching
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame, text=Config.APP_NAME, font=Config.GUI_TITLE_FONT
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        # Left panel - host selection
        self.create_hosts_panel(main_frame)

        # Right panel - commands and results
        self.create_command_panel(main_frame)

        # Bottom panel - control buttons
        self.create_control_panel(main_frame)

    def create_hosts_panel(self, parent):
        # Hosts frame
        hosts_frame = ttk.LabelFrame(
            parent, text="Hosts", padding=Config.GUI_FRAME_PADDING
        )
        hosts_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        hosts_frame.columnconfigure(0, weight=1)
        hosts_frame.rowconfigure(2, weight=1)

        # Prefix selection frame
        prefix_frame = ttk.Frame(hosts_frame)
        prefix_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        ttk.Label(prefix_frame, text="Prefix:").pack(side=tk.LEFT, padx=(0, 5))
        # Use prefix from arguments if available
        initial_prefix = getattr(self.args, "prefix", Config.DEFAULTS["prefix_filter"])
        self.prefix_var = tk.StringVar(value=initial_prefix)
        self.prefix_entry = ttk.Entry(
            prefix_frame,
            textvariable=self.prefix_var,
            width=Config.GUI_PREFIX_ENTRY_WIDTH,
        )
        self.prefix_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.prefix_entry.bind("<Return>", lambda e: self.load_hosts())

        ttk.Button(prefix_frame, text="Load", command=self.load_hosts).pack(
            side=tk.LEFT, padx=Config.GUI_BUTTON_PADX
        )
        ttk.Button(prefix_frame, text="Clear", command=self.clear_prefix).pack(
            side=tk.LEFT
        )

        # Selection buttons
        buttons_frame = ttk.Frame(hosts_frame)
        buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        ttk.Button(
            buttons_frame, text="Select All", command=self.select_all_hosts
        ).pack(side=tk.LEFT, padx=Config.GUI_BUTTON_PADX)
        ttk.Button(
            buttons_frame, text="Deselect All", command=self.deselect_all_hosts
        ).pack(side=tk.LEFT, padx=Config.GUI_BUTTON_PADX)
        ttk.Button(
            buttons_frame, text="Expand All", command=self.expand_all_groups
        ).pack(side=tk.LEFT, padx=Config.GUI_BUTTON_PADX)
        ttk.Button(
            buttons_frame, text="Collapse All", command=self.collapse_all_groups
        ).pack(side=tk.LEFT, padx=Config.GUI_BUTTON_PADX)
        ttk.Button(buttons_frame, text="Refresh", command=self.refresh_hosts).pack(
            side=tk.LEFT, padx=Config.GUI_BUTTON_PADX
        )

        # Host tree
        tree_frame = ttk.Frame(hosts_frame)
        tree_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # Treeview for hosts with checkboxes
        self.hosts_tree = ttk.Treeview(
            tree_frame,
            selectmode="extended",
            columns=("checkbox", "hostname"),
            displaycolumns=("checkbox",),
            show="tree headings",
        )
        self.hosts_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbar for tree
        tree_scrollbar = ttk.Scrollbar(
            tree_frame, orient=tk.VERTICAL, command=self.hosts_tree.yview
        )
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.hosts_tree.configure(yscrollcommand=tree_scrollbar.set)

        # Column configuration
        self.hosts_tree.heading("#0", text="Hosts")
        self.hosts_tree.heading(
            "checkbox", text=Config.get_gui_symbol("checkbox_header")
        )
        self.hosts_tree.heading("hostname", text="Hostname")
        self.hosts_tree.column(
            "#0",
            width=Config.GUI_TREE_HOST_COLUMN_WIDTH,
            minwidth=Config.GUI_TREE_HOST_COLUMN_MIN_WIDTH,
        )
        self.hosts_tree.column(
            "checkbox",
            width=Config.GUI_TREE_CHECKBOX_COLUMN_WIDTH,
            minwidth=Config.GUI_TREE_CHECKBOX_COLUMN_MIN_WIDTH,
            anchor="center",
        )
        self.hosts_tree.column("hostname", width=0, minwidth=0, stretch=False)

        # Style configuration for highlighting
        self.hosts_tree.tag_configure(
            "selected_host",
            background=Config.get_color("selected_host_bg"),
            foreground=Config.get_color("selected_host_fg"),
        )
        self.hosts_tree.tag_configure(
            "unselected_host",
            background=Config.get_color("unselected_host_bg"),
            foreground=Config.get_color("unselected_host_fg"),
        )
        self.hosts_tree.tag_configure(
            "group",
            background=Config.get_color("group_bg"),
            foreground=Config.get_color("group_fg"),
        )

        # Selection handling
        self.hosts_tree.bind("<<TreeviewSelect>>", self.on_host_selection_change)
        self.hosts_tree.bind("<Button-1>", self.on_tree_click)
        self.hosts_tree.bind("<Double-1>", self.on_tree_double_click)
        self.hosts_tree.bind("<Button-3>", self.on_tree_right_click)

        # Create context menu
        self.context_menu = tk.Menu(self.hosts_tree, tearoff=0)
        self.context_menu.add_command(
            label="Select Host", command=self.context_select_host
        )
        self.context_menu.add_command(
            label="Deselect", command=self.context_deselect_host
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Host Information", command=self.context_show_info
        )
        self.context_menu.add_command(
            label="Test Connection", command=self.context_test_connection
        )

        # Variable to store selected context menu item
        self.context_item = None

    def _get_hostname_for_item(self, item_id: str) -> str:
        """Return the host alias stored for the given tree item."""

        if not item_id:
            return ""

        hostname = ""
        if "hostname" in self.hosts_tree["columns"]:
            hostname = self.hosts_tree.set(item_id, "hostname")

        if hostname:
            return hostname

        text_value = self.hosts_tree.item(item_id, "text")
        if not text_value:
            return ""

        return text_value.split(" (", 1)[0]

    def create_command_panel(self, parent):
        # Command frame
        command_frame = ttk.LabelFrame(parent, text="Command Execution", padding="5")
        command_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        command_frame.columnconfigure(0, weight=1)
        command_frame.rowconfigure(4, weight=1)  # Update row number for stretching

        # Command input field
        ttk.Label(command_frame, text="Command to execute:").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )

        # Options frame (checkboxes above input field)
        options_frame = ttk.Frame(command_frame)
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        # Sudo checkbox
        self.sudo_var = tk.BooleanVar(value=Config.DEFAULTS["sudo_enabled"])
        self.sudo_checkbox = ttk.Checkbutton(
            options_frame,
            text="sudo",
            variable=self.sudo_var,
            command=self.update_selection_info,
        )
        self.sudo_checkbox.pack(side=tk.LEFT, padx=(0, 10))

        # Verbose output checkbox
        verbose_default = getattr(
            self.args, "verbose", Config.DEFAULTS["verbose_output"]
        )
        self.verbose_var = tk.BooleanVar(value=verbose_default)
        self.verbose_checkbox = ttk.Checkbutton(
            options_frame,
            text="Verbose Output",
            variable=self.verbose_var,
        )
        self.verbose_checkbox.pack(side=tk.LEFT)

        # Command input field frame
        cmd_input_frame = ttk.Frame(command_frame)
        cmd_input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        cmd_input_frame.columnconfigure(0, weight=1)

        self.command_entry = ttk.Entry(
            cmd_input_frame, font=Config.GUI_COMMAND_ENTRY_FONT
        )
        self.command_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.command_entry.bind("<Return>", lambda e: self.execute_command())
        self.command_entry.bind("<KeyRelease>", lambda e: self.update_selection_info())

        # Results area
        ttk.Label(command_frame, text="Execution Results:").grid(
            row=3, column=0, sticky=tk.W, pady=(0, 5)
        )

        # Scrollable text field for results with both scrollbars
        results_container = ttk.Frame(command_frame)
        results_container.grid(
            row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )
        results_container.columnconfigure(0, weight=1)
        results_container.rowconfigure(0, weight=1)

        self.results_text = tk.Text(
            results_container,
            wrap=tk.NONE,
            font=Config.GUI_RESULTS_TEXT_FONT,
            state=tk.DISABLED,
        )
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        results_vscroll = ttk.Scrollbar(
            results_container, orient=tk.VERTICAL, command=self.results_text.yview
        )
        results_vscroll.grid(row=0, column=1, sticky=(tk.N, tk.S))

        results_hscroll = ttk.Scrollbar(
            results_container, orient=tk.HORIZONTAL, command=self.results_text.xview
        )
        results_hscroll.grid(row=1, column=0, sticky=(tk.W, tk.E))

        self.results_text.configure(
            yscrollcommand=results_vscroll.set, xscrollcommand=results_hscroll.set
        )

    def create_control_panel(self, parent):
        # Button frame
        control_frame = ttk.Frame(parent)
        control_frame.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky=(tk.W, tk.E),
            pady=Config.GUI_CONTROL_PANEL_PADY,
        )

        # Selected hosts information
        self.selection_label = ttk.Label(control_frame, text="Selected hosts: 0")
        self.selection_label.pack(side=tk.LEFT)

        # Additional information
        self.status_label = ttk.Label(
            control_frame,
            text=Config.MESSAGES["ready_status"],
            foreground=Config.get_color("status_ready"),
        )
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))

        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT)

        self.execute_button = ttk.Button(
            button_frame,
            text="Execute Command",
            command=self.execute_command,
            state=tk.DISABLED,
        )
        self.execute_button.pack(side=tk.LEFT, padx=(0, 5))

        self.expand_output_button = ttk.Button(
            button_frame,
            text="Expand Output",
            command=self.open_results_window,
        )
        self.expand_output_button.pack(side=tk.LEFT, padx=(0, 5))

        self.clear_button = ttk.Button(
            button_frame,
            text="Clear Results",
            command=self.clear_results,
        )
        self.clear_button.pack(side=tk.LEFT, padx=(0, 5))

        self.exit_button = ttk.Button(
            button_frame,
            text="Exit",
            command=self.root.quit,
        )
        self.exit_button.pack(side=tk.LEFT)

    def load_hosts(self):
        try:
            # Get prefix from input field
            prefix = Config.validate_prefix(self.prefix_var.get())

            # Get grouped hosts
            groups = self.config_parser.get_grouped_hosts_with_prefix(prefix)

            # Clear tree and selection
            for item in self.hosts_tree.get_children():
                self.hosts_tree.delete(item)
            self.selected_hosts.clear()

            if not groups:
                if prefix:
                    self.append_result(
                        Config.get_message("hosts_with_prefix_not_found", prefix=prefix)
                        + "\n"
                    )
                else:
                    self.append_result(Config.get_message("hosts_not_found") + "\n")
                self.update_selection_info()
                return

            # Add groups and hosts to tree
            total_hosts = 0

            for group_name in sorted(groups.keys()):
                hosts_in_group = groups[group_name]
                total_hosts += len(hosts_in_group)

                # Create group header
                group_display = f"Group '{group_name}' ({len(hosts_in_group)} hosts)"
                group_id = self.hosts_tree.insert(
                    "",
                    "end",
                    text=group_display,
                    values=(Config.get_gui_symbol("unchecked"), ""),
                    tags=("group",),
                )

                # Add hosts to group
                for host in hosts_in_group:
                    host_info = self.config_parser.get_host_info(host)
                    host_display = f"{host}"
                    if host_info and "hostname" in host_info:
                        host_display += f" ({host_info['hostname']})"

                    self.hosts_tree.insert(
                        group_id,
                        "end",
                        text=host_display,
                        values=(Config.get_gui_symbol("unchecked"), host),
                        tags=("host", "unselected_host"),
                    )

                # Expand group by default setting
                self.hosts_tree.item(
                    group_id, open=Config.DEFAULTS["tree_groups_expanded"]
                )

            # Show statistics
            all_hosts_count = len(self.config_parser.get_all_hosts())

            if prefix:
                self.append_result(
                    Config.get_message(
                        "hosts_loaded_with_prefix",
                        count=total_hosts,
                        prefix=prefix,
                        groups=len(groups),
                    )
                    + "\n"
                )
            else:
                self.append_result(
                    Config.get_message(
                        "hosts_loaded", count=total_hosts, groups=len(groups)
                    )
                    + "\n"
                )

            self.append_result(
                Config.get_message("total_hosts_info", total=all_hosts_count) + "\n"
            )
            self.update_selection_info()

        except Exception as exc:
            messagebox.showerror("Error", f"Host loading error: {exc}")
            self.append_result(
                f"{Config.get_gui_symbol('error')} Host loading error: {exc}\n"
            )

    def on_tree_click(self, event):
        item_id = self.hosts_tree.identify("item", event.x, event.y)
        column = self.hosts_tree.identify("column", event.x, event.y)

        if not item_id:
            return

        tags = self.hosts_tree.item(item_id, "tags")

        # Click on checkbox column
        if column == "#1":  # checkbox column
            if "group" in tags:
                # Click on group - toggle entire group
                self.toggle_group_selection(item_id)
            elif "host" in tags:
                # Click on host - toggle host
                self.toggle_host_selection(item_id)
        elif column == "#0":  # click on name
            if "group" in tags:
                # Click on group name - collapse/expand
                current_open = self.hosts_tree.item(item_id, "open")
                self.hosts_tree.item(item_id, open=not current_open)

    def toggle_host_selection(self, host_id):
        hostname = self._get_hostname_for_item(host_id)
        if not hostname:
            return
        if hostname in self.selected_hosts:
            self.selected_hosts.remove(hostname)
            self.hosts_tree.set(host_id, "checkbox", Config.get_gui_symbol("unchecked"))
        else:
            self.selected_hosts.add(hostname)
            self.hosts_tree.set(host_id, "checkbox", Config.get_gui_symbol("checked"))

        self.update_selection_info()

    def toggle_group_selection(self, group_id):
        # Get all children belonging to the group
        children = self.hosts_tree.get_children(group_id)
        if not children:
            return

        # Check whether every host in the group is already selected
        all_selected = True
        for child_id in children:
            hostname = self._get_hostname_for_item(child_id)
            if hostname and hostname not in self.selected_hosts:
                all_selected = False
                break

        # Toggle selection state for the whole group
        if all_selected:
            # Remove selection from each host in the group
            for child_id in children:
                hostname = self._get_hostname_for_item(child_id)
                if hostname:
                    if hostname in self.selected_hosts:
                        self.selected_hosts.remove(hostname)
                    self.hosts_tree.set(
                        child_id, "checkbox", Config.get_gui_symbol("unchecked")
                    )
            self.hosts_tree.set(
                group_id, "checkbox", Config.get_gui_symbol("unchecked")
            )
        else:
            # Select every host in the group
            for child_id in children:
                hostname = self._get_hostname_for_item(child_id)
                if hostname:
                    if hostname not in self.selected_hosts:
                        self.selected_hosts.add(hostname)
                    self.hosts_tree.set(
                        child_id, "checkbox", Config.get_gui_symbol("checked")
                    )
            self.hosts_tree.set(group_id, "checkbox", Config.get_gui_symbol("checked"))

        self.update_selection_info()

    def update_host_display(self, host_id, selected):
        # Update checkbox state to reflect selection
        if selected:
            self.hosts_tree.set(host_id, "checkbox", Config.get_gui_symbol("checked"))
        else:
            self.hosts_tree.set(host_id, "checkbox", Config.get_gui_symbol("unchecked"))

    def on_tree_double_click(self, event):
        item_id = self.hosts_tree.identify("item", event.x, event.y)
        if not item_id:
            return

        tags = self.hosts_tree.item(item_id, "tags")

        if "host" in tags:
            hostname = self._get_hostname_for_item(item_id)
            if hostname:
                self.show_host_info_dialog(hostname)

    def show_host_info_dialog(self, hostname):
        info = self.config_parser.get_host_info(hostname)

        # Create a new window
        info_window = tk.Toplevel(self.root)
        info_window.title(f"Host information: {hostname}")
        info_window.geometry("400x300")
        info_window.resizable(True, True)

        # Frame with host details
        info_frame = ttk.Frame(info_window, padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        title_label = ttk.Label(
            info_frame, text=f"{hostname}", font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Text area with host information
        info_text = scrolledtext.ScrolledText(
            info_frame, wrap=tk.WORD, font=("Consolas", 10)
        )
        info_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Populate host information
        if info:
            for key, value in info.items():
                info_text.insert(tk.END, f"{key:15s}: {value}\n")
        else:
            info_text.insert(tk.END, "Host information not found")

        info_text.config(state=tk.DISABLED)

        # Buttons
        button_frame = ttk.Frame(info_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(
            button_frame,
            text="Test connection",
            command=lambda: self.test_host_connection(hostname, info_text),
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Close", command=info_window.destroy).pack(
            side=tk.RIGHT
        )

    def test_host_connection(self, hostname, output_widget):
        def append_text(text: str):
            output_widget.config(state=tk.NORMAL)
            output_widget.insert(tk.END, text)
            output_widget.see(tk.END)
            output_widget.config(state=tk.DISABLED)

        def _test():
            self.root.after(
                0, lambda: append_text(f"\nTesting connection to {hostname}...\n")
            )
            try:
                result = self.ssh_executor.test_connection(hostname)
                if result["success"]:
                    message = f"Connection successful: {result['output']}\n"
                else:
                    message = f"Connection error: {result['error']}\n"
            except Exception as exc:  # pragma: no cover - asynchronous error
                message = f"Exception: {exc}\n"
            self.root.after(0, lambda: append_text(message))

        thread = threading.Thread(target=_test)
        thread.daemon = True
        thread.start()

    def on_host_selection_change(self, event):
        # Placeholder for additional selection change logic
        pass

    def on_tree_right_click(self, event):
        # Right click shows the context menu
        item_id = self.hosts_tree.identify("item", event.x, event.y)
        if item_id:
            self.context_item = item_id
            # Show context menu
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()

    def context_select_host(self):
        # Select host from context menu
        if self.context_item:
            tags = self.hosts_tree.item(self.context_item, "tags")
            if "host" in tags:
                self.toggle_host_selection(self.context_item)

    def context_deselect_host(self):
        # Deselect host from context menu
        if self.context_item:
            tags = self.hosts_tree.item(self.context_item, "tags")
            if "host" in tags:
                hostname = self._get_hostname_for_item(self.context_item)
                if hostname in self.selected_hosts:
                    self.toggle_host_selection(self.context_item)

    def context_show_info(self):
        # Show host information from context menu
        if self.context_item:
            tags = self.hosts_tree.item(self.context_item, "tags")
            if "host" in tags:
                hostname = self._get_hostname_for_item(self.context_item)
                if hostname:
                    self.show_host_info_dialog(hostname)

    def context_test_connection(self):
        # Run quick connection test from context menu
        if self.context_item:
            tags = self.hosts_tree.item(self.context_item, "tags")
            if "host" in tags:
                hostname = self._get_hostname_for_item(self.context_item)
                if hostname:
                    self.quick_test_connection(hostname)

    def quick_test_connection(self, hostname):
        # Quick connection test with status bar feedback
        def _test():
            self.root.after(
                0,
                lambda: self.status_label.config(
                    text=f"Testing {hostname}...", foreground="orange"
                ),
            )

            try:
                result = self.ssh_executor.test_connection(hostname)

                if result["success"]:
                    self.root.after(
                        0,
                        lambda: self.status_label.config(
                            text=f"{hostname} reachable", foreground="green"
                        ),
                    )
                else:
                    self.root.after(
                        0,
                        lambda: self.status_label.config(
                            text=f"{hostname} unreachable", foreground="red"
                        ),
                    )

                # return status to default after 3 seconds
                self.root.after(3000, lambda: self.update_selection_info())

            except Exception:
                self.root.after(
                    0,
                    lambda: self.status_label.config(
                        text=f"Error testing {hostname}", foreground="red"
                    ),
                )
                self.root.after(3000, lambda: self.update_selection_info())

        thread = threading.Thread(target=_test)
        thread.daemon = True
        thread.start()

    def select_all_hosts(self):
        self.selected_hosts.clear()

        for group_id in self.hosts_tree.get_children():
            # Mark group checkbox as selected
            self.hosts_tree.set(group_id, "checkbox", Config.get_gui_symbol("checked"))

            for host_id in self.hosts_tree.get_children(group_id):
                hostname = self._get_hostname_for_item(host_id)
                if hostname:
                    self.selected_hosts.add(hostname)
                    self.hosts_tree.set(
                        host_id, "checkbox", Config.get_gui_symbol("checked")
                    )

        self.update_selection_info()

    def deselect_all_hosts(self):
        self.selected_hosts.clear()

        for group_id in self.hosts_tree.get_children():
            # Remove selection from the entire group
            self.hosts_tree.set(
                group_id, "checkbox", Config.get_gui_symbol("unchecked")
            )

            for host_id in self.hosts_tree.get_children(group_id):
                hostname = self._get_hostname_for_item(host_id)
                if hostname and hostname in self.selected_hosts:
                    self.selected_hosts.remove(hostname)
                self.hosts_tree.set(
                    host_id, "checkbox", Config.get_gui_symbol("unchecked")
                )

        self.update_selection_info()

    def refresh_hosts(self):
        self.selected_hosts.clear()
        self.config_parser = SSHConfigParser(self.ssh_config_path)
        self.ssh_executor = SSHExecutor(self.ssh_config_path)
        self.load_hosts()
        self.update_selection_info()

    def clear_prefix(self):
        self.prefix_var.set("")
        self.load_hosts()

    def expand_all_groups(self):
        for group_id in self.hosts_tree.get_children():
            if "group" in self.hosts_tree.item(group_id, "tags"):
                self.hosts_tree.item(group_id, open=True)

    def collapse_all_groups(self):
        for group_id in self.hosts_tree.get_children():
            if "group" in self.hosts_tree.item(group_id, "tags"):
                self.hosts_tree.item(group_id, open=False)

    def update_selection_info(self):
        count = len(self.selected_hosts)
        self.selection_label.config(text=f"Selected hosts: {count}")

        # Update status message
        if count > 0:
            hosts_list = ", ".join(list(self.selected_hosts)[:3])
            if count > 3:
                hosts_list += f" and {count - 3} more"
            self.status_label.config(text=f"Selected: {hosts_list}", foreground="blue")
        else:
            self.status_label.config(text="Ready", foreground="green")

        # Enable or disable execute button
        if count > 0 and self.command_entry.get().strip():
            self.execute_button.config(state=tk.NORMAL)
        else:
            self.execute_button.config(state=tk.DISABLED)

    def execute_command(self):
        # Execute command on selected hosts
        base_command = self.command_entry.get().strip()
        if not base_command:
            messagebox.showwarning("Warning", "Enter a command to execute")
            return

        if not self.selected_hosts:
            messagebox.showwarning("Warning", "Select hosts to execute the command")
            return

        # Sudo
        sudo_enabled = self.sudo_var.get()
        verbose_enabled = self.verbose_var.get()

        command = base_command
        if sudo_enabled:
            if not command.startswith("sudo "):
                command = f"sudo {command}"

        # Check for potentially dangerous command
        dangerous_result = Config.check_dangerous_command(command)
        if dangerous_result["is_dangerous"]:
            messagebox.showerror(
                "Dangerous command!",
                f"Command blocked as potentially dangerous:\n\n{command}\n\n"
                f"Reason: {dangerous_result['reason']}\n\n"
                "Executing dangerous commands is disabled for safety.",
            )
            return

        if Config.requires_confirmation(command):
            confirm = messagebox.askyesno(
                "Confirmation required",
                f"Command requires confirmation:\n\n{command}\n\n"
                f"Hosts: {', '.join(self.selected_hosts)}\n\n"
                "Execute this command?",
                icon="warning",
            )
            if not confirm:
                return

        self.execute_button.config(state=tk.DISABLED, text="Executing...")
        self.status_label.config(text="Executing commands...", foreground="orange")

        thread = threading.Thread(
            target=self._execute_command_thread,
            args=(
                command,
                sorted(self.selected_hosts, key=lambda host: host.lower()),
                sudo_enabled,
                verbose_enabled,
            ),
        )
        thread.daemon = True
        thread.start()

    def _execute_command_thread(
        self, command, hosts, sudo_enabled: bool, verbose_enabled: bool
    ):
        try:
            sudo_info = " (sudo)" if sudo_enabled else ""
            verbose_info = " (detailed output)" if verbose_enabled else ""

            self.append_result(
                f"\nExecuting command: {command}{sudo_info}{verbose_info}\n"
            )
            self.append_result(f"On hosts: {', '.join(hosts)}\n")
            self.append_result("=" * 60 + "\n")

            # Execute command on each host
            for host in hosts:
                if verbose_enabled:
                    self.append_result(f"\nHost: {host}\n")
                else:
                    self.append_result(f"\n{host}: ")

                try:
                    result = self.ssh_executor.execute_command(host, command)
                    if result["success"]:
                        if verbose_enabled:
                            self.append_result(
                                f"Success:\n{result['output']}\n"
                            )
                            if result["error"]:
                                self.append_result(f"Warnings:\n{result['error']}\n")
                        else:
                            # Short summary
                            output = (
                                result["output"][:100] + "..."
                                if len(result["output"]) > 100
                                else result["output"]
                            )
                            self.append_result(f"{output.replace(chr(10), ' ')}\n")
                    else:
                        if verbose_enabled:
                            self.append_result(
                                f"Error:\n{result['error']}\n"
                            )
                        else:
                            error = (
                                result["error"][:100] + "..."
                                if len(result["error"]) > 100
                                else result["error"]
                            )
                            self.append_result(f"{error.replace(chr(10), ' ')}\n")

                except Exception as exc:
                    if verbose_enabled:
                        self.append_result(f"Exception: {exc}\n")
                    else:
                        self.append_result(f"Error: {str(exc)[:50]}...\n")

                if verbose_enabled:
                    self.append_result("-" * 40 + "\n")

            self.append_result(f"\nExecution completed on {len(hosts)} hosts\n")

        except Exception as exc:
            self.append_result(f"\nCritical error: {exc}\n")

        finally:
            # Restore button to its initial state
            self.root.after(0, self._reset_execute_button)

    def _reset_execute_button(self):
        self.execute_button.config(state=tk.NORMAL, text="Execute Command")
        self.update_selection_info()

    def open_results_window(self):
        window = tk.Toplevel(self.root)
        window.title("Command Output")
        window.geometry("900x600")
        window.minsize(600, 400)

        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)

        container = ttk.Frame(window, padding="10")
        container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        text_widget = tk.Text(
            container,
            wrap=tk.NONE,
            font=Config.GUI_RESULTS_TEXT_FONT,
        )
        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        vscroll = ttk.Scrollbar(
            container, orient=tk.VERTICAL, command=text_widget.yview
        )
        vscroll.grid(row=0, column=1, sticky=(tk.N, tk.S))

        hscroll = ttk.Scrollbar(
            container, orient=tk.HORIZONTAL, command=text_widget.xview
        )
        hscroll.grid(row=1, column=0, sticky=(tk.W, tk.E))

        text_widget.configure(yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)
        text_widget.insert(tk.END, self.results_text.get("1.0", tk.END))
        text_widget.focus_set()

        button_bar = ttk.Frame(container)
        button_bar.grid(row=2, column=0, columnspan=2, sticky=tk.E, pady=(5, 0))
        ttk.Button(
            button_bar,
            text="Copy Output",
            command=self.copy_results_to_clipboard,
        ).pack(side=tk.RIGHT)

    def copy_results_to_clipboard(self):
        content = self.results_text.get("1.0", tk.END)
        if not content.strip():
            self.status_label.config(
                text="Output buffer is empty",
                foreground=Config.get_color("status_info"),
            )
            self.root.after(3000, lambda: self.update_selection_info())
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.status_label.config(
            text="Output copied to clipboard",
            foreground=Config.get_color("status_info"),
        )
        self.root.after(3000, lambda: self.update_selection_info())

    def append_result(self, text):
        def _append():
            self.results_text.config(state=tk.NORMAL)
            self.results_text.insert(tk.END, text)
            self.results_text.see(tk.END)
            self.results_text.config(state=tk.DISABLED)

        self.root.after(0, _append)

    def clear_results(self):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = CommandExecutorApp(root)
    root.mainloop()
