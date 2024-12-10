import socket
import threading

class BingoClient:
    def __init__(self, host="127.0.0.1", port=5000, is_host=False):
        self.host = host
        self.port = port
        self.is_host = is_host
        self.client_socket = None
        self.connect_to_server()

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        print("Conectado ao servidor Bingo.")
        # Envia mensagem de JOIN (apenas para identificação simples)
        self.client_socket.sendall("JOIN".encode("utf-8"))
        # Thread para receber mensagens do servidor
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def receive_messages(self):
        while True:
            data = self.client_socket.recv(1024)
            if not data:
                break
            mensagem = data.decode("utf-8")
            # Interpretar mensagens do servidor
            if mensagem.startswith("NUMERO"):
                numero = mensagem.split()[1]
                print(f">> Número sorteado: {numero}")
            elif mensagem.startswith("VENCEDOR"):
                vencedor = mensagem.split()[1]
                print(f">> Temos um vencedor! Jogador índice: {vencedor}")
            else:
                print(f"Servidor: {mensagem}")

    def sortear_numero(self):
        """
        Apenas o 'host' deve chamar este método.
        """
        if self.is_host:
            self.client_socket.sendall("SORTEAR".encode("utf-8"))
        else:
            print("Somente o Host pode sortear número.")

    def close(self):
        self.client_socket.close()
