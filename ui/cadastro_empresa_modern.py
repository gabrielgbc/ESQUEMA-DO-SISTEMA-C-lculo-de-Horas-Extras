"""
ui/cadastro_empresa_modern.py
Interface MODERNA para cadastro de empresas
"""
import tkinter as tk
from tkinter import ttk, messagebox
from models.database import get_db
from models.empresa import Empresa

class ModernEntry(tk.Frame):
    """Campo de entrada moderno com label flutuante"""
    def __init__(self, parent, label_text, **kwargs):
        super().__init__(parent, bg='#0f172a')
        
        self.label_text = label_text
        
        # Label
        self.label = tk.Label(
            self,
            text=label_text,
            font=('Segoe UI', 10),
            bg='#0f172a',
            fg='#94a3b8'
        )
        self.label.pack(anchor='w', pady=(0, 5))
        
        # Entry
        self.entry = tk.Entry(
            self,
            font=('Segoe UI', 11),
            bg='#1e293b',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=2,
            highlightbackground='#334155',
            highlightcolor='#6366f1',
            **kwargs
        )
        # slightly reduce vertical padding of input fields so listing area
        # can gain more vertical space without changing fonts
        self.entry.pack(fill=tk.X, ipady=6, ipadx=15)
        
        # Efeitos
        self.entry.bind('<FocusIn>', self.on_focus_in)
        self.entry.bind('<FocusOut>', self.on_focus_out)
    
    def on_focus_in(self, e):
        self.label.config(fg='#6366f1', font=('Segoe UI', 10, 'bold'))
    
    def on_focus_out(self, e):
        self.label.config(fg='#94a3b8', font=('Segoe UI', 10))
    
    def get(self):
        return self.entry.get()
    
    def delete(self, first, last):
        self.entry.delete(first, last)
    
    def insert(self, index, string):
        self.entry.insert(index, string)

class ModernButton(tk.Button):
    """Botão moderno customizado"""
    def __init__(self, parent, text, command, style='primary', **kwargs):
        
        # Estilos
        styles = {
            'primary': {'bg': '#6366f1', 'hover': '#4f46e5'},
            'success': {'bg': '#10b981', 'hover': '#059669'},
            'secondary': {'bg': '#64748b', 'hover': '#475569'},
            'danger': {'bg': '#ef4444', 'hover': '#dc2626'},
            'warning': {'bg': '#f59e0b', 'hover': '#d97706'}
        }
        
        self.style_config = styles.get(style, styles['primary'])
        
        super().__init__(
            parent,
            text=text,
            command=command,
            font=('Segoe UI', 11, 'bold'),
            bg=self.style_config['bg'],
            fg='white',
            activebackground=self.style_config['hover'],
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            borderwidth=0,
            padx=30,
            pady=12,
            **kwargs
        )
        
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
    
    def on_enter(self, e):
        self.config(bg=self.style_config['hover'])
    
    def on_leave(self, e):
        self.config(bg=self.style_config['bg'])

class CadastroEmpresaModern:
    def __init__(self, parent):
        self.parent = parent
        self.parent.configure(bg='#0f172a')
        self.db = get_db()
        self.empresa_editando_id = None
        self.setup_ui()
        self.carregar_empresas()
    
    def setup_ui(self):
        """Configura interface moderna"""
        
        # Card principal do formulário
        form_card = tk.Frame(self.parent, bg='#1e293b')
        # keep the form compact so the list/table below can get more room
        form_card.pack(fill=tk.X, pady=(0, 10))
        
        # Padding interno
        form_inner = tk.Frame(form_card, bg='#1e293b')
        form_inner.pack(fill=tk.X, padx=20, pady=10)
        
        # Título do formulário
        title_frame = tk.Frame(form_inner, bg='#1e293b')
        title_frame.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            title_frame,
            text="🏢 Dados da Empresa",
            font=('Segoe UI', 16, 'bold'),
            bg='#1e293b',
            fg='white'
        ).pack(side=tk.LEFT)
        
        # Grid de campos
        fields_frame = tk.Frame(form_inner, bg='#1e293b')
        fields_frame.pack(fill=tk.X)
        
        # Configurar grid
        fields_frame.columnconfigure(0, weight=1)
        fields_frame.columnconfigure(1, weight=1)
        
        # Nome (span 2 colunas)
        self.entry_nome = ModernEntry(fields_frame, "Nome da Empresa *")
        self.entry_nome.grid(row=0, column=0, columnspan=2, sticky='ew', pady=3, padx=2)
        
        # CNPJ e Telefone (lado a lado)
        self.entry_cnpj = ModernEntry(fields_frame, "CNPJ *")
        self.entry_cnpj.grid(row=1, column=0, sticky='ew', pady=3, padx=2)
        self.entry_telefone = ModernEntry(fields_frame, "Telefone")
        self.entry_telefone.grid(row=1, column=1, sticky='ew', pady=3, padx=2)

        # Endereço e Email (lado a lado)
        self.entry_endereco = ModernEntry(fields_frame, "Endereço")
        self.entry_endereco.grid(row=2, column=0, sticky='ew', pady=3, padx=2)

        self.entry_email = ModernEntry(fields_frame, "Email")
        self.entry_email.grid(row=2, column=1, sticky='ew', pady=3, padx=2)

        # Botões
        btn_frame = tk.Frame(form_inner, bg='#1e293b')
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.btn_salvar = ModernButton(
            btn_frame,
            "💾 Salvar",
            self.salvar_empresa,
            style='success'
        )
        self.btn_salvar.pack(side=tk.LEFT, padx=5)
        
        ModernButton(
            btn_frame,
            "🗑️ Limpar",
            self.limpar_campos,
            style='secondary'
        ).pack(side=tk.LEFT, padx=5)
        
        # Card da lista
        list_card = tk.Frame(self.parent, bg='#1e293b')
        list_card.pack(fill=tk.BOTH, expand=True)
        
        # Padding interno
        list_inner = tk.Frame(list_card, bg='#1e293b')
        # reduce padding around the list to free more vertical space
        list_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)
        
        # Título da lista
        list_title = tk.Frame(list_inner, bg='#1e293b')
        list_title.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            list_title,
            text="📋 Empresas Cadastradas",
            font=('Segoe UI', 16, 'bold'),
            bg='#1e293b',
            fg='white'
        ).pack(side=tk.LEFT)
        
        # Contador
        self.label_count = tk.Label(
            list_title,
            text="0 empresas",
            font=('Segoe UI', 11),
            bg='#1e293b',
            fg='#94a3b8'
        )
        self.label_count.pack(side=tk.RIGHT)
        
        # Container da tabela
        table_container = tk.Frame(list_inner, bg='#0f172a')
        table_container.pack(fill=tk.BOTH, expand=True)
        
        # Estilo do Treeview
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Modern.Treeview',
            background='#1e293b',
            foreground='white',
            fieldbackground='#1e293b',
            borderwidth=0,
            relief='flat',
            # a slightly smaller rowheight plus a larger visible height
            # will let the table show more rows while keeping the same font
            rowheight=32
        )
        
        style.map('Modern.Treeview',
            background=[('selected', '#6366f1')],
            foreground=[('selected', 'white')]
        )
        
        style.configure('Modern.Treeview.Heading',
            background='#334155',
            foreground='white',
            relief='flat',
            borderwidth=0,
            font=('Segoe UI', 10, 'bold')
        )
        
        # Treeview
        columns = ("ID", "Nome", "CNPJ", "Telefone", "Email")
        # increase visible rows so the table occupies more vertical space
        # and shows more entries without changing fonts
        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            height=14,
            style='Modern.Treeview'
        )
        
        # Configurar colunas
        self.tree.column("ID", width=50, anchor='center')
        self.tree.column("Nome", width=200)
        self.tree.column("CNPJ", width=150)
        self.tree.column("Telefone", width=120)
        self.tree.column("Email", width=180)
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        # Scrollbar moderna
        scrollbar = ttk.Scrollbar(
            table_container,
            orient=tk.VERTICAL,
            command=self.tree.yview
        )
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botões de ação
        action_frame = tk.Frame(list_inner, bg='#1e293b')
        action_frame.pack(fill=tk.X, pady=(20, 0))
        
        ModernButton(
            action_frame,
            "✏️ Editar Selecionada",
            self.editar_empresa,
            style='primary'
        ).pack(side=tk.LEFT, padx=5)
        
        ModernButton(
            action_frame,
            "🗑️ Excluir Selecionada",
            self.excluir_empresa,
            style='danger'
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
                    mensagem = "✅ Empresa atualizada com sucesso!"
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
                mensagem = "✅ Empresa cadastrada com sucesso!"
            
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
        self.btn_salvar.config(text="💾 Salvar")
        self.entry_nome.delete(0, tk.END)
        self.entry_cnpj.delete(0, tk.END)
        self.entry_endereco.delete(0, tk.END)
        self.entry_telefone.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
    
    def carregar_empresas(self):
        """Carrega empresas no Treeview"""
        # Limpa treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Carrega do banco
        empresas = self.db.query(Empresa).all()
        
        for emp in empresas:
            self.tree.insert("", tk.END, values=(
                emp.id,
                emp.nome,
                emp.cnpj,
                emp.telefone or "-",
                emp.email or "-"
            ))
        
        # Atualiza contador
        self.label_count.config(
            text=f"{len(empresas)} empresa{'s' if len(empresas) != 1 else ''}"
        )
    
    def editar_empresa(self):
        """Edita empresa selecionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Atenção", "Selecione uma empresa!")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        self.empresa_editando_id = values[0]
        self.btn_salvar.config(text="💾 Atualizar")
        
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
            messagebox.showinfo("Sucesso", "✅ Empresa excluída!")
            self.carregar_empresas()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir: {str(e)}")
            self.db.rollback()