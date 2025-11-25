"""
ui/registro_jornada.py
Interface para registro de jornadas de trabalho - VERSÃO INTEGRADA
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from sqlalchemy import text
from models.database import get_db

class RegistroJornadaUI:
    def __init__(self, parent):
        self.parent = parent
        self.db = get_db()
        self.funcionarios_dict = {}
        
        # Verifica e adiciona coluna empresa se necessário
        self._verificar_estrutura_banco()
        
        self.setup_ui()
        self.carregar_funcionarios()
        self.carregar_registros()
    
    def _verificar_estrutura_banco(self):
        """Verifica e adapta estrutura do banco se necessário"""
        try:
            from sqlalchemy import inspect
            from models.database import engine
            
            inspector = inspect(engine)
            
            if 'funcionarios' in inspector.get_table_names():
                colunas = [col['name'] for col in inspector.get_columns('funcionarios')]
                
                # Verifica se coluna empresa existe
                if 'empresa' not in colunas and 'empresa_id' in colunas:
                    print("✅ Banco usa empresa_id (estrutura nova)")
                elif 'empresa' not in colunas and 'empresa_id' not in colunas:
                    print("⚠️ Adicionando suporte a empresa...")
                    try:
                        with engine.connect() as conn:
                            conn.execute(text("ALTER TABLE funcionarios ADD COLUMN empresa VARCHAR(200) DEFAULT 'Sem Empresa'"))
                            conn.commit()
                            print("✅ Coluna empresa adicionada")
                    except Exception as e:
                        print(f"ℹ️ Coluna empresa já pode existir: {e}")
        except Exception as e:
            print(f"⚠️ Erro ao verificar estrutura: {e}")
    
    def setup_ui(self):
        """Configura a interface"""
        # Título
        title_frame = tk.Frame(self.parent, bg="white")
        title_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            title_frame,
            text="Registro de Jornada de Trabalho",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack()
        
        # Frame de formulário
        form_frame = tk.LabelFrame(self.parent, text="📝 Dados da Jornada", padx=20, pady=20)
        form_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Funcionário
        tk.Label(form_frame, text="Funcionário:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.combo_funcionario = ttk.Combobox(form_frame, width=37, state="readonly")
        self.combo_funcionario.grid(row=0, column=1, pady=5, padx=10)
        
        # Data
        tk.Label(form_frame, text="Data (DD/MM/AAAA):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_data = tk.Entry(form_frame, width=40)
        self.entry_data.grid(row=1, column=1, pady=5, padx=10)
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        # Hora Entrada
        tk.Label(form_frame, text="Hora Entrada (HH:MM):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_entrada = tk.Entry(form_frame, width=40)
        self.entry_entrada.grid(row=2, column=1, pady=5, padx=10)
        
        # Hora Saída
        tk.Label(form_frame, text="Hora Saída (HH:MM):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.entry_saida = tk.Entry(form_frame, width=40)
        self.entry_saida.grid(row=3, column=1, pady=5, padx=10)
        
        # Intervalo
        tk.Label(form_frame, text="Intervalo (horas):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.entry_intervalo = tk.Entry(form_frame, width=40)
        self.entry_intervalo.grid(row=4, column=1, pady=5, padx=10)
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
            padx=20,
            pady=5,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="📊 Resumo Extras/Faltas",
            command=self.abrir_relatorio,
            bg="#3498db",
            fg="white",
            padx=20,
            pady=5,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🗑️ Limpar",
            command=self.limpar_campos,
            bg="#95a5a6",
            fg="white",
            padx=20,
            pady=5,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        # Frame de resultado
        result_frame = tk.LabelFrame(self.parent, text="Resultado do Cálculo", padx=20, pady=15)
        result_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.label_result = tk.Label(
            result_frame,
            text="Preencha os dados e clique em 'Salvar Registro'",
            font=("Arial", 11),
            fg="#7f8c8d"
        )
        self.label_result.pack()
        
        # Lista de registros
        list_frame = tk.LabelFrame(self.parent, text="📋 Registros Recentes", padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Treeview
        columns = ("ID", "Funcionário", "Empresa", "Data", "Entrada", "Saída", "H.Trab", "H.Extra", "H.Falta")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        col_widths = [40, 150, 120, 80, 70, 70, 70, 70, 70]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botão excluir
        tk.Button(
            self.parent,
            text="🗑️ Excluir Registro Selecionado",
            command=self.excluir_registro,
            bg="#e74c3c",
            fg="white",
            padx=15,
            pady=5
        ).pack(pady=10)
    
    def carregar_funcionarios(self):
        """Carrega lista de funcionários"""
        try:
            from models.funcionario import Funcionario
            funcionarios = self.db.query(Funcionario).all()
            
            self.funcionarios_dict = {}
            lista_display = []
            
            for func in funcionarios:
                # Tenta pegar nome da empresa de diferentes formas
                try:
                    if hasattr(func, 'empresa') and func.empresa:
                        empresa_nome = func.empresa.nome if hasattr(func.empresa, 'nome') else str(func.empresa)
                    else:
                        empresa_nome = "Sem Empresa"
                except:
                    empresa_nome = "Sem Empresa"
                
                display = f"{func.nome} - {empresa_nome}"
                lista_display.append(display)
                self.funcionarios_dict[display] = func
            
            self.combo_funcionario['values'] = lista_display
            print(f"✅ {len(funcionarios)} funcionários carregados")
            
        except Exception as e:
            print(f"⚠️ Erro ao carregar funcionários: {e}")
            messagebox.showwarning("Aviso", f"Erro ao carregar funcionários:\n{str(e)}")
    
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
        """Calcula horas extras e faltantes"""
        diferenca = horas_trabalhadas - carga_horaria_diaria
        
        if diferenca > 0:
            return round(diferenca, 2), 0.0
        else:
            return 0.0, round(abs(diferenca), 2)
    
    def salvar_registro(self):
        """Salva registro de jornada"""
        try:
            from models.registro_jornada import RegistroJornada
            
            # Validações
            if not self.combo_funcionario.get():
                messagebox.showwarning("Atenção", "Selecione um funcionário!")
                return
            
            funcionario = self.funcionarios_dict[self.combo_funcionario.get()]
            
            # Converte data
            data_str = self.entry_data.get().strip()
            data = datetime.strptime(data_str, "%d/%m/%Y").date()
            
            # ⚠️ VERIFICA SE JÁ EXISTE REGISTRO PARA ESTE FUNCIONÁRIO NESTA DATA
            registro_existente = self.db.query(RegistroJornada).filter(
                RegistroJornada.funcionario_id == funcionario.id,
                RegistroJornada.data == data
            ).first()
            
            if registro_existente:
                resposta = messagebox.askyesno(
                    "Registro Duplicado",
                    f"⚠️ Já existe um registro para {funcionario.nome} em {data_str}!\n\n"
                    f"Registro existente:\n"
                    f"• Entrada: {registro_existente.hora_entrada.strftime('%H:%M')}\n"
                    f"• Saída: {registro_existente.hora_saida.strftime('%H:%M')}\n"
                    f"• Horas trabalhadas: {registro_existente.horas_trabalhadas:.2f}h\n\n"
                    f"Deseja SUBSTITUIR o registro anterior pelo novo?"
                )
                
                if not resposta:
                    return
                
                # Remove o registro antigo
                self.db.delete(registro_existente)
                self.db.commit()
                print(f"⚠️ Registro anterior excluído (ID: {registro_existente.id})")
            
            # Converte horários
            entrada_str = self.entry_entrada.get().strip()
            saida_str = self.entry_saida.get().strip()
            hora_entrada = datetime.strptime(entrada_str, "%H:%M").time()
            hora_saida = datetime.strptime(saida_str, "%H:%M").time()
            
            intervalo = float(self.entry_intervalo.get().strip())
            
            # Calcula jornada
            horas_trabalhadas = self.calcular_horas_trabalhadas(hora_entrada, hora_saida, intervalo)
            horas_extras, horas_faltantes = self.calcular_extras_faltas(
                horas_trabalhadas, 
                funcionario.carga_horaria_diaria
            )
            
            # Cria registro
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
            
            # Mostra resultado
            resultado = f"""✅ Jornada registrada com sucesso!

📊 Horas Trabalhadas: {horas_trabalhadas:.2f}h
⏰ Horas Extras: {horas_extras:.2f}h
⚠️ Horas Faltantes: {horas_faltantes:.2f}h"""
            
            self.label_result.config(text=resultado, fg="#27ae60")
            
            messagebox.showinfo("Sucesso", f"Jornada registrada!\n\nFuncionário: {funcionario.nome}")
            
            self.limpar_campos()
            self.carregar_registros()
            
            print(f"✅ Registro salvo - Funcionário ID: {funcionario.id}")
            
        except ValueError as e:
            messagebox.showerror("Erro", "Formato de data/hora inválido!\n\nUse:\nData: DD/MM/AAAA\nHora: HH:MM")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar:\n{str(e)}")
            self.db.rollback()
    
    def limpar_campos(self):
        """Limpa os campos do formulário"""
        self.combo_funcionario.set('')
        self.entry_data.delete(0, tk.END)
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.entry_entrada.delete(0, tk.END)
        self.entry_saida.delete(0, tk.END)
        self.entry_intervalo.delete(0, tk.END)
        self.entry_intervalo.insert(0, "1.0")
        self.label_result.config(
            text="Preencha os dados e clique em 'Salvar Registro'",
            fg="#7f8c8d"
        )
    
    def carregar_registros(self):
        """Carrega registros no Treeview - SEM DUPLICATAS"""
        # Limpa treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # Query que pega apenas o registro mais recente de cada funcionário por dia
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
            
            for row in result:
                # Formata valores
                data_fmt = row[3].strftime('%d/%m/%Y') if hasattr(row[3], 'strftime') else str(row[3])
                entrada_fmt = row[4].strftime('%H:%M') if hasattr(row[4], 'strftime') else str(row[4])
                saida_fmt = row[5].strftime('%H:%M') if hasattr(row[5], 'strftime') else str(row[5])
                
                self.tree.insert("", tk.END, values=(
                    row[0],  # id
                    row[1],  # nome
                    row[2],  # empresa
                    data_fmt,
                    entrada_fmt,
                    saida_fmt,
                    f"{row[6]:.1f}h",
                    f"{row[7]:.1f}h",
                    f"{row[8]:.1f}h"
                ))
            
        except Exception as e:
            print(f"⚠️ Erro ao carregar registros: {e}")
            import traceback
            traceback.print_exc()
    
    def excluir_registro(self):
        """Exclui registro selecionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Atenção", "Selecione um registro!")
            return
        
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este registro?"):
            item = self.tree.item(selection[0])
            reg_id = item['values'][0]
            
            try:
                from models.registro_jornada import RegistroJornada
                
                reg = self.db.query(RegistroJornada).filter(
                    RegistroJornada.id == reg_id
                ).first()
                
                self.db.delete(reg)
                self.db.commit()
                
                messagebox.showinfo("Sucesso", "Registro excluído!")
                self.carregar_registros()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir:\n{str(e)}")
                self.db.rollback()
    
    def abrir_relatorio(self):
        """Abre relatório consolidado em janela popup"""
        RelatorioSaldoPopup(self.parent)


class RelatorioSaldoPopup:
    """Janela popup com relatório consolidado de extras/faltas"""
    
    def __init__(self, parent):
        self.janela = tk.Toplevel(parent)
        self.janela.title("Relatório Consolidado - Extras e Faltas")
        self.janela.geometry("1000x600")
        self.db = get_db()
        
        self.setup_ui()
        self.carregar_dados()
    
    def setup_ui(self):
        """Configura interface do relatório"""
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
            text="🔄 Atualizar Dados",
            command=self.carregar_dados,
            bg="#3498db",
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="❌ Fechar",
            command=self.janela.destroy,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
    
    def carregar_dados(self):
        """Carrega dados do relatório consolidado"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # Verifica se há registros
            total_reg = self.db.execute(text("SELECT COUNT(*) FROM registros_jornada")).scalar()
            
            if total_reg == 0:
                messagebox.showinfo(
                    "Aviso",
                    "Nenhum registro de jornada cadastrado!\n\n"
                    "Cadastre jornadas primeiro."
                )
                return
            
            # Query consolidada
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
                messagebox.showinfo(
                    "Aviso",
                    "Nenhum funcionário com horas extras ou faltantes ainda."
                )
                return
            
            # Preenche tabela
            for id_func, nome, empresa, total_extras, total_faltas in registros:
                total_extras = float(total_extras or 0)
                total_faltas = float(total_faltas or 0)
                
                # Calcula saldo
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
            
            print(f"✅ Relatório: {len(registros)} funcionários")
            
        except Exception as e:
            import traceback
            error = traceback.format_exc()
            messagebox.showerror("Erro", f"Erro ao carregar relatório:\n{str(e)}")
            print(f"❌ Erro:\n{error}")