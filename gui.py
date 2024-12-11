import tkinter as tk
from tkinter import font as tkFont
from bingo.jogo import JogoBingo
from database import DatabaseManager
from bingo.client import BingoClient

class BingoGUI(tk.Tk):
	def __init__(self, modo_host=False):
		"""
		modo_host = True indica que este cliente é o HOST do jogo
					False indica que este cliente é um jogador normal
		"""
		super().__init__()
		self.title("Simulador de Bingo")
		self.geometry("500x400")

		# Paleta de cores (exemplo)
		self.bg_color = "#FFD700"   # Dourado claro
		self.btn_color = "#FFA500"  # Laranja
		self.highlight_color = "#FF6347"  # Tomate (hover)

		# Definição de fontes
		self.title_font = tkFont.Font(family="Helvetica", size=18, weight="bold")
		self.normal_font = tkFont.Font(family="Arial", size=12)
		self.bold_font = tkFont.Font(family="Arial", size=12, weight="bold")

		# Definir se este GUI é o host ou não
		self.modo_host = modo_host

		# Configurar background
		self.configure(bg=self.bg_color)

		# Instâncias de jogo e DB
		self.jogo = None
		self.vencedor = None
		self.num_rodadas = 0
		self.db = DatabaseManager()

		# Construir interface
		self._construir_interface()

		self.modo_host = modo_host
		# Criar client
		self.client = BingoClient(is_host=self.modo_host)

		# Se não for host, desabilitar o botão "Sortear"
		if not self.modo_host:
			self.botao_sortear.config(state=tk.DISABLED)
		
		# Iniciar loop de verificação de mensagens
		self.after(500, self.verificar_mensagens)

	def verificar_mensagens(self):
		self.after(500, self.verificar_mensagens)

	def sortear_numero(self):
		# Host envia comando ao servidor
		if self.client and self.modo_host:
			self.client.sortear_numero()

	def _construir_interface(self):
		# Título principal
		label_titulo = tk.Label(self, text="BINGO!", font=self.title_font, bg=self.bg_color)
		label_titulo.pack(pady=10)

		# Frame para botões
		frame_botoes = tk.Frame(self, bg=self.bg_color)
		frame_botoes.pack(pady=10)

		# Botão de Iniciar Jogo
		self.botao_iniciar = tk.Button(
			frame_botoes, 
			text="Iniciar Jogo", 
			font=self.bold_font, 
			bg=self.btn_color, 
			fg="white",
			command=self.iniciar_jogo
		)
		self.botao_iniciar.pack(side=tk.LEFT, padx=5)

		# Botão de Sortear Número (apenas ativo se for HOST)
		self.botao_sortear = tk.Button(
			frame_botoes, 
			text="Sortear Número", 
			font=self.bold_font, 
			bg=self.btn_color, 
			fg="white",
			command=self.sortear_numero
		)
		self.botao_sortear.pack(side=tk.LEFT, padx=5)

		if not self.modo_host:
			self.botao_sortear.config(state=tk.DISABLED)

		self.botao_historico = tk.Button(
			frame_botoes, 
			text="Histórico", 
			font=self.bold_font, 
			bg=self.btn_color, 
			fg="white",
			command=self.mostrar_historico
		)
		self.botao_historico.pack(side=tk.LEFT, padx=5)

		self.label_numero = tk.Label(self, text="", font=self.title_font, bg=self.bg_color)
		self.label_numero.pack(pady=5)

		self.label_resultado = tk.Label(self, text="", font=self.normal_font, bg=self.bg_color)
		self.label_resultado.pack(pady=5)

	def iniciar_jogo(self):
		self.jogo = JogoBingo(numero_jogadores=2)
		self.vencedor = None
		self.num_rodadas = 0
		self.label_numero.config(text="Jogo Iniciado!")
		self.label_resultado.config(text="Boa sorte a todos!")

	def sortear_numero(self):
		if self.jogo and self.vencedor is None:
			# Host sorteia número
			self.num_rodadas += 1
			numero = self.jogo.sortear_numero()
			self.jogo.marcar_cartoes(numero)

			self.label_numero.config(text=f"Número Sorteado: {numero}")

			vencedor = self.jogo.verificar_vencedor()
			if vencedor is not None:
				self.vencedor = vencedor
				self.label_resultado.config(text=f"Jogador {vencedor + 1} venceu!")
				self.botao_sortear.config(state=tk.DISABLED)

				self.db.registrar_resultado(vencedor=(vencedor+1), numero_rodadas=self.num_rodadas)
			else:
				self.label_resultado.config(text="Ainda sem vencedor...")


	def mostrar_historico(self):
		# Janela de histórico
		historico_janela = tk.Toplevel(self)
		historico_janela.title("Histórico de Resultados")
		historico_janela.geometry("300x200")
		historico_janela.configure(bg=self.bg_color)

		cursor = self.db.conn.cursor()
		cursor.execute("SELECT * FROM resultados")
		resultados = cursor.fetchall()

		texto = ""
		for r in resultados:
			id_partida, vencedor, numero_rodadas = r
			texto += f"Partida {id_partida}: Jogador {vencedor} venceu em {numero_rodadas} rodadas.\n"

		label_historico = tk.Label(
			historico_janela, 
			text=texto, 
			font=self.normal_font, 
			bg=self.bg_color, 
			justify=tk.LEFT
		)
		label_historico.pack(padx=10, pady=10)


def main():
	app = BingoGUI()
	app.mainloop()

if __name__ == "__main__":
	main()