import random

class CartaoBingo:
    def __init__(self, tamanho=5, intervalo=(1, 75)):
        self.tamanho = tamanho
        self.intervalo = intervalo
        self.numeros = []
        self.gerar_cartao()

    def gerar_cartao(self):
        todos = random.sample(range(self.intervalo[0], self.intervalo[1] + 1), self.tamanho * self.tamanho)
        for i in range(self.tamanho):
            linha = todos[i*self.tamanho:(i+1)*self.tamanho]
            self.numeros.append(linha)

    def marcar_numero(self, numero):
        for i in range(self.tamanho):
            for j in range(self.tamanho):
                if self.numeros[i][j] == numero:
                    self.numeros[i][j] = "X"

    def verificar_linha(self):
        for i in range(self.tamanho):
            if all(x == "X" for x in self.numeros[i]):
                return True
        return False

    def verificar_bingo(self):
        for i in range(self.tamanho):
            for j in range(self.tamanho):
                if self.numeros[i][j] != "X":
                    return False
        return True