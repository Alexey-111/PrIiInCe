import sqlite3, sys, os
import tkinter as tk
from tkinter import ttk
from DB import DB
import pandas as pd
from tkinter.messagebox import showerror, showinfo

BOOK_HEADERS = ["№", "Название", "Жанр", "Афтор", "Адрес", "Цена"]
POSTAFSHIK_HEADERS = ["№", "№ документа", "Наименование"]
STUDENT_HEADERS = ["№", "Фамилия Имя Отчество", "Группа"]
FORMULYAR_HEADERS = ["№", "Дата выдачи", "Дата возврата", "№ книги", "№ студента"]
LIBRARY_HEADERS = ["№", "Название книги", "Жанр", "Афтор", "Студент", "Поставшик", "Дата выдачи"]
SPISANIYA_HEADERS = ["№", "Дата", "Причина", "№ книги"]

class WindowMain(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Отдел кадров')
        self.last_headers = None

        # Создание фрейма для отображения таблицы
        self.table_frame = tk.Frame(self, width=700, height=400)
        self.table_frame.grid(row=0, column=0, padx=5, pady=5)

        # Загрузка фона
        lbl = tk.Label(self.table_frame, text='Таблица не открыта', font=("Calibri", 40))
        lbl.place(relwidth=1, relheight=1)

        # Создание меню
        self.menu_bar = tk.Menu(self, background='#555', foreground='white')

        # Меню "Файл"
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Выход", command=self.quit)
        self.menu_bar.add_cascade(label="Файл", menu=file_menu)

        # Меню "Справочники"
        references_menu = tk.Menu(self.menu_bar, tearoff=0)
        references_menu.add_command(label="книги", command=lambda: self.show_table("SELECT * FROM book", BOOK_HEADERS))
        references_menu.add_command(label="Поставщики", command=lambda: self.show_table("SELECT * FROM postafshik", POSTAFSHIK_HEADERS))
        references_menu.add_command(label="Студенты", command=lambda: self.show_table("SELECT * FROM student", STUDENT_HEADERS))
        self.menu_bar.add_cascade(label="Справочники", menu=references_menu)

        # Меню "Таблицы"
        tables_menu = tk.Menu(self.menu_bar, tearoff=0)
        tables_menu.add_command(label="Формуляр", command=lambda: self.show_table("SELECT * FROM formulyar", FORMULYAR_HEADERS))
        tables_menu.add_command(label="Библиотека", command=lambda: self.show_table('''
                SELECT school_library.id, book.name AS book_name, book.genre AS book_genre, 
                       book.author AS book_author, student.FIO AS student_name, 
                       postafshik.name AS postafshik_name, formulyar.date_vudochi AS date_vudochi
                FROM school_library
                JOIN book ON school_library.id_book = book.id_book
                JOIN student ON school_library.id_student = student.id_student
                JOIN postafshik ON school_library.id_postafshik = postafshik.id_postafshik
                JOIN formulyar ON school_library.id_formulyar = formulyar.id_formulyar
        ''', LIBRARY_HEADERS)) # SQL-запрос, который вместо id подставляет значения из таблицы.
        tables_menu.add_command(label="Списания", command=lambda: self.show_table("SELECT * FROM spisaniya", SPISANIYA_HEADERS))
        self.menu_bar.add_cascade(label="Таблицы", menu=tables_menu)

        # Меню "Отчёты"
        reports_menu = tk.Menu(self.menu_bar, tearoff=0)
        reports_menu.add_command(label="Создать Отчёт", command=self.to_xlsx)
        self.menu_bar.add_cascade(label="Отчёты", menu=reports_menu)

        # Меню "Сервис"
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="Руководство пользователя")
        help_menu.add_command(label="O программе")
        self.menu_bar.add_cascade(label="Сервис", menu=help_menu)

        # Установка меню в главное окно
        self.config(menu=self.menu_bar)

        btn_width = 15
        pad = 5

        # Создание кнопок и виджетов для поиска и редактирования данных
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=0, column=1)
        tk.Button(btn_frame, text="добавить", width=btn_width, command=self.add).pack(pady=pad)
        tk.Button(btn_frame, text="удалить", width=btn_width, command=self.delete).pack(pady=pad)
        tk.Button(btn_frame, text="изменить", width=btn_width, command=self.change).pack(pady=pad)

        search_frame = tk.Frame(self)
        search_frame.grid(row=1, column=0, pady=pad)
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.grid(row=0, column=0, padx=pad)
        tk.Button(search_frame, text="Поиск", width=20, command=self.search).grid(row=0, column=1, padx=pad)
        tk.Button(search_frame, text="Искать далее", width=20, command=self.search_next).grid(row=0, column=2, padx=pad)
        tk.Button(search_frame, text="Сброс", width=20, command=self.reset_search).grid(row=0, column=3, padx=pad)

    def search_in_table(self, table, search_terms, start_item=None):
        table.selection_remove(table.selection())  # Сброс предыдущего выделения

        items = table.get_children('')
        start_index = items.index(start_item) + 1 if start_item else 0

        for item in items[start_index:]:
            values = table.item(item, 'values')
            for term in search_terms:
                if any(term.lower() in str(value).lower() for value in values):
                    table.selection_add(item)
                    table.focus(item)
                    table.see(item)
                    return item  # Возвращаем найденный элемент

    def reset_search(self):
        if self.last_headers:
            self.table.selection_remove(self.table.selection())
        self.search_entry.delete(0, 'end')

    def search(self):
        if self.last_headers:
            self.current_item = self.search_in_table(self.table, self.search_entry.get().split(','))

    def search_next(self):
        if self.last_headers:
            if self.current_item:
                self.current_item = self.search_in_table(self.table, self.search_entry.get().split(','), start_item=self.current_item)
    
    def to_xlsx(self):
        if self.last_headers == BOOK_HEADERS:
            sql_query = "SELECT * FROM book"
            table_name = "book"
        elif self.last_headers == POSTAFSHIK_HEADERS:
            sql_query = "SELECT * FROM postafshik"
            table_name = "postafshik"
        elif self.last_headers == STUDENT_HEADERS:
            sql_query = "SELECT * FROM student"
            table_name = "student"
        elif self.last_headers == FORMULYAR_HEADERS:
            sql_query = "SELECT * FROM formulyar"
            table_name = "formulyar"
        elif self.last_headers == LIBRARY_HEADERS:
            sql_query = '''
                SELECT school_library.id, book.name AS book_name, book.genre AS book_genre, 
                       book.author AS book_author, student.FIO AS student_name, 
                       postafshik.name AS postafshik_name, formulyar.date_vudochi AS date_vudochi
                FROM school_library
                JOIN book ON school_library.id_book = book.id_book
                JOIN student ON school_library.id_student = student.id_student
                JOIN postafshik ON school_library.id_postafshik = postafshik.id_postafshik
                JOIN formulyar ON school_library.id_formulyar = formulyar.id_formulyar
        '''
            table_name = "school_library"
        elif self.last_headers == SPISANIYA_HEADERS:
            sql_query = "SELECT * FROM spisaniya"
            table_name = "spisaniya"
        else: return

        dir = sys.path[0] + "\\export"
        os.makedirs(dir, exist_ok=True)
        path = dir + f"\\{table_name}.xlsx"

        # Подключение к базе данных SQLite
        conn = sqlite3.connect("book_bd.db")
        cursor = conn.cursor()
        # Получите данные из базы данных
        cursor.execute(sql_query)
        data = cursor.fetchall()
        # Создайте DataFrame из данных
        df = pd.DataFrame(data, columns=self.last_headers)
        # Создайте объект writer для записи данных в Excel
        writer = pd.ExcelWriter(path, engine='xlsxwriter')
        # Запишите DataFrame в файл Excel
        df.to_excel(writer, 'Лист 1', index=False)
        # Сохраните результат
        writer.close()

        showinfo(title="Успешно", message=f"Данные экспортированы в {path}")
    
    def show_table(self, sql_query, headers = None):
        # Очистка фрейма перед отображением новых данных
        for widget in self.table_frame.winfo_children(): widget.destroy()

        # Подключение к базе данных SQLite
        conn = sqlite3.connect("book_bd.db")
        cursor = conn.cursor()

        # Выполнение SQL-запроса
        cursor.execute(sql_query)
        self.last_sql_query = sql_query

        # Получение заголовков таблицы и данных
        if headers == None: # если заголовки не были переданы используем те что в БД
            table_headers = [description[0] for description in cursor.description]
        else: # иначе используем те что передали
            table_headers = headers
            self.last_headers = headers
        table_data = cursor.fetchall()

        # Закрытие соединения с базой данных
        conn.close()
            
        canvas = tk.Canvas(self.table_frame, width=865, height=480)
        canvas.pack(fill="both", expand=True)

        x_scrollbar = ttk.Scrollbar(self.table_frame, orient="horizontal", command=canvas.xview)
        x_scrollbar.pack(side="bottom", fill="x")

        canvas.configure(xscrollcommand=x_scrollbar.set)

        self.table = ttk.Treeview(self.table_frame, columns=table_headers, show="headings", height=23)
        for header in table_headers: 
            self.table.heading(header, text=header)
            self.table.column(header, width=len(header) * 10 + 100) # установка ширины столбца исходя длины его заголовка
        for row in table_data: self.table.insert("", "end", values=row)

        canvas.create_window((0, 0), window=self.table, anchor="nw")

        self.table.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
    
    def update_table(self):
        self.show_table(self.last_sql_query, self.last_headers)
        
    def add(self):
        if self.last_headers == BOOK_HEADERS:
            WindowBook("add")
        elif self.last_headers == POSTAFSHIK_HEADERS:
            WindowPostafshik("add")
        elif self.last_headers == STUDENT_HEADERS:
            WindowStudent("add")
        elif self.last_headers == FORMULYAR_HEADERS:
            WindowFormulyar("add")
        elif self.last_headers == LIBRARY_HEADERS:
            WindowSchoolLibrary("add")
        elif self.last_headers == SPISANIYA_HEADERS:
            WindowSpisaniya("add")
        else: return

    def delete(self):
        if self.last_headers:
            select_item = self.table.selection()
            if select_item:
                item_data = self.table.item(select_item[0])["values"]
            else:
                showerror(title="Ошибка", message="He выбранна запись")
                return
        else:
            return

        if self.last_headers == BOOK_HEADERS:
            WindowBook("delete", item_data)
        elif self.last_headers == POSTAFSHIK_HEADERS:
            WindowPostafshik("delete", item_data)
        elif self.last_headers == STUDENT_HEADERS:
            WindowStudent("delete", item_data)
        elif self.last_headers == FORMULYAR_HEADERS:
            WindowFormulyar("delete", item_data)
        elif self.last_headers == LIBRARY_HEADERS:
            WindowSchoolLibrary("delete", item_data)
        elif self.last_headers == SPISANIYA_HEADERS:
            WindowSpisaniya("delete", item_data)
        else: return

    def change(self):
        if self.last_headers:
            select_item = self.table.selection()
            if select_item:
                item_data = self.table.item(select_item[0])["values"]
            else:
                showerror(title="Ошибка", message="He выбранна запись")
                return
        else:
            return

        if self.last_headers == BOOK_HEADERS:
            WindowBook("change", item_data)
        elif self.last_headers == POSTAFSHIK_HEADERS:
            WindowPostafshik("change", item_data)
        elif self.last_headers == STUDENT_HEADERS:
            WindowStudent("change", item_data)
        elif self.last_headers == FORMULYAR_HEADERS:
            WindowFormulyar("change", item_data)
        elif self.last_headers == LIBRARY_HEADERS:
            WindowSchoolLibrary("change", item_data)
        elif self.last_headers == SPISANIYA_HEADERS:
            WindowSpisaniya("change", item_data)
        else: return

class WindowBook(tk.Toplevel):
    def __init__(self, operation, select_row = None):
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', lambda: self.quit_win())
        if select_row: self.select_row = select_row

        if operation == "add":
            tk.Label(self, text="Название").grid(row=0, column=0)
            self.name = tk.Entry(self, width=20)
            self.name.grid(row=0, column=1)

            tk.Label(self, text="Жанр").grid(row=1, column=0)
            self.genre = tk.Entry(self, width=20)
            self.genre.grid(row=1, column=1)

            tk.Label(self, text="Афтор").grid(row=2, column=0)
            self.author = tk.Entry(self, width=20)
            self.author.grid(row=2, column=1)

            tk.Label(self, text="Адрес").grid(row=3, column=0)
            self.adress = tk.Entry(self, width=20)
            self.adress.grid(row=3, column=1)

            tk.Label(self, text="Цена").grid(row=4, column=0)
            self.price = tk.Entry(self, width=20)
            self.price.grid(row=4, column=1)

            tk.Button(self, text="Отмена", command=self.quit_win).grid(row=5, column=0)
            tk.Button(self, text="Сохранить", command=self.add).grid(row=5, column=1, sticky="e")

        elif operation == "delete":
            tk.Label(self, text=f"Вы действиельно хотите удалить запись\nИз таблицы 'Книги'?").grid(row=0, column=0, columnspan=2)
            tk.Label(self, text=f"Значение: {self.select_row[1]}").grid(row=1, column=0, columnspan=2)
            tk.Button(self, text="Да", command=self.delete, width=12).grid(row=2, column=0)
            tk.Button(self, text="Нет", command=self.quit_win, width=12).grid(row=2, column=1)
        
        elif operation == "change":
            tk.Label(self, text="Наименование поля").grid(row=0, column=0)
            tk.Label(self, text="Текушее значение ").grid(row=0, column=1)
            tk.Label(self, text="Новое значение   ").grid(row=0, column=2)

            tk.Label(self, text="Название").grid(row=1, column=0)
            tk.Label(self, text=self.select_row[1]).grid(row=1, column=1)
            self.name = tk.Entry(self, width=20)
            self.name.grid(row=1, column=2)

            tk.Label(self, text="Жанр").grid(row=2, column=0)
            tk.Label(self, text=self.select_row[2]).grid(row=2, column=1)
            self.genre = tk.Entry(self, width=20)
            self.genre.grid(row=2, column=2)

            tk.Label(self, text="Афтор").grid(row=3, column=0)
            tk.Label(self, text=self.select_row[3]).grid(row=3, column=1)
            self.author = tk.Entry(self, width=20)
            self.author.grid(row=3, column=2)

            tk.Label(self, text="Адрес").grid(row=4, column=0)
            tk.Label(self, text=self.select_row[4]).grid(row=4, column=1)
            self.adress = tk.Entry(self, width=20)
            self.adress.grid(row=4, column=2)

            tk.Label(self, text="Цена").grid(row=5, column=0)
            tk.Label(self, text=self.select_row[5]).grid(row=5, column=1)
            self.price = tk.Entry(self, width=20)
            self.price.grid(row=5, column=2)

            tk.Button(self, text="Отмена", command=self.quit_win).grid(row=6, column=0)
            tk.Button(self, text="Сохранить", command=self.change).grid(row=6, column=2, sticky="e")
    
    def quit_win(self):
        win.deiconify()
        win.update_table()
        self.destroy()
    
    def add(self):
        name = self.name.get()
        genre = self.genre.get()
        author = self.author.get()
        adress = self.adress.get()
        price = self.price.get()

        if name and genre and author and adress and price:
            try:
                conn = sqlite3.connect("book_bd.db")
                cursor = conn.cursor()
                cursor.execute(f"INSERT INTO book (name, genre, author, adress, price) VALUES (?, ?, ?, ?, ?)",
                            (name, genre, author, adress, price))
                conn.commit()
                conn.close()
                self.quit_win()
            except sqlite3.Error as e:
                showerror(title="Ошибка", message=str(e))
        else:
            showerror(title="Ошибка", message="Заполните все поля")

    def delete(self):
        try:
            conn = sqlite3.connect("book_bd.db")
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM book WHERE id_book = ?", (self.select_row[0],))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

    def change(self):
        name = self.name.get() or self.select_row[1]
        genre = self.genre.get() or self.select_row[2]
        author = self.author.get() or self.select_row[3]
        adress = self.adress.get() or self.select_row[4]
        price = self.price.get() or self.select_row[5]
        try:
            conn = sqlite3.connect("book_bd.db")
            cursor = conn.cursor()
            cursor.execute(f"UPDATE book SET (name, genre, author, adress, price) = (?, ?, ?, ?, ?) WHERE id_book = {self.select_row[0]}",
                        (name, genre, author, adress, price))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

class WindowPostafshik(tk.Toplevel):
    def __init__(self, operation, select_row = None):
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', lambda: self.quit_win())
        if select_row: self.select_row = select_row

        if operation == "add":
            tk.Label(self, text="№ документа").grid(row=0, column=0)
            self.n_doc = tk.Entry(self, width=20)
            self.n_doc.grid(row=0, column=1)

            tk.Label(self, text="Наименование").grid(row=1, column=0)
            self.post_name = tk.Entry(self, width=20)
            self.post_name.grid(row=1, column=1)

            tk.Button(self, text="Отмена", command=self.quit_win).grid(row=2, column=0)
            tk.Button(self, text="Сохранить", command=self.add).grid(row=2, column=1, sticky="e")

        elif operation == "delete":
            tk.Label(self, text=f"Вы действиельно хотите удалить запись\nИз таблицы 'Книги'?").grid(row=0, column=0, columnspan=2)
            tk.Label(self, text=f"Значение: {self.select_row[1]}").grid(row=1, column=0, columnspan=2)
            tk.Button(self, text="Да", command=self.delete, width=12).grid(row=2, column=0)
            tk.Button(self, text="Нет", command=self.quit_win, width=12).grid(row=2, column=1)
        
        elif operation == "change":
            tk.Label(self, text="Наименование поля").grid(row=0, column=0)
            tk.Label(self, text="Текушее значение ").grid(row=0, column=1)
            tk.Label(self, text="Новое значение   ").grid(row=0, column=2)

            tk.Label(self, text="№ документа").grid(row=1, column=0)
            tk.Label(self, text=self.select_row[1]).grid(row=1, column=1)
            self.n_doc = tk.Entry(self, width=20)
            self.n_doc.grid(row=1, column=2)

            tk.Label(self, text="Наименование").grid(row=2, column=0)
            tk.Label(self, text=self.select_row[2]).grid(row=2, column=1)
            self.post_name = tk.Entry(self, width=20)
            self.post_name.grid(row=2, column=2)

            tk.Button(self, text="Отмена", command=self.quit_win).grid(row=3, column=0)
            tk.Button(self, text="Сохранить", command=self.change).grid(row=3, column=2, sticky="e")
    
    def quit_win(self):
        win.deiconify()
        win.update_table()
        self.destroy()
    
    def add(self):
        n_doc = self.n_doc.get()
        post_name = self.post_name.get()

        if n_doc and post_name:
            try:
                conn = sqlite3.connect("book_bd.db")
                cursor = conn.cursor()
                cursor.execute(f"INSERT INTO postafshik (N_dokumenta, name) VALUES (?, ?)", (n_doc, post_name))
                conn.commit()
                conn.close()
                self.quit_win()
            except sqlite3.Error as e:
                showerror(title="Ошибка", message=str(e))
        else:
            showerror(title="Ошибка", message="Заполните все поля")

    def delete(self):
        try:
            conn = sqlite3.connect("book_bd.db")
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM postafshik WHERE id_postafshik = ?", (self.select_row[0],))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

    def change(self):
        n_doc = self.n_doc.get() or self.select_row[1]
        post_name = self.post_name.get() or self.select_row[2]
        try:
            conn = sqlite3.connect("book_bd.db")
            cursor = conn.cursor()
            cursor.execute(f"UPDATE postafshik SET (N_dokumenta, name) = (?, ?) WHERE id_postafshik = {self.select_row[0]}",
                        (n_doc, post_name))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

class WindowStudent(tk.Toplevel):
    def __init__(self, operation, select_row = None):
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', lambda: self.quit_win())
        if select_row: self.select_row = select_row

        if operation == "add":
            tk.Label(self, text="Фамилия Имя Отчество").grid(row=0, column=0)
            self.fio = tk.Entry(self, width=20)
            self.fio.grid(row=0, column=1)

            tk.Label(self, text="Группа").grid(row=1, column=0)
            self.gruop = tk.Entry(self, width=20)
            self.gruop.grid(row=1, column=1)

            tk.Button(self, text="Отмена", command=self.quit_win).grid(row=2, column=0)
            tk.Button(self, text="Сохранить", command=self.add).grid(row=2, column=1, sticky="e")

        elif operation == "delete":
            tk.Label(self, text=f"Вы действиельно хотите удалить запись\nИз таблицы 'Книги'?").grid(row=0, column=0, columnspan=2)
            tk.Label(self, text=f"Значение: {self.select_row[1]}").grid(row=1, column=0, columnspan=2)
            tk.Button(self, text="Да", command=self.delete, width=12).grid(row=2, column=0)
            tk.Button(self, text="Нет", command=self.quit_win, width=12).grid(row=2, column=1)
        
        elif operation == "change":
            tk.Label(self, text="Наименование поля").grid(row=0, column=0)
            tk.Label(self, text="Текушее значение ").grid(row=0, column=1)
            tk.Label(self, text="Новое значение   ").grid(row=0, column=2)

            tk.Label(self, text="Фамилия Имя Отчество").grid(row=1, column=0)
            tk.Label(self, text=self.select_row[1]).grid(row=1, column=1)
            self.fio = tk.Entry(self, width=20)
            self.fio.grid(row=1, column=2)

            tk.Label(self, text="Группа").grid(row=2, column=0)
            tk.Label(self, text=self.select_row[2]).grid(row=2, column=1)
            self.gruop = tk.Entry(self, width=20)
            self.gruop.grid(row=2, column=2)

            tk.Button(self, text="Отмена", command=self.quit_win).grid(row=3, column=0)
            tk.Button(self, text="Сохранить", command=self.change).grid(row=3, column=2, sticky="e")
    
    def quit_win(self):
        win.deiconify()
        win.update_table()
        self.destroy()
    
    def add(self):
        fio = self.fio.get()
        gruop = self.gruop.get()

        if fio and gruop:
            try:
                conn = sqlite3.connect("book_bd.db")
                cursor = conn.cursor()
                cursor.execute(f"INSERT INTO student (FIO, gruop) VALUES (?, ?)", (fio, gruop))
                conn.commit()
                conn.close()
                self.quit_win()
            except sqlite3.Error as e:
                showerror(title="Ошибка", message=str(e))
        else:
            showerror(title="Ошибка", message="Заполните все поля")

    def delete(self):
        try:
            conn = sqlite3.connect("book_bd.db")
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM student WHERE id_student = ?", (self.select_row[0],))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

    def change(self):
        fio = self.fio.get() or self.select_row[1]
        gruop = self.gruop.get() or self.select_row[2]
        try:
            conn = sqlite3.connect("book_bd.db")
            cursor = conn.cursor()
            cursor.execute(f"UPDATE student SET (FIO, gruop) = (?, ?) WHERE id_student = {self.select_row[0]}",
                        (fio, gruop))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

class WindowFormulyar(tk.Toplevel):
    def __init__(self, operation, select_row = None):
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', lambda: self.quit_win())
        if select_row: self.select_row = select_row

        if operation == "add":
            tk.Label(self, text="Дата выдачи").grid(row=0, column=0)
            self.date_vidach = tk.Entry(self, width=20)
            self.date_vidach.grid(row=0, column=1)

            tk.Label(self, text="Дата возврата").grid(row=1, column=0)
            self.date_vozvar = tk.Entry(self, width=20)
            self.date_vozvar.grid(row=1, column=1)

            tk.Label(self, text="№ книги").grid(row=2, column=0)
            self.n_book = tk.Entry(self, width=20)
            self.n_book.grid(row=2, column=1)

            tk.Label(self, text="№ студента").grid(row=3, column=0)
            self.n_student = tk.Entry(self, width=20)
            self.n_student.grid(row=3, column=1)

            tk.Button(self, text="Отмена", command=self.quit_win).grid(row=4, column=0)
            tk.Button(self, text="Сохранить", command=self.add).grid(row=4, column=1, sticky="e")

        elif operation == "delete":
            tk.Label(self, text=f"Вы действиельно хотите удалить запись\nИз таблицы 'Книги'?").grid(row=0, column=0, columnspan=2)
            tk.Label(self, text=f"Значение: {self.select_row[1]}").grid(row=1, column=0, columnspan=2)
            tk.Button(self, text="Да", command=self.delete, width=12).grid(row=2, column=0)
            tk.Button(self, text="Нет", command=self.quit_win, width=12).grid(row=2, column=1)
        
        elif operation == "change":
            tk.Label(self, text="Наименование поля").grid(row=0, column=0)
            tk.Label(self, text="Текушее значение ").grid(row=0, column=1)
            tk.Label(self, text="Новое значение   ").grid(row=0, column=2)

            tk.Label(self, text="Дата выдачи").grid(row=1, column=0)
            tk.Label(self, text=self.select_row[1]).grid(row=1, column=1)
            self.date_vidach = tk.Entry(self, width=20)
            self.date_vidach.grid(row=1, column=2)

            tk.Label(self, text="Дата возврата").grid(row=2, column=0)
            tk.Label(self, text=self.select_row[2]).grid(row=2, column=1)
            self.date_vozvar = tk.Entry(self, width=20)
            self.date_vozvar.grid(row=2, column=2)

            tk.Label(self, text="№ книги").grid(row=3, column=0)
            tk.Label(self, text=self.select_row[3]).grid(row=3, column=1)
            self.n_book = tk.Entry(self, width=20)
            self.n_book.grid(row=3, column=2)

            tk.Label(self, text="№ студента").grid(row=4, column=0)
            tk.Label(self, text=self.select_row[4]).grid(row=4, column=1)
            self.n_student = tk.Entry(self, width=20)
            self.n_student.grid(row=4, column=2)

            tk.Button(self, text="Отмена", command=self.quit_win).grid(row=5, column=0)
            tk.Button(self, text="Сохранить", command=self.change).grid(row=5, column=2, sticky="e")
    
    def quit_win(self):
        win.deiconify()
        win.update_table()
        self.destroy()
    
    def add(self):
        date_vidach = self.date_vidach.get()
        date_vozvar = self.date_vozvar.get()
        n_book = self.n_book.get()
        n_student = self.n_student.get()

        if date_vidach and date_vozvar and n_book and n_student:
            try:
                conn = sqlite3.connect("book_bd.db")
                cursor = conn.cursor()
                cursor.execute(f"INSERT INTO formulyar (date_vudochi, date_vozvrata, id_book, id_student) VALUES (?, ?, ?, ?)",
                            (date_vidach, date_vozvar, n_book, n_student))
                conn.commit()
                conn.close()
                self.quit_win()
            except sqlite3.Error as e:
                showerror(title="Ошибка", message=str(e))
        else:
            showerror(title="Ошибка", message="Заполните все поля")

    def delete(self):
        try:
            conn = sqlite3.connect("book_bd.db")
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM formulyar WHERE id_formulyar = ?", (self.select_row[0],))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

    def change(self):
        date_vidach = self.date_vidach.get() or self.select_row[1]
        date_vozvar = self.date_vozvar.get() or self.select_row[2]
        n_book = self.n_book.get() or self.select_row[3]
        n_student = self.n_student.get() or self.select_row[4]
        try:
            conn = sqlite3.connect("book_bd.db")
            cursor = conn.cursor()
            cursor.execute(f'''
                           UPDATE formulyar SET (date_vudochi, date_vozvrata, id_book, id_student) = (?, ?, ?, ?) 
                           WHERE id_formulyar = {self.select_row[0]}''', (date_vidach, date_vozvar, n_book, n_student))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

class WindowSchoolLibrary(tk.Toplevel):
    def __init__(self, operation, select_row = None):
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', lambda: self.quit_win())
        if select_row: self.select_row = select_row

        if operation == "add":
            tk.Label(self, text="Название").grid(row=0, column=0)
            self.name = tk.Entry(self, width=20)
            self.name.grid(row=0, column=1)

            tk.Label(self, text="Жанр").grid(row=1, column=0)
            self.genre = tk.Entry(self, width=20)
            self.genre.grid(row=1, column=1)

            tk.Label(self, text="Афтор").grid(row=2, column=0)
            self.author = tk.Entry(self, width=20)
            self.author.grid(row=2, column=1)

            tk.Label(self, text="Адрес").grid(row=3, column=0)
            self.adress = tk.Entry(self, width=20)
            self.adress.grid(row=3, column=1)

            tk.Label(self, text="Цена").grid(row=4, column=0)
            self.price = tk.Entry(self, width=20)
            self.price.grid(row=4, column=1)

            tk.Button(self, text="Отмена", command=self.quit_win).grid(row=5, column=0)
            tk.Button(self, text="Сохранить", command=self.add).grid(row=5, column=1, sticky="e")

        elif operation == "delete":
            tk.Label(self, text=f"Вы действиельно хотите удалить запись\nИз таблицы 'Книги'?").grid(row=0, column=0, columnspan=2)
            tk.Label(self, text=f"Значение: {self.select_row[1]}").grid(row=1, column=0, columnspan=2)
            tk.Button(self, text="Да", command=self.delete, width=12).grid(row=2, column=0)
            tk.Button(self, text="Нет", command=self.quit_win, width=12).grid(row=2, column=1)
        
        elif operation == "change":
            tk.Label(self, text="Наименование поля").grid(row=0, column=0)
            tk.Label(self, text="Текушее значение ").grid(row=0, column=1)
            tk.Label(self, text="Новое значение   ").grid(row=0, column=2)

            tk.Label(self, text="Название").grid(row=1, column=0)
            tk.Label(self, text=self.select_row[1]).grid(row=1, column=1)
            self.name = tk.Entry(self, width=20)
            self.name.grid(row=1, column=2)

            tk.Label(self, text="Жанр").grid(row=2, column=0)
            tk.Label(self, text=self.select_row[2]).grid(row=2, column=1)
            self.genre = tk.Entry(self, width=20)
            self.genre.grid(row=2, column=2)

            tk.Label(self, text="Афтор").grid(row=3, column=0)
            tk.Label(self, text=self.select_row[3]).grid(row=3, column=1)
            self.author = tk.Entry(self, width=20)
            self.author.grid(row=3, column=2)

            tk.Label(self, text="Адрес").grid(row=4, column=0)
            tk.Label(self, text=self.select_row[4]).grid(row=4, column=1)
            self.adress = tk.Entry(self, width=20)
            self.adress.grid(row=4, column=2)

            tk.Label(self, text="Цена").grid(row=5, column=0)
            tk.Label(self, text=self.select_row[5]).grid(row=5, column=1)
            self.price = tk.Entry(self, width=20)
            self.price.grid(row=5, column=2)

            tk.Button(self, text="Отмена", command=self.quit_win).grid(row=6, column=0)
            tk.Button(self, text="Сохранить", command=self.change).grid(row=6, column=2, sticky="e")
    
    def quit_win(self):
        win.deiconify()
        win.update_table()
        self.destroy()
    
    def add(self):
        name = self.name.get()
        genre = self.genre.get()
        author = self.author.get()
        adress = self.adress.get()
        price = self.price.get()

        if name and genre and author and adress and price:
            try:
                conn = sqlite3.connect("book_bd.db")
                cursor = conn.cursor()
                cursor.execute(f"INSERT INTO book (name, genre, author, adress, price) VALUES (?, ?, ?, ?, ?)",
                            (name, genre, author, adress, price))
                conn.commit()
                conn.close()
                self.quit_win()
            except sqlite3.Error as e:
                showerror(title="Ошибка", message=str(e))
        else:
            showerror(title="Ошибка", message="Заполните все поля")

    def delete(self):
        try:
            conn = sqlite3.connect("book_bd.db")
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM book WHERE id_book = ?", (self.select_row[0],))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

    def change(self):
        name = self.name.get() or self.select_row[1]
        genre = self.genre.get() or self.select_row[2]
        author = self.author.get() or self.select_row[3]
        adress = self.adress.get() or self.select_row[4]
        price = self.price.get() or self.select_row[5]
        try:
            conn = sqlite3.connect("book_bd.db")
            cursor = conn.cursor()
            cursor.execute(f"UPDATE book SET (name, genre, author, adress, price) = (?, ?, ?, ?, ?) WHERE id_book = {self.select_row[0]}",
                        (name, genre, author, adress, price))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

class WindowSpisaniya(tk.Toplevel):
    def __init__(self, operation, select_row = None):
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', lambda: self.quit_win())
        if select_row: self.select_row = select_row

        if operation == "add":
            tk.Label(self, text="Дата").grid(row=0, column=0)
            self.date = tk.Entry(self, width=20)
            self.date.grid(row=0, column=1)

            tk.Label(self, text="Причина").grid(row=1, column=0)
            self.prichina = tk.Entry(self, width=20)
            self.prichina.grid(row=1, column=1)

            tk.Label(self, text="№ книги").grid(row=2, column=0)
            self.n_book = tk.Entry(self, width=20)
            self.n_book.grid(row=2, column=1)

            tk.Button(self, text="Отмена", command=self.quit_win).grid(row=3, column=0)
            tk.Button(self, text="Сохранить", command=self.add).grid(row=3, column=1, sticky="e")

        elif operation == "delete":
            tk.Label(self, text=f"Вы действиельно хотите удалить запись\nИз таблицы 'Книги'?").grid(row=0, column=0, columnspan=2)
            tk.Label(self, text=f"Значение: {self.select_row[1]}").grid(row=1, column=0, columnspan=2)
            tk.Button(self, text="Да", command=self.delete, width=12).grid(row=2, column=0)
            tk.Button(self, text="Нет", command=self.quit_win, width=12).grid(row=2, column=1)
        
        elif operation == "change":
            tk.Label(self, text="Наименование поля").grid(row=0, column=0)
            tk.Label(self, text="Текушее значение ").grid(row=0, column=1)
            tk.Label(self, text="Новое значение   ").grid(row=0, column=2)

            tk.Label(self, text="Дата").grid(row=1, column=0)
            tk.Label(self, text=self.select_row[1]).grid(row=1, column=1)
            self.date = tk.Entry(self, width=20)
            self.date.grid(row=1, column=2)

            tk.Label(self, text="Причина").grid(row=2, column=0)
            tk.Label(self, text=self.select_row[2]).grid(row=2, column=1)
            self.prichina = tk.Entry(self, width=20)
            self.prichina.grid(row=2, column=2)

            tk.Label(self, text="№ книги").grid(row=3, column=0)
            tk.Label(self, text=self.select_row[3]).grid(row=3, column=1)
            self.n_book = tk.Entry(self, width=20)
            self.n_book.grid(row=3, column=2)

            tk.Button(self, text="Отмена", command=self.quit_win).grid(row=4, column=0)
            tk.Button(self, text="Сохранить", command=self.change).grid(row=4, column=2, sticky="e")
    
    def quit_win(self):
        win.deiconify()
        win.update_table()
        self.destroy()
    
    def add(self):
        date = self.date.get()
        prichina = self.prichina.get()
        n_book = self.n_book.get()

        if date and prichina and n_book:
            try:
                conn = sqlite3.connect("book_bd.db")
                cursor = conn.cursor()
                cursor.execute(f"INSERT INTO spisaniya (date_spisaniya, prichina, id_book) VALUES (?, ?, ?)",
                            (date, prichina, n_book))
                conn.commit()
                conn.close()
                self.quit_win()
            except sqlite3.Error as e:
                showerror(title="Ошибка", message=str(e))
        else:
            showerror(title="Ошибка", message="Заполните все поля")

    def delete(self):
        try:
            conn = sqlite3.connect("book_bd.db")
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM spisaniya WHERE id_spisaniya = ?", (self.select_row[0],))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

    def change(self):
        date = self.date.get() or self.select_row[1]
        prichina = self.prichina.get() or self.select_row[2]
        n_book = self.n_book.get() or self.select_row[3]
        try:
            conn = sqlite3.connect("book_bd.db")
            cursor = conn.cursor()
            cursor.execute(f'''
                           UPDATE spisaniya SET (date_spisaniya, prichina, id_book) = (?, ?, ?) 
                           WHERE id_spisaniya = {self.select_row[0]}''', (date, prichina, n_book))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

if __name__ == "__main__":
    db = DB()
    win = WindowMain()
    win.mainloop()