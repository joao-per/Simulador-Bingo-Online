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
        self.receive_queue = queue.Queue()

        # Cartão local do jogador (somente se is_host=False).
        self.cartao_local = None

        # Inicia conexão
        self.connect_to_server()

    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host_ip, self.port))
            print("Conectado ao servidor Bingo.")
        except Exception as e:
            print("Erro ao conectar no servidor:", e)
            sys.exit(1)

        # Inicia thread de receção de mensagens
        threading.Thread(target=self.receive_messages, daemon=True).start()

        # Envia msg de HOST ou JOIN
        if self.is_host:
            self.send_msg("HOST")
        else:
            self.send_msg(f"JOIN {self.nome_jogador}")

    def receive_messages(self):
        """
        Fica a ler mensagens do servidor e as coloca em self.receive_queue
        para que a GUI possa interpretá-las.
        """
        try:
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                # Pode chegar mais de uma linha ao mesmo tempo, então dividimos
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
        Interpreta linha do servidor. Exemplos:
          - "CARD 5" => indica que as próximas 5 linhas são a matriz do cartão
          - "NUMERO 23" => marcar no self.cartao_local
          - "VENCEDOR Maria" => exibir mensagem de vencedor
          - "PLAYERS A,B,C" => lista de jogadores
          - "STATUS Aguardando 1 jogador..." => se for host, exibe status
        """
        print(f"[DEBUG] Recebido: {linha}")
        partes = linha.split(" ")
        cmd = partes[0]

        if cmd == "CARD":
            # Ex: "CARD 5"
            tamanho = int(partes[1])
            # Precisamos ler 'tamanho' linhas a seguir => mas elas podem vir picadas
            # Para simplificar, vou guardar num buffer e extrair mais tarde.
            # Porém, aqui como chamamos processar_linha a cada vez que chega algo,
            # iremos ativar um "modo" de leitura do cartão. 
            self.cartao_local = CartaoBingo(tamanho=tamanho)
            self.cartao_local.numeros = []  # reset, pois iremos preencher

            # As próximas N linhas do socket vão conter a matriz. 
            # Solução simples: armazenar "estamos_a_esperar_cartao=5" e no loop
            #   das próximas 5 messages, iremos append. 
            # Aqui, farei self.expected_card_lines = tamanho 
            # e usarei self.reading_card = True
            self.expected_card_lines = tamanho
            self.reading_card = True

        elif hasattr(self, "reading_card") and getattr(self, "reading_card", False) is True:
            # Estamos lendo as linhas do cartão
            linha_numeros = [int(x) for x in linha.split()]
            self.cartao_local.numeros.append(linha_numeros)
            self.expected_card_lines -= 1
            if self.expected_card_lines <= 0:
                self.reading_card = False
                print("Cartão recebido com sucesso:", self.cartao_local.numeros)

        elif cmd == "NUMERO":
            # "NUMERO 23"
            numero = int(partes[1])
            # Marcamos no cartao_local
            if self.cartao_local:
                self.cartao_local.marcar_numero(numero)
                print(f"Marcado número {numero} no cartão local.")
            # A GUI depois pode chamar a func de atualizar

        elif cmd == "VENCEDOR":
            vencedor_nome = " ".join(partes[1:])
            print(f"*** Temos um vencedor: {vencedor_nome} ***")

        elif cmd == "PLAYERS":
            # "PLAYERS nome1,nome2,nome3"
            lista_str = " ".join(partes[1:])
            nomes = lista_str.split(",")
            print("Jogadores conectados:", nomes)

        elif cmd == "STATUS":
            # Mensagem para o host
            status_msg = " ".join(partes[1:])
            print(f"[STATUS] {status_msg}")

        else:
            print(">> Mensagem não reconhecida:", linha)

    def sortear_numero(self):
        """
        Envia "SORTEAR" para o servidor. 
        (Apenas Host deve chamar isto.)
        """
        if self.is_host:
            self.send_msg("SORTEAR")
        else:
            print("ERRO: Não és o Host.")

    def send_msg(self, texto):
        """
        Envia uma mensagem para o servidor (com \n no final).
        """
        try:
            self.client_socket.sendall((texto + "\n").encode("utf-8"))
        except BrokenPipeError:
            print("ERRO: Conexão com o servidor foi encerrada (BrokenPipe).")

    def close(self):
        self.send_msg("SAIR")
        self.client_socket.close()
