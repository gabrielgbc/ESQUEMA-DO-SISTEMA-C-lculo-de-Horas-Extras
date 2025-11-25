"""
ui/main_window.py
Janela principal - ATUALIZADA para usar interfaces modernas
"""
import tkinter as tk
from tkinter import ttk

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Controle de Horas")
        self.root.geometry("1400x800")
        self.root.resizable(True, True)
        
        # Configurar tema escuro
        self.root.configure(bg='#0f172a')
        
        # Variáveis
        self.current_view = None
        self.menu_buttons = []
        
        self.setup_styles()
        self.setup_ui()
    
    def setup_styles(self):
        """Configura estilos TTK modernos"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Treeview moderno
        style.configure('Modern.Treeview',
            background='#1e293b',
            foreground='white',
            fieldbackground='#1e293b',
            borderwidth=0,
            relief='flat'
        )
        style.map('Modern.Treeview',
            background=[('selected', '#6366f1')],
            foreground=[('selected', 'white')]
        )
        
        style.configure('Modern.Treeview.Heading',
            background='#334155',
            foreground='white',
            relief='flat',
            borderwidth=0
        )
    
    def setup_ui(self):
        """Configura a interface principal"""
        # Container principal
        main_container = tk.Frame(self.root, bg='#0f172a')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar (menu lateral)
        self.setup_sidebar(main_container)
        
        # Área de conteúdo
        self.setup_content_area(main_container)
        
        # Mostra tela inicial
        self.show_home()
    
    def setup_sidebar(self, parent):
        """Cria sidebar moderna"""
        sidebar = tk.Frame(parent, bg='#1e293b', width=280)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Logo/Header
        header = tk.Frame(sidebar, bg='#1e293b', height=100)
        header.pack(fill=tk.X, pady=(20, 30))
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="⏰",
            font=('Segoe UI', 40),
            bg='#1e293b',
            fg='#6366f1'
        ).pack()
        
        tk.Label(
            header,
            text="Racon – Controle de Horas",
            font=('Segoe UI', 12, 'bold'),
            bg='#1e293b',
            fg='white'
        ).pack()
        
        # Menu items
        menu_items = [
            ("🏠", "Início", self.show_home, '#6366f1'),
            ("🏢", "Empresas", self.show_cadastro_empresa, '#8b5cf6'),
            ("👤", "Funcionários", self.show_cadastro_funcionario, '#ec4899'),
            ("⏱️", "Jornadas", self.show_registro_jornada, '#f59e0b'),
            ("📊", "Relatórios", self.show_relatorios, '#10b981'),
            ("🤖", "Chat IA", self.show_chat_ia, '#06b6d4')
        ]
        
        # Container dos botões
        menu_container = tk.Frame(sidebar, bg='#1e293b')
        menu_container.pack(fill=tk.BOTH, expand=True, padx=15)
        
        for icon, text, command, color in menu_items:
            btn_frame = tk.Frame(menu_container, bg='#1e293b')
            btn_frame.pack(fill=tk.X, pady=5)
            
            btn = tk.Button(
                btn_frame,
                text=f"{icon}  {text}",
                command=command,
                font=('Segoe UI', 11),
                bg='#334155',
                fg='white',
                activebackground=color,
                activeforeground='white',
                relief=tk.FLAT,
                cursor='hand2',
                anchor='w',
                padx=20,
                pady=15,
                borderwidth=0,
                highlightthickness=0
            )
            btn.pack(fill=tk.X)
            
            # Efeito hover
            def on_enter(e, b=btn, c=color):
                b.config(bg=c)
            def on_leave(e, b=btn):
                b.config(bg='#334155')
            
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
            
            self.menu_buttons.append(btn)
        
        # Footer
        footer = tk.Frame(sidebar, bg='#1e293b', height=60)
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        tk.Label(
            footer,
            text="v2.0 Modern",
            font=('Segoe UI', 9),
            bg='#1e293b',
            fg='#64748b'
        ).pack()
    
    def setup_content_area(self, parent):
        """Cria área de conteúdo moderna"""
        content_container = tk.Frame(parent, bg='#0f172a')
        content_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Header do conteúdo
        header = tk.Frame(content_container, bg='#1e293b', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        self.page_title = tk.Label(
            header,
            text="Dashboard",
            font=('Segoe UI', 24, 'bold'),
            bg='#1e293b',
            fg='white'
        )
        self.page_title.pack(side=tk.LEFT, padx=30, pady=20)
        
        # Área de conteúdo scrollável
        self.content_frame = tk.Frame(content_container, bg='#0f172a')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Rodapé
        footer_main = tk.Frame(content_container, bg='#0f172a', height=28)
        footer_main.pack(side=tk.BOTTOM, fill=tk.X)
        footer_main.pack_propagate(False)

        tk.Label(
            footer_main,
            text="Desenvolvedores: Gabriel Bego Cirelli & Maurício de Souza",
            font=('Segoe UI', 9),
            bg='#0f172a',
            fg='#94a3b8'
        ).pack(side=tk.RIGHT, padx=20)
    
    def clear_content(self):
        """Limpa o conteúdo"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def create_card(self, parent, title, subtitle, icon, color, column, command=None):
        """Cria um card moderno"""
        card = tk.Frame(parent, bg='#1e293b', relief=tk.FLAT)
        card.grid(row=0, column=column, padx=15, pady=15, sticky='nsew')
        
        parent.columnconfigure(column, weight=1)
        
        inner = tk.Frame(card, bg='#1e293b')
        inner.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Ícone
        icon_label = tk.Label(
            inner,
            text=icon,
            font=('Segoe UI', 48),
            bg='#1e293b',
            fg=color
        )
        icon_label.pack()
        
        # Título
        tk.Label(
            inner,
            text=title,
            font=('Segoe UI', 18, 'bold'),
            bg='#1e293b',
            fg='white'
        ).pack(pady=(10, 5))
        
        # Subtítulo
        tk.Label(
            inner,
            text=subtitle,
            font=('Segoe UI', 11),
            bg='#1e293b',
            fg='#94a3b8'
        ).pack()
        
        # Botão de ação
        if command:
            btn = tk.Button(
                inner,
                text="Acessar →",
                command=command,
                font=('Segoe UI', 10, 'bold'),
                bg=color,
                fg='white',
                activebackground=color,
                activeforeground='white',
                relief=tk.FLAT,
                cursor='hand2',
                padx=20,
                pady=8,
                borderwidth=0
            )
            btn.pack(pady=(15, 0))
            
            def on_enter(e):
                e.widget.config(bg=self._darken_color(color))
            def on_leave(e):
                e.widget.config(bg=color)
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
        
        # Hover no card
        def card_enter(e):
            card.config(bg='#334155')
            inner.config(bg='#334155')
            icon_label.config(bg='#334155')
            for child in inner.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(bg='#334155')
        
        def card_leave(e):
            card.config(bg='#1e293b')
            inner.config(bg='#1e293b')
            icon_label.config(bg='#1e293b')
            for child in inner.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(bg='#1e293b')
        
        card.bind('<Enter>', card_enter)
        card.bind('<Leave>', card_leave)
        
        return card
    
    def _darken_color(self, color):
        """Escurece cor"""
        darker = {
            '#6366f1': '#4f46e5',
            '#8b5cf6': '#7c3aed',
            '#ec4899': '#db2777',
            '#f59e0b': '#d97706',
            '#10b981': '#059669',
            '#06b6d4': '#0891b2'
        }
        return darker.get(color, color)
    
    def show_home(self):
        """Mostra tela inicial"""
        self.clear_content()
        self.page_title.config(text="Dashboard")
        
        # Welcome
        welcome = tk.Frame(self.content_frame, bg='#0f172a')
        welcome.pack(fill=tk.X, pady=(0, 30))
        
        tk.Label(
            welcome,
            text="Bem-vindo de volta! 👋",
            font=('Segoe UI', 28, 'bold'),
            bg='#0f172a',
            fg='white'
        ).pack(anchor='w')
        
        tk.Label(
            welcome,
            text="Gerencie suas horas de forma inteligente",
            font=('Segoe UI', 13),
            bg='#0f172a',
            fg='#94a3b8'
        ).pack(anchor='w', pady=(5, 0))
        
        # Cards grid
        cards_frame = tk.Frame(self.content_frame, bg='#0f172a')
        cards_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_card(cards_frame, "Empresas", "Gerencie suas empresas", "🏢", '#8b5cf6', 0, self.show_cadastro_empresa)
        self.create_card(cards_frame, "Funcionários", "Cadastre e gerencie", "👤", '#ec4899', 1, self.show_cadastro_funcionario)
        self.create_card(cards_frame, "Jornadas", "Registre horas", "⏱️", '#f59e0b', 2, self.show_registro_jornada)
        self.create_card(cards_frame, "Relatórios", "Visualize estatísticas", "📊", '#10b981', 3, self.show_relatorios)
    
    def show_cadastro_empresa(self):
        """Mostra cadastro de empresas MODERNO"""
        try:
            from ui.cadastro_empresa_modern import CadastroEmpresaModern
            self.clear_content()
            self.page_title.config(text="Empresas")
            CadastroEmpresaModern(self.content_frame)
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()
    
    def show_cadastro_funcionario(self):
        """Mostra cadastro de funcionários MODERNO"""
        try:
            from ui.cadastro_funcionario_modern import CadastroFuncionarioModern
            self.clear_content()
            self.page_title.config(text="Funcionários")
            CadastroFuncionarioModern(self.content_frame)
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()
    
    def show_registro_jornada(self):
        """Mostra registro de jornada MODERNO"""
        try:
            from ui.registro_jornada_modern import RegistroJornadaModern
            self.clear_content()
            self.page_title.config(text="Registro de Jornada")
            RegistroJornadaModern(self.content_frame)
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()
    
    def show_relatorios(self):
        """Mostra relatórios MODERNO"""
        try:
            from ui.relatorios_modern import RelatoriosModern
            self.clear_content()
            self.page_title.config(text="Relatórios")
            RelatoriosModern(self.content_frame)
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()
    
    def show_chat_ia(self):
        """Mostra chat IA MODERNO"""
        try:
            from ui.chat_ia_modern import ChatIAModern
            self.clear_content()
            self.page_title.config(text="Assistente IA")
            ChatIAModern(self.content_frame)
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()