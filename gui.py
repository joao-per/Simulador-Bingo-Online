import tkinter as tk
from tkinter import font as tkFont
import threading

from database import DatabaseManager
from bingo.client import BingoClient

class BingoGUI(tk.Tk):
    def __init__(self, is_host=True, nome="Jogador"):
        super().__init__()
        self.title("Simulador de Bingo")
        self.geometry("800x600")

        self.is_host = is_host
        self.nome = nome

        # Cores e fontes
        self.bg_color = "#FFD700"   # Dourado claro
        self.btn_color = "#FFA500"  # Laranja
        self.highlight_color = "#FF6347"
        self.title_font = tkFont.Font(family="Helvetica", size=18, weight="bold")
        self.normal_font = tkFont.Font(family="Arial", size=12)
        self.bold_font = tkFont.Font(family="Arial", size=12, weight="bold")

        self.configure(bg=self.bg_color)

        # DB local apenas para histórico
        self.db = DatabaseManager()

        # Cria o client (conecta ao servidor). 
        self.client = BingoClient(
            host_ip="127.0.0.1", 
            port=5001, 
            is_host=self.is_host, 
            nome_jogador=self.nome
        )

        # Elementos de interface
        self.label_status = None
        self.label_jogadores = None
        self.frame_cartao = None
        self.label_celulas = []

        self._montar_gui()

        # Thread/loop que observa a queue do client para atualizar UI
        self.parar = False
        threading.Thread(target=self._monitorar_mensagens, daemon=True).start()

    def _montar_gui(self):
        lbl_titulo = tk.Label(self, text="BINGO ONLINE", font=self.title_font, bg=self.bg_color)
        lbl_titulo.pack(pady=10)

        frame_top = tk.Frame(self, bg=self.bg_color)
        frame_top.pack(pady=5)

        # Se for host, exibimos o botão "Sortear"
        if self.is_host:
            btn_sortear = tk.Button(
                frame_top, 
                text="Sortear Número", 
                bg=self.btn_color, 
                fg="white",
                font=self.bold_font,
                command=self.sortear_numero
            )
            btn_sortear.pack(side=tk.LEFT, padx=10)

        btn_historico = tk.Button(
            frame_top,
            text="Histórico",
            bg=self.btn_color,
            fg="white",
            font=self.bold_font,
            command=self.mostrar_historico
        )
        btn_historico.pack(side=tk.LEFT, padx=10)

        self.label_status = tk.Label(self, text="", font=self.normal_font, bg=self.bg_color)
        self.label_status.pack(pady=5)

        self.label_jogadores = tk.Label(self, text="Jogadores conectados: ?", font=self.normal_font, bg=self.bg_color)
        self.label_jogadores.pack(pady=5)

        # Frame para cartão
        self.frame_cartao = tk.Frame(self, bg=self.bg_color)
        self.frame_cartao.pack(pady=10)

        # Montamos (inicialmente) células vazias
        # mas só iremos preenchê-las se/quando tivermos self.client.cartao_local
        for i in range(5):
            row_labels = []
            for j in range(5):
                lbl = tk.Label(
                    self.frame_cartao,
                    text="--",
                    font=self.bold_font,
                    width=4,
                    height=2,
                    bg="white",
                    relief="ridge",
                    borderwidth=2
                )
                lbl.grid(row=i, column=j, padx=2, pady=2)
                row_labels.append(lbl)
            self.label_celulas.append(row_labels)

    def sortear_numero(self):
        """
        Chamado pelo host. Envia 'SORTEAR' ao servidor.
        """
        self.client.sortear_numero()

    def mostrar_historico(self):
        """
        Exibe janela de resultados gravados no sqlite local.
        """
        win = tk.Toplevel(self)
        win.title("Histórico")
        win.geometry("300x200")
        win.configure(bg=self.bg_color)

        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM resultados")
        resultados = cursor.fetchall()

        text = ""
        for r in resultados:
            pid, vencedor, nrods = r
            text += f"ID {pid} => Jogador {vencedor} em {nrods} rodadas.\n"

        lbl = tk.Label(win, text=text, bg=self.bg_color, font=self.normal_font, justify=tk.LEFT)
        lbl.pack(padx=10, pady=10)

    def _monitorar_mensagens(self):
        while not self.parar:
            # 1) Atualizar a exibição do cartao local
            if self.client.cartao_local:
                self._atualizar_cartao_na_ui()

            # 2) Dormir um pouco
            self.after(500)
        print("Fin fin fin fin.")

    def _atualizar_cartao_na_ui(self):
        cartao = self.client.cartao_local
        if len(cartao.numeros) != 5:
            return  # ou cartao.tamanho se for !=5

        for i in range(5):
            for j in range(5):
                val = cartao.numeros[i][j]
                lbl = self.label_celulas[i][j]
                lbl.config(text=str(val))
                if val == "X":
                    lbl.config(bg="#90EE90")
                else:
                    lbl.config(bg="white")


    def destroy(self):
        """
        Overriding para fechar o client e evitar threads penduradas.
        """
        self.parar = True
        self.client.close()
        super().destroy()
