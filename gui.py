import tkinter as tk
from tkinter import font as tkFont
import threading

from database import DatabaseManager
from bingo.client import BingoClient
from bingo.cartao import CartaoBingo

class BingoGUI(tk.Tk):
    def __init__(self, is_host=True, nome="Jogador"):
        super().__init__()
        self.title("Simulador de Bingo")
        self.geometry("800x600")
        self.configure(bg="#FFD700")  # fundo dourado

        self.is_host = is_host
        self.nome = nome

        # Fontes e cores
        self.btn_color = "#FFA500"
        self.normal_font = tkFont.Font(family="Arial", size=12)
        self.bold_font = tkFont.Font(family="Arial", size=12, weight="bold")
        self.title_font = tkFont.Font(family="Helvetica", size=18, weight="bold")

        # DB local (para histórico)
        self.db = DatabaseManager()

        # Conexão com o servidor
        self.client = BingoClient(
            host_ip="127.0.0.1",
            port=5001,
            is_host=self.is_host,
            nome_jogador=self.nome
        )

        self.label_status = None
        self.label_jogadores = None
        self.label_ultimo_numero = None
        self.label_ultimos_10 = None
        self.label_vencedor = None

        self.frame_cartao = None
        self.label_celulas = []

        self._build_gui()

        # Thread de atualização
        self.stop_thread = False
        threading.Thread(target=self._update_loop, daemon=True).start()

    def _build_gui(self):
        # Título
        lbl_titulo = tk.Label(self, text="BINGO ONLINE", font=self.title_font, bg="#FFD700")
        lbl_titulo.pack(pady=10)

        # Frame topo
        frame_top = tk.Frame(self, bg="#FFD700")
        frame_top.pack(pady=5)

        # Se host, botão "Sortear"
        if self.is_host:
            btn_sortear = tk.Button(
                frame_top, text="Sortear Número",
                font=self.bold_font, bg=self.btn_color, fg="white",
                command=self.sortear_numero
            )
            btn_sortear.pack(side=tk.LEFT, padx=10)

        # Botão Histórico (host ou jogador)
        btn_hist = tk.Button(
            frame_top, text="Histórico",
            font=self.bold_font, bg=self.btn_color, fg="white",
            command=self.mostrar_historico
        )
        btn_hist.pack(side=tk.LEFT, padx=10)

        # Labels de info
        self.label_status = tk.Label(self, text="", font=self.normal_font, bg="#FFD700")
        self.label_status.pack(pady=5)

        self.label_jogadores = tk.Label(self, text="Jogadores conectados: ?", font=self.normal_font, bg="#FFD700")
        self.label_jogadores.pack(pady=5)


        frame_info = tk.Frame(self, bg="#FFD700")
        frame_info.pack(pady=5)

        self.label_ultimo_numero = tk.Label(frame_info, text="Último Número: --", font=self.bold_font, bg="#FFD700")
        self.label_ultimo_numero.pack(pady=5)

        self.label_ultimos_10 = tk.Label(frame_info, text="Últimos 10: []", font=self.normal_font, bg="#FFD700")
        self.label_ultimos_10.pack(pady=5)

        self.label_vencedor = tk.Label(frame_info, text="", font=self.normal_font, bg="#FFD700", fg="red")
        self.label_vencedor.pack(pady=5)


        if not self.is_host:
            self.frame_cartao = tk.Frame(self, bg="#FFD700")
            self.frame_cartao.pack(pady=10)
            for i in range(5):
                row_labels = []
                for j in range(5):
                    lbl = tk.Label(
                        self.frame_cartao, text="--",
                        font=self.bold_font,
                        width=4, height=2,
                        bg="white", relief="ridge", borderwidth=2
                    )
                    lbl.grid(row=i, column=j, padx=2, pady=2)
                    row_labels.append(lbl)
                self.label_celulas.append(row_labels)

    def sortear_numero(self):
        """
        Host envia "SORTEAR" ao servidor.
        """
        self.client.sortear_numero()

    def mostrar_historico(self):
        win = tk.Toplevel(self)
        win.title("Histórico de Resultados")
        win.geometry("300x200")
        win.configure(bg="#FFD700")

        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM resultados")
        resultados = cursor.fetchall()

        text = ""
        for r in resultados:
            pid, vencedor, nrods = r
            text += f"ID {pid} => Jogador {vencedor} venceu em {nrods} rodadas.\n"

        lbl = tk.Label(win, text=text, bg="#FFD700", font=self.normal_font, justify=tk.LEFT)
        lbl.pack(padx=10, pady=10)

    def _update_loop(self):
        """
        Atualiza a interface de acordo com o estado do client, a cada 500ms.
        """
        while not self.stop_thread:
            self._atualizar_interface()
            self.after(500)  # dá um 'descanso' de 500ms

    def _atualizar_interface(self):
        # 1) Atualizar label_jogadores
        if self.client.jogadores_lista:
            jgs = ", ".join(self.client.jogadores_lista)
            self.label_jogadores.config(text=f"Jogadores conectados: {jgs}")

        # 2) Atualizar label_status (sobretudo para o host)
        if self.client.status_msg:
            self.label_status.config(text=self.client.status_msg)
        elif self.client.erro_msg:
            # Se houve erro do servidor
            self.label_status.config(text=f"ERRO: {self.client.erro_msg}")
        else:
            self.label_status.config(text="")

        # 3) Exibir último número e últimos 10
        if len(self.client.ultimos_numeros) > 0:
            ultimo = self.client.ultimos_numeros[-1]
            self.label_ultimo_numero.config(text=f"Último Número: {ultimo}")
            ultimos_str = ", ".join(str(x) for x in self.client.ultimos_numeros)
            self.label_ultimos_10.config(text=f"Últimos 10: {ultimos_str}")
        else:
            self.label_ultimo_numero.config(text="Último Número: --")
            self.label_ultimos_10.config(text="Últimos 10: []")

        # 4) Mostrar vencedor
        if self.client.vencedor_msg:
            self.label_vencedor.config(text=f"VENCEDOR: {self.client.vencedor_msg}")


        # 5) Se for jogador e tiver cartao_local, desenhar
        if not self.is_host and self.client.cartao_local and len(self.client.cartao_local.numeros) == 5:
            self._desenhar_cartao()

    def _desenhar_cartao(self):
        """
        Copia os valores do cartao_local para a grelha de labels.
        """
        cartao = self.client.cartao_local
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
        Fecha a janela com segurança.
        """
        self.stop_thread = True
        self.client.close()
        super().destroy()
