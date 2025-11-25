import tkinter as tk
from ui.relatorios import RelatoriosUI

# Teste simples
root = tk.Tk()
root.title("Teste Relatórios")
root.geometry("900x600")

try:
    RelatoriosUI(root)
    print("✅ Relatórios carregou com sucesso!")
    root.mainloop()
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()