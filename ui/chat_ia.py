"""
ui/chat_ia.py
Interface de chat com IA para análise de dados - CORRIGIDO
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, timedelta
from models.database import get_db
from models.funcionario import Funcionario
from models.empresa import Empresa
from models.registro_jornada import RegistroJornada
from sqlalchemy import func
import json

class ChatIAUI:
    def __init__(self, parent):
        self.parent = parent
        self.db = get_db()
        
        # Tenta importar IA
        try:
            from services.ia_service import IAService
            self.ia_service = IAService()
            self.ia_disponivel = self.ia_service.habilitado
        except Exception as e:
            print(f"⚠️ IA Service não disponível: {e}")
            self.ia_service = None
            self.ia_disponivel = False
        
        self.historico_conversa = []
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface"""
        # Título
        title_frame = tk.Frame(self.parent, bg="white")
        title_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            title_frame,
            text="🤖 Assistente IA - Análise de Dados",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack()
        
        if not self.ia_disponivel:
            tk.Label(
                title_frame,
                text="⚠️ IA não configurada. Configure GEMINI_API_KEY no arquivo .env",
                font=("Arial", 10),
                bg="white",
                fg="#e74c3c"
            ).pack()
        
        # Frame de chat
        chat_frame = tk.LabelFrame(self.parent, text="Conversa", padx=10, pady=10)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Área de mensagens
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg="#f8f9fa",
            state=tk.DISABLED,
            height=20
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Configurar tags de formatação
        self.chat_display.tag_config("user", foreground="#2c3e50", font=("Arial", 10, "bold"))
        self.chat_display.tag_config("assistant", foreground="#27ae60", font=("Arial", 10, "bold"))
        self.chat_display.tag_config("system", foreground="#7f8c8d", font=("Arial", 9, "italic"))
        
        # Frame de entrada
        input_frame = tk.Frame(chat_frame)
        input_frame.pack(fill=tk.X)
        
        self.entry_mensagem = tk.Entry(input_frame, font=("Arial", 11))
        self.entry_mensagem.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.entry_mensagem.bind("<Return>", lambda e: self.enviar_mensagem())
        
        tk.Button(
            input_frame,
            text="Enviar",
            command=self.enviar_mensagem,
            bg="#3498db",
            fg="white",
            padx=20,
            pady=5,
            cursor="hand2"
        ).pack(side=tk.LEFT)
        
        # Frame de sugestões
        suggestions_frame = tk.LabelFrame(self.parent, text="Perguntas Sugeridas", padx=10, pady=10)
        suggestions_frame.pack(fill=tk.X, padx=20, pady=10)
        
        sugestoes = [
            "Quais empresas estão cadastradas?",
            "Mostre os funcionários da empresa X",
            "Qual funcionário tem mais horas extras?",
            "Analise as horas extras do último mês",
            "Quais funcionários têm horas faltantes?",
            "Mostre o total de horas extras por empresa"
        ]
        
        for i, sugestao in enumerate(sugestoes):
            btn = tk.Button(
                suggestions_frame,
                text=sugestao,
                command=lambda s=sugestao: self.usar_sugestao(s),
                bg="#ecf0f1",
                fg="#2c3e50",
                cursor="hand2",
                relief=tk.FLAT,
                padx=10,
                pady=5
            )
            row = i // 3
            col = i % 3
            btn.grid(row=row, column=col, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # Configura colunas para expansão uniforme
        for col in range(3):
            suggestions_frame.columnconfigure(col, weight=1)
        
        # Mensagem inicial
        self.adicionar_mensagem_sistema(
            "Olá! Sou seu assistente de análise de dados. Pergunte-me sobre:\n"
            "• Empresas cadastradas\n"
            "• Funcionários e seus dados\n"
            "• Horas extras e faltantes\n"
            "• Análises e estatísticas\n\n"
            "Digite sua pergunta abaixo ou clique em uma sugestão!"
        )
    
    def usar_sugestao(self, sugestao):
        """Usa uma sugestão como mensagem"""
        self.entry_mensagem.delete(0, tk.END)
        self.entry_mensagem.insert(0, sugestao)
        self.enviar_mensagem()
    
    def adicionar_mensagem_sistema(self, texto):
        """Adiciona mensagem do sistema"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "ℹ️ Sistema: ", "system")
        self.chat_display.insert(tk.END, f"{texto}\n\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def adicionar_mensagem_usuario(self, texto):
        """Adiciona mensagem do usuário"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "👤 Você: ", "user")
        self.chat_display.insert(tk.END, f"{texto}\n\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def adicionar_mensagem_assistente(self, texto):
        """Adiciona mensagem da IA"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "🤖 Assistente: ", "assistant")
        self.chat_display.insert(tk.END, f"{texto}\n\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def enviar_mensagem(self):
        """Processa e envia mensagem"""
        mensagem = self.entry_mensagem.get().strip()
        if not mensagem:
            return
        
        self.entry_mensagem.delete(0, tk.END)
        self.adicionar_mensagem_usuario(mensagem)
        
        if not self.ia_disponivel:
            # Modo sem IA - respostas baseadas em regras
            resposta = self.processar_sem_ia(mensagem)
        else:
            # Modo com IA
            resposta = self.processar_com_ia(mensagem)
        
        self.adicionar_mensagem_assistente(resposta)
    
    def processar_sem_ia(self, mensagem):
        """Processa mensagem sem IA (regras simples)"""
        msg_lower = mensagem.lower()
        
        try:
            if "empresa" in msg_lower and ("quais" in msg_lower or "mostre" in msg_lower):
                empresas = self.db.query(Empresa).all()
                if empresas:
                    resp = "📊 Empresas cadastradas:\n\n"
                    for emp in empresas:
                        num_func = self.db.query(Funcionario).filter(
                            Funcionario.empresa_id == emp.id
                        ).count()
                        resp += f"• {emp.nome} (ID: {emp.id})\n"
                        resp += f"  CNPJ: {emp.cnpj}\n"
                        resp += f"  Funcionários: {num_func}\n\n"
                    return resp
                else:
                    return "Nenhuma empresa cadastrada ainda."
            
            elif "funcionário" in msg_lower or "funcionario" in msg_lower:
                funcionarios = self.db.query(Funcionario).all()
                if funcionarios:
                    resp = "👥 Funcionários cadastrados:\n\n"
                    for func in funcionarios:
                        try:
                            empresa = func.empresa.nome if func.empresa else "Sem empresa"
                        except:
                            empresa = "Sem empresa"
                        resp += f"• {func.nome} (ID: {func.id})\n"
                        resp += f"  Cargo: {func.cargo}\n"
                        resp += f"  Empresa: {empresa}\n"
                        resp += f"  Carga horária: {func.carga_horaria_diaria}h\n\n"
                    return resp
                else:
                    return "Nenhum funcionário cadastrado ainda."
            
            elif "hora" in msg_lower and "extra" in msg_lower:
                data_inicio = datetime.now().date() - timedelta(days=30)
                data_fim = datetime.now().date()
                
                # Query corrigida - usando select_from explicitamente
                resultados = self.db.query(
                    Funcionario.id,
                    Funcionario.nome,
                    Empresa.nome.label('empresa_nome'),
                    func.sum(RegistroJornada.horas_extras).label('total_extras')
                ).select_from(Funcionario).join(
                    RegistroJornada, RegistroJornada.funcionario_id == Funcionario.id
                ).outerjoin(
                    Empresa, Funcionario.empresa_id == Empresa.id
                ).filter(
                    RegistroJornada.data.between(data_inicio, data_fim)
                ).group_by(
                    Funcionario.id, Funcionario.nome, Empresa.nome
                ).order_by(
                    func.sum(RegistroJornada.horas_extras).desc()
                ).all()
                
                if resultados:
                    resp = f"⏰ Horas extras (últimos 30 dias):\n\n"
                    for func_id, nome, empresa, total in resultados:
                        empresa_txt = empresa or "Sem empresa"
                        resp += f"• {nome} (ID: {func_id})\n"
                        resp += f"  Empresa: {empresa_txt}\n"
                        resp += f"  Horas extras: {total:.2f}h\n\n"
                    return resp
                else:
                    return "Nenhum registro de horas extras nos últimos 30 dias."
            
            else:
                return (
                    "Desculpe, não entendi sua pergunta. Tente perguntar sobre:\n"
                    "• 'Quais empresas estão cadastradas?'\n"
                    "• 'Mostre os funcionários'\n"
                    "• 'Análise de horas extras'\n"
                    "\nOu configure a IA para respostas mais inteligentes!"
                )
        
        except Exception as e:
            print(f"❌ Erro ao processar: {e}")
            import traceback
            traceback.print_exc()
            return f"Erro ao processar: {str(e)}"
    
    def processar_com_ia(self, mensagem):
        """Processa mensagem com IA"""
        try:
            # Coleta contexto dos dados
            contexto = self.coletar_contexto()
            
            # Adiciona ao histórico
            self.historico_conversa.append({
                'role': 'user',
                'content': mensagem
            })
            
            # Monta prompt com contexto
            prompt_completo = f"""
Você é um assistente especializado em análise de dados de RH e gestão de horas.

DADOS DISPONÍVEIS:
{json.dumps(contexto, indent=2, ensure_ascii=False)}

HISTÓRICO DA CONVERSA:
{json.dumps(self.historico_conversa[-5:], indent=2, ensure_ascii=False)}

PERGUNTA DO USUÁRIO: {mensagem}

Responda de forma clara, objetiva e útil. Se precisar de dados que não estão disponíveis, sugira como o usuário pode obtê-los.
"""
            
            resposta = self.ia_service.responder_consulta(prompt_completo)
            
            # Adiciona resposta ao histórico
            self.historico_conversa.append({
                'role': 'assistant',
                'content': resposta
            })
            
            return resposta
            
        except Exception as e:
            print(f"❌ Erro ao processar com IA: {e}")
            import traceback
            traceback.print_exc()
            return f"Erro ao processar com IA: {str(e)}"
    
    def coletar_contexto(self):
        """Coleta dados do sistema para contexto"""
        try:
            # Empresas
            empresas = self.db.query(Empresa).all()
            empresas_data = [
                {
                    'id': e.id,
                    'nome': e.nome,
                    'cnpj': e.cnpj
                } for e in empresas
            ]
            
            # Funcionários
            funcionarios = self.db.query(Funcionario).all()
            funcionarios_data = [
                {
                    'id': f.id,
                    'nome': f.nome,
                    'cargo': f.cargo,
                    'empresa_id': f.empresa_id,
                    'empresa_nome': f.empresa.nome if f.empresa else None,
                    'carga_horaria': f.carga_horaria_diaria
                } for f in funcionarios
            ]
            
            # Resumo de horas extras (últimos 30 dias) - Query corrigida
            data_inicio = datetime.now().date() - timedelta(days=30)
            data_fim = datetime.now().date()
            
            registros_resumo = self.db.query(
                Funcionario.id,
                Funcionario.nome,
                func.sum(RegistroJornada.horas_extras).label('total_extras'),
                func.sum(RegistroJornada.horas_faltantes).label('total_faltantes'),
                func.count(RegistroJornada.id).label('num_registros')
            ).select_from(Funcionario).join(
                RegistroJornada, RegistroJornada.funcionario_id == Funcionario.id
            ).filter(
                RegistroJornada.data.between(data_inicio, data_fim)
            ).group_by(
                Funcionario.id, Funcionario.nome
            ).all()
            
            registros_data = [
                {
                    'funcionario_id': r[0],
                    'funcionario_nome': r[1],
                    'horas_extras_total': float(r[2] or 0),
                    'horas_faltantes_total': float(r[3] or 0),
                    'num_registros': r[4]
                } for r in registros_resumo
            ]
            
            return {
                'empresas': empresas_data,
                'funcionarios': funcionarios_data,
                'resumo_ultimos_30_dias': registros_data,
                'data_hoje': datetime.now().strftime('%d/%m/%Y')
            }
        
        except Exception as e:
            print(f"Erro ao coletar contexto: {e}")
            import traceback
            traceback.print_exc()
            return {}