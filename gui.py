import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
import threading

from database import DatabaseManager
from bingo.client import BingoClient

class BingoGUI(tk.Tk):
    def __init__(self, is_host=True, nome="Jogador"):
        super().__init__()
        self.title("BINGO - Versão Deluxe")
        self.geometry("850x650")

        self.is_host = is_host
        self.nome = nome

        # DB local
        self.db = DatabaseManager()

        # Client
        self.client = BingoClient(
            host_ip="127.0.0.1",
            port=5002,
            is_host=self.is_host,
            nome_jogador=self.nome
        )

        # Configura estilo
        self._setup_style()

        # Construir UI
        self._build_ui()

        # Thread de atualização
        self.stop_thread = False
        threading.Thread(target=self._update_loop, daemon=True).start()

        # NOVA FEATURE 1: Exibir um pequeno "chat log" local
        self.chat_msgs = []
        # NOVA FEATURE 2: Temporizador ou contagem de sorteios
        self.sorteios_count = 0

    def _setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")  # ou "default", "alt", etc.

        style.configure("MainFrame.TFrame", background="#ECECEC")
        style.configure("Title.TLabel", background="#ECECEC", foreground="#4B0082",
                        font=("Verdana", 24, "bold"))
        style.configure("SubTitle.TLabel", background="#ECECEC", foreground="#800000",
                        font=("Verdana", 14, "bold"))
        style.configure("Normal.TLabel", background="#ECECEC", foreground="#000000",
                        font=("Arial", 12))
        style.configure("Highlight.TLabel", background="#ECECEC", foreground="#DC143C",
                        font=("Arial", 12, "bold"))

        style.configure("Bingo.TButton",
                        font=("Arial", 12, "bold"),
                        background="#00BFFF",
                        foreground="#FFFFFF",
                        padding=8)

        style.configure("Card.TLabelframe", background="#ECECEC",
                        borderwidth=3, relief="ridge")
        style.configure("Card.TLabelframe.Label", font=("Arial", 12, "bold"), foreground="#333333")

    def _build_ui(self):
        main_frame = ttk.Frame(self, style="MainFrame.TFrame")
        main_frame.pack(fill="both", expand=True)

        lbl_title = ttk.Label(main_frame, text="BINGO DELUXE", style="Title.TLabel")
        lbl_title.pack(pady=10)

        lbl_user = ttk.Label(main_frame, text=f"Jogador: {self.nome}", style="SubTitle.TLabel")
        lbl_user.pack()

        # Frame de botões
        frame_buttons = ttk.Frame(main_frame, style="MainFrame.TFrame")
        frame_buttons.pack(pady=10)

        if self.is_host:
            self.btn_sortear = ttk.Button(
                frame_buttons, text="Sortear Número",
                style="Bingo.TButton", command=self.sortear_numero
            )
            self.btn_sortear.pack(side="left", padx=8)

        self.btn_hist = ttk.Button(
            frame_buttons, text="Histórico",
            style="Bingo.TButton", command=self.mostrar_historico
        )
        self.btn_hist.pack(side="left", padx=8)

        # Status e lista de jogadores
        self.lbl_status = ttk.Label(main_frame, text="", style="Normal.TLabel")
        self.lbl_status.pack(pady=5)

        self.lbl_jogadores = ttk.Label(main_frame, text="Jogadores: ?", style="Normal.TLabel")
        self.lbl_jogadores.pack(pady=5)

        # Info do jogo
        info_frame = ttk.Frame(main_frame, style="MainFrame.TFrame")
        info_frame.pack(pady=10)

        self.lbl_ultimo_num = ttk.Label(info_frame, text="Último Número: --", style="SubTitle.TLabel")
        self.lbl_ultimo_num.pack(pady=5)

        self.lbl_ultimos_10 = ttk.Label(info_frame, text="Últimos 10: []", style="Normal.TLabel")
        self.lbl_ultimos_10.pack(pady=5)

        self.lbl_linha = ttk.Label(info_frame, text="", style="Highlight.TLabel")
        self.lbl_linha.pack(pady=5)

        self.lbl_bingo = ttk.Label(info_frame, text="", style="Highlight.TLabel")
        self.lbl_bingo.pack(pady=5)

        self.lbl_sorteios_count = ttk.Label(info_frame, text="Sorteios realizados: 0", style="Normal.TLabel")
        self.lbl_sorteios_count.pack(pady=5)

        self.labels_cartao = []
        if not self.is_host:
            self.frame_cartao = ttk.Labelframe(main_frame, text="Meu Cartão", style="Card.TLabelframe")
            self.frame_cartao.pack(pady=15)

            for i in range(5):
                row_lbls = []
                for j in range(5):
                    lbl = ttk.Label(self.frame_cartao, text="--", style="Normal.TLabel")
                    lbl.grid(row=i, column=j, padx=4, pady=4, ipadx=10, ipady=5)
                    row_lbls.append(lbl)
                self.labels_cartao.append(row_lbls)

        # NOVA FEATURE 1: Mini Chat Log
        self.lbl_chat_title = ttk.Label(main_frame, text="CHAT LOG (apenas local)", style="SubTitle.TLabel")
        self.lbl_chat_title.pack(pady=5)

        self.txt_chat = tk.Text(main_frame, height=6, width=60, font=("Arial", 10))
        self.txt_chat.pack(padx=10, pady=5)
        self.txt_chat.insert("end", "Bem-vindo(a) ao Bingo Chat local...\n")  # Exemplo

    def sortear_numero(self):
        self.client.sortear_numero()
        self.sorteios_count += 1

    def mostrar_historico(self):
        win = tk.Toplevel(self)
        win.title("Histórico")
        win.geometry("350x300")
        win.configure(bg="#ECECEC")

        lbl_t = tk.Label(win, text="Resultados Gravados", bg="#ECECEC", font=("Verdana", 14, "bold"))
        lbl_t.pack(pady=10)

        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM resultados")
        results = cursor.fetchall()

        text = ""
        for r in results:
            pid, vencedor, nrods = r
            text += f"ID:{pid} => Jogador {vencedor} em {nrods} rodadas\n"

        lbl_res = tk.Label(win, text=text, bg="#ECECEC", font=("Arial", 12), justify="left")
        lbl_res.pack(pady=10)

    def _update_loop(self):
        while not self.stop_thread:
            self._atualizar_ui()
            self.after(500)

    def _atualizar_ui(self):
        c = self.client

        if c.jogadores_lista:
            self.lbl_jogadores.config(text=f"Jogadores: {', '.join(c.jogadores_lista)}")
        else:
            self.lbl_jogadores.config(text="Jogadores: ?")

        if c.status_msg:
            self.lbl_status.config(text=c.status_msg)
        elif c.erro_msg:
            self.lbl_status.config(text=f"ERRO: {c.erro_msg}")
        else:
            self.lbl_status.config(text="")

        if c.ultimos_numeros:
            ultimo = c.ultimos_numeros[-1]
            self.lbl_ultimo_num.config(text=f"Último Número: {ultimo}")
            lst = ", ".join(str(x) for x in c.ultimos_numeros)
            self.lbl_ultimos_10.config(text=f"Últimos 10: [{lst}]")
        else:
            self.lbl_ultimo_num.config(text="Último Número: --")
            self.lbl_ultimos_10.config(text="Últimos 10: []")

        # Linha / Bingo
        if c.linha_vencedor:
            self.lbl_linha.config(text=f"Vencedor da LINHA: {c.linha_vencedor}")
        if c.bingo_vencedor:
            self.lbl_bingo.config(text=f"Vencedor do BINGO: {c.bingo_vencedor}")
            # Se sou host, desabilito sortear
            if self.is_host and hasattr(self, "btn_sortear"):
                self.btn_sortear["state"] = "disabled"

        # Atualiza o label do contador de sorteios (nossa NOVA FEATURE)
        self.lbl_sorteios_count.config(text=f"Sorteios realizados: {self.sorteios_count}")

        # Se for jogador, desenhar cartao
        if not self.is_host and c.cartao_local and len(c.cartao_local.numeros) == 5:
            for i in range(5):
                for j in range(5):
                    val = c.cartao_local.numeros[i][j]
                    lbl = self.labels_cartao[i][j]
                    lbl.config(text=str(val))
                    if val == "X":
                        lbl.config(foreground="#006400")  # verde escuro
                    else:
                        lbl.config(foreground="#000000")

        # Exemplo de atualizar um "chat local"
        if c.linha_vencedor or c.bingo_vencedor:
            msg = f"[INFO] {c.linha_vencedor or ''} {c.bingo_vencedor or ''}"
            if msg.strip():
                self._inserir_chat(msg)

    def _inserir_chat(self, msg):
        self.txt_chat.insert("end", msg + "\n")
        self.txt_chat.see("end")

    def destroy(self):
        self.stop_thread = True
        self.client.close()
        super().destroy()
