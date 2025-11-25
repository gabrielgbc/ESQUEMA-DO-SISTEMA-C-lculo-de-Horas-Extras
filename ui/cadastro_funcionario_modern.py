"""
ui/cadastro_funcionario_modern.py
Interface MODERNA para cadastro de funcionários
"""
import tkinter as tk
from tkinter import ttk, messagebox
from models.database import get_db
from models.funcionario import Funcionario
from models.empresa import Empresa
from models.registro_jornada import RegistroJornada

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
        self.entry.pack(fill=tk.X, ipady=10, ipadx=15)
        
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

class ModernCombobox(tk.Frame):
    """Combobox moderno"""
    def __init__(self, parent, label_text, **kwargs):
        super().__init__(parent, bg='#0f172a')
        
        # Label
        tk.Label(
            self,
            text=label_text,
            font=('Segoe UI', 10),
            bg='#0f172a',
            fg='#94a3b8'
        ).pack(anchor='w', pady=(0, 5))
        
        # Combobox com estilo
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Modern.TCombobox',
            fieldbackground='#1e293b',
            background='#1e293b',
            foreground='white',
            arrowcolor='#6366f1',
            borderwidth=0
        )
        
        self.combo = ttk.Combobox(
            self,
            font=('Segoe UI', 11),
            style='Modern.TCombobox',
            state='readonly',
            **kwargs
        )
        self.combo.pack(fill=tk.X, ipady=8)
    
    def get(self):
        return self.combo.get()
    
    def set(self, value):
        self.combo.set(value)
    
    def configure(self, **kwargs):
        self.combo.configure(**kwargs)
    
    def __getitem__(self, key):
        return self.combo[key]
    
    def __setitem__(self, key, value):
        self.combo[key] = value

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

class CadastroFuncionarioModern:
    def __init__(self, parent):
        self.parent = parent
        self.parent.configure(bg='#0f172a')
        self.db = get_db()
        self.funcionario_editando_id = None
        self.empresas_dict = {}
        self.setup_ui()
        self.carregar_empresas()
        self.carregar_funcionarios()
    
    def setup_ui(self):
        """Configura interface moderna"""
        
        # Card principal do formulário
        # Form compact (reduced paddings to show more content on screen)
        form_card = tk.Frame(self.parent, bg='#1e293b')
        form_card.pack(fill=tk.X, pady=(0, 8))
        
        # Padding interno
        form_inner = tk.Frame(form_card, bg='#1e293b')
        form_inner.pack(fill=tk.X, padx=20, pady=12)
        
        # Título do formulário
        title_frame = tk.Frame(form_inner, bg='#1e293b')
        title_frame.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            title_frame,
            text="👤 Dados do Funcionário",
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
        self.entry_nome = ModernEntry(fields_frame, "Nome do Funcionário *")
        self.entry_nome.grid(row=0, column=0, columnspan=2, sticky='ew', pady=2, padx=2)
        
        # Cargo e Empresa (lado a lado)
        self.entry_cargo = ModernEntry(fields_frame, "Cargo *")
        self.entry_cargo.grid(row=1, column=0, sticky='ew', pady=2, padx=2)
        
        self.combo_empresa = ModernCombobox(fields_frame, "Empresa")
        self.combo_empresa.grid(row=1, column=1, sticky='ew', pady=2, padx=2)
        
        # Carga Horária e Valor Hora (lado a lado)
        self.entry_carga = ModernEntry(fields_frame, "Carga Horária Diária (horas) *")
        self.entry_carga.grid(row=2, column=0, sticky='ew', pady=2, padx=2)
        self.entry_carga.insert(0, "8.0")
        
        self.entry_valor = ModernEntry(fields_frame, "Valor da Hora (R$) *")
        self.entry_valor.grid(row=2, column=1, sticky='ew', pady=2, padx=2)
        
        # Botões
        btn_frame = tk.Frame(form_inner, bg='#1e293b')
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.btn_salvar = ModernButton(
            btn_frame,
            "💾 Salvar",
            self.salvar_funcionario,
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
        # list section - slightly more compact to show multiple tables fully
        list_card = tk.Frame(self.parent, bg='#1e293b')
        list_card.pack(fill=tk.BOTH, expand=True, pady=(8,0))
        
        # Padding interno
        list_inner = tk.Frame(list_card, bg='#1e293b')
        list_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título da lista
        list_title = tk.Frame(list_inner, bg='#1e293b')
        list_title.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            list_title,
            text="📋 Funcionários Cadastrados",
            font=('Segoe UI', 16, 'bold'),
            bg='#1e293b',
            fg='white'
        ).pack(side=tk.LEFT)
        
        # Contador
        self.label_count = tk.Label(
            list_title,
            text="0 funcionários",
            font=('Segoe UI', 11),
            bg='#1e293b',
            fg='#94a3b8'
        )
        self.label_count.pack(side=tk.RIGHT)
        
        # Container da tabela
        table_container = tk.Frame(list_inner, bg='#0f172a')
        # Make table container slightly smaller vertically so 3 tables can fit
        table_container.pack(fill=tk.BOTH, expand=True)
        
        # Estilo do Treeview
        style = ttk.Style()
        style.theme_use('clam')
        
        # reduce rowheight to make the table more compact and show more rows
        style.configure('Modern.Treeview',
            background='#1e293b',
            foreground='white',
            fieldbackground='#1e293b',
            borderwidth=0,
            relief='flat',
            rowheight=28
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
        columns = ("ID", "Nome", "Cargo", "Empresa", "Carga H.", "Valor/H")
        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            height=8,
            style='Modern.Treeview'
        )
        
        # Configurar colunas
        self.tree.column("ID", width=50, anchor='center')
        self.tree.column("Nome", width=180)
        self.tree.column("Cargo", width=120)
        self.tree.column("Empresa", width=150)
        self.tree.column("Carga H.", width=80, anchor='center')
        self.tree.column("Valor/H", width=100, anchor='center')
        
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
        
        # Allow editing / deleting via buttons, double-click and context menu
        ModernButton(
            action_frame,
            "✏️ Editar Selecionado",
            self.editar_funcionario,
            style='primary'
        ).pack(side=tk.LEFT, padx=5)
        
        ModernButton(
            action_frame,
            "🗑️ Excluir Selecionado",
            self.excluir_funcionario,
            style='danger'
        ).pack(side=tk.LEFT, padx=5)

        # Double click to edit
        self.tree.bind('<Double-1>', lambda e: self.editar_funcionario())

        # Right-click context menu for edit/delete
        self._menu = tk.Menu(self.parent, tearoff=0)
        self._menu.add_command(label='✏️ Editar', command=self.editar_funcionario)
        self._menu.add_command(label='🗑️ Excluir', command=self.excluir_funcionario)

        def _show_context(event):
            item = self.tree.identify_row(event.y)
            if item:
                # select clicked row
                self.tree.selection_set(item)
                try:
                    self._menu.tk_popup(event.x_root, event.y_root)
                finally:
                    self._menu.grab_release()

        # Windows/Mac right button is Button-3
        self.tree.bind('<Button-3>', _show_context)

        # Bind Delete key to delete action
        self.tree.bind('<Delete>', lambda e: self.excluir_funcionario())
    
    def carregar_empresas(self):
        """Carrega lista de empresas"""
        empresas = self.db.query(Empresa).all()
        self.empresas_dict = {"Nenhuma": None}
        
        for emp in empresas:
            self.empresas_dict[f"{emp.nome} ({emp.cnpj})"] = emp
        
        self.combo_empresa['values'] = list(self.empresas_dict.keys())
        self.combo_empresa.set("Nenhuma")
    
    def salvar_funcionario(self):
        """Salva ou atualiza funcionário"""
        try:
            nome = self.entry_nome.get().strip()
            cargo = self.entry_cargo.get().strip()
            carga = float(self.entry_carga.get().strip())
            valor = float(self.entry_valor.get().strip())
            
            empresa_key = self.combo_empresa.get()
            empresa = self.empresas_dict.get(empresa_key)
            empresa_id = empresa.id if empresa else None
            
            if not nome or not cargo:
                messagebox.showwarning("Atenção", "Preencha Nome e Cargo!")
                return
            
            if self.funcionario_editando_id:
                # Modo edição
                funcionario = self.db.query(Funcionario).filter(
                    Funcionario.id == self.funcionario_editando_id
                ).first()
                
                if funcionario:
                    funcionario.nome = nome
                    funcionario.cargo = cargo
                    funcionario.carga_horaria_diaria = carga
                    funcionario.valor_hora = valor
                    funcionario.empresa_id = empresa_id
                    mensagem = "✅ Funcionário atualizado com sucesso!"
                else:
                    messagebox.showerror("Erro", "Funcionário não encontrado!")
                    return
            else:
                # Modo criação
                funcionario = Funcionario(
                    nome=nome,
                    cargo=cargo,
                    carga_horaria_diaria=carga,
                    valor_hora=valor,
                    empresa_id=empresa_id
                )
                self.db.add(funcionario)
                mensagem = "✅ Funcionário cadastrado com sucesso!"
            
            self.db.commit()
            messagebox.showinfo("Sucesso", mensagem)
            self.limpar_campos()
            self.carregar_funcionarios()
            
        except ValueError:
            messagebox.showerror("Erro", "Valores numéricos inválidos!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
            self.db.rollback()
    
    def limpar_campos(self):
        """Limpa os campos do formulário"""
        self.funcionario_editando_id = None
        self.btn_salvar.config(text="💾 Salvar")
        self.entry_nome.delete(0, tk.END)
        self.entry_cargo.delete(0, tk.END)
        self.entry_carga.delete(0, tk.END)
        self.entry_carga.insert(0, "8.0")
        self.entry_valor.delete(0, tk.END)
        self.combo_empresa.set("Nenhuma")
    
    def carregar_funcionarios(self):
        """Carrega funcionários no Treeview"""
        # Limpa treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Carrega do banco
        funcionarios = self.db.query(Funcionario).all()
        
        for func in funcionarios:
            try:
                empresa_nome = func.empresa.nome if func.empresa else "-"
            except:
                empresa_nome = "-"
            
            self.tree.insert("", tk.END, values=(
                func.id,
                func.nome,
                func.cargo,
                empresa_nome,
                f"{func.carga_horaria_diaria}h",
                f"R$ {func.valor_hora:.2f}"
            ))
        
        # Atualiza contador
        self.label_count.config(
            text=f"{len(funcionarios)} funcionário{'s' if len(funcionarios) != 1 else ''}"
        )
    
    def editar_funcionario(self):
        """Edita funcionário selecionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Atenção", "Selecione um funcionário!")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        self.funcionario_editando_id = values[0]
        self.btn_salvar.config(text="💾 Atualizar")
        
        self.entry_nome.delete(0, tk.END)
        self.entry_nome.insert(0, values[1])
        self.entry_cargo.delete(0, tk.END)
        self.entry_cargo.insert(0, values[2])
        
        # Define empresa
        empresa_nome = values[3]
        if empresa_nome != "-":
            for key in self.empresas_dict.keys():
                if empresa_nome in key:
                    self.combo_empresa.set(key)
                    break
        else:
            self.combo_empresa.set("Nenhuma")
        
        self.entry_carga.delete(0, tk.END)
        self.entry_carga.insert(0, values[4].replace('h', ''))
        self.entry_valor.delete(0, tk.END)
        self.entry_valor.insert(0, values[5].replace('R$ ', ''))
    
    def excluir_funcionario(self):
        """Exclui funcionário selecionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Atenção", "Selecione um funcionário!")
            return
        
        item = self.tree.item(selection[0])
        func_id = item['values'][0]
        func_nome = item['values'][1]
        
        # Verifica se há registros vinculados
        num_registros = self.db.query(RegistroJornada).filter(
            RegistroJornada.funcionario_id == func_id
        ).count()
        
        if num_registros > 0:
            resposta = messagebox.askyesnocancel(
                "Confirmar Exclusão",
                f"O funcionário '{func_nome}' possui {num_registros} registro(s) de jornada.\n\n"
                f"Deseja excluir o funcionário E todos os seus registros?\n\n"
                f"SIM = Excluir tudo\nNÃO = Cancelar"
            )
            
            if resposta is None or not resposta:
                return
        else:
            if not messagebox.askyesno("Confirmar", f"Deseja realmente excluir '{func_nome}'?"):
                return
        
        try:
            # Exclui registros primeiro (se houver)
            if num_registros > 0:
                self.db.query(RegistroJornada).filter(
                    RegistroJornada.funcionario_id == func_id
                ).delete()
            
            # Exclui funcionário
            func = self.db.query(Funcionario).filter(Funcionario.id == func_id).first()
            self.db.delete(func)
            self.db.commit()
            
            mensagem = "✅ Funcionário excluído!"
            if num_registros > 0:
                mensagem += f"\n{num_registros} registro(s) também foram excluídos."
            
            messagebox.showinfo("Sucesso", mensagem)
            self.carregar_funcionarios()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir: {str(e)}")
            self.db.rollback()