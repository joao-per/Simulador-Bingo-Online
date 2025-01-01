import tkinter as tk
from gui import BingoGUI

def start_launcher():
    root = tk.Tk()
    root.title("Escolher Modo")
    root.geometry("300x200")

    label = tk.Label(root, text="Deseja ser HOST ou JOGADOR?", font=("Arial", 12))
    label.pack(pady=10)

    def modo_host():
        root.destroy()
        app = BingoGUI(is_host=True, nome="HOST")
        app.mainloop()

    def modo_jogador():
        subroot = tk.Toplevel(root)
        subroot.title("Nome do Jogador")
        subroot.geometry("250x120")

        lbl = tk.Label(subroot, text="Digite seu nome:")
        lbl.pack(pady=5)
        entry_nome = tk.Entry(subroot)
        entry_nome.pack()

        def confirmar():
            nome = entry_nome.get().strip()
            if nome:
                subroot.destroy()
                root.destroy()
                app = BingoGUI(is_host=False, nome=nome)
                app.mainloop()

        btn_ok = tk.Button(subroot, text="OK", command=confirmar)
        btn_ok.pack(pady=5)

    btn_h = tk.Button(root, text="HOST", width=10, command=modo_host, bg="#FFA500", fg="white")
    btn_j = tk.Button(root, text="JOGADOR", width=10, command=modo_jogador, bg="#FFA500", fg="white")
    btn_h.pack(pady=5)
    btn_j.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    start_launcher()
