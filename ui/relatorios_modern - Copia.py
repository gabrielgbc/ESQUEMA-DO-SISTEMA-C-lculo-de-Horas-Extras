"""
ui/relatorios_modern.py
Interface MODERNA para relatórios
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from models.database import get_db
from models.funcionario import Funcionario
from models.empresa import Empresa
from models.registro_jornada import RegistroJornada
from services.calculo_service import CalculoService
from sqlalchemy import func, text

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
        # Ensure combobox field looks dark and text is visible when readonly
        style.configure('Modern.TCombobox',
            fieldbackground='#0f172a',
            background='#0f172a',
            foreground='#e6eef6',
            arrowcolor='#6366f1'
        )
        # Explicitly map the readonly state so some platforms don't use the
        # system light background for readonly comboboxes
        style.map('Modern.TCombobox',
            fieldbackground=[('readonly', '#0f172a')],
            background=[('readonly', '#0f172a')],
            foreground=[('readonly', '#e6eef6')]
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
    
    def bind(self, event, handler):
        self.combo.bind(event, handler)
    
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

class RelatoriosModern:
    def __init__(self, parent):
        self.parent = parent
        self.parent.configure(bg='#0f172a')
        self.db = get_db()
        self.calculo_service = CalculoService()
        
        self.setup_ui()
        self.carregar_funcionarios()
        self.carregar_empresas()
    
    def setup_ui(self):
        """Configura interface"""
        
        # Make the whole page scrollable: create a canvas-backed scrollable
        # inner frame inside self.parent so the user can scroll down to the
        # detailed table when it doesn't fit the visible area.
        container = tk.Frame(self.parent, bg='#0f172a')
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container, bg='#0f172a', highlightthickness=0)
        v_scroll = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=v_scroll.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # A frame that will hold all content — we create a window for it
        scrollable_inner = tk.Frame(canvas, bg='#0f172a')
        canvas_window = canvas.create_window((0, 0), window=scrollable_inner, anchor='nw')

        # Keep scrollregion updated
        def _on_frame_config(event):
            canvas.configure(scrollregion=canvas.bbox('all'))

        scrollable_inner.bind('<Configure>', _on_frame_config)

        # Make canvas window resize to canvas width so child widgets wrap
        def _on_canvas_config(event):
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind('<Configure>', _on_canvas_config)

        # Add mousewheel scrolling support (Windows, OSX, Linux)
        def _on_mousewheel(event):
            # Windows and macOS wheel behavior
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
            else:
                # Linux uses Button-4 and Button-5 for wheel; event.num present
                if event.num == 4:
                    canvas.yview_scroll(-3, 'units')
                elif event.num == 5:
                    canvas.yview_scroll(3, 'units')

        # Bind multiple wheel events to the canvas
        canvas.bind_all('<MouseWheel>', _on_mousewheel)
        canvas.bind_all('<Button-4>', _on_mousewheel)
        canvas.bind_all('<Button-5>', _on_mousewheel)

        # Card de filtros
        filter_card = tk.Frame(scrollable_inner, bg='#1e293b')
        filter_card.pack(fill=tk.X, pady=(0, 15))

        filter_inner = tk.Frame(filter_card, bg='#1e293b')
        filter_inner.pack(fill=tk.X, padx=30, pady=20)
        
        # Título
        tk.Label(
            filter_inner,
            text="🔍 Filtros",
            font=('Segoe UI', 16, 'bold'),
            bg='#1e293b',
            fg='white'
        ).pack(anchor='w', pady=(0, 20))
        
        # Grid de filtros
        filters_grid = tk.Frame(filter_inner, bg='#1e293b')
        filters_grid.pack(fill=tk.X)
        
        filters_grid.columnconfigure(0, weight=1)
        filters_grid.columnconfigure(1, weight=1)
        filters_grid.columnconfigure(2, weight=1)
        
        # Empresa
        self.combo_empresa = ModernCombobox(filters_grid, "Empresa")
        self.combo_empresa.grid(row=0, column=0, sticky='ew', pady=3, padx=2)
        self.combo_empresa.bind("<<ComboboxSelected>>", lambda e: self.filtrar_funcionarios())
        
        # Funcionário
        self.combo_funcionario = ModernCombobox(filters_grid, "Funcionário")
        self.combo_funcionario.grid(row=0, column=1, sticky='ew', pady=3, padx=2)
        
        # Período
        self.combo_periodo = ModernCombobox(filters_grid, "Período")
        self.combo_periodo.grid(row=0, column=2, sticky='ew', pady=3, padx=2)
        self.combo_periodo['values'] = [
            "Últimos 7 dias",
            "Últimos 30 dias",
            "Este mês",
            "Mês passado"
        ]
        self.combo_periodo.set("Últimos 30 dias")
        
        # Botão gerar
        btn_frame = tk.Frame(filter_inner, bg='#1e293b')
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        ModernButton(
            btn_frame,
            "📊 Gerar Relatório",
            self.gerar_relatorio,
            style='success'
        ).pack(side=tk.LEFT)
        
        # Card de resumo
        summary_card = tk.Frame(scrollable_inner, bg='#1e293b')
        summary_card.pack(fill=tk.X, pady=(0, 15))

        summary_inner = tk.Frame(summary_card, bg='#1e293b')
        summary_inner.pack(fill=tk.BOTH, padx=30, pady=20)
        
        tk.Label(
            summary_inner,
            text="📈 Resumo do Período",
            font=('Segoe UI', 16, 'bold'),
            bg='#1e293b',
            fg='white'
        ).pack(anchor='w', pady=(0, 15))
        
        # Grid de cards de estatísticas
        stats_grid = tk.Frame(summary_inner, bg='#1e293b')
        stats_grid.pack(fill=tk.X)
        
        stats_grid.columnconfigure(0, weight=1)
        stats_grid.columnconfigure(1, weight=1)
        stats_grid.columnconfigure(2, weight=1)
        
        # Card de horas extras
        # create_stat_card now returns (card_frame, value_label)
        card, label = self.create_stat_card(
            stats_grid, "⏰", "Horas Extras", "0.00h", "#f59e0b"
        )
        self.card_extras_frame = card
        self.card_extras = label
        self.card_extras_frame.grid(row=0, column=0, sticky='ew', padx=5)
        
        # Card de horas faltantes
        card, label = self.create_stat_card(
            stats_grid, "⚠️", "Horas Faltantes", "0.00h", "#ef4444"
        )
        self.card_faltas_frame = card
        self.card_faltas = label
        self.card_faltas_frame.grid(row=0, column=1, sticky='ew', padx=5)
        
        # Card de valor
        card, label = self.create_stat_card(
            stats_grid, "💰", "Valor Extras", "R$ 0,00", "#10b981"
        )
        self.card_valor_frame = card
        self.card_valor = label
        self.card_valor_frame.grid(row=0, column=2, sticky='ew', padx=5)
        
        # Card da tabela
        table_card = tk.Frame(scrollable_inner, bg='#1e293b')
        table_card.pack(fill=tk.BOTH, expand=True)

        table_inner = tk.Frame(table_card, bg='#1e293b')
        table_inner.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Título
        tk.Label(
            table_inner,
            text="📋 Detalhamento por Funcionário",
            font=('Segoe UI', 16, 'bold'),
            bg='#1e293b',
            fg='white'
        ).pack(anchor='w', pady=(0, 20))
        
        # Tabela
        table_container = tk.Frame(table_inner, bg='#0f172a')
        table_container.pack(fill=tk.BOTH, expand=True)
        
        style = ttk.Style()
        style.configure('Modern.Treeview',
            background='#1e293b',
            foreground='white',
            fieldbackground='#1e293b',
            borderwidth=0,
            relief='flat',
            rowheight=40
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
        
        columns = ("ID", "Funcionário", "Empresa", "Cargo", "H.Extra", "H.Falta", "Valor")
        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            height=10,
            style='Modern.Treeview'
        )
        
        col_widths = [40, 180, 150, 120, 80, 80, 100]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='center' if col == 'ID' else tk.W)
        
        scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # improve row visibility by defining alternating tag colors
        try:
            self.tree.tag_configure('odd', background='#0f172a', foreground='white')
            self.tree.tag_configure('even', background='#1e293b', foreground='white')
        except Exception:
            # some tkinter versions are picky about tag styling — ignore failures
            pass
    
    def create_stat_card(self, parent, icon, title, value, color):
        """Cria card de estatística"""
        card = tk.Frame(parent, bg='#334155', relief=tk.FLAT)
        
        inner = tk.Frame(card, bg='#334155')
        inner.pack(fill=tk.BOTH, padx=20, pady=20)
        
        # Ícone
        tk.Label(
            inner,
            text=icon,
            font=('Segoe UI', 32),
            bg='#334155',
            fg=color
        ).pack()
        
        # Título
        tk.Label(
            inner,
            text=title,
            font=('Segoe UI', 10),
            bg='#334155',
            fg='#94a3b8'
        ).pack(pady=(5, 0))
        
        # Valor
        value_label = tk.Label(
            inner,
            text=value,
            font=('Segoe UI', 18, 'bold'),
            bg='#334155',
            fg='white'
        )
        value_label.pack(pady=(5, 0))
        
        # return both the outer card (to be placed in the grid) and the
        # label so callers can update the displayed value easily
        return card, value_label
    
    def carregar_empresas(self):
        """Carrega empresas"""
        try:
            empresas = self.db.query(Empresa).all()
            self.empresas_dict = {"Todas": None}
            
            for e in empresas:
                self.empresas_dict[f"{e.nome}"] = e
            
            self.combo_empresa['values'] = list(self.empresas_dict.keys())
            self.combo_empresa.set("Todas")
        except Exception as e:
            print(f"Erro ao carregar empresas: {e}")
    
    def filtrar_funcionarios(self):
        """Filtra funcionários por empresa"""
        try:
            empresa_key = self.combo_empresa.get()
            empresa_selecionada = self.empresas_dict.get(empresa_key)
            
            if empresa_selecionada:
                funcionarios = self.db.query(Funcionario).filter(
                    Funcionario.empresa_id == empresa_selecionada.id
                ).all()
            else:
                funcionarios = self.db.query(Funcionario).all()
            
            self.funcionarios_dict = {"Todos": None}
            
            for f in funcionarios:
                self.funcionarios_dict[f.nome] = f
            
            self.combo_funcionario['values'] = list(self.funcionarios_dict.keys())
            self.combo_funcionario.set("Todos")
        except Exception as e:
            print(f"Erro ao filtrar funcionários: {e}")
    
    def carregar_funcionarios(self):
        """Carrega funcionários"""
        try:
            funcionarios = self.db.query(Funcionario).all()
            self.funcionarios_dict = {"Todos": None}
            
            for f in funcionarios:
                self.funcionarios_dict[f.nome] = f
            
            self.combo_funcionario['values'] = list(self.funcionarios_dict.keys())
            self.combo_funcionario.set("Todos")
        except Exception as e:
            print(f"Erro ao carregar funcionários: {e}")
    
    def calcular_periodo(self):
        """Calcula período"""
        periodo = self.combo_periodo.get()
        hoje = datetime.now().date()
        
        if periodo == "Últimos 7 dias":
            data_inicio = hoje - timedelta(days=7)
            data_fim = hoje
        elif periodo == "Últimos 30 dias":
            data_inicio = hoje - timedelta(days=30)
            data_fim = hoje
        elif periodo == "Este mês":
            data_inicio = hoje.replace(day=1)
            data_fim = hoje
        elif periodo == "Mês passado":
            primeiro_dia_mes_atual = hoje.replace(day=1)
            data_fim = primeiro_dia_mes_atual - timedelta(days=1)
            data_inicio = data_fim.replace(day=1)
        else:
            data_inicio = hoje - timedelta(days=30)
            data_fim = hoje
        
        return data_inicio, data_fim
    
    def gerar_relatorio(self):
        """Gera relatório"""
        try:
            # Defensive: make sure the tree (table) exists before operating on it
            if not hasattr(self, 'tree') or self.tree is None:
                messagebox.showerror("Erro", "Tabela de detalhamento não está disponível no momento. Reabra a tela e tente novamente.")
                return

            for item in self.tree.get_children():
                self.tree.delete(item)
            
            data_inicio, data_fim = self.calcular_periodo()
            
            empresa_key = self.combo_empresa.get()
            empresa_selecionada = self.empresas_dict.get(empresa_key)
            
            func_key = self.combo_funcionario.get()
            func_selecionado = self.funcionarios_dict.get(func_key)
            
            # Build the query from the registros_jornada side so the join
            # relationship is explicit and SQLAlchemy can determine the left
            # side. We aggregate hours per funcionario and also bring the
            # empresa name.
            query = self.db.query(
                Funcionario.id,
                Funcionario.nome,
                Funcionario.cargo,
                Funcionario.valor_hora,
                Empresa.nome.label('empresa_nome'),
                func.coalesce(func.sum(RegistroJornada.horas_extras), 0).label('total_extras'),
                func.coalesce(func.sum(RegistroJornada.horas_faltantes), 0).label('total_faltantes')
            ).select_from(RegistroJornada).join(
                Funcionario, RegistroJornada.funcionario_id == Funcionario.id
            ).outerjoin(
                Empresa, Funcionario.empresa_id == Empresa.id
            ).filter(
                RegistroJornada.data.between(data_inicio, data_fim)
            )
            
            if empresa_selecionada:
                query = query.filter(Funcionario.empresa_id == empresa_selecionada.id)
            
            if func_selecionado:
                query = query.filter(Funcionario.id == func_selecionado.id)
            
            # Group by the selected non-aggregated columns so SQL engines
            # that require explicit grouping won't complain.
            query = query.group_by(
                Funcionario.id,
                Funcionario.nome,
                Funcionario.cargo,
                Funcionario.valor_hora,
                Empresa.nome
            )
            resultados = query.all()
            print(f"[relatorios] query returned {len(resultados)} result(s)")
            
            total_horas_extras = 0
            total_horas_faltantes = 0
            total_valor_extras = 0
            
            # Insert rows with alternating tags for visibility
            for idx, (func_id, nome, cargo, valor_hora, empresa_nome, h_extra, h_falta) in enumerate(resultados):
                print(f"[relatorios] row: id={func_id}, nome={nome}, extras={h_extra}, faltas={h_falta}")
                h_extra = h_extra or 0
                h_falta = h_falta or 0
                valor_extra = self.calculo_service.calcular_valor_horas_extras(h_extra, valor_hora)
                empresa_txt = empresa_nome or "Sem empresa"
                
                tag = 'even' if idx % 2 == 0 else 'odd'
                self.tree.insert("", tk.END, values=(
                    func_id,
                    nome,
                    empresa_txt,
                    cargo,
                    f"{h_extra:.2f}h",
                    f"{h_falta:.2f}h",
                    f"R$ {valor_extra:.2f}"
                ), tags=(tag,))
                
                total_horas_extras += h_extra
                total_horas_faltantes += h_falta
                total_valor_extras += valor_extra
            
            # Atualiza cards
            self.card_extras.config(text=f"{total_horas_extras:.2f}h")
            self.card_faltas.config(text=f"{total_horas_faltantes:.2f}h")
            self.card_valor.config(text=f"R$ {total_valor_extras:.2f}")
            
            if not resultados:
                messagebox.showinfo("Aviso", "Nenhum registro encontrado para o período.")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao gerar relatório:\n\n{str(e)}")


class RelatorioSaldoPopup:
    """Popup com resumo de saldos"""
    def __init__(self, parent):
        self.janela = tk.Toplevel(parent)
        self.janela.title("Relatório de Saldos")
        self.janela.geometry("1000x600")
        self.janela.configure(bg='#0f172a')
        self.db = get_db()
        
        self.setup_ui()
        self.carregar_dados()
    
    def setup_ui(self):
        """Configura interface"""
        # Header
        header = tk.Frame(self.janela, bg='#1e293b', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="📊 Relatório Consolidado - Extras e Faltas",
            font=('Segoe UI', 18, 'bold'),
            bg='#1e293b',
            fg='white'
        ).pack(pady=25)
        
        # Conteúdo
        content = tk.Frame(self.janela, bg='#0f172a')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Tabela
        table_frame = tk.Frame(content, bg='#1e293b')
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        table_inner = tk.Frame(table_frame, bg='#1e293b')
        table_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        style = ttk.Style()
        style.configure('Popup.Treeview',
            background='#1e293b',
            foreground='white',
            fieldbackground='#1e293b',
            rowheight=40
        )
        
        style.configure('Popup.Treeview.Heading',
            background='#334155',
            foreground='white',
            font=('Segoe UI', 10, 'bold')
        )
        
        columns = ("ID", "Funcionário", "Empresa", "H.Extra", "H.Falta", "Saldo")
        self.tree = ttk.Treeview(
            table_inner,
            columns=columns,
            show="headings",
            height=15,
            style='Popup.Treeview'
        )
        
        col_widths = [60, 200, 150, 100, 100, 320]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(table_inner, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botões
        btn_frame = tk.Frame(self.janela, bg='#0f172a')
        btn_frame.pack(pady=15)
        
        ModernButton(
            btn_frame,
            "🔄 Atualizar",
            self.carregar_dados,
            style='info'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="✖ Fechar",
            command=self.janela.destroy,
            font=('Segoe UI', 11, 'bold'),
            bg='#64748b',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            padx=30,
            pady=12
        ).pack(side=tk.LEFT, padx=5)
    
    def carregar_dados(self):
        """Carrega dados"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            query = text("""
                SELECT 
                    f.id,
                    f.nome,
                    COALESCE(e.nome, f.empresa, 'Sem Empresa') as empresa,
                    COALESCE(SUM(r.horas_extras), 0) as total_extras,
                    COALESCE(SUM(r.horas_faltantes), 0) as total_faltas
                FROM funcionarios f
                LEFT JOIN registros_jornada r ON f.id = r.funcionario_id
                LEFT JOIN empresas e ON f.empresa_id = e.id
                GROUP BY f.id, f.nome, empresa
                HAVING total_extras > 0 OR total_faltas > 0
                ORDER BY f.nome
            """)
            
            result = self.db.execute(query)
            registros = result.fetchall()
            
            if not registros:
                messagebox.showinfo("Aviso", "Nenhum funcionário com horas extras ou faltantes.")
                return
            
            for id_func, nome, empresa, total_extras, total_faltas in registros:
                total_extras = float(total_extras or 0)
                total_faltas = float(total_faltas or 0)
                
                if total_extras > total_faltas:
                    sobra = total_extras - total_faltas
                    mensagem = f"✅ Sobra {sobra:.1f}h de horas extras"
                elif total_faltas > total_extras:
                    falta = total_faltas - total_extras
                    mensagem = f"⚠️ Faltam {falta:.1f}h para compensar"
                else:
                    mensagem = "⚖️ Saldo zero (extras = faltas)"
                
                self.tree.insert("", tk.END, values=(
                    id_func,
                    nome,
                    empresa,
                    f"{total_extras:.1f}h",
                    f"{total_faltas:.1f}h",
                    mensagem
                ))
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar:\n{str(e)}")
