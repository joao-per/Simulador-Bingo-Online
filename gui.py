import tkinter as tk
from bingo.jogo import JogoBingo

class BingoGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Bingo")
        self.geometry("400x300")
        
        self.jogo = None
        self.vencedor = None

        self.label_info = tk.Label(self, text="Bem-vindo ao Bingo!")
        self.label_info.pack(pady=10)

        self.botao_iniciar = tk.Button(self, text="Iniciar Jogo", command=self.iniciar_jogo)
        self.botao_iniciar.pack(pady=5)

        self.botao_sortear = tk.Button(self, text="Sortear Número", command=self.sortear_numero, state=tk.DISABLED)
        self.botao_sortear.pack(pady=5)

        self.label_numero = tk.Label(self, text="", font=("Helvetica", 16))
        self.label_numero.pack(pady=10)

        self.label_resultado = tk.Label(self, text="", font=("Helvetica", 12))
        self.label_resultado.pack(pady=10)

    def iniciar_jogo(self):
        self.jogo = JogoBingo(numero_jogadores=2)
        self.vencedor = None
        self.label_info.config(text="Jogo iniciado!")
        self.botao_sortear.config(state=tk.NORMAL)
        self.label_numero.config(text="")
        self.label_resultado.config(text="")

    def sortear_numero(self):
        if self.jogo and self.vencedor is None:
            numero = self.jogo.sortear_numero()
            self.jogo.marcar_cartoes(numero)
            self.label_numero.config(text=f"Número Sorteado: {numero}")

            vencedor = self.jogo.verificar_vencedor()
            if vencedor is not None:
                self.vencedor = vencedor
                self.label_resultado.config(text=f"Jogador {vencedor + 1} venceu!")
                self.botao_sortear.config(state=tk.DISABLED)
            else:
                self.label_resultado.config(text="Ainda sem vencedor...")

def main():
    app = BingoGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
