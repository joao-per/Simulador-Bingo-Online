import sqlite3

class DatabaseManager:
    def __init__(self, db_name="bingo.db"):
        self.db_name = db_name
        self.conn = None
        self.create_tables()

    def create_tables(self):
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS resultados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vencedor_linha TEXT,
                vencedor_bingo TEXT,
                concorrentes TEXT,
                numero_sorteios INTEGER
            )
        """)
        self.conn.commit()

    def registar_jogo(self, vencedor_linha, vencedor_bingo, concorrentes, numero_sorteios):
        c = self.conn.cursor()
        c.execute("""
            INSERT INTO resultados (vencedor_linha, vencedor_bingo, concorrentes, numero_sorteios)
            VALUES (?, ?, ?, ?)
        """, (vencedor_linha, vencedor_bingo, concorrentes, numero_sorteios))
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
