import socket
import threading
import random
from bingo.cartao import CartaoBingo

class BingoServer:
	def __init__(self, host="127.0.0.1", port=5001):
		self.host = host
		self.port = port
		self.server_socket = None
		self.host_conn = None
		self.players = []
		self.premio_linha_conquistado = False
		self.premio_bingo_conquistado = False
		self.concorrentes = []
		self.numeros_sorteados = set()
		self.numeros_sorteios = 0
		self.vencedor_linha = None
		self.vencedor_bingo = None
		self.start_server()


	def start_server(self):
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_socket.bind((self.host, self.port))
		self.server_socket.listen(5)
		threading.Thread(target=self.accept_clients, daemon=True).start()

	def accept_clients(self):
		while True:
			conn, addr = self.server_socket.accept()
			threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

	def handle_client(self, conn, addr):
		try:
			while True:
				data = conn.recv(1024)
				if not data:
					break
				msg = data.decode("utf-8").strip()
				if not msg:
					continue
				parts = msg.split(" ")
				cmd = parts[0]
				if cmd == "HOST":
					self.registar_host(conn, addr)
				elif cmd == "JOIN":
					nome = " ".join(parts[1:])
					self.registar_jogador(conn, addr, nome)
				elif cmd == "SORTEAR":
					self.processar_sorteio(conn, addr)
				elif cmd == "SAIR":
					self.broadcast_evento(f"EVENT saiu: {self.get_nome(conn)}")
					break
		except:
			pass
		finally:
			self.remover_participante(conn, addr)
			conn.close()

	def registar_host(self, conn, addr):
		if not self.host_conn:
			self.host_conn = (conn, addr)
			self.enviar_msg(conn, "STATUS Aguardando 2 jogador(es) para iniciar...")
		else:
			self.enviar_msg(conn, "ERRO Já existe um Host conectado.")

	def registar_jogador(self, conn, addr, nome):
		cartao = CartaoBingo()
		info = {"conn": conn, "addr": addr, "nome": nome, "cartao": cartao}
		self.players.append(info)
		self.enviar_msg(conn, f"CARD {cartao.tamanho}")
		for linha in cartao.numeros:
			self.enviar_msg(conn, " ".join(str(x) for x in linha))
		self.broadcast_players()
		self.atualizar_status_para_host()
		self.broadcast_evento(f"EVENT entrou: {nome}")

	def remover_participante(self, conn, addr):
		if self.host_conn and self.host_conn[0] == conn:
			self.host_conn = None
		else:
			alvo = None
			for p in self.players:
				if p["conn"] == conn:
					alvo = p
					break
			if alvo:
				self.players.remove(alvo)
				self.broadcast_players()
				self.atualizar_status_para_host()

	def processar_sorteio(self, conn, addr):
		if not self.host_conn or self.host_conn[0] != conn:
			self.enviar_msg(conn, "ERRO Somente o Host pode sortear.")
			return
		if len(self.players) < 2:
			self.enviar_msg(conn, "ERRO Não há jogadores suficientes (min 2).")
			return
		if self.premio_bingo_conquistado:
			self.enviar_msg(conn, "ERRO Já houve BINGO. Não pode mais sortear.")
			return
		while True:
			numero = random.randint(1, 75)
			if numero not in self.numeros_sorteados:
				self.numeros_sorteados.add(numero)
				break
		self.broadcast(f"NUMERO {numero}")
		for p in self.players:
			p["cartao"].marcar_numero(numero)
		for p in self.players:
			if not self.premio_linha_conquistado and p["cartao"].verificar_linha():
				self.premio_linha_conquistado = True
				self.broadcast(f"LINHA {p['nome']}")
				self.broadcast_evento(f"EVENT linha: {p['nome']}")
			if not self.premio_bingo_conquistado and p["cartao"].verificar_bingo():
				self.premio_bingo_conquistado = True
				self.broadcast(f"BINGO {p['nome']}")
				self.broadcast_evento(f"EVENT bingo: {p['nome']}")
				self.registrar_resultado()
				break



	def registrar_resultado(self):
		db = DatabaseManager()
		concorrentes = ", ".join([p["nome"] for p in self.players])
		db.registrar_jogo(
			vencedor_linha=self.vencedor_linha,
			vencedor_bingo=self.vencedor_bingo,
			concorrentes=concorrentes,
			numero_sorteios=self.numero_sorteios
		)
		db.close()

	def atualizar_status_para_host(self):
		if not self.host_conn:
			return
		qtd = len(self.players)
		if qtd < 2:
			self.enviar_msg(self.host_conn[0], f"STATUS Aguardando {2 - qtd} jogador(es) para iniciar...")
		else:
			self.enviar_msg(self.host_conn[0], "STATUS Já pode iniciar.")

	def broadcast_players(self):
		nomes = [p["nome"] for p in self.players]
		self.broadcast("PLAYERS " + ",".join(nomes))

	def broadcast_evento(self, texto):
		self.broadcast(texto)

	def get_nome(self, conn):
		for p in self.players:
			if p["conn"] == conn:
				return p["nome"]
		if self.host_conn and self.host_conn[0] == conn:
			return "HOST"
		return "Desconhecido"

	def broadcast(self, texto):
		if self.host_conn:
			self.enviar_msg(self.host_conn[0], texto)
		for p in self.players:
			self.enviar_msg(p["conn"], texto)

	def enviar_msg(self, conn, texto):
		try:
			conn.sendall((texto + "\n").encode("utf-8"))
		except:
			pass

if __name__ == "__main__":
	server = BingoServer()
	while True:
		pass