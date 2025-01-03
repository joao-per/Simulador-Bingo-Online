import socket
import threading
import sys
from bingo.cartao import CartaoBingo

class BingoClient:
    def __init__(self, host_ip="127.0.0.1", port=5002, is_host=False, nome_jogador="Jogador"):
        self.host_ip = host_ip
        self.port = port
        self.is_host = is_host
        self.nome_jogador = nome_jogador

        self.client_socket = None

        # Armazena as informações para a GUI:
        self.cartao_local = None  # se for jogador
        self.jogadores_lista = []
        self.ultimos_numeros = []
        self.status_msg = ""
        self.erro_msg = ""
        self.linha_vencedor = ""
        self.bingo_vencedor = ""

        # Leitura do cartão (modo)
        self.reading_card = False
        self.expected_card_lines = 0

        self.connect_to_server()
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host_ip, self.port))
            print("Conectado ao servidor Bingo.")
        except Exception as e:
            print("Erro ao conectar no servidor:", e)
            sys.exit(1)

        # Envia se és HOST ou JOIN
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
        except Exception as e:
            print("Erro em receive_messages:", e)
        finally:
            print("Conexão fechada.")
            self.client_socket.close()

    def processar_linha(self, linha):
        print("[DEBUG] Recebido:", linha)
        partes = linha.split()
        cmd = partes[0]

        if cmd == "CARD":
            # Ex: "CARD 5"
            tamanho = int(partes[1])
            if not self.is_host:
                self.cartao_local = CartaoBingo(tamanho=tamanho)
                self.cartao_local.numeros = []
                self.expected_card_lines = tamanho
                self.reading_card = True

        elif self.reading_card:
            # Estamos a ler as linhas do cartão
            linha_numeros = [int(x) for x in linha.split()]
            self.cartao_local.numeros.append(linha_numeros)
            self.expected_card_lines -= 1
            if self.expected_card_lines <= 0:
                self.reading_card = False
                print("[CLIENT] Cartão recebido:", self.cartao_local.numeros)

        elif cmd == "NUMERO":
            numero = int(partes[1])
            self.ultimos_numeros.append(numero)
            # limitar a 10
            if len(self.ultimos_numeros) > 10:
                self.ultimos_numeros.pop(0)
            # Se for jogador, marcar no cartao_local
            if self.cartao_local:
                self.cartao_local.marcar_numero(numero)

        elif cmd == "LINHA":
            vencedor = " ".join(partes[1:])
            self.linha_vencedor = vencedor

        elif cmd == "BINGO":
            vencedor = " ".join(partes[1:])
            self.bingo_vencedor = vencedor

        elif cmd == "PLAYERS":
            # "PLAYERS nome1,nome2"
            lista_str = " ".join(partes[1:])
            nomes = lista_str.split(",")
            self.jogadores_lista = nomes

        elif cmd == "STATUS":
            self.status_msg = " ".join(partes[1:])

        elif cmd == "ERRO":
            self.erro_msg = " ".join(partes[1:])
        else:
            print("[CLIENT] Comando não reconhecido:", linha)

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
