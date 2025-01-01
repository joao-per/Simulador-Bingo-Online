import socket
import threading
import queue
import sys
from bingo.cartao import CartaoBingo

class BingoClient:
    def __init__(self, host_ip="127.0.0.1", port=5001, is_host=False, nome_jogador="Jogador"):
        self.host_ip = host_ip
        self.port = port
        self.is_host = is_host
        self.nome_jogador = nome_jogador

        self.client_socket = None

        # Se for jogador, terá um cartao_local
        self.cartao_local = None

        # Guardar estado para exibir na GUI:
        self.jogadores_lista = []       # ex.: ["Maria", "Joao"]
        self.ultimos_numeros = []       # até 10 numeros
        self.status_msg = ""            # p/ o host: "Aguardando 1 jogador...", etc.
        self.vencedor_msg = ""          # ex.: "Fulano" se é o vencedor
        self.erro_msg = ""              # caso servidor envie "ERRO ..." ou algo similar

        # Conexão
        self.connect_to_server()
        # Thread para receber mensagens
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host_ip, self.port))
            print("Conectado ao servidor Bingo.")
        except Exception as e:
            print("Erro ao conectar no servidor:", e)
            sys.exit(1)

        # Envia msg de HOST ou JOIN
        if self.is_host:
            self.send_msg("HOST")
        else:
            self.send_msg(f"JOIN {self.nome_jogador}")

    def receive_messages(self):
        """
        Fica a ler mensagens do servidor, uma por linha, e processa.
        """
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
            print("Conexão com o servidor foi fechada.")
            self.client_socket.close()

    def processar_linha(self, linha):
        """
        Interpreta o que chega do servidor e atualiza atributos (para a GUI).
        """
        print("[DEBUG] Recebido:", linha)
        partes = linha.split()
        cmd = partes[0]

        # Recebe o CARTAO (apenas jogador)
        if cmd == "CARD":
            # "CARD 5"
            tamanho = int(partes[1])
            self.cartao_local = CartaoBingo(tamanho=tamanho)
            self.cartao_local.numeros = []
            self.expected_card_lines = tamanho
            self.reading_card = True

        elif hasattr(self, "reading_card") and getattr(self, "reading_card", False) is True:
            # Linha de cartão
            linha_numeros = [int(x) for x in linha.split()]
            self.cartao_local.numeros.append(linha_numeros)
            self.expected_card_lines -= 1
            if self.expected_card_lines <= 0:
                self.reading_card = False
                print("Cartão recebido:", self.cartao_local.numeros)

        elif cmd == "NUMERO":
            # "NUMERO 23"
            numero = int(partes[1])
            # Adiciona ao histórico local
            self.ultimos_numeros.append(numero)
            # Mantém só os últimos 10
            if len(self.ultimos_numeros) > 10:
                self.ultimos_numeros.pop(0)

            # Se for jogador com cartao_local, marca
            if self.cartao_local:
                self.cartao_local.marcar_numero(numero)

        elif cmd == "VENCEDOR":
            # "VENCEDOR NomeDoJogador"
            vencedor_nome = " ".join(partes[1:])
            self.vencedor_msg = vencedor_nome

        elif cmd == "PLAYERS":
            # "PLAYERS joao,maria,zezinho"
            lista_str = " ".join(partes[1:])
            nomes = lista_str.split(",")
            self.jogadores_lista = nomes

        elif cmd == "STATUS":
            # ex.: "STATUS Aguardando 1 jogador..."
            msg = " ".join(partes[1:])
            self.status_msg = msg

        elif cmd == "ERRO":
            # ex.: "ERRO mensagem"
            msg = " ".join(partes[1:])
            self.erro_msg = msg

        else:
            print(">> Mensagem não reconhecida:", linha)

    def sortear_numero(self):
        """
        Envia "SORTEAR" para o servidor (apenas host).
        """
        if self.is_host:
            self.send_msg("SORTEAR")

    def send_msg(self, texto):
        try:
            self.client_socket.sendall((texto + "\n").encode("utf-8"))
        except BrokenPipeError:
            print("ERRO: Conexão com o servidor foi encerrada (BrokenPipe).")

    def close(self):
        try:
            self.send_msg("SAIR")
        except:
            pass
        self.client_socket.close()
