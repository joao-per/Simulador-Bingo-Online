import sqlite3

class DatabaseManager:
    def __init__(self, db_name="bingo.db"):
        self.db_name = db_name
        self.conn = None
        self.create_tables()

    def create_tables(self):
        self.conn = sqlite3.connect(self.db_name)
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resultados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vencedor INTEGER,
                numero_rodadas INTEGER
            )
        """)
        self.conn.commit()

    def registrar_resultado(self, vencedor, numero_rodadas):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO resultados (vencedor, numero_rodadas)
            VALUES (?, ?)
        """, (vencedor, numero_rodadas))
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()