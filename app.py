"""
app.py
Arquivo principal - Ponto de entrada do sistema
"""
import tkinter as tk
from ui.main_window import MainWindow
from models.database import init_db

def main():
    """Função principal que inicia o sistema"""
    # Inicializa o banco de dados
    print("Inicializando banco de dados...")
    init_db()
    print("Banco de dados inicializado com sucesso!")
    
    # Cria janela principal
    root = tk.Tk()
    
    # Configura ícone e tema (opcional)
    try:
        # root.iconbitmap('icon.ico')  # Descomente se tiver um ícone
        pass
    except:
        pass
    
    # Inicializa aplicação
    app = MainWindow(root)
    
    # Inicia loop principal
    root.mainloop()

if __name__ == "__main__":
    main()