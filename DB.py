import sqlite3

class DB:
    def __init__(self):
        self.conn = sqlite3.connect('book_bd.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS "book" (
                    "id_book" INTEGER NOT NULL,
                    "name" TEXT NOT NULL,
                    "genre" TEXT NOT NULL,
                    "author" TEXT NOT NULL,
                    "adress" TEXT NOT NULL,
                    "price" INTEGER,
                    PRIMARY KEY ("id_book" AUTOINCREMENT))''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS "spisaniya" (
                    "id_spisaniya" INTEGER NOT NULL,
                    "date_spisaniya" DATE NOT NULL,
                    "prichina" TEXT NOT NULL,
                    "id_book" INTEGER NOT NULL,
                    PRIMARY KEY ("id_spisaniya" AUTOINCREMENT))''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS "student" (
                    "id_student" INTEGER NOT NULL,
                    "FIO" TEXT NOT NULL,
                    "gruop" TEXT NOT NULL,
                    PRIMARY KEY ("id_student" AUTOINCREMENT))''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS "postafshik" (
                    "id_postafshik" INTEGER NOT NULL,
                    "N_dokumenta" INTEGER NOT NULL,
                    "name" TEXT NOT NULL,
                    PRIMARY KEY ("id_postafshik" AUTOINCREMENT))''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS "formulyar" (
                    "id_formulyar" INTEGER NOT NULL,
                    "date_vudochi" DATE NOT NULL,
                    "date_vozvrata" DATE NOT NULL,
                    "id_book" INTEGER NOT NULL,
                    "id_student" INTEGER NOT NULL,
                    PRIMARY KEY ("id_formulyar" AUTOINCREMENT))''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS "school_library" (
                    "id" INTEGER NOT NULL,
                    "id_book" INTEGER NOT NULL,
                    "id_spisaniya" INTEGER NOT NULL,
                    "id_student" INTEGER NOT NULL,
                    "id_postafshik" INTEGER NOT NULL,
                    "id_formulyar" INTEGER NOT NULL,
                    PRIMARY KEY ("id" AUTOINCREMENT))''')
        self.conn.commit()

db = DB()
