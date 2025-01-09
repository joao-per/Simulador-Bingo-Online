import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
import threading
from database import DatabaseManager
from bingo.client import BingoClient

class BingoGUI(tk.Tk):
	def __init__(self, is_host=True, nome="Jogador"):
		super().__init__()
		self.title("Simulador de Bingo Deluxe")
		self.geometry("600x650")
		self.is_host = is_host
		self.nome = nome
		self.db = DatabaseManager()
		self.client = BingoClient(host_ip="127.0.0.1", port=5001, is_host=self.is_host, nome_jogador=self.nome)
		self._setup_style()
		self._build_ui()
		self.stop_thread = False
		threading.Thread(target=self._update_loop, daemon=True).start()
		self.sorteios_count = 0
		self.ja_foi_registrado = False

	def _setup_style(self):
		style = ttk.Style(self)
		style.theme_use("clam")
		style.configure("MainFrame.TFrame", background="#FFD700")
		style.configure("Title.TLabel", background="#FFD700", foreground="#8B0000", font=("Helvetica", 24, "bold"))
		style.configure("SubTitle.TLabel", background="#FFD700", foreground="#800000", font=("Helvetica", 14, "bold"))
		style.configure("Normal.TLabel", background="#FFD700", foreground="#000000", font=("Arial", 12))
		style.configure("Highlight.TLabel", background="#FFD700", foreground="#DC143C", font=("Arial", 12, "bold"))
		style.configure("Bingo.TButton", font=("Arial", 12, "bold"), background="#FFA500", foreground="#FFFFFF", padding=8)
		style.configure("Card.TLabelframe", background="#FFD700", borderwidth=3, relief="ridge")
		style.configure("Card.TLabelframe.Label", font=("Arial", 12, "bold"), foreground="#333333")

	def _build_ui(self):
		main_frame = ttk.Frame(self, style="MainFrame.TFrame")
		main_frame.pack(fill="both", expand=True)

		lbl_title = ttk.Label(main_frame, text="BINGO DELUXE", style="Title.TLabel")
		lbl_title.pack(pady=10)

		lbl_user = ttk.Label(main_frame, text=f"Jogador: {self.nome}", style="SubTitle.TLabel")
		lbl_user.pack()

		frame_buttons = ttk.Frame(main_frame, style="MainFrame.TFrame")
		frame_buttons.pack(pady=10)

		if self.is_host:
			self.btn_sortear = ttk.Button(frame_buttons, text="Sortear Número", style="Bingo.TButton", command=self.sortear_numero)
			self.btn_sortear.pack(side="left", padx=8)

		self.btn_hist = ttk.Button(frame_buttons, text="Histórico", style="Bingo.TButton", command=self.mostrar_historico)
		self.btn_hist.pack(side="left", padx=8)

		self.btn_eventos = ttk.Button(frame_buttons, text="Log de Eventos", style="Bingo.TButton", command=self.abrir_log_eventos)
		self.btn_eventos.pack(side="left", padx=8)

		self.lbl_status = ttk.Label(main_frame, text="", style="Normal.TLabel")
		self.lbl_status.pack(pady=5)

		self.lbl_jogadores = ttk.Label(main_frame, text="Jogadores: ?", style="Normal.TLabel")
		self.lbl_jogadores.pack(pady=5)

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

		if self.is_host:
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

	def abrir_log_eventos(self):
		w = tk.Toplevel(self)
		w.title("Log de Eventos")
		w.geometry("400x300")
		w.configure(bg="#FFD700")
		t = tk.Label(w, text="LOG DE EVENTOS", bg="#FFD700", fg="#8B0000", font=("Helvetica", 16, "bold"))
		t.pack(pady=5)
		tx = tk.Text(w, height=12, width=45, font=("Arial", 11))
		tx.pack(padx=10, pady=10)
		for e in self.client.eventos:
			tx.insert("end", e + "\n")
		tx.config(state="disabled")

	def sortear_numero(self):
		self.client.sortear_numero()
		self.sorteios_count += 1

	def mostrar_historico(self):
		win = tk.Toplevel(self)
		win.title("Histórico")
		win.geometry("400x400")
		win.configure(bg="#FFD700")
		lbl_t = tk.Label(win, text="Histórico de Jogos", bg="#FFD700", fg="#8B0000", font=("Helvetica", 14, "bold"))
		lbl_t.pack(pady=10)
		c = self.db.conn.cursor()
		c.execute("SELECT * FROM resultados")
		resultados = c.fetchall()
		texto = ""
		for r in resultados:
			jogo_id, vencedor_linha, vencedor_bingo, concorrentes, numero_sorteios = r
			texto += f"Jogo {jogo_id}:\n"
			texto += f"- Vencedor 1ª Linha: {vencedor_linha}\n"
			texto += f"- Vencedor Bingo: {vencedor_bingo}\n"
			texto += f"- Concorrentes: {concorrentes}\n"
			texto += f"- Nº de Sorteios: {numero_sorteios}\n\n"
		lbl_res = tk.Label(win, text=texto, bg="#FFD700", font=("Arial", 12), justify="left")
		lbl_res.pack(pady=10)

	def _update_loop(self):
		while not self.stop_thread:
			self._atualizar_ui()
			self.after(50)

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
			u = c.ultimos_numeros[-1]
			self.lbl_ultimo_num.config(text=f"Último Número: {u}")
			xx = ", ".join(str(x) for x in c.ultimos_numeros)
			self.lbl_ultimos_10.config(text=f"Últimos 10: [{xx}]")
		else:
			self.lbl_ultimo_num.config(text="Último Número: --")
			self.lbl_ultimos_10.config(text="Últimos 10: []")
		if c.linha_vencedor:
			self.lbl_linha.config(text=f"Vencedor da LINHA: {c.linha_vencedor}")
		if c.bingo_vencedor:
			self.lbl_bingo.config(text=f"Vencedor do BINGO: {c.bingo_vencedor}")
			if self.is_host and hasattr(self, "btn_sortear"):
				self.btn_sortear["state"] = "disabled"
		if self.is_host:
			self.lbl_sorteios_count.config(text=f"Sorteios realizados: {self.sorteios_count}")
		if not self.is_host and c.cartao_local and len(c.cartao_local.numeros) == 5:
			for i in range(5):
				for j in range(5):
					val = c.cartao_local.numeros[i][j]
					lbl = self.labels_cartao[i][j]
					lbl.config(text=str(val))
					if val == "X":
						lbl.config(foreground="#006400")
						""" add a background color to the label """
						lbl.config(background="#007523")
					else:
						lbl.config(foreground="#000000")
		if c.bingo_vencedor and self.is_host and self.ja_foi_registrado:
			self.ja_foi_registrado = True
			self.db.registrar_jogo(vencedor_linha=c.linha_vencedor, vencedor_bingo=c.bingo_vencedor, concorrentes=", ".join(c.jogadores_lista), numero_sorteios=self.sorteios_count)

	def destroy(self):
		self.stop_thread = True
		self.client.close()
		super().destroy()
