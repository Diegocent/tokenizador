import tkinter as tk
from interfaz import InterfazTokenizador

def main():
    """Función principal para ejecutar la aplicación"""
    root = tk.Tk()
    app = InterfazTokenizador(root)
    root.mainloop()

if __name__ == "__main__":
    main()