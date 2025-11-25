"""
ui/chat_ia_modern.py
Interface MODERNA para chat com IA
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
import os

class ModernButton(tk.Button):
    """Botão moderno"""
    def __init__(self, parent, text, command, style='primary', **kwargs):
        styles = {
            'primary': {'bg': '#6366f1', 'hover': '#4f46e5'},
            'secondary': {'bg': '#64748b', 'hover': '#475569'},
            'success': {'bg': '#10b981', 'hover': '#059669'}
        }
        
        self.style_config = styles.get(style, styles['primary'])
        
        super().__init__(
            parent,
            text=text,
            command=command,
            font=('Segoe UI', 10, 'bold'),
            bg=self.style_config['bg'],
            fg='white',
            activebackground=self.style_config['hover'],
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            borderwidth=0,
            padx=15,
            pady=8,
            **kwargs
        )
        
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
    
    def on_enter(self, e):
        self.config(bg=self.style_config['hover'])
    
    def on_leave(self, e):
        self.config(bg=self.style_config['bg'])

class ChatIAModern:
    def __init__(self, parent):
        self.parent = parent
        self.parent.configure(bg='#0f172a')
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
        """Configura interface"""
        
        # Header com status
        header = tk.Frame(self.parent, bg='#1e293b')
        header.pack(fill=tk.X, pady=(0, 15))
        
        header_inner = tk.Frame(header, bg='#1e293b')
        header_inner.pack(fill=tk.X, padx=30, pady=20)
        
        # Título e status
        title_frame = tk.Frame(header_inner, bg='#1e293b')
        title_frame.pack(fill=tk.X)
        
        tk.Label(
            title_frame,
            text="🤖 Assistente IA",
            font=('Segoe UI', 16, 'bold'),
            bg='#1e293b',
            fg='white'
        ).pack(side=tk.LEFT)
        
        # Status badge
        status_frame = tk.Frame(title_frame, bg='#1e293b')
        status_frame.pack(side=tk.RIGHT)
        
        if self.ia_disponivel:
            status_color = '#10b981'
            status_text = "✓ IA Ativa"
        else:
            status_color = '#ef4444'
            status_text = "⚠ IA Desativada"
        
        tk.Label(
            status_frame,
            text=status_text,
            font=('Segoe UI', 9, 'bold'),
            bg=status_color,
            fg='white',
            padx=12,
            pady=6
        ).pack()
        
        if not self.ia_disponivel:
            tk.Label(
                header_inner,
                text="Configure GEMINI_API_KEY no arquivo .env para habilitar IA",
                font=('Segoe UI', 9),
                bg='#1e293b',
                fg='#94a3b8'
            ).pack(anchor='w', pady=(10, 0))
        
        # Card do chat
        chat_card = tk.Frame(self.parent, bg='#1e293b')
        chat_card.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        chat_inner = tk.Frame(chat_card, bg='#1e293b')
        chat_inner.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Área de mensagens
        messages_frame = tk.Frame(chat_inner, bg='#1e293b')
        messages_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # ScrolledText customizado
        self.chat_display = scrolledtext.ScrolledText(
            messages_frame,
            wrap=tk.WORD,
            font=('Segoe UI', 10),
            bg='#0f172a',
            fg='white',
            state=tk.DISABLED,
            insertbackground='white',
            relief=tk.FLAT,
            borderwidth=0,
            padx=15,
            pady=15
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        # Tornar o scrolledtext responsivo ao scroll do mouse (Windows/macOS/Linux)
        # ao focar (mouse sobre) setamos o foco para receber os eventos de wheel.
        self.chat_display.bind('<Enter>', lambda e: self.chat_display.focus_set())
        self.chat_display.bind('<Leave>', lambda e: self.parent.focus_set())

        # Handler compatível com diferentes plataformas
        def _on_mousewheel(event):
            try:
                if os.name == 'nt':
                    # Windows: event.delta é múltiplo de 120
                    self.chat_display.yview_scroll(-1 * int(event.delta / 120), 'units')
                else:
                    # macOS / Linux (on X11 delta may be small/1)
                    self.chat_display.yview_scroll(-1 * int(event.delta), 'units')
            except Exception:
                # Ignora qualquer problema e tenta fallback
                pass

        # Bind do mouse wheel para Windows/macOS
        self.chat_display.bind('<MouseWheel>', _on_mousewheel)
        # Bind do mouse wheel para X11 (Linux)
        self.chat_display.bind('<Button-4>', lambda e: self.chat_display.yview_scroll(-1, 'units'))
        self.chat_display.bind('<Button-5>', lambda e: self.chat_display.yview_scroll(1, 'units'))
        
        # Tags de formatação
        self.chat_display.tag_config("user", 
            foreground='#60a5fa', 
            font=('Segoe UI', 10, 'bold'),
            spacing1=10
        )
        self.chat_display.tag_config("assistant", 
            foreground='#34d399', 
            font=('Segoe UI', 10, 'bold'),
            spacing1=10
        )
        self.chat_display.tag_config("system", 
            foreground='#94a3b8', 
            font=('Segoe UI', 9),
            spacing1=10
        )
        self.chat_display.tag_config("message",
            spacing3=10
        )
        
        # Frame de entrada
        input_frame = tk.Frame(chat_inner, bg='#1e293b')
        input_frame.pack(fill=tk.X)
        
        # Campo de entrada moderno
        entry_container = tk.Frame(input_frame, bg='#334155', relief=tk.FLAT)
        entry_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.entry_mensagem = tk.Entry(
            entry_container,
            font=('Segoe UI', 11),
            bg='#334155',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT,
            borderwidth=0
        )
        self.entry_mensagem.pack(fill=tk.BOTH, padx=15, pady=12)
        self.entry_mensagem.bind("<Return>", lambda e: self.enviar_mensagem())
        
        # Botão enviar
        ModernButton(
            input_frame,
            "➤ Enviar",
            self.enviar_mensagem,
            style='success'
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Card de sugestões
        suggestions_card = tk.Frame(self.parent, bg='#1e293b')
        suggestions_card.pack(fill=tk.X)
        
        sugg_inner = tk.Frame(suggestions_card, bg='#1e293b')
        sugg_inner.pack(fill=tk.X, padx=30, pady=20)
        
        tk.Label(
            sugg_inner,
            text="💡 Perguntas Sugeridas",
            font=('Segoe UI', 12, 'bold'),
            bg='#1e293b',
            fg='white'
        ).pack(anchor='w', pady=(0, 15))
        
        # Grid de sugestões
        sugestoes = [
            "Quais empresas estão cadastradas?",
            "Mostre os funcionários da empresa X",
            "Qual funcionário tem mais horas extras?",
            "Analise as horas extras do último mês",
            "Quais funcionários têm horas faltantes?",
            "Total de horas extras por empresa"
        ]
        
        sugg_grid = tk.Frame(sugg_inner, bg='#1e293b')
        sugg_grid.pack(fill=tk.X)
        
        for i, sugestao in enumerate(sugestoes):
            btn = tk.Button(
                sugg_grid,
                text=sugestao,
                command=lambda s=sugestao: self.usar_sugestao(s),
                font=('Segoe UI', 9),
                bg='#334155',
                fg='white',
                activebackground='#475569',
                activeforeground='white',
                relief=tk.FLAT,
                cursor='hand2',
                anchor='w',
                padx=10,
                pady=5
            )
            row = i // 2
            col = i % 2
            btn.grid(row=row, column=col, padx=2, pady=2, sticky='ew')
            
            # Hover effect
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg='#475569'))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg='#334155'))
        
        sugg_grid.columnconfigure(0, weight=1)
        sugg_grid.columnconfigure(1, weight=1)
        
        # Mensagem inicial
        self.adicionar_mensagem_sistema(
            "👋 Olá! Sou seu assistente de análise de dados.\n\n"
            "Posso ajudar você com:\n"
            "• Empresas cadastradas\n"
            "• Funcionários e seus dados\n"
            "• Horas extras e faltantes\n"
            "• Análises e estatísticas\n\n"
            "Digite sua pergunta ou clique em uma sugestão!"
        )
    
    def usar_sugestao(self, sugestao):
        """Usa sugestão"""
        self.entry_mensagem.delete(0, tk.END)
        self.entry_mensagem.insert(0, sugestao)
        self.enviar_mensagem()
    
    def adicionar_mensagem_sistema(self, texto):
        """Adiciona mensagem do sistema"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "ℹ️ Sistema\n", "system")
        self.chat_display.insert(tk.END, f"{texto}\n\n", "message")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def adicionar_mensagem_usuario(self, texto):
        """Adiciona mensagem do usuário"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "👤 Você\n", "user")
        self.chat_display.insert(tk.END, f"{texto}\n\n", "message")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def adicionar_mensagem_assistente(self, texto):
        """Adiciona mensagem da IA"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "🤖 Assistente\n", "assistant")
        self.chat_display.insert(tk.END, f"{texto}\n\n", "message")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def enviar_mensagem(self):
        """Envia mensagem"""
        mensagem = self.entry_mensagem.get().strip()
        if not mensagem:
            return
        
        self.entry_mensagem.delete(0, tk.END)
        self.adicionar_mensagem_usuario(mensagem)
        
        if not self.ia_disponivel:
            resposta = self.processar_sem_ia(mensagem)
        else:
            resposta = self.processar_com_ia(mensagem)
        
        self.adicionar_mensagem_assistente(resposta)
    
    def processar_sem_ia(self, mensagem):
        """Processa sem IA (regras)"""
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
                        resp += f"• {emp.nome}\n"
                        resp += f"  CNPJ: {emp.cnpj}\n"
                        resp += f"  Funcionários: {num_func}\n\n"
                    return resp
                else:
                    return "Nenhuma empresa cadastrada ainda."
            
            elif "funcionário" in msg_lower or "funcionario" in msg_lower:
                funcionarios = self.db.query(Funcionario).all()
                if funcionarios:
                    resp = "👥 Funcionários cadastrados:\n\n"
                    for func in funcionarios[:10000]:  # Limita a 10000 para evitar excesso
                        empresa = func.empresa.nome if func.empresa else "Sem empresa"
                        resp += f"• {func.nome}\n"
                        resp += f"  Cargo: {func.cargo}\n"
                        resp += f"  Empresa: {empresa}\n"
                        resp += f"  Carga horária: {func.carga_horaria_diaria}h\n\n"
                    
                    if len(funcionarios) > 10000:
                        resp += f"... e mais {len(funcionarios) - 10000} funcionários"
                    
                    return resp
                else:
                    return "Nenhum funcionário cadastrado ainda."
            
            elif "hora" in msg_lower and "extra" in msg_lower:
                data_inicio = datetime.now().date() - timedelta(days=30)
                data_fim = datetime.now().date()
                
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
                ).limit(10).all()
                
                if resultados:
                    resp = f"⏰ Horas extras (últimos 30 dias):\n\n"
                    for func_id, nome, empresa, total in resultados:
                        empresa_txt = empresa or "Sem empresa"
                        resp += f"• {nome}\n"
                        resp += f"  Empresa: {empresa_txt}\n"
                        resp += f"  Horas extras: {total:.2f}h\n\n"
                    return resp
                else:
                    return "Nenhum registro de horas extras nos últimos 30 dias."
            
            else:
                return (
                    "Desculpe, não entendi sua pergunta. Tente perguntar sobre:\n\n"
                    "• 'Quais empresas estão cadastradas?'\n"
                    "• 'Mostre os funcionários'\n"
                    "• 'Análise de horas extras'\n\n"
                    "Ou configure a IA para respostas mais inteligentes!"
                )
        
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()
            return f"Erro ao processar: {str(e)}"
    
    def processar_com_ia(self, mensagem):
        """Processa com IA"""
        try:
            contexto = self.coletar_contexto()
            
            self.historico_conversa.append({
                'role': 'user',
                'content': mensagem
            })
            
            prompt_completo = f"""
Você é um assistente especializado em análise de dados de RH e gestão de horas.

DADOS DISPONÍVEIS:
{json.dumps(contexto, indent=2, ensure_ascii=False)}

HISTÓRICO:
{json.dumps(self.historico_conversa[-5:], indent=2, ensure_ascii=False)}

PERGUNTA: {mensagem}

Responda de forma clara, objetiva e útil.
"""
            
            resposta = self.ia_service.responder_consulta(prompt_completo)
            
            self.historico_conversa.append({
                'role': 'assistant',
                'content': resposta
            })
            
            return resposta
            
        except Exception as e:
            print(f"❌ Erro IA: {e}")
            import traceback
            traceback.print_exc()
            return f"Erro ao processar com IA: {str(e)}"
    
    def coletar_contexto(self):
        """Coleta contexto do sistema"""
        try:
            empresas = self.db.query(Empresa).all()
            empresas_data = [
                {'id': e.id, 'nome': e.nome, 'cnpj': e.cnpj} 
                for e in empresas
            ]
            
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
            return {}
