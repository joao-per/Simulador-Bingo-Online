from bingo.jogo import JogoBingo

def main():
    jogo = JogoBingo(numero_jogadores=2, tamanho_cartao=5, intervalo_numeros=(1, 75))
    print("Jogo de Bingo iniciado (versão inicial)!")

if __name__ == "__main__":
    main()
