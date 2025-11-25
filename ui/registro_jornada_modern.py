"""
ui/registro_jornada_modern.py
Interface MODERNA para registro de jornadas
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from sqlalchemy import text
from models.database import get_db

class ModernEntry(tk.Frame):
    """Campo de entrada moderno"""
    def __init__(self, parent, label_text, **kwargs):
        super().__init__(parent, bg='#0f172a')
        
        tk.Label(
            self,
            text=label_text,
            font=('Segoe UI', 10),
            bg='#0f172a',
            fg='#94a3b8'
        ).pack(anchor='w', pady=(0, 5))
        
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
        # slightly more compact vertically so the list area has more room
        self.entry.pack(fill=tk.X, ipady=6, ipadx=15)
        
        self.entry.bind('<FocusIn>', self.on_focus_in)
        self.entry.bind('<FocusOut>', self.on_focus_out)
    
    def on_focus_in(self, e):
        self['bg'] = '#6366f1'
    
    def on_focus_out(self, e):
        self['bg'] = '#0f172a'
    
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
        
        tk.Label(
            self,
            text=label_text,
            font=('Segoe UI', 10),
            bg='#0f172a',
            fg='#94a3b8'
        ).pack(anchor='w', pady=(0, 5))
        
        style = ttk.Style()
        style.configure('Modern.TCombobox',
            fieldbackground='#1e293b',
            background='#1e293b',
            foreground='white',
            arrowcolor='#6366f1'
        )
        
        self.combo = ttk.Combobox(
            self,
            font=('Segoe UI', 11),
            style='Modern.TCombobox',
            state='readonly',
            **kwargs
        )
        # slightly reduce combobox vertical padding to save space for the table
        self.combo.pack(fill=tk.X, ipady=5)
    
    def get(self):
        return self.combo.get()
    
    def set(self, value):
        self.combo.set(value)
    
    def __getitem__(self, key):
        return self.combo[key]
    
    def __setitem__(self, key, value):
        self.combo[key] = value

class ModernButton(tk.Button):
    """Botão moderno"""
    def __init__(self, parent, text, command, style='primary', **kwargs):
        styles = {
            'primary': {'bg': '#6366f1', 'hover': '#4f46e5'},
            'success': {'bg': '#10b981', 'hover': '#059669'},
            'secondary': {'bg': '#64748b', 'hover': '#475569'},
            'danger': {'bg': '#ef4444', 'hover': '#dc2626'},
            'info': {'bg': '#3b82f6', 'hover': '#2563eb'}
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
            padx=25,
            pady=8,
            **kwargs
        )
        
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
    
    def on_enter(self, e):
        self.config(bg=self.style_config['hover'])
    
    def on_leave(self, e):
        self.config(bg=self.style_config['bg'])

class RegistroJornadaModern:
    def __init__(self, parent):
        self.parent = parent
        self.parent.configure(bg='#0f172a')
        self.db = get_db()
        self.funcionarios_dict = {}
        
        self.setup_ui()
        self.carregar_funcionarios()
        self.carregar_registros()
    
    def setup_ui(self):
        """Configura interface moderna"""
        
        # Card do formulário
        form_card = tk.Frame(self.parent, bg='#1e293b')
        form_card.pack(fill=tk.X, pady=(0, 10))
        
        form_inner = tk.Frame(form_card, bg='#1e293b')
        form_inner.pack(fill=tk.X, padx=20, pady=10)
        
        # Título
        title_frame = tk.Frame(form_inner, bg='#1e293b')
        title_frame.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            title_frame,
            text="⏱️ Registro de Jornada",
            font=('Segoe UI', 16, 'bold'),
            bg='#1e293b',
            fg='white'
        ).pack(side=tk.LEFT)
        
        # Grid de campos
        fields_frame = tk.Frame(form_inner, bg='#1e293b')
        fields_frame.pack(fill=tk.X)
        
        fields_frame.columnconfigure(0, weight=1)
        fields_frame.columnconfigure(1, weight=1)
        fields_frame.columnconfigure(2, weight=1)
        
        # Funcionário (span 3 colunas)
        self.combo_funcionario = ModernCombobox(fields_frame, "Funcionário *")
        self.combo_funcionario.grid(row=0, column=0, columnspan=3, sticky='ew', pady=3, padx=2)
        
        # Data, Entrada, Saída (3 colunas)
        self.entry_data = ModernEntry(fields_frame, "Data (DD/MM/AAAA) *")
        self.entry_data.grid(row=1, column=0, sticky='ew', pady=3, padx=2)
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        self.entry_entrada = ModernEntry(fields_frame, "Entrada (HH:MM) *")
        self.entry_entrada.grid(row=1, column=1, sticky='ew', pady=3, padx=2)
        
        self.entry_saida = ModernEntry(fields_frame, "Saída (HH:MM) *")
        self.entry_saida.grid(row=1, column=2, sticky='ew', pady=3, padx=2)
        
        # Intervalo (1 coluna)
        self.entry_intervalo = ModernEntry(fields_frame, "Intervalo (horas)")
        self.entry_intervalo.grid(row=2, column=0, sticky='ew', pady=3, padx=2)
        self.entry_intervalo.insert(0, "1.0")
        
        # Área de resultado
        result_card = tk.Frame(fields_frame, bg='#334155', relief=tk.FLAT)
        result_card.grid(row=2, column=1, columnspan=2, sticky='ew', pady=3, padx=2)
        
        result_inner = tk.Frame(result_card, bg='#334155')
        result_inner.pack(fill=tk.BOTH, padx=15, pady=15)
        
        tk.Label(
            result_inner,
            text="📊 Resultado",
            font=('Segoe UI', 10, 'bold'),
            bg='#334155',
            fg='#94a3b8'
        ).pack(anchor='w')
        
        self.label_result = tk.Label(
            result_inner,
            text="Preencha os dados acima",
            font=('Segoe UI', 9),
            bg='#334155',
            fg='#cbd5e1',
            justify=tk.LEFT
        )
        self.label_result.pack(anchor='w', pady=(5, 0))
        
        # Botões
        btn_frame = tk.Frame(form_inner, bg='#1e293b')
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ModernButton(
            btn_frame,
            "💾 Salvar Jornada",
            self.salvar_registro,
            style='success'
        ).pack(side=tk.LEFT, padx=5)
        
        ModernButton(
            btn_frame,
            "📊 Ver Resumo",
            self.abrir_relatorio,
            style='info'
        ).pack(side=tk.LEFT, padx=5)
        
        ModernButton(
            btn_frame,
            "🗑️ Limpar",
            self.limpar_campos,
            style='secondary'
        ).pack(side=tk.LEFT, padx=5)
        
        # Card da lista
        list_card = tk.Frame(self.parent, bg='#1e293b')
        list_card.pack(fill=tk.BOTH, expand=True)
        
        # reduce padding so the table can occupy more vertical space
        list_inner = tk.Frame(list_card, bg='#1e293b')
        list_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Título da lista
        list_title = tk.Frame(list_inner, bg='#1e293b')
        list_title.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            list_title,
            text="📋 Registros Recentes",
            font=('Segoe UI', 16, 'bold'),
            bg='#1e293b',
            fg='white'
        ).pack(side=tk.LEFT)
        
        self.label_count = tk.Label(
            list_title,
            text="0 registros",
            font=('Segoe UI', 11),
            bg='#1e293b',
            fg='#94a3b8'
        )
        self.label_count.pack(side=tk.RIGHT)
        
        # Tabela
        table_container = tk.Frame(list_inner, bg='#0f172a')
        table_container.pack(fill=tk.BOTH, expand=True)
        
        style = ttk.Style()
        # Make rows taller and slightly increase the font so the table looks bigger
        style.configure('Modern.Treeview',
            background='#1e293b',
            foreground='white',
            fieldbackground='#1e293b',
            borderwidth=0,
            relief='flat',
            # use a moderate row height so more rows fit on-screen
            rowheight=36
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
        
        columns = ("ID", "Funcionário", "Empresa", "Data", "Entrada", "Saída", "H.Trab", "H.Extra", "H.Falta")
            # Increase visible rows so the table uses more vertical space and
            # shows more records. With smaller rowheight this yields a better
            # balance of visible rows.
        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            height=22,
            style='Modern.Treeview'
        )
        
        # Widen columns so values have space and table looks more prominent
        col_widths = [60, 220, 200, 120, 110, 110, 110, 110, 110]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='center' if col == 'ID' else tk.W)
        
        scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botão de ação
        action_frame = tk.Frame(list_inner, bg='#1e293b')
        action_frame.pack(fill=tk.X, pady=(20, 0))
        
        ModernButton(
            action_frame,
            "🗑️ Excluir Selecionado",
            self.excluir_registro,
            style='danger'
        ).pack(side=tk.LEFT, padx=5)
    
    def carregar_funcionarios(self):
        """Carrega funcionários"""
        try:
            from models.funcionario import Funcionario
            funcionarios = self.db.query(Funcionario).all()
            
            self.funcionarios_dict = {}
            lista_display = []
            
            for func in funcionarios:
                try:
                    empresa_nome = func.empresa.nome if func.empresa else "Sem Empresa"
                except:
                    empresa_nome = "Sem Empresa"
                
                display = f"{func.nome} - {empresa_nome}"
                lista_display.append(display)
                self.funcionarios_dict[display] = func
            
            self.combo_funcionario['values'] = lista_display
        except Exception as e:
            print(f"⚠️ Erro ao carregar funcionários: {e}")
    
    def calcular_horas_trabalhadas(self, hora_entrada, hora_saida, intervalo):
        """Calcula horas trabalhadas"""
        dt_entrada = datetime.combine(datetime.today(), hora_entrada)
        dt_saida = datetime.combine(datetime.today(), hora_saida)
        
        if dt_saida < dt_entrada:
            dt_saida += timedelta(days=1)
        
        diferenca = dt_saida - dt_entrada
        horas_totais = diferenca.total_seconds() / 3600
        horas_trabalhadas = horas_totais - intervalo
        
        return round(horas_trabalhadas, 2)
    
    def calcular_extras_faltas(self, horas_trabalhadas, carga_horaria_diaria):
        """Calcula extras e faltas"""
        diferenca = horas_trabalhadas - carga_horaria_diaria
        
        if diferenca > 0:
            return round(diferenca, 2), 0.0
        else:
            return 0.0, round(abs(diferenca), 2)
    
    def salvar_registro(self):
        """Salva registro"""
        try:
            from models.registro_jornada import RegistroJornada
            
            if not self.combo_funcionario.get():
                messagebox.showwarning("Atenção", "Selecione um funcionário!")
                return
            
            funcionario = self.funcionarios_dict[self.combo_funcionario.get()]
            
            data_str = self.entry_data.get().strip()
            data = datetime.strptime(data_str, "%d/%m/%Y").date()
            
            # Verifica duplicata
            from models.registro_jornada import RegistroJornada
            registro_existente = self.db.query(RegistroJornada).filter(
                RegistroJornada.funcionario_id == funcionario.id,
                RegistroJornada.data == data
            ).first()
            
            if registro_existente:
                resposta = messagebox.askyesno(
                    "Registro Duplicado",
                    f"⚠️ Já existe um registro para {funcionario.nome} em {data_str}!\n\n"
                    f"Deseja SUBSTITUIR o registro anterior?"
                )
                
                if not resposta:
                    return
                
                self.db.delete(registro_existente)
                self.db.commit()
            
            entrada_str = self.entry_entrada.get().strip()
            saida_str = self.entry_saida.get().strip()
            hora_entrada = datetime.strptime(entrada_str, "%H:%M").time()
            hora_saida = datetime.strptime(saida_str, "%H:%M").time()
            
            intervalo = float(self.entry_intervalo.get().strip())
            
            horas_trabalhadas = self.calcular_horas_trabalhadas(hora_entrada, hora_saida, intervalo)
            horas_extras, horas_faltantes = self.calcular_extras_faltas(
                horas_trabalhadas, 
                funcionario.carga_horaria_diaria
            )
            
            registro = RegistroJornada(
                funcionario_id=funcionario.id,
                data=data,
                hora_entrada=hora_entrada,
                hora_saida=hora_saida,
                intervalo=intervalo,
                horas_trabalhadas=horas_trabalhadas,
                horas_extras=horas_extras,
                horas_faltantes=horas_faltantes
            )
            
            self.db.add(registro)
            self.db.commit()
            
            resultado = f"""✅ Jornada Registrada!

📊 H. Trabalhadas: {horas_trabalhadas:.2f}h
⏰ H. Extras: {horas_extras:.2f}h
⚠️ H. Faltantes: {horas_faltantes:.2f}h"""
            
            self.label_result.config(text=resultado, fg='#10b981')
            
            messagebox.showinfo("Sucesso", f"✅ Jornada registrada!\n\nFuncionário: {funcionario.nome}")
            
            self.limpar_campos()
            self.carregar_registros()
            
        except ValueError:
            messagebox.showerror("Erro", "Formato de data/hora inválido!\n\nUse:\nData: DD/MM/AAAA\nHora: HH:MM")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar:\n{str(e)}")
            self.db.rollback()
    
    def limpar_campos(self):
        """Limpa campos"""
        self.combo_funcionario.set('')
        self.entry_data.delete(0, tk.END)
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.entry_entrada.delete(0, tk.END)
        self.entry_saida.delete(0, tk.END)
        self.entry_intervalo.delete(0, tk.END)
        self.entry_intervalo.insert(0, "1.0")
        self.label_result.config(text="Preencha os dados acima", fg='#cbd5e1')
    
    def carregar_registros(self):
        """Carrega registros"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            query = text("""
                SELECT r.id, f.nome, 
                       COALESCE(e.nome, f.empresa, 'Sem Empresa') as empresa_nome,
                       r.data, r.hora_entrada, r.hora_saida, 
                       r.horas_trabalhadas, r.horas_extras, r.horas_faltantes
                FROM registros_jornada r
                JOIN funcionarios f ON r.funcionario_id = f.id
                LEFT JOIN empresas e ON f.empresa_id = e.id
                WHERE r.id IN (
                    SELECT MAX(id) 
                    FROM registros_jornada 
                    GROUP BY funcionario_id, data
                )
                ORDER BY r.data DESC, r.hora_entrada DESC
                LIMIT 50
            """)
            
            result = self.db.execute(query)
            count = 0
            
            for row in result:
                data_fmt = row[3].strftime('%d/%m/%Y') if hasattr(row[3], 'strftime') else str(row[3])
                entrada_fmt = row[4].strftime('%H:%M') if hasattr(row[4], 'strftime') else str(row[4])
                saida_fmt = row[5].strftime('%H:%M') if hasattr(row[5], 'strftime') else str(row[5])
                
                self.tree.insert("", tk.END, values=(
                    row[0],
                    row[1],
                    row[2],
                    data_fmt,
                    entrada_fmt,
                    saida_fmt,
                    f"{row[6]:.1f}h",
                    f"{row[7]:.1f}h",
                    f"{row[8]:.1f}h"
                ))
                count += 1
            
            self.label_count.config(text=f"{count} registro{'s' if count != 1 else ''}")
            
        except Exception as e:
            print(f"⚠️ Erro ao carregar registros: {e}")
    
    def excluir_registro(self):
        """Exclui registro"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Atenção", "Selecione um registro!")
            return
        
        if messagebox.askyesno("Confirmar", "Deseja excluir este registro?"):
            item = self.tree.item(selection[0])
            reg_id = item['values'][0]
            
            try:
                from models.registro_jornada import RegistroJornada
                
                reg = self.db.query(RegistroJornada).filter(
                    RegistroJornada.id == reg_id
                ).first()
                
                self.db.delete(reg)
                self.db.commit()
                
                messagebox.showinfo("Sucesso", "✅ Registro excluído!")
                self.carregar_registros()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir:\n{str(e)}")
                self.db.rollback()
    
    def abrir_relatorio(self):
        """Abre relatório"""
        from ui.relatorios_modern import RelatorioSaldoPopup
        RelatorioSaldoPopup(self.parent)
