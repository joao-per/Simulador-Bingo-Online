import socket
import threading
import sys
from bingo.cartao import CartaoBingo

class BingoClient:
    def __init__(self, host_ip="127.0.0.1", port=5001, is_host=False, nome_jogador="Jogador"):
        self.host_ip = host_ip
        self.port = port
        self.is_host = is_host
        self.nome_jogador = nome_jogador
        self.client_socket = None
        self.cartao_local = None
        self.jogadores_lista = []
        self.ultimos_numeros = []
        self.status_msg = ""
        self.erro_msg = ""
        self.linha_vencedor = ""
        self.bingo_vencedor = ""
        self.reading_card = False
        self.expected_card_lines = 0
        self.eventos = []
        self.connect_to_server()
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host_ip, self.port))
        except:
            sys.exit(1)
        if self.is_host:
            self.send_msg("HOST")
        else:
            self.send_msg(f"JOIN {self.nome_jogador}")

    def receive_messages(self):
        try:
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                linhas = data.decode("utf-8").split("\n")
                for linha in linhas:
                    linha = linha.strip()
                    if linha:
                        self.processar_linha(linha)
        except:
            pass
        finally:
            self.client_socket.close()

    def processar_linha(self, linha):
        parts = linha.split()
        cmd = parts[0]
        if cmd == "CARD":
            tamanho = int(parts[1])
            if not self.is_host:
                self.cartao_local = CartaoBingo(tamanho=tamanho)
                self.cartao_local.numeros = []
                self.expected_card_lines = tamanho
                self.reading_card = True
        elif self.reading_card:
            linha_nums = [int(x) for x in linha.split()]
            self.cartao_local.numeros.append(linha_nums)
            self.expected_card_lines -= 1
            if self.expected_card_lines <= 0:
                self.reading_card = False
        elif cmd == "NUMERO":
            numero = int(parts[1])
            self.ultimos_numeros.append(numero)
            if len(self.ultimos_numeros) > 10:
                self.ultimos_numeros.pop(0)
            if self.cartao_local:
                self.cartao_local.marcar_numero(numero)
        elif cmd == "LINHA":
            self.linha_vencedor = " ".join(parts[1:])
            self.eventos.append(f"Primeira linha de {self.linha_vencedor}")
        elif cmd == "BINGO":
            self.bingo_vencedor = " ".join(parts[1:])
            self.eventos.append(f"Cartão completo de {self.bingo_vencedor}")
        elif cmd == "PLAYERS":
            lista_str = " ".join(parts[1:])
            nomes = lista_str.split(",")
            self.jogadores_lista = nomes
        elif cmd == "STATUS":
            self.status_msg = " ".join(parts[1:])
        elif cmd == "ERRO":
            self.erro_msg = " ".join(parts[1:])
        elif cmd == "EVENT":
            resto = linha[5:].strip()
            self.eventos.append(resto)
        else:
            pass

    def sortear_numero(self):
        if self.is_host:
            self.send_msg("SORTEAR")

    def send_msg(self, texto):
        try:
            self.client_socket.sendall((texto + "\n").encode("utf-8"))
        except:
            pass

    def close(self):
        try:
            self.send_msg("SAIR")
        except:
            pass
        self.client_socket.close()