# import tkinter as tk
# from tkinter import ttk, filedialog
# import os
# from lexer import tokenize
# from my_parser import Parser
#
# class IDE(tk.Tk):
#     def __init__(self):
#         super().__init__()
#
#         # Проверка Tkinter
#         try:
#             self._setup_ui()
#         except Exception as e:
#             print(f"Ошибка инициализации GUI: {e}")
#             raise
#
#     def _setup_ui(self):
#         self.title("Анализатор printf")
#         self.geometry("800x600")
#
#         # Главный контейнер
#         main_frame = ttk.Frame(self)
#         main_frame.pack(fill=tk.BOTH, expand=True)
#
#         # Редактор
#         self.editor = tk.Text(main_frame, wrap=tk.WORD, font=('Menlo', 12))
#         self.editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
#
#         # Панель инструментов
#         toolbar = ttk.Frame(main_frame)
#         ttk.Button(toolbar, text="Анализировать", command=self.run_analysis).pack(side=tk.LEFT)
#         toolbar.pack(fill=tk.X, padx=10, pady=5)
#
#         # Консоль
#         self.console = tk.Text(main_frame, height=8, state=tk.DISABLED, bg="#f0f0f0")
#         self.console.pack(fill=tk.X, padx=10, pady=5)
#
#         # Меню
#         self._create_menu()
#
#     def _create_menu(self):
#         menubar = tk.Menu(self)
#
#         # Меню Файл
#         file_menu = tk.Menu(menubar, tearoff=0)
#         file_menu.add_command(label="Открыть", command=self.open_file)
#         file_menu.add_command(label="Сохранить", command=self.save_file)
#         menubar.add_cascade(label="Файл", menu=file_menu)
#
#         self.config(menu=menubar)
#
#     def run_analysis(self):
#         code = self.editor.get("1.0", tk.END)
#         tokens = [t for t in tokenize(code) if t.type not in ('WHITESPACE',)]
#
#         parser = Parser(tokens)
#         errors = parser.parse()
#
#         self.console.config(state=tk.NORMAL)
#         self.console.delete(1.0, tk.END)
#
#         if errors:
#             for error in errors:
#                 self.console.insert(tk.END, f"● {error}\n")
#         else:
#             self.console.insert(tk.END, "✓ Программа корректна\n")
#
#         self.console.config(state=tk.DISABLED)
#
#     def open_file(self):
#         path = filedialog.askopenfilename(filetypes=[("C files", "*.c")])
#         if path:
#             with open(path, 'r') as f:
#                 self.editor.delete(1.0, tk.END)
#                 self.editor.insert(tk.END, f.read())
#
#     def save_file(self):
#         path = filedialog.asksaveasfilename(defaultextension=".c")
#         if path:
#             with open(path, 'w') as f:
#                 f.write(self.editor.get(1.0, tk.END))
#
# if __name__ == "__main__":
#     try:
#         app = IDE()
#         app.mainloop()
#     except tk.TclError as e:
#         print(f"Fatal GUI error: {e}\nПроверьте установку Tkinter!")

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
import os
import re
from lexer import tokenize, Token
from my_parser import Parser


class IDE(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Compiler v1.0")
        self.geometry("1000x700")
        self.is_modified = False
        self.current_file = None
        self.icons = {
            'new': '■',
            'open': '📂',
            'save': '💾',
            'start': '▶',  # Новая иконка
            'undo': '↩',
            'redo': '↪',
            'cut': '✂',
            'copy': '⎘',
            'paste': '📋',
            'help': '❓'
        }
        # Настройка стилей
        self._setup_theme()
        self._setup_ui()
        self._bind_events()

    # ---------------------------
    # Основные методы интерфейса
    # ---------------------------

    def _setup_theme(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure(bg='#2d2d2d')

        self.style.configure(
            'TButton',
            background='#3d3d3d',
            foreground='white',
            font=('Arial', 10)
        )

    def _setup_ui(self):
        # Главный контейнер
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Меню
        self._create_menu()

        # Панель инструментов
        self._create_toolbar(main_frame)

        # Редактор с нумерацией строк
        self._create_editor(main_frame)

        # Консоль ошибок
        self._create_console(main_frame)

    def _create_menu(self):
        menubar = tk.Menu(self)

        # Меню: Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Новый", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Открыть", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Сохранить", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Сохранить как...", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.on_close)
        menubar.add_cascade(label="Файл", menu=file_menu)

        # Меню: Правка
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Отменить", command=lambda: self.editor.edit_undo(), accelerator="Ctrl+Z")
        edit_menu.add_command(label="Повторить", command=lambda: self.editor.edit_redo(), accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Вырезать", command=lambda: self.editor.event_generate("<<Cut>>"),
                              accelerator="Ctrl+X")
        edit_menu.add_command(label="Копировать", command=lambda: self.editor.event_generate("<<Copy>>"),
                              accelerator="Ctrl+C")
        edit_menu.add_command(label="Вставить", command=lambda: self.editor.event_generate("<<Paste>>"),
                              accelerator="Ctrl+V")
        menubar.add_cascade(label="Правка", menu=edit_menu)

        # Меню: Текст
        text_menu = self._create_docs_menu(menubar)
        menubar.add_cascade(label="Текст", menu=text_menu)

        # Меню: Справка
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Справка", command=self.show_help)
        help_menu.add_command(label="О программе", command=self.show_about)
        menubar.add_cascade(label="Справка", menu=help_menu)

        self.config(menu=menubar)

    def _create_docs_menu(self, parent):
        text_menu = tk.Menu(parent, tearoff=0)
        docs = [
            ("Постановка задачи", "ProblemStatement.html"),
            ("Грамматика", "Grammar.html"),
            ("Классификация грамматики", "GrammarClassification.html"),
            ("Метод анализа", "MethodOfAnalysis.html"),
            ("Диагностика ошибок", "NeutralizingErrors.html"),
            ("Тестовый пример", "TestCase.html"),
            ("Список литературы", "ListOfLiterature.html"),
            ("Исходный код", "About.html")
        ]
        for label, filename in docs:
            text_menu.add_command(
                label=label,
                command=lambda f=filename: self.open_doc(f)
            )
        return text_menu

    def _create_toolbar(self, parent):
        toolbar = ttk.Frame(parent)
        buttons = [
            ('new', self.icons['new'] + ' Новый', self.new_file),
            ('open', self.icons['open'] + ' Открыть', self.open_file),
            ('save', self.icons['save'] + ' Сохранить', self.save_file),
            ('start', self.icons['start'] + ' Пуск', self.run_analysis),
            ('undo', self.icons['undo'] + ' Отменить', lambda: self.editor.edit_undo()),
            ('redo', self.icons['redo'] + ' Повторить', lambda: self.editor.edit_redo()),
            ('cut', self.icons['cut'] + ' Вырезать', lambda: self.editor.event_generate("<<Cut>>")),
            ('copy', self.icons['copy'] + ' Копировать', lambda: self.editor.event_generate("<<Copy>>")),
            ('paste', self.icons['paste'] + ' Вставить', lambda: self.editor.event_generate("<<Paste>>")),
            ('help', self.icons['help'] + ' Справка', self.show_help)
        ]

        for icon, text, cmd in buttons:
            btn = ttk.Button(
                toolbar,
                text=text,
                command=cmd,
                style='TButton'
            )
            btn.pack(side=tk.LEFT, padx=2)

        toolbar.pack(fill=tk.X, padx=5, pady=5)

    def _create_editor(self, parent):
        editor_frame = ttk.Frame(parent)

        # Номера строк
        self.line_numbers = tk.Text(
            editor_frame,
            width=4,
            padx=5,
            state='disabled',
            bg='#1e1e1e',
            fg='#858585',
            font=('Menlo', 12)
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Основной редактор
        self.editor = tk.Text(
            editor_frame,
            wrap=tk.NONE,
            font=('Menlo', 12),
            undo=True,
            bg='#1e1e1e',
            fg='white',
            insertbackground='white'
        )
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Привязка прокрутки
        scroll = ttk.Scrollbar(editor_frame, command=self._sync_scroll)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor.config(yscrollcommand=self._update_scroll)

        editor_frame.pack(fill=tk.BOTH, expand=True)

    def _create_console(self, parent):
        self.console = tk.Text(
            parent,
            height=8,
            state='disabled',
            bg='#1e1e1e',
            fg='#e06c75',
            font=('Menlo', 10)
        )
        self.console.pack(fill=tk.BOTH, padx=5, pady=5)
        self.console.bind("<Double-Button-1>", self._jump_to_error)

    # ---------------------------
    # Основная логика приложения
    # ---------------------------

    def run_analysis(self):
        """Основной метод анализа кода"""
        # Очистка предыдущих ошибок
        self.editor.tag_remove("error", "1.0", tk.END)
        code = self.editor.get("1.0", tk.END)

        # Лексический анализ
        tokens = tokenize(code)
        lex_errors = [t for t in tokens if t.type == 'ERROR']

        # Синтаксический анализ
        parser = Parser(tokens)
        syntax_errors = parser.parse()

        # Обработка ошибок
        self._process_errors(lex_errors + syntax_errors)

    def _process_errors(self, errors):
        """Обработка и отображение ошибок"""
        self.console.config(state=tk.NORMAL)
        self.console.delete("1.0", tk.END)

        # Настройка подсветки
        self.editor.tag_config(
            "error",
            background="#4b1f1f",
            underline=True,
            underlinefg="#ff5555"
        )

        for error in errors:
            # Обработка лексических ошибок
            if isinstance(error, Token):
                line, col = error.position
                msg = f"Лексическая ошибка: '{error.value}'"
                length = len(error.value)

            # Обработка синтаксических ошибок
            else:
                line, col = self._parse_error_position(error)
                msg = error
                length = 1

            # Подсветка в редакторе
            start = f"{line}.{col - 1}"
            end = f"{line}.{col + length - 1}"
            self.editor.tag_add("error", start, end)

            # Вывод в консоль
            self.console.insert(tk.END, f"● Строка {line}: {msg}\n")

        if not errors:
            self.console.insert(tk.END, "✓ Программа корректна\n")

        self.console.config(state=tk.DISABLED)

    def _parse_error_position(self, error_msg):
        """Извлечение позиции из сообщения об ошибке"""
        match = re.search(r'Строка (\d+):(\d+)', error_msg)
        if match:
            return int(match.group(1)), int(match.group(2))
        return 1, 1

    def _jump_to_error(self, event):
        """Переход к ошибке по двойному клику"""
        line = self.console.index(f"@{event.x},{event.y} linestart")
        error_text = self.console.get(line, f"{line} lineend")

        match = re.search(r'Строка (\d+)', error_text)
        if match:
            line_num = match.group(1)
            self.editor.mark_set("insert", f"{line_num}.0")
            self.editor.see(f"{line_num}.0")

    # Остальные методы (new_file, open_file и т.д.) остаются без изменений
    # ...

    def _bind_events(self):
        self.editor.bind('<<Modified>>', self._on_text_modified)
        self.editor.bind('<KeyRelease>', self._update_line_numbers)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _on_text_modified(self, event):
        self.is_modified = True
        self.editor.edit_modified(False)

    def _update_line_numbers(self, event=None):
        lines = self.editor.get('1.0', 'end-1c').split('\n')
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        for i, _ in enumerate(lines, 1):
            self.line_numbers.insert('end', f'{i}\n')
        self.line_numbers.config(state='disabled')

    def _sync_scroll(self, *args):
        self.editor.yview(*args)
        self.line_numbers.yview(*args)

    def _update_scroll(self, first, last):
        self.line_numbers.yview_moveto(first)
        self.editor.yview_moveto(first)

    def new_file(self):
        if self.is_modified:
            if not self._ask_save_changes():
                return
        self.editor.delete('1.0', 'end')
        self.is_modified = False

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("C files", "*.c")])
        if path:
            with open(path, 'r') as f:
                self.editor.delete('1.0', 'end')
                self.editor.insert('1.0', f.read())
            self.is_modified = False

    def save_file(self):
        if not hasattr(self, 'current_file') or not self.current_file:
            self.save_as()
        else:
            self._save_to_file(self.current_file)

    def save_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".c")
        if path:
            self._save_to_file(path)
            self.current_file = path

    def _save_to_file(self, path):
        with open(path, 'w') as f:
            f.write(self.editor.get('1.0', 'end'))
        self.is_modified = False

    def on_close(self):
        if self.is_modified:
            choice = messagebox.askyesnocancel(
                "Сохранение",
                "Хотите сохранить изменения перед закрытием?"
            )
            if choice is None:  # Отмена
                return
            if choice:  # Да
                self.save_file()
        self.destroy()

    def open_doc(self, filename):
        doc_path = os.path.join('docs', filename)
        if os.path.exists(doc_path):
            webbrowser.open(f'file://{os.path.abspath(doc_path)}')
        else:
            messagebox.showerror("Ошибка", f"Файл {filename} не найден")

    def show_about(self):
        about_text = (
            "Compiler - текстовый редактор для языкового процессора\n\n"
            "Название приложения: Compiler\n"
            "Версия: 1.0\n"
            "Автор: Махалина Б.А.\n"
            "Дата создания: 10.03.2025"
        )
        messagebox.showinfo("О программе", about_text)

    def show_help(self):
        self.open_doc('help.html')

    def _ask_save_changes(self):
        return messagebox.askyesno(
            "Сохранение",
            "Сохранить изменения в текущем файле?"
        )


if __name__ == "__main__":
    app = IDE()
    app.mainloop()


