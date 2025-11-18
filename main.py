import tkinter as tk
from interfaz import BogotaGraphEditor

if __name__ == "__main__":
    root = tk.Tk()
    
    app = BogotaGraphEditor(root)
    root.mainloop()