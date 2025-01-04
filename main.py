import tkinter as tk
from gui import BingoGUI

def start_launcher():
	root = tk.Tk()
	root.title("Escolher Modo")
	root.geometry("350x220")
	root.configure(bg="#FFD700")
	ft = ("Helvetica", 14, "bold")
	lb = tk.Label(root, text="Deseja ser HOST ou JOGADOR?", font=ft, bg="#FFD700", fg="#8B0000")
	lb.pack(pady=20)
	def mh():
		root.destroy()
		app = BingoGUI(is_host=True, nome="HOST")
		app.mainloop()
	def mj():
		s = tk.Toplevel(root)
		s.title("Nome do Jogador")
		s.geometry("300x140")
		s.configure(bg="#FFD700")
		lb2 = tk.Label(s, text="Digite seu nome:", bg="#FFD700", font=("Arial", 11), fg="#8B0000")
		lb2.pack(pady=10)
		en = tk.Entry(s, font=("Arial", 11))
		en.pack()
		def cf():
			nm = en.get().strip()
			if nm:
				s.destroy()
				root.destroy()
				ax = BingoGUI(is_host=False, nome=nm)
				ax.mainloop()
		b = tk.Button(s, text="OK", command=cf, bg="#FFA500", fg="white", font=("Arial", 11, "bold"))
		b.pack(pady=10)
	bt_h = tk.Button(root, text="HOST", width=12, command=mh, bg="#FFA500", fg="white", font=("Arial", 11, "bold"))
	bt_j = tk.Button(root, text="JOGADOR", width=12, command=mj, bg="#FFA500", fg="white", font=("Arial", 11, "bold"))
	bt_h.pack(pady=5)
	bt_j.pack(pady=5)
	root.mainloop()

if __name__ == "__main__":
	start_launcher()