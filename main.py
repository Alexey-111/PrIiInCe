# Импортирование необходимых библиотек
import tkinter as tk
from tkinter import ttk
import sqlite3
from PIL import Image, ImageTk

# Определение основного класса приложения
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Настройка основного окна приложенияiuou
        self.title('Отдел кадров')
        self.geometry('865x450')
        self.resizable(width=False, height=False)

        # Создание рамки для отображения таблицы
        self.table_frame = tk.Frame(self, width=700, height=400)
        self.table_frame.grid(row=0, column=0, padx=5, pady=5)

        # Загрузка изображения и размещение его на рамке
        bg = ImageTk.PhotoImage(Image.open("bg.png"), size=(700, 400))
        lbl = tk.Label(self.table_frame, image=bg, font=("Calibri", 40))
        lbl.image = bg
        lbl.place(relwidth=1, relheight=1)

        # Создание меню
        self.menu_bar = tk.Menu(self)

        # Меню "Файл"
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Выход", command=self.quit)
        self.menu_bar.add_cascade(label="Файл", menu=file_menu)

        # Меню "Справочники"
        references_menu = tk.Menu(self.menu_bar, tearoff=0)
        references_menu.add_command(label="книги", command=lambda: self.show_table("SELECT * FROM book"))
        references_menu.add_command(label="Поставщики", command=lambda: self.show_table("SELECT * FROM postafshik"))
        references_menu.add_command(label="Студенты", command=lambda: self.show_table("SELECT * FROM student"))
        self.menu_bar.add_cascade(label="Справочники", menu=references_menu)

        # Меню "Таблицы"
        tables_menu = tk.Menu(self.menu_bar, tearoff=0)
        tables_menu.add_command(label="Формуляр", command=lambda: self.show_table("SELECT * FROM formulyar"))
        tables_menu.add_command(label="Библиотека", command=lambda: self.show_table('''
                SELECT school_library.id, book.name AS book_name, book.genre AS book_genre, 
                       book.author AS book_author, student.FIO AS student_name, 
                       postafshik.name AS postafshik_name, formulyar.date_vudochi AS date_vudochi
                FROM school_library
                JOIN book ON school_library.id_book = book.id_book
                JOIN student ON school_library.id_student = student.id_student
                JOIN postafshik ON school_library.id_postafshik = postafshik.id_postafshik
                JOIN formulyar ON school_library.id_formulyar = formulyar.id_formulyar
        ''')) # SQL-запрос, который вместо id подставляет значения из таблицы.
        tables_menu.add_command(label="Списания", command=lambda: self.show_table("SELECT * FROM spisaniya"))
        self.menu_bar.add_cascade(label="Таблицы", menu=tables_menu)

        # Меню "Отчёты" (пока без действий)
        reports_menu = tk.Menu(self.menu_bar, tearoff=0)
        reports_menu.add_command(label="Создать Отчёт")
        self.menu_bar.add_cascade(label="Отчёты", menu=reports_menu)

        # Меню "Сервис" (пока без действий)
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="Руководство пользователя")
        help_menu.add_command(label="O программе")
        self.menu_bar.add_cascade(label="Сервис", menu=help_menu)

        # Установка меню в основное окно
        self.config(menu=self.menu_bar)

        # Настройка кнопок и поля поиска
        btn_width = 15
        pad = 5

        # Фрейм с кнопками
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=0, column=1)
        tk.Button(btn_frame, text="добавить", width=btn_width).pack(pady=pad)
        tk.Button(btn_frame, text="удалить", width=btn_width).pack(pady=pad)
        tk.Button(btn_frame, text="изменить", width=btn_width).pack(pady=pad)

        # Фрейм с полем поиска
        search_frame = tk.Frame(self)
        search_frame.grid(row=1, column=0)
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.grid(row=0, column=0, padx=pad)
        tk.Button(search_frame, text="Поиск", width=20).grid(row=0, column=1, padx=pad)
        tk.Button(search_frame, text="настроить поиск").grid(row=0, column=2, padx=pad)
    
    # Метод для отображения таблицы
    def show_table(self, sql_query):
        # Очистка предыдущего содержимого таблицы
        for widget in self.table_frame.winfo_children(): widget.destroy()

        # Установка соединения с базой данных SQLite
        conn = sqlite3.connect("book_bd.db")
        cursor = conn.cursor()

        # Выполнение SQL-запроса
        cursor.execute(sql_query)

        # Получение заголовков таблицы и данных
        table_headers = [description[0] for description in cursor.description]
        table_data = cursor.fetchall()

        # Закрытие соединения с базой данных
        conn.close()
            
        # Создание холста для отображения таблицы
        canvas = tk.Canvas(self.table_frame, width=700, height=350)
        canvas.pack(fill="both", expand=True)

        # Добавление горизонтальной полосы прокрутки
        x_scrollbar = ttk.Scrollbar(self.table_frame, orient="horizontal", command=canvas.xview)
        x_scrollbar.pack(side="bottom", fill="x")

        canvas.configure(xscrollcommand=x_scrollbar.set)

        # Создание таблицы для отображения данных
        table = ttk.Treeview(self.table_frame, columns=table_headers, show="headings")
        for header in table_headers: table.heading(header, text=header)
        for row in table_data: table.insert("", "end", values=row)

        # Создание окна на холсте и привязка таблицы к нему
        canvas.create_window((0, 0), window=table, anchor="nw")

        # Обновление таблицы и настройка области прокрутки
        table.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

# Запуск приложения
if __name__ == "__main__":
    MainApp().mainloop()
