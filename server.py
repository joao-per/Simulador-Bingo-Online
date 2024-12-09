import socket
import threading
from bingo.jogo import JogoBingo

class BingoServer:
    def __init__(self, host="127.0.0.1", port=5000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []  # Lista de (conn, addr)
        self.jogo = None
        self.start_server()

    def start_server(self):
        self.jogo = JogoBingo(numero_jogadores=0)  # Inicia sem jogadores
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Servidor Bingo iniciado em {self.host}:{self.port}")

        # Thread que fica à escuta de novos clientes
        threading.Thread(target=self.accept_clients, daemon=True).start()

    def accept_clients(self):
        while True:
            conn, addr = self.server_socket.accept()
            print(f"Novo cliente conectado: {addr}")
            self.clients.append((conn, addr))
            self.jogo.cartoes.append(self.jogo.criar_cartoes())
            threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

    def handle_client(self, conn, addr):
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                mensagem = data.decode("utf-8")

                if mensagem.startswith("SORTEAR"):
                    numero = self.jogo.sortear_numero()
                    self.jogo.marcar_cartoes(numero)
                    vencedor = self.jogo.verificar_vencedor()
                    self.broadcast(f"NUMERO {numero}")
                    if vencedor is not None:
                        self.broadcast(f"VENCEDOR {vencedor}")
                elif mensagem.startswith("JOIN"):
                    pass

        except Exception as e:
            print("Erro no handle_client:", e)
        finally:
            conn.close()
            self.clients.remove((conn, addr))
            print(f"Cliente {addr} desconectado")

    def broadcast(self, msg):
        for c, _ in self.clients:
            c.sendall(msg.encode("utf-8"))

if __name__ == "__main__":
    server = BingoServer()
    # Mantém o servidor a correr
    while True:
        pass
