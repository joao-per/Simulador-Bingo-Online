import random
from .cartao import CartaoBingo

class JogoBingo:
    """
    Classe que gerencia o jogo de Bingo.
    - Responsável por criar os cartões.
    - Realizar o sorteio de números.
    - Verificar se houve vencedor.
    """

    def __init__(self, numero_jogadores=1, tamanho_cartao=5, intervalo_numeros=(1, 75)):
        self.numero_jogadores = numero_jogadores
        self.tamanho_cartao = tamanho_cartao
        self.intervalo_numeros = intervalo_numeros
        self.cartoes = []
        self.numeros_sorteados = []
        self.criar_cartoes()

    def criar_cartoes(self):
        """
        Cria um cartão de Bingo para cada jogador.
        """
        for _ in range(self.numero_jogadores):
            self.cartoes.append(CartaoBingo(self.tamanho_cartao, self.intervalo_numeros))

    def sortear_numero(self):
        """
        Sorteia um número que ainda não tenha sido sorteado.
        """
        while True:
            numero = random.randint(self.intervalo_numeros[0], self.intervalo_numeros[1])
            if numero not in self.numeros_sorteados:
                self.numeros_sorteados.append(numero)
                return numero

    def marcar_cartoes(self, numero):
        """
        Marca o número sorteado em todos os cartões.
        """
        for cartao in self.cartoes:
            cartao.marcar_numero(numero)

    def verificar_vencedor(self):
        """
        Verifica se algum jogador (cartão) já completou o Bingo.
        Retorna o índice do jogador vencedor, ou None se não houver.
        """
        for i, cartao in enumerate(self.cartoes):
            if cartao.verificar_bingo():
                return i
        return None
