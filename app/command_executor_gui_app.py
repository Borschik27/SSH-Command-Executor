#!/usr/bin/env python3

# Компонент GUI приложения Command Executor.

import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from config import Config
from ssh_config_parser import SSHConfigParser
from ssh_executor import SSHExecutor


class CommandExecutorApp:
    def __init__(self, root, args=None):
        self.root = root
        self.args = args or type("Args", (), {})()  # Пустой объект если args не передан

        # Настройка окна из конфигурации
        self.root.title(Config.GUI_WINDOW_TITLE)
        self.root.geometry(Config.GUI_WINDOW_GEOMETRY)
        self.root.minsize(Config.GUI_WINDOW_MIN_WIDTH, Config.GUI_WINDOW_MIN_HEIGHT)

        # Инициализация компонентов с настройками из args
        ssh_config_path = getattr(self.args, "config", Config.DEFAULT_SSH_CONFIG_PATH)
        self.ssh_config_path = ssh_config_path
        self.config_parser = SSHConfigParser(ssh_config_path)
        self.ssh_executor = SSHExecutor(ssh_config_path)
        self.selected_hosts = set()

        # Создание интерфейса
        self.create_widgets()
        self.load_hosts()

    def create_widgets(self):
        # Главный контейнер
        main_frame = ttk.Frame(self.root, padding=Config.GUI_MAIN_PADDING)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настройка растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Заголовок
        title_label = ttk.Label(main_frame, text=Config.APP_NAME, font=Config.GUI_TITLE_FONT)
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        # Левая панель - выбор хостов
        self.create_hosts_panel(main_frame)

        # Правая панель - команды и результаты
        self.create_command_panel(main_frame)

        # Нижняя панель - кнопки управления
        self.create_control_panel(main_frame)

    def create_hosts_panel(self, parent):
        # Фрейм для хостов
        hosts_frame = ttk.LabelFrame(parent, text="Хосты", padding=Config.GUI_FRAME_PADDING)
        hosts_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        hosts_frame.columnconfigure(0, weight=1)
        hosts_frame.rowconfigure(2, weight=1)

        # Фрейм для выбора префикса
        prefix_frame = ttk.Frame(hosts_frame)
        prefix_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        ttk.Label(prefix_frame, text="Префикс:").pack(side=tk.LEFT, padx=(0, 5))
        # Используем префикс из аргументов если есть
        initial_prefix = getattr(self.args, "prefix", Config.DEFAULTS["prefix_filter"])
        self.prefix_var = tk.StringVar(value=initial_prefix)
        self.prefix_entry = ttk.Entry(prefix_frame, textvariable=self.prefix_var, width=Config.GUI_PREFIX_ENTRY_WIDTH)
        self.prefix_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.prefix_entry.bind("<Return>", lambda e: self.load_hosts())

        ttk.Button(prefix_frame, text="Загрузить", command=self.load_hosts).pack(side=tk.LEFT, padx=Config.GUI_BUTTON_PADX)
        ttk.Button(prefix_frame, text="Очистить", command=self.clear_prefix).pack(side=tk.LEFT)

        # Кнопки выбора
        buttons_frame = ttk.Frame(hosts_frame)
        buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        ttk.Button(buttons_frame, text="Выбрать все", command=self.select_all_hosts).pack(side=tk.LEFT, padx=Config.GUI_BUTTON_PADX)
        ttk.Button(buttons_frame, text="Снять выбор", command=self.deselect_all_hosts).pack(side=tk.LEFT, padx=Config.GUI_BUTTON_PADX)
        ttk.Button(buttons_frame, text="Развернуть", command=self.expand_all_groups).pack(side=tk.LEFT, padx=Config.GUI_BUTTON_PADX)
        ttk.Button(buttons_frame, text="Свернуть", command=self.collapse_all_groups).pack(side=tk.LEFT, padx=Config.GUI_BUTTON_PADX)
        ttk.Button(buttons_frame, text="Обновить", command=self.refresh_hosts).pack(side=tk.LEFT, padx=Config.GUI_BUTTON_PADX)

        # Дерево хостов
        tree_frame = ttk.Frame(hosts_frame)
        tree_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # Treeview для хостов с чекбоксами
        self.hosts_tree = ttk.Treeview(tree_frame, selectmode="extended", columns=("checkbox",), show="tree headings")
        self.hosts_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Скроллбар для дерева
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.hosts_tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.hosts_tree.configure(yscrollcommand=tree_scrollbar.set)

        # Настройка колонок
        self.hosts_tree.heading("#0", text="Хосты")
        self.hosts_tree.heading("checkbox", text=Config.get_gui_symbol("checkbox_header"))
        self.hosts_tree.column("#0", width=Config.GUI_TREE_HOST_COLUMN_WIDTH, minwidth=Config.GUI_TREE_HOST_COLUMN_MIN_WIDTH)
        self.hosts_tree.column("checkbox", width=Config.GUI_TREE_CHECKBOX_COLUMN_WIDTH, minwidth=Config.GUI_TREE_CHECKBOX_COLUMN_MIN_WIDTH, anchor="center")

        # Настройка стилей для подсветки
        self.hosts_tree.tag_configure("selected_host", background=Config.get_color("selected_host_bg"), foreground=Config.get_color("selected_host_fg"))
        self.hosts_tree.tag_configure("unselected_host", background=Config.get_color("unselected_host_bg"), foreground=Config.get_color("unselected_host_fg"))
        self.hosts_tree.tag_configure("group", background=Config.get_color("group_bg"), foreground=Config.get_color("group_fg"))

        # Обработка выбора
        self.hosts_tree.bind("<<TreeviewSelect>>", self.on_host_selection_change)
        self.hosts_tree.bind("<Button-1>", self.on_tree_click)
        self.hosts_tree.bind("<Double-1>", self.on_tree_double_click)
        self.hosts_tree.bind("<Button-3>", self.on_tree_right_click)

        # Создаем контекстное меню
        self.context_menu = tk.Menu(self.hosts_tree, tearoff=0)
        self.context_menu.add_command(label="Выбрать хост", command=self.context_select_host)
        self.context_menu.add_command(label="Снять выбор", command=self.context_deselect_host)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Информация о хосте", command=self.context_show_info)
        self.context_menu.add_command(label="Тест подключения", command=self.context_test_connection)

        # Переменная для хранения выбранного элемента контекстного меню
        self.context_item = None

    def create_command_panel(self, parent):
        # Фрейм для команд
        command_frame = ttk.LabelFrame(parent, text="Выполнение команд", padding="5")
        command_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        command_frame.columnconfigure(0, weight=1)
        command_frame.rowconfigure(4, weight=1)  # Обновляем номер строки для растягивания

        # Поле ввода команды
        ttk.Label(command_frame, text="Команда для выполнения:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        # Фрейм для опций (чекбоксы над полем ввода)
        options_frame = ttk.Frame(command_frame)
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        # Галочка sudo
        self.sudo_var = tk.BooleanVar(value=Config.DEFAULTS["sudo_enabled"])
        self.sudo_checkbox = ttk.Checkbutton(
            options_frame,
            text="sudo",
            variable=self.sudo_var,
            command=self.update_selection_info,
        )
        self.sudo_checkbox.pack(side=tk.LEFT, padx=(0, 10))

        # Галочка показа подробного вывода
        verbose_default = getattr(self.args, "verbose", Config.DEFAULTS["verbose_output"])
        self.verbose_var = tk.BooleanVar(value=verbose_default)
        self.verbose_checkbox = ttk.Checkbutton(
            options_frame,
            text="Подробный вывод",
            variable=self.verbose_var,
        )
        self.verbose_checkbox.pack(side=tk.LEFT)

        # Фрейм для поля ввода команды
        cmd_input_frame = ttk.Frame(command_frame)
        cmd_input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        cmd_input_frame.columnconfigure(0, weight=1)

        self.command_entry = ttk.Entry(cmd_input_frame, font=Config.GUI_COMMAND_ENTRY_FONT)
        self.command_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.command_entry.bind("<Return>", lambda e: self.execute_command())
        self.command_entry.bind("<KeyRelease>", lambda e: self.update_selection_info())

        # Область результатов
        ttk.Label(command_frame, text="Результаты выполнения:").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))

        # Текстовое поле с прокруткой для результатов
        self.results_text = scrolledtext.ScrolledText(
            command_frame,
            wrap=tk.WORD,
            font=Config.GUI_RESULTS_TEXT_FONT,
            state=tk.DISABLED,
        )
        self.results_text.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

    def create_control_panel(self, parent):
        # Фрейм для кнопок
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=Config.GUI_CONTROL_PANEL_PADY)

        # Информация о выбранных хостах
        self.selection_label = ttk.Label(control_frame, text="Выбрано хостов: 0")
        self.selection_label.pack(side=tk.LEFT)

        # Дополнительная информация
        self.status_label = ttk.Label(
            control_frame,
            text=Config.MESSAGES["ready_status"],
            foreground=Config.get_color("status_ready"),
        )
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))

        # Кнопки управления
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT)

        self.execute_button = ttk.Button(
            button_frame,
            text="Выполнить команду",
            command=self.execute_command,
            state=tk.DISABLED,
        )
        self.execute_button.pack(side=tk.LEFT, padx=(0, 5))

        self.clear_button = ttk.Button(
            button_frame,
            text="Очистить результаты",
            command=self.clear_results,
        )
        self.clear_button.pack(side=tk.LEFT, padx=(0, 5))

        self.exit_button = ttk.Button(
            button_frame,
            text="Выход",
            command=self.root.quit,
        )
        self.exit_button.pack(side=tk.LEFT)

    def load_hosts(self):
        try:
            # Получаем префикс из поля ввода
            prefix = Config.validate_prefix(self.prefix_var.get())

            # Получаем сгруппированные хосты
            groups = self.config_parser.get_grouped_hosts_with_prefix(prefix)

            # Очищаем дерево и выбор
            for item in self.hosts_tree.get_children():
                self.hosts_tree.delete(item)
            self.selected_hosts.clear()

            if not groups:
                if prefix:
                    self.append_result(Config.get_message("hosts_with_prefix_not_found", prefix=prefix) + "\n")
                else:
                    self.append_result(Config.get_message("hosts_not_found") + "\n")
                self.update_selection_info()
                return

            # Добавляем группы и хосты в дерево
            total_hosts = 0

            for group_name in sorted(groups.keys()):
                hosts_in_group = groups[group_name]
                total_hosts += len(hosts_in_group)

                # Создаем заголовок группы
                group_display = f"Группа '{group_name}' ({len(hosts_in_group)} хостов)"
                group_id = self.hosts_tree.insert(
                    "",
                    "end",
                    text=group_display,
                    values=(Config.get_gui_symbol("unchecked"),),
                    tags=("group",),
                )

                # Добавляем хосты в группу
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

                # Разворачиваем группу по настройке по умолчанию
                self.hosts_tree.item(group_id, open=Config.DEFAULTS["tree_groups_expanded"])

            # Показываем статистику
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
                    Config.get_message("hosts_loaded", count=total_hosts, groups=len(groups)) + "\n"
                )

            self.append_result(Config.get_message("total_hosts_info", total=all_hosts_count) + "\n")
            self.update_selection_info()

        except Exception as exc:
            messagebox.showerror("Ошибка", f"Ошибка загрузки хостов: {exc}")
            self.append_result(f"{Config.get_gui_symbol('error')} Ошибка загрузки хостов: {exc}\n")

    def on_tree_click(self, event):
        item_id = self.hosts_tree.identify("item", event.x, event.y)
        column = self.hosts_tree.identify("column", event.x, event.y)

        if not item_id:
            return

        tags = self.hosts_tree.item(item_id, "tags")

        # Клик по колонке чекбокса
        if column == "#1":  # колонка чекбокса
            if "group" in tags:
                # Клик по группе - переключаем всю группу
                self.toggle_group_selection(item_id)
            elif "host" in tags:
                # Клик по хосту - переключаем хост
                self.toggle_host_selection(item_id)
        elif column == "#0":  # клик по названию
            if "group" in tags:
                # Клик по названию группы - сворачиваем/разворачиваем
                current_open = self.hosts_tree.item(item_id, "open")
                self.hosts_tree.item(item_id, open=not current_open)

    def toggle_host_selection(self, host_id):
        values = self.hosts_tree.item(host_id, "values")
        if len(values) < 2:
            return

        hostname = values[1]  # hostname теперь во втором элементе values
        if hostname in self.selected_hosts:
            self.selected_hosts.remove(hostname)
            self.hosts_tree.set(host_id, "checkbox", Config.get_gui_symbol("unchecked"))
        else:
            self.selected_hosts.add(hostname)
            self.hosts_tree.set(host_id, "checkbox", Config.get_gui_symbol("checked"))

        self.update_selection_info()

    def toggle_group_selection(self, group_id):
        # Получаем всех детей группы
        children = self.hosts_tree.get_children(group_id)
        if not children:
            return

        # Проверяем, выбраны ли все хосты в группе
        all_selected = True
        for child_id in children:
            values = self.hosts_tree.item(child_id, "values")
            if len(values) >= 2:
                hostname = values[1]
                if hostname not in self.selected_hosts:
                    all_selected = False
                    break

        # Переключаем состояние всей группы
        if all_selected:
            # Снимаем выбор со всех хостов группы
            for child_id in children:
                values = self.hosts_tree.item(child_id, "values")
                if len(values) >= 2:
                    hostname = values[1]
                    if hostname in self.selected_hosts:
                        self.selected_hosts.remove(hostname)
                    self.hosts_tree.set(child_id, "checkbox", Config.get_gui_symbol("unchecked"))
            self.hosts_tree.set(group_id, "checkbox", Config.get_gui_symbol("unchecked"))
        else:
            # Выбираем все хосты группы
            for child_id in children:
                values = self.hosts_tree.item(child_id, "values")
                if len(values) >= 2:
                    hostname = values[1]
                    if hostname not in self.selected_hosts:
                        self.selected_hosts.add(hostname)
                    self.hosts_tree.set(child_id, "checkbox", Config.get_gui_symbol("checked"))
            self.hosts_tree.set(group_id, "checkbox", Config.get_gui_symbol("checked"))

        self.update_selection_info()

    def update_host_display(self, host_id, selected):
        # Состояние отображается через чекбокс
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
            values = self.hosts_tree.item(item_id, "values")
            if len(values) >= 2:
                hostname = values[1]
                self.show_host_info_dialog(hostname)

    def show_host_info_dialog(self, hostname):
        info = self.config_parser.get_host_info(hostname)

        # Создаем новое окно
        info_window = tk.Toplevel(self.root)
        info_window.title(f"Информация о хосте: {hostname}")
        info_window.geometry("400x300")
        info_window.resizable(True, True)

        # Фрейм с информацией
        info_frame = ttk.Frame(info_window, padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        title_label = ttk.Label(info_frame, text=f"{hostname}", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))

        # Текстовое поле с информацией
        info_text = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD, font=("Consolas", 10))
        info_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Заполняем информацией
        if info:
            for key, value in info.items():
                info_text.insert(tk.END, f"{key:15s}: {value}\n")
        else:
            info_text.insert(tk.END, "Информация о хосте не найдена")

        info_text.config(state=tk.DISABLED)

        # Кнопки
        button_frame = ttk.Frame(info_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(
            button_frame,
            text="Тест подключения",
            command=lambda: self.test_host_connection(hostname, info_text),
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Закрыть", command=info_window.destroy).pack(side=tk.RIGHT)

    def test_host_connection(self, hostname, output_widget):
        def append_text(text: str):
            output_widget.config(state=tk.NORMAL)
            output_widget.insert(tk.END, text)
            output_widget.see(tk.END)
            output_widget.config(state=tk.DISABLED)

        def _test():
            self.root.after(0, lambda: append_text(f"\nТестирование подключения к {hostname}...\n"))
            try:
                result = self.ssh_executor.test_connection(hostname)
                if result["success"]:
                    message = f"Подключение успешно: {result['output']}\n"
                else:
                    message = f"Ошибка подключения: {result['error']}\n"
            except Exception as exc:  # pragma: no cover - асинхронная ошибка
                message = f"Исключение: {exc}\n"
            self.root.after(0, lambda: append_text(message))

        thread = threading.Thread(target=_test)
        thread.daemon = True
        thread.start()

    def on_host_selection_change(self, event):
        # Эта функция может быть использована для дополнительной логики
        pass

    def on_tree_right_click(self, event):
        # Правый клик - показ контекстного меню
        item_id = self.hosts_tree.identify("item", event.x, event.y)
        if item_id:
            self.context_item = item_id
            # Показываем контекстное меню
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()

    def context_select_host(self):
        # Выбрать хост
        if self.context_item:
            tags = self.hosts_tree.item(self.context_item, "tags")
            if "host" in tags:
                self.toggle_host_selection(self.context_item)

    def context_deselect_host(self):
        # Снять выбор
        if self.context_item:
            tags = self.hosts_tree.item(self.context_item, "tags")
            if "host" in tags:
                values = self.hosts_tree.item(self.context_item, "values")
                if len(values) >= 2 and values[1] in self.selected_hosts:
                    self.toggle_host_selection(self.context_item)

    def context_show_info(self):
        # Показать информацию о хосте
        if self.context_item:
            tags = self.hosts_tree.item(self.context_item, "tags")
            if "host" in tags:
                values = self.hosts_tree.item(self.context_item, "values")
                if len(values) >= 2:
                    self.show_host_info_dialog(values[1])

    def context_test_connection(self):
        # Тест подключения к хосту
        if self.context_item:
            tags = self.hosts_tree.item(self.context_item, "tags")
            if "host" in tags:
                values = self.hosts_tree.item(self.context_item, "values")
                if len(values) >= 2:
                    self.quick_test_connection(values[1])

    def quick_test_connection(self, hostname):
        # Быстрый тест подключения с показом результата в статусе
        def _test():
            self.root.after(
                0, lambda: self.status_label.config(text=f"Тестирование {hostname}...", foreground="orange")
            )

            try:
                result = self.ssh_executor.test_connection(hostname)

                if result["success"]:
                    self.root.after(0, lambda: self.status_label.config(text=f"{hostname} доступен", foreground="green"))
                else:
                    self.root.after(0, lambda: self.status_label.config(text=f"{hostname} недоступен", foreground="red"))

                # Через 3 секунды вернуть статус к обычному
                self.root.after(3000, lambda: self.update_selection_info())

            except Exception as exc:
                self.root.after(0, lambda: self.status_label.config(text=f"Ошибка теста {hostname}", foreground="red"))
                self.root.after(3000, lambda: self.update_selection_info())

        thread = threading.Thread(target=_test)
        thread.daemon = True
        thread.start()

    def select_all_hosts(self):
        self.selected_hosts.clear()

        for group_id in self.hosts_tree.get_children():
            # Выбираем группу
            self.hosts_tree.set(group_id, "checkbox", Config.get_gui_symbol("checked"))

            for host_id in self.hosts_tree.get_children(group_id):
                values = self.hosts_tree.item(host_id, "values")
                if len(values) >= 2:
                    hostname = values[1]
                    self.selected_hosts.add(hostname)
                    self.hosts_tree.set(host_id, "checkbox", Config.get_gui_symbol("checked"))

        self.update_selection_info()

    def deselect_all_hosts(self):
        self.selected_hosts.clear()

        for group_id in self.hosts_tree.get_children():
            # Снимаем выбор с группы
            self.hosts_tree.set(group_id, "checkbox", Config.get_gui_symbol("unchecked"))

            for host_id in self.hosts_tree.get_children(group_id):
                self.hosts_tree.set(host_id, "checkbox", Config.get_gui_symbol("unchecked"))

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
        self.selection_label.config(text=f"Выбрано хостов: {count}")

        # Обновляем статус
        if count > 0:
            hosts_list = ", ".join(list(self.selected_hosts)[:3])
            if count > 3:
                hosts_list += f" и еще {count - 3}"
            self.status_label.config(text=f"Выбраны: {hosts_list}", foreground="blue")
        else:
            self.status_label.config(text="Готов к работе", foreground="green")

        # Активируем/деактивируем кнопку выполнения
        if count > 0 and self.command_entry.get().strip():
            self.execute_button.config(state=tk.NORMAL)
        else:
            self.execute_button.config(state=tk.DISABLED)

    def execute_command(self):
        # Выполнение команды на выбранных хостах
        base_command = self.command_entry.get().strip()
        if not base_command:
            messagebox.showwarning("Предупреждение", "Введите команду для выполнения")
            return

        if not self.selected_hosts:
            messagebox.showwarning("Предупреждение", "Выберите хосты для выполнения команды")
            return

        # Sudo
        command = base_command
        if self.sudo_var.get():
            if not command.startswith("sudo "):
                command = f"sudo {command}"

        self.execute_button.config(state=tk.DISABLED, text="Выполняется...")
        self.status_label.config(text="Выполнение команд...", foreground="orange")

        thread = threading.Thread(
            target=self._execute_command_thread,
            args=(command, sorted(self.selected_hosts, key=lambda host: host.lower())),
        )
        thread.daemon = True
        thread.start()

    def _execute_command_thread(self, command, hosts):
        try:
            sudo_info = " (sudo)" if self.sudo_var.get() else ""
            verbose_info = " (Подробный вывод)" if self.verbose_var.get() else ""

            self.append_result(f"\nВыполнение команды: {command}{sudo_info}{verbose_info}\n")
            self.append_result(f"На хостах: {', '.join(hosts)}\n")
            self.append_result("=" * 60 + "\n")

            # Выполняем команду на каждом хосте
            for host in hosts:
                if self.verbose_var.get():
                    self.append_result(f"\nХост: {host}\n")
                else:
                    self.append_result(f"\n{host}: ")

                try:
                    result = self.ssh_executor.execute_command(host, command)
                    if result["success"]:
                        if self.verbose_var.get():
                            self.append_result(
                                f"Успешно (код: {result['return_code']}):\n{result['output']}\n"
                            )
                            if result["error"]:
                                self.append_result(f"Предупреждения:\n{result['error']}\n")
                        else:
                            # Краткий вывод
                            output = (
                                result["output"][:100] + "..."
                                if len(result["output"]) > 100
                                else result["output"]
                            )
                            self.append_result(f"{output.replace(chr(10), ' ')}\n")
                    else:
                        if self.verbose_var.get():
                            self.append_result(
                                f"Ошибка (код: {result['return_code']}):\n{result['error']}\n"
                            )
                        else:
                            error = (
                                result["error"][:100] + "..."
                                if len(result["error"]) > 100
                                else result["error"]
                            )
                            self.append_result(f"{error.replace(chr(10), ' ')}\n")

                except Exception as exc:
                    if self.verbose_var.get():
                        self.append_result(f"Исключение: {exc}\n")
                    else:
                        self.append_result(f"Ошибка: {str(exc)[:50]}...\n")

                if self.verbose_var.get():
                    self.append_result("-" * 40 + "\n")

            self.append_result(f"\nВыполнение завершено на {len(hosts)} хостах\n")

        except Exception as exc:
            self.append_result(f"\nКритическая ошибка: {exc}\n")

        finally:
            # Возвращаем кнопку в исходное состояние
            self.root.after(0, self._reset_execute_button)

    def _reset_execute_button(self):
        self.execute_button.config(state=tk.NORMAL, text="Выполнить команду")
        self.update_selection_info()

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
