"""
app_jornada_adaptado.py
Sistema adaptado para trabalhar com o banco existente
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Time, ForeignKey, func, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# =============================================================================
# CONFIGURAÇÃO INICIAL
# =============================================================================

# Use o banco existente
DATABASE_URL = 'sqlite:///horas_extras.db'  # Seu banco atual

Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)

# =============================================================================
# VERIFICAR E ADAPTAR ESTRUTURA
# =============================================================================

def verificar_e_adicionar_coluna_empresa():
    """Adiciona coluna empresa se não existir"""
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    
    if 'funcionarios' in inspector.get_table_names():
        colunas = [col['name'] for col in inspector.get_columns('funcionarios')]
        
        if 'empresa' not in colunas:
            print("⚠️  Coluna 'empresa' não encontrada. Adicionando...")
            with engine.connect() as conn:
                try:
                    conn.execute(text("ALTER TABLE funcionarios ADD COLUMN empresa VARCHAR(200) DEFAULT 'Sem Empresa'"))
                    conn.commit()
                    print("✅ Coluna 'empresa' adicionada com sucesso!")
                    
                    # Atualiza registros existentes
                    conn.execute(text("UPDATE funcionarios SET empresa = 'Empresa Padrão' WHERE empresa IS NULL OR empresa = ''"))
                    conn.commit()
                    print("✅ Registros existentes atualizados!")
                except Exception as e:
                    print(f"❌ Erro ao adicionar coluna: {e}")
                    print("💡 A coluna 'empresa' pode já existir ou haver outro problema")
        else:
            print("✅ Coluna 'empresa' já existe!")

# Executa verificação
verificar_e_adicionar_coluna_empresa()

# =============================================================================
# MODELOS DO BANCO DE DADOS
# =============================================================================

class Funcionario(Base):
    __tablename__ = "funcionarios"
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    cargo = Column(String(100))
    empresa = Column(String(200), default='Empresa Padrão')
    carga_horaria_diaria = Column(Float, default=8.0)
    valor_hora = Column(Float, default=0.0)
    
    # Define como non-eager para evitar conflitos
    __mapper_args__ = {
        'confirm_deleted_rows': False,
    }

class RegistroJornada(Base):
    __tablename__ = "registros_jornada"
    
    id = Column(Integer, primary_key=True, index=True)
    funcionario_id = Column(Integer, ForeignKey('funcionarios.id', ondelete="CASCADE"), nullable=False)
    data = Column(Date, nullable=False)
    hora_entrada = Column(Time, nullable=False)
    hora_saida = Column(Time, nullable=False)
    intervalo = Column(Float, default=0.0)
    horas_trabalhadas = Column(Float, nullable=False)
    horas_extras = Column(Float, default=0.0)
    horas_faltantes = Column(Float, default=0.0)

# =============================================================================
# FUNÇÕES DE CÁLCULO
# =============================================================================

def calcular_horas_trabalhadas(hora_entrada, hora_saida, intervalo):
    """Calcula horas trabalhadas"""
    from datetime import datetime, timedelta
    
    dt_entrada = datetime.combine(datetime.today(), hora_entrada)
    dt_saida = datetime.combine(datetime.today(), hora_saida)
    
    if dt_saida < dt_entrada:
        dt_saida += timedelta(days=1)
    
    diferenca = dt_saida - dt_entrada
    horas_totais = diferenca.total_seconds() / 3600
    horas_trabalhadas = horas_totais - intervalo
    
    return round(horas_trabalhadas, 2)

def calcular_extras_faltas(horas_trabalhadas, carga_horaria_diaria):
    """Calcula horas extras e faltantes"""
    diferenca = horas_trabalhadas - carga_horaria_diaria
    
    if diferenca > 0:
        return round(diferenca, 2), 0.0
    else:
        return 0.0, round(abs(diferenca), 2)

# =============================================================================
# FUNÇÃO DE RELATÓRIO - ADAPTADA
# =============================================================================

def obter_relatorio_extras_faltas(session):
    """Gera relatório consolidado - ADAPTADO para usar SQL direto"""
    try:
        # Usa SQL direto para garantir compatibilidade
        query = text("""
            SELECT 
                f.id,
                f.nome,
                COALESCE(f.empresa, 'Sem Empresa') as empresa,
                COALESCE(SUM(r.horas_extras), 0) as total_extras,
                COALESCE(SUM(r.horas_faltantes), 0) as total_faltas
            FROM funcionarios f
            LEFT JOIN registros_jornada r ON f.id = r.funcionario_id
            GROUP BY f.id, f.nome, f.empresa
            HAVING total_extras > 0 OR total_faltas > 0
        """)
        
        result = session.execute(query)
        registros = result.fetchall()
        
        resultado_final = []

        for id_func, nome, empresa, total_extras, total_faltas in registros:
            total_extras = float(total_extras or 0)
            total_faltas = float(total_faltas or 0)

            if total_extras > total_faltas:
                sobra = total_extras - total_faltas
                mensagem = f"Sobra {round(sobra,1)}h de horas extras"
            elif total_faltas > total_extras:
                falta = total_faltas - total_extras
                mensagem = f"Faltam {round(falta,1)}h para compensar (horas faltantes)"
            else:
                mensagem = "Não há saldo. Extras e faltas se compensaram."

            resultado_final.append({
                "id": id_func,
                "funcionario": nome,
                "empresa": empresa,
                "total_extras": round(total_extras, 1),
                "total_faltas": round(total_faltas, 1),
                "saldo_msg": mensagem
            })

        return resultado_final
    
    except Exception as e:
        print(f"❌ Erro no relatório: {e}")
        import traceback
        traceback.print_exc()
        return []

# =============================================================================
# TELA SECUNDÁRIA - RELATÓRIO
# =============================================================================

class TelaRelatorioSaldo:
    def __init__(self, parent):
        self.janela = tk.Toplevel(parent)
        self.janela.title("Relatório de Extras/Faltas por Funcionário")
        self.janela.geometry("1000x600")
        self.session = Session()
        
        self.setup_ui()
        self.carregar_dados()
    
    def setup_ui(self):
        """Configura interface"""
        # Título
        title_frame = tk.Frame(self.janela, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="📊 Relatório Consolidado - Extras e Faltas",
            font=("Arial", 16, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack(pady=15)
        
        # Frame da tabela
        table_frame = tk.Frame(self.janela)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Treeview
        columns = ("ID", "Funcionário", "Empresa", "Total H.Extra", "Total H.Falta", "Saldo")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        
        col_widths = [60, 200, 150, 120, 120, 300]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=tk.CENTER if col == "ID" else tk.W)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botões
        btn_frame = tk.Frame(self.janela)
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="Atualizar Dados",
            command=self.carregar_dados,
            bg="#3498db",
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Fechar",
            command=self.janela.destroy,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
    
    def carregar_dados(self):
        """Carrega dados do relatório"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # Verifica se há registros
            total_reg = self.session.execute(text("SELECT COUNT(*) FROM registros_jornada")).scalar()
            
            if total_reg == 0:
                messagebox.showinfo(
                    "Aviso",
                    "Nenhum registro de jornada cadastrado!\n\n"
                    "Cadastre jornadas na tela principal primeiro."
                )
                return
            
            relatorio = obter_relatorio_extras_faltas(self.session)
            
            if not relatorio:
                messagebox.showinfo(
                    "Aviso",
                    "Nenhum funcionário com horas extras ou faltantes ainda."
                )
                return
            
            for registro in relatorio:
                self.tree.insert("", tk.END, values=(
                    registro["id"],
                    registro["funcionario"],
                    registro["empresa"],
                    f"{registro['total_extras']}h",
                    f"{registro['total_faltas']}h",
                    registro["saldo_msg"]
                ))
            
            print(f"✅ Relatório: {len(relatorio)} funcionários")
        
        except Exception as e:
            import traceback
            error = traceback.format_exc()
            messagebox.showerror("Erro", f"Erro ao carregar relatório:\n{str(e)}")
            print(f"❌ Erro:\n{error}")

# =============================================================================
# TELA PRINCIPAL
# =============================================================================

class TelaRegistroJornada:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Registro de Jornada")
        self.root.geometry("1200x700")
        self.session = Session()
        
        self.funcionarios_dict = {}
        
        self.setup_ui()
        self.carregar_funcionarios()
        self.carregar_registros()
    
    def setup_ui(self):
        """Configura interface principal"""
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="Sistema de Controle de Horas Extras",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack(pady=20)
        
        # Formulário
        form_frame = tk.LabelFrame(self.root, text="📝 Dados da Jornada", padx=20, pady=20, font=("Arial", 12, "bold"))
        form_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Funcionário
        tk.Label(form_frame, text="Funcionário:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=8)
        self.combo_funcionario = ttk.Combobox(form_frame, width=45, state="readonly", font=("Arial", 10))
        self.combo_funcionario.grid(row=0, column=1, pady=8, padx=10, sticky=tk.W)
        
        # Data
        tk.Label(form_frame, text="Data (DD/MM/AAAA):", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=8)
        self.entry_data = tk.Entry(form_frame, width=48, font=("Arial", 10))
        self.entry_data.grid(row=1, column=1, pady=8, padx=10, sticky=tk.W)
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        # Hora Entrada
        tk.Label(form_frame, text="Hora Entrada (HH:MM):", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, pady=8)
        self.entry_entrada = tk.Entry(form_frame, width=48, font=("Arial", 10))
        self.entry_entrada.grid(row=2, column=1, pady=8, padx=10, sticky=tk.W)
        
        # Hora Saída
        tk.Label(form_frame, text="Hora Saída (HH:MM):", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, pady=8)
        self.entry_saida = tk.Entry(form_frame, width=48, font=("Arial", 10))
        self.entry_saida.grid(row=3, column=1, pady=8, padx=10, sticky=tk.W)
        
        # Intervalo
        tk.Label(form_frame, text="Intervalo (horas):", font=("Arial", 10)).grid(row=4, column=0, sticky=tk.W, pady=8)
        self.entry_intervalo = tk.Entry(form_frame, width=48, font=("Arial", 10))
        self.entry_intervalo.grid(row=4, column=1, pady=8, padx=10, sticky=tk.W)
        self.entry_intervalo.insert(0, "1.0")
        
        # Botões
        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=15)
        
        tk.Button(
            btn_frame,
            text="💾 Salvar Registro",
            command=self.salvar_registro,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="📊 Resumo Extras/Faltas",
            command=self.abrir_relatorio,
            bg="#3498db",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🗑️ Limpar",
            command=self.limpar_campos,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        # Tabela
        table_frame = tk.LabelFrame(self.root, text="📋 Registros Recentes", padx=10, pady=10, font=("Arial", 12, "bold"))
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ("ID", "Funcionário", "Empresa", "Data", "Entrada", "Saída", "H.Trab", "H.Extra", "H.Falta")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        
        col_widths = [50, 150, 120, 90, 70, 70, 70, 70, 70]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Button(
            self.root,
            text="🗑️ Excluir Selecionado",
            command=self.excluir_registro,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        ).pack(pady=10)
    
    def carregar_funcionarios(self):
        """Carrega funcionários do banco EXISTENTE"""
        try:
            funcionarios = self.session.query(Funcionario).all()
            
            self.funcionarios_dict = {}
            lista_display = []
            
            for func in funcionarios:
                empresa = func.empresa if hasattr(func, 'empresa') and func.empresa else "Sem Empresa"
                display = f"{func.nome} - {empresa}"
                lista_display.append(display)
                self.funcionarios_dict[display] = func
            
            self.combo_funcionario['values'] = lista_display
            
            print(f"✅ {len(funcionarios)} funcionários carregados")
        
        except Exception as e:
            print(f"⚠️  Erro ao carregar funcionários: {e}")
            messagebox.showwarning("Aviso", f"Erro ao carregar funcionários:\n{str(e)}")
    
    def salvar_registro(self):
        """Salva registro usando ID EXISTENTE do funcionário"""
        try:
            funcionario_display = self.combo_funcionario.get()
            if not funcionario_display:
                messagebox.showwarning("Atenção", "Selecione um funcionário!")
                return
            
            funcionario = self.funcionarios_dict[funcionario_display]
            
            data_str = self.entry_data.get().strip()
            data = datetime.strptime(data_str, "%d/%m/%Y").date()
            
            entrada_str = self.entry_entrada.get().strip()
            saida_str = self.entry_saida.get().strip()
            hora_entrada = datetime.strptime(entrada_str, "%H:%M").time()
            hora_saida = datetime.strptime(saida_str, "%H:%M").time()
            
            intervalo = float(self.entry_intervalo.get().strip())
            
            horas_trabalhadas = calcular_horas_trabalhadas(hora_entrada, hora_saida, intervalo)
            horas_extras, horas_faltantes = calcular_extras_faltas(horas_trabalhadas, funcionario.carga_horaria_diaria)
            
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
            
            self.session.add(registro)
            self.session.commit()
            
            messagebox.showinfo(
                "Sucesso",
                f"Jornada registrada!\n\n"
                f"Funcionário: {funcionario.nome} (ID: {funcionario.id})\n"
                f"H.Trabalhadas: {horas_trabalhadas}h\n"
                f"H.Extras: {horas_extras}h\n"
                f"H.Faltantes: {horas_faltantes}h"
            )
            
            self.limpar_campos()
            self.carregar_registros()
            
            print(f"✅ Registro salvo - Funcionário ID: {funcionario.id}")
        
        except ValueError as e:
            messagebox.showerror("Erro", f"Formato inválido:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar:\n{str(e)}")
            self.session.rollback()
    
    def limpar_campos(self):
        """Limpa formulário"""
        self.combo_funcionario.set('')
        self.entry_data.delete(0, tk.END)
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.entry_entrada.delete(0, tk.END)
        self.entry_saida.delete(0, tk.END)
        self.entry_intervalo.delete(0, tk.END)
        self.entry_intervalo.insert(0, "1.0")
    
    def carregar_registros(self):
        """Carrega registros na tabela"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            query = text("""
                SELECT r.id, f.nome, COALESCE(f.empresa, 'Sem Empresa'), r.data, 
                       r.hora_entrada, r.hora_saida, r.horas_trabalhadas, 
                       r.horas_extras, r.horas_faltantes
                FROM registros_jornada r
                JOIN funcionarios f ON r.funcionario_id = f.id
                ORDER BY r.data DESC
                LIMIT 50
            """)
            
            result = self.session.execute(query)
            
            for row in result:
                self.tree.insert("", tk.END, values=(
                    row[0],  # id
                    row[1],  # nome
                    row[2],  # empresa
                    row[3].strftime('%d/%m/%Y') if hasattr(row[3], 'strftime') else row[3],
                    row[4].strftime('%H:%M') if hasattr(row[4], 'strftime') else row[4],
                    row[5].strftime('%H:%M') if hasattr(row[5], 'strftime') else row[5],
                    f"{row[6]:.1f}h",
                    f"{row[7]:.1f}h",
                    f"{row[8]:.1f}h"
                ))
        
        except Exception as e:
            print(f"⚠️  Erro ao carregar registros: {e}")
    
    def excluir_registro(self):
        """Exclui registro selecionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Atenção", "Selecione um registro!")
            return
        
        if messagebox.askyesno("Confirmar", "Deseja excluir este registro?"):
            item = self.tree.item(selection[0])
            reg_id = item['values'][0]
            
            try:
                self.session.execute(text("DELETE FROM registros_jornada WHERE id = :id"), {"id": reg_id})
                self.session.commit()
                messagebox.showinfo("Sucesso", "Registro excluído!")
                self.carregar_registros()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro:\n{str(e)}")
                self.session.rollback()
    
    def abrir_relatorio(self):
        """Abre relatório"""
        TelaRelatorioSaldo(self.root)

# =============================================================================
# MAIN
# =============================================================================

def main():
    """Execução principal"""
    print("🚀 Iniciando Sistema - Modo Adaptado")
    print("📦 Usando banco existente: horas_extras.db")
    
    root = tk.Tk()
    app = TelaRegistroJornada(root)
    root.mainloop()

if __name__ == "__main__":
    main()