"""
ui/cadastro_empresa.py
Interface para cadastro e gestão de empresas
"""
import tkinter as tk
from tkinter import ttk, messagebox
from models.database import get_db
from models.empresa import Empresa

class CadastroEmpresa:
    def __init__(self, parent):
        self.parent = parent
        self.db = get_db()
        self.empresa_editando_id = None
        self.setup_ui()
        self.carregar_empresas()
    
    def setup_ui(self):
        """Configura a interface"""
        # Título
        title_frame = tk.Frame(self.parent, bg="white")
        title_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            title_frame,
            text="🏢 Cadastro de Empresas",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack()
        
        # Frame de formulário
        form_frame = tk.LabelFrame(self.parent, text="Dados da Empresa", padx=20, pady=20)
        form_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Nome
        tk.Label(form_frame, text="Nome da Empresa:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_nome = tk.Entry(form_frame, width=40)
        self.entry_nome.grid(row=0, column=1, pady=5, padx=10)
        
        # CNPJ
        tk.Label(form_frame, text="CNPJ:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_cnpj = tk.Entry(form_frame, width=40)
        self.entry_cnpj.grid(row=1, column=1, pady=5, padx=10)
        
        # Endereço
        tk.Label(form_frame, text="Endereço:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_endereco = tk.Entry(form_frame, width=40)
        self.entry_endereco.grid(row=2, column=1, pady=5, padx=10)
        
        # Telefone
        tk.Label(form_frame, text="Telefone:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.entry_telefone = tk.Entry(form_frame, width=40)
        self.entry_telefone.grid(row=3, column=1, pady=5, padx=10)
        
        # Email
        tk.Label(form_frame, text="Email:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.entry_email = tk.Entry(form_frame, width=40)
        self.entry_email.grid(row=4, column=1, pady=5, padx=10)
        
        # Botões
        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=15)
        
        self.btn_salvar = tk.Button(
            btn_frame,
            text="Salvar",
            command=self.salvar_empresa,
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=5,
            cursor="hand2"
        )
        self.btn_salvar.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Limpar",
            command=self.limpar_campos,
            bg="#95a5a6",
            fg="white",
            padx=20,
            pady=5,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        # Lista de empresas
        list_frame = tk.LabelFrame(self.parent, text="Empresas Cadastradas", padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Treeview
        columns = ("ID", "Nome", "CNPJ", "Telefone", "Email")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        col_widths = [50, 200, 150, 120, 180]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botões de ação
        action_frame = tk.Frame(self.parent, bg="white")
        action_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(
            action_frame,
            text="Editar Selecionada",
            command=self.editar_empresa,
            bg="#3498db",
            fg="white",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="Excluir Selecionada",
            command=self.excluir_empresa,
            bg="#e74c3c",
            fg="white",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
    
    def salvar_empresa(self):
        """Salva ou atualiza empresa"""
        try:
            nome = self.entry_nome.get().strip()
            cnpj = self.entry_cnpj.get().strip()
            endereco = self.entry_endereco.get().strip()
            telefone = self.entry_telefone.get().strip()
            email = self.entry_email.get().strip()
            
            if not nome or not cnpj:
                messagebox.showwarning("Atenção", "Preencha Nome e CNPJ!")
                return
            
            if self.empresa_editando_id:
                # Modo edição
                empresa = self.db.query(Empresa).filter(
                    Empresa.id == self.empresa_editando_id
                ).first()
                
                if empresa:
                    empresa.nome = nome
                    empresa.cnpj = cnpj
                    empresa.endereco = endereco
                    empresa.telefone = telefone
                    empresa.email = email
                    mensagem = "Empresa atualizada com sucesso!"
                else:
                    messagebox.showerror("Erro", "Empresa não encontrada!")
                    return
            else:
                # Modo criação
                empresa = Empresa(
                    nome=nome,
                    cnpj=cnpj,
                    endereco=endereco,
                    telefone=telefone,
                    email=email
                )
                self.db.add(empresa)
                mensagem = "Empresa cadastrada com sucesso!"
            
            self.db.commit()
            messagebox.showinfo("Sucesso", mensagem)
            self.limpar_campos()
            self.carregar_empresas()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
            self.db.rollback()
    
    def limpar_campos(self):
        """Limpa os campos do formulário"""
        self.empresa_editando_id = None
        self.btn_salvar.config(text="Salvar")
        self.entry_nome.delete(0, tk.END)
        self.entry_cnpj.delete(0, tk.END)
        self.entry_endereco.delete(0, tk.END)
        self.entry_telefone.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
    
    def carregar_empresas(self):
        """Carrega empresas no Treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        empresas = self.db.query(Empresa).all()
        for emp in empresas:
            self.tree.insert("", tk.END, values=(
                emp.id,
                emp.nome,
                emp.cnpj,
                emp.telefone or "-",
                emp.email or "-"
            ))
    
    def editar_empresa(self):
        """Edita empresa selecionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Atenção", "Selecione uma empresa!")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        self.empresa_editando_id = values[0]
        self.btn_salvar.config(text="Atualizar")
        
        self.entry_nome.delete(0, tk.END)
        self.entry_nome.insert(0, values[1])
        self.entry_cnpj.delete(0, tk.END)
        self.entry_cnpj.insert(0, values[2])
        self.entry_telefone.delete(0, tk.END)
        self.entry_telefone.insert(0, values[3] if values[3] != "-" else "")
        self.entry_email.delete(0, tk.END)
        self.entry_email.insert(0, values[4] if values[4] != "-" else "")
    
    def excluir_empresa(self):
        """Exclui empresa selecionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Atenção", "Selecione uma empresa!")
            return
        
        item = self.tree.item(selection[0])
        emp_id = item['values'][0]
        emp_nome = item['values'][1]
        
        if not messagebox.askyesno("Confirmar", f"Deseja realmente excluir '{emp_nome}'?"):
            return
        
        try:
            empresa = self.db.query(Empresa).filter(Empresa.id == emp_id).first()
            self.db.delete(empresa)
            self.db.commit()
            messagebox.showinfo("Sucesso", "Empresa excluída!")
            self.carregar_empresas()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir: {str(e)}")
            self.db.rollback()
