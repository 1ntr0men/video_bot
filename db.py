import sqlite3
import datetime


class DB:
    def __init__(self):
        conn = sqlite3.connect("users.db", check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()


class Users:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             vk_id INTEGER,
                             date VARCHAR(20)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, vk_id):
        cursor = self.connection.cursor()
        date = 0
        cursor.execute('''INSERT INTO users
                          (vk_id, date)
                          VALUES (?,?)''', (vk_id, date))
        cursor.close()
        self.connection.commit()

    def non_subscribe(self, vk_id):
        cursor = self.connection.cursor()
        date = -1
        cursor.execute('''UPDATE users
                                    SET date = ?
                                    WHERE vk_id = ?''', (date, vk_id))
        cursor.close()
        self.connection.commit()

    def subscribe(self, vk_id):
        cursor = self.connection.cursor()
        date = int(datetime.datetime.now().strftime("%j")) + 31
        cursor.execute('''UPDATE users
                            SET date = ?
                            WHERE vk_id = ?''', (date, vk_id))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor
        cursor.execute("SELECT * FROM users WHERE id = ?", (str(user_id),))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows

    def exists(self, vk_id):
        cursor = self.connection.cursor()
        date = datetime.datetime.now().strftime("%j")
        cursor.execute("SELECT * FROM users WHERE vk_id = ?", (vk_id,))
        row = cursor.fetchone()
        return (True, row[2]) if row else (False,)
