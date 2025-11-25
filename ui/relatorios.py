"""
ui/relatorios.py
Interface para visualização de relatórios - VERSÃO COMPLETA ATUALIZADA
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from models.database import get_db
from models.funcionario import Funcionario
from models.empresa import Empresa
from models.registro_jornada import RegistroJornada
from services.calculo_service import CalculoService
from sqlalchemy import func

class RelatoriosUI:
    def __init__(self, parent):
        self.parent = parent
        self.db = get_db()
        self.calculo_service = CalculoService()
        
        self.setup_ui()
        self.carregar_funcionarios()
        self.carregar_empresas()
    
    def setup_ui(self):
        """Configura a interface"""
        # Título
        title_frame = tk.Frame(self.parent, bg="white")
        title_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            title_frame,
            text="📊 Relatórios e Estatísticas",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack()
        
        # Frame de filtros
        filter_frame = tk.LabelFrame(self.parent, text="Filtros", padx=20, pady=15)
        filter_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Empresa
        tk.Label(filter_frame, text="Empresa:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.combo_empresa = ttk.Combobox(filter_frame, width=35, state="readonly")
        self.combo_empresa.grid(row=0, column=1, pady=5, padx=10)
        self.combo_empresa.bind("<<ComboboxSelected>>", lambda e: self.filtrar_funcionarios())
        
        # Funcionário
        tk.Label(filter_frame, text="Funcionário:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.combo_funcionario = ttk.Combobox(filter_frame, width=35, state="readonly")
        self.combo_funcionario.grid(row=1, column=1, pady=5, padx=10)
        
        # Período
        tk.Label(filter_frame, text="Período:").grid(row=2, column=0, sticky=tk.W, pady=5)
        period_frame = tk.Frame(filter_frame)
        period_frame.grid(row=2, column=1, pady=5, padx=10, sticky=tk.W)
        
        self.combo_periodo = ttk.Combobox(
            period_frame,
            values=["Últimos 7 dias", "Últimos 30 dias", "Este mês", "Mês passado", "Personalizado"],
            width=20,
            state="readonly"
        )
        self.combo_periodo.set("Últimos 30 dias")
        self.combo_periodo.pack(side=tk.LEFT)
        
        # Botões
        btn_frame = tk.Frame(filter_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)
        
        tk.Button(
            btn_frame,
            text="📊 Gerar Relatório",
            command=self.gerar_relatorio,
            bg="#3498db",
            fg="white",
            padx=20,
            pady=5,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        # Frame de resumo
        self.summary_frame = tk.LabelFrame(self.parent, text="Resumo", padx=20, pady=15)
        self.summary_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.label_summary = tk.Label(
            self.summary_frame,
            text="Selecione os filtros e clique em 'Gerar Relatório'",
            font=("Arial", 11),
            fg="#7f8c8d",
            justify=tk.LEFT
        )
        self.label_summary.pack()
        
        # Frame de detalhes
        detail_frame = tk.LabelFrame(self.parent, text="Detalhamento por Funcionário", padx=10, pady=10)
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Treeview
        columns = ("ID", "Funcionário", "Empresa", "Cargo", "H.Extra", "H.Falta", "Valor H.Extra")
        self.tree = ttk.Treeview(detail_frame, columns=columns, show="headings", height=10)
        
        col_widths = [40, 150, 150, 100, 80, 80, 100]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def carregar_empresas(self):
        """Carrega lista de empresas"""
        try:
            empresas = self.db.query(Empresa).all()
            self.empresas_dict = {"Todas": None}
            
            for e in empresas:
                self.empresas_dict[f"{e.nome} (ID: {e.id})"] = e
            
            self.combo_empresa['values'] = list(self.empresas_dict.keys())
            self.combo_empresa.set("Todas")
        except Exception as e:
            print(f"Erro ao carregar empresas: {e}")
    
    def filtrar_funcionarios(self):
        """Filtra funcionários pela empresa selecionada"""
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
                empresa_nome = f.empresa.nome if f.empresa else "Sem empresa"
                self.funcionarios_dict[f"{f.nome} (ID: {f.id}) - {empresa_nome}"] = f
            
            self.combo_funcionario['values'] = list(self.funcionarios_dict.keys())
            self.combo_funcionario.set("Todos")
        except Exception as e:
            print(f"Erro ao filtrar funcionários: {e}")
    
    def carregar_funcionarios(self):
        """Carrega lista de funcionários"""
        try:
            funcionarios = self.db.query(Funcionario).all()
            self.funcionarios_dict = {"Todos": None}
            
            for f in funcionarios:
                empresa_nome = f.empresa.nome if f.empresa else "Sem empresa"
                self.funcionarios_dict[f"{f.nome} (ID: {f.id}) - {empresa_nome}"] = f
            
            self.combo_funcionario['values'] = list(self.funcionarios_dict.keys())
            self.combo_funcionario.set("Todos")
        except Exception as e:
            print(f"Erro ao carregar funcionários: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar funcionários: {str(e)}")
    
    def calcular_periodo(self):
        """Calcula data inicial e final baseado no período selecionado"""
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
        """Gera relatório com base nos filtros"""
        try:
            # Limpa treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Calcula período
            data_inicio, data_fim = self.calcular_periodo()
            
            # Filtro de empresa
            empresa_key = self.combo_empresa.get()
            empresa_selecionada = self.empresas_dict.get(empresa_key)
            
            # Filtro de funcionário
            func_key = self.combo_funcionario.get()
            if not func_key:
                messagebox.showwarning("Atenção", "Selecione um funcionário!")
                return
            
            func_selecionado = self.funcionarios_dict.get(func_key)
            
            # Query base
            query = self.db.query(
                Funcionario.id,
                Funcionario.nome,
                Funcionario.cargo,
                Funcionario.valor_hora,
                Empresa.nome.label('empresa_nome'),
                func.sum(RegistroJornada.horas_extras).label('total_extras'),
                func.sum(RegistroJornada.horas_faltantes).label('total_faltantes')
            ).join(RegistroJornada).outerjoin(Empresa, Funcionario.empresa_id == Empresa.id).filter(
                RegistroJornada.data.between(data_inicio, data_fim)
            )
            
            # Aplica filtro de empresa se necessário
            if empresa_selecionada:
                query = query.filter(Funcionario.empresa_id == empresa_selecionada.id)
            
            # Aplica filtro de funcionário se necessário
            if func_selecionado:
                query = query.filter(Funcionario.id == func_selecionado.id)
            
            query = query.group_by(Funcionario.id)
            
            resultados = query.all()
            
            # Totalizadores
            total_horas_extras = 0
            total_horas_faltantes = 0
            total_valor_extras = 0
            
            # Preenche treeview
            for func_id, nome, cargo, valor_hora, empresa_nome, h_extra, h_falta in resultados:
                h_extra = h_extra or 0
                h_falta = h_falta or 0
                valor_extra = self.calculo_service.calcular_valor_horas_extras(h_extra, valor_hora)
                empresa_txt = empresa_nome or "Sem empresa"
                
                self.tree.insert("", tk.END, values=(
                    func_id,
                    nome,
                    empresa_txt,
                    cargo,
                    f"{h_extra:.2f}h",
                    f"{h_falta:.2f}h",
                    f"R$ {valor_extra:.2f}"
                ))
                
                total_horas_extras += h_extra
                total_horas_faltantes += h_falta
                total_valor_extras += valor_extra
            
            # Atualiza resumo
            summary_text = f"""📊 RESUMO DO PERÍODO: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}

⏰ Total de Horas Extras: {total_horas_extras:.2f}h
⚠️ Total de Horas Faltantes: {total_horas_faltantes:.2f}h
💰 Valor Total de Horas Extras: R$ {total_valor_extras:.2f}
👥 Funcionários no período: {len(resultados)}"""
            
            self.label_summary.config(text=summary_text, fg="#2c3e50")
            
            if not resultados:
                messagebox.showinfo("Aviso", "Nenhum registro encontrado para o período selecionado.")
            else:
                print(f"✅ Relatório gerado: {len(resultados)} funcionários")
        
        except Exception as e:
            print(f"❌ Erro ao gerar relatório: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao gerar relatório:\n\n{str(e)}")