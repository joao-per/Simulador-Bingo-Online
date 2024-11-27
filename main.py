from bingo.jogo import JogoBingo

def main():
    jogo = JogoBingo(numero_jogadores=2, tamanho_cartao=5, intervalo_numeros=(1, 75))
    print("Bingamos!")

    vencedor = None
    rodada = 1

    while vencedor is None:
        print(f"\n--- Rodada {rodada} ---")
        numero_sorteado = jogo.sortear_numero()
        print(f"Número sorteado: {numero_sorteado}")
        jogo.marcar_cartoes(numero_sorteado)

        vencedor = jogo.verificar_vencedor()
        if vencedor is not None:
            print(f"\nJogador {vencedor + 1} venceu!")
        else:
            print("Nenhum vencedor ainda...")

        rodada += 1

    print("Fim do jogo!")

if __name__ == "__main__":
    main()
