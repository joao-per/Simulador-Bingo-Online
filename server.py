import socket
import threading
from bingo.jogo import JogoBingo
from bingo.cartao import CartaoBingo

class BingoServer:
    def __init__(self, host="127.0.0.1", port=5001):
        self.host = host
        self.port = port
        self.server_socket = None

        self.host_conn = None
        self.players = []

        self.jogo = JogoBingo(numero_jogadores=0)

        self.start_server()

    def start_server(self):
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
            threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

    def handle_client(self, conn, addr):
        """
        Recebe mensagens do cliente e atua em conformidade.
        """
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                mensagem = data.decode("utf-8").strip()
                if not mensagem:
                    continue

                partes = mensagem.split(" ")

                if partes[0] == "HOST":
                    self.registar_host(conn, addr)
                
                elif partes[0] == "JOIN":
                    # JOIN NomeDoJogador
                    nome = " ".join(partes[1:])  # se o jogador tiver espaços no nome
                    self.registar_jogador(conn, addr, nome)
                
                elif partes[0] == "SORTEAR":
                    # Só funciona se for o host e se >=2 players
                    self.processar_sorteio(conn, addr)

                else:
                    print("Mensagem desconhecida:", mensagem)

        except Exception as e:
            print("Erro no handle_client:", e)
        finally:
            # Se era o host, removemos. Se era player, removemos da lista. 
            self.remover_participante(conn, addr)
            conn.close()

    def registar_host(self, conn, addr):
        """
        Define este conn como host, se ainda não houver um.
        """
        if self.host_conn is None:
            self.host_conn = (conn, addr)
            print(f"Host registrado: {addr}")
            # Avisar o host do status inicial (quantos jogadores no momento).
            qtd = len(self.players)
            faltam = max(0, 2 - qtd)
            mensagem_host = f"STATUS Esperando {faltam} jogador(es) para iniciar."
            self.enviar_msg(conn, mensagem_host)
        else:
            # Se já existe host, rejeitar?
            self.enviar_msg(conn, "ERRO Já existe um Host conectado.")

    def registar_jogador(self, conn, addr, nome):
        """
        Cria cartao, adiciona ao 'players', envia cartao e lista de jogadores.
        """
        # Criar cartao para este jogador
        cartao = CartaoBingo(tamanho=5, intervalo=(1,75))
        # Guardar no JogoBingo
        self.jogo.cartoes.append(cartao)
        self.jogo.numero_jogadores += 1

        jogador_info = {
            "conn": conn,
            "addr": addr,
            "nome": nome,
            "cartao": cartao
        }
        self.players.append(jogador_info)

        print(f"Jogador '{nome}' registado. Total de jogadores: {len(self.players)}")

        # CARD 5 (tamanho)
        # 10 22 33 44 55
        # 66 11 23 41 09
        # ...
        self.enviar_cartao(conn, cartao)

        # Atualizar a lista de jogadores para todos
        self.broadcast_players()

        # Caso haja host, atualiza o host com o status:
        self.atualizar_status_para_host()

    def remover_participante(self, conn, addr):
        """
        Remove conn tanto da lista de jogadores quanto do host, se aplicável.
        """
        if self.host_conn and self.host_conn[0] == conn:
            print("Host disconectado.")
            self.host_conn = None
        else:
            # Verifica se está na lista de players
            removido = None
            for p in self.players:
                if p["conn"] == conn:
                    removido = p
                    break
            if removido:
                self.players.remove(removido)
                self.jogo.cartoes.remove(removido["cartao"])
                self.jogo.numero_jogadores -= 1
                print(f"Jogador '{removido['nome']}' desconectado.")
                # Atualiza o host (quantos faltam?)
                self.atualizar_status_para_host()
                # Re-broadcast do players
                self.broadcast_players()

    def processar_sorteio(self, conn, addr):
        """
        Host solicita SORTEAR. Só funciona se >= 2 jogadores.
        """
        # Verifica se é mesmo o host
        if not self.host_conn or self.host_conn[0] != conn:
            self.enviar_msg(conn, "ERRO Somente o Host pode sortear.")
            return
        # Verifica se há >=2 jogadores
        if len(self.players) < 2:
            self.enviar_msg(conn, "ERRO Não há jogadores suficientes (mín. 2)!")
            return

        # Sorteia e atualiza cartoes
        numero = self.jogo.sortear_numero()
        self.jogo.marcar_cartoes(numero)

        # Verifica se houve vencedor
        index_vencedor = self.jogo.verificar_vencedor()
        vencedor_nome = None
        if index_vencedor is not None:
            # players[i] tem cartao => index i => confere
            vencedor_nome = self.players[index_vencedor]["nome"]

        # Envia broadcast "NUMERO <numero>"
        self.broadcast(f"NUMERO {numero}")

        # Se houver vencedor, broadcast "VENCEDOR <nome>"
        if vencedor_nome:
            self.broadcast(f"VENCEDOR {vencedor_nome}")

    def enviar_cartao(self, conn, cartao):
        """
        Envia para 'conn' a mensagem "CARD <tamanho>" + linhas de números.
        """
        # Exemplo de protocolo textual
        msg_inicial = f"CARD {cartao.tamanho}"
        self.enviar_msg(conn, msg_inicial)

        for linha in cartao.numeros:
            # Converte cada número para string e junta com espaço
            linha_str = " ".join(str(x) for x in linha)
            self.enviar_msg(conn, linha_str)

    def broadcast_players(self):
        """
        Envia a todos a lista de jogadores conectados: "PLAYERS nome1,nome2,nome3"
        """
        nomes = [p["nome"] for p in self.players]
        msg = "PLAYERS " + ",".join(nomes)
        self.broadcast(msg)

    def atualizar_status_para_host(self):
        """
        Manda ao host: "STATUS Esperando X jogador(es)..." se <2,
        ou "STATUS Pode iniciar" se >=2.
        """
        if not self.host_conn:
            return

        qtd = len(self.players)
        if qtd < 2:
            faltam = 2 - qtd
            msg = f"STATUS Aguardando {faltam} jogador(es) para iniciar."
        else:
            msg = "STATUS Já pode iniciar (2+ jogadores conectados)."
        self.enviar_msg(self.host_conn[0], msg)

    def broadcast(self, texto):
        """
        Envia 'texto' para todos (host + todos os jogadores).
        """
        # Host
        if self.host_conn:
            self.enviar_msg(self.host_conn[0], texto)
        # Jogadores
        for p in self.players:
            self.enviar_msg(p["conn"], texto)

    def enviar_msg(self, conn, texto):
        """
        Envia 'texto' (com \n no final) a um socket conn.
        Tratamos eventuais exceções (e.g., BrokenPipe).
        """
        try:
            conn.sendall((texto + "\n").encode("utf-8"))
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")


if __name__ == "__main__":
    server = BingoServer()
    while True:
        pass
