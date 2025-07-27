import os
import json
import time
import datetime
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pystray
from PIL import Image, ImageDraw
import io
import sys

# Importações para controle de instância única
from win32event import CreateMutex
from win32api import CloseHandle, GetLastError
from winerror import ERROR_ALREADY_EXISTS

class PostmanAutomatizado(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Postman Automatizado")
        self.geometry("950x700")
        self.minsize(950, 700)
        
        # Configurar expansão de linhas e colunas para melhor adaptação
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Variáveis para controle da bandeja do sistema
        self.icon = None
        self.is_minimized = False
        
        # Interceptar o evento de fechamento da janela
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Variáveis de configuração
        self.config = {
            "url_base": "",
            "username": "",
            "password": "",
            "token": "",
            "client_id": "",
            "client_secret": "",
            "timeout": 30,
            "fila": ""
        }
        
        # Lista de caminhos (múltiplos)
        self.lista_caminhos = []
        
        # Caminho atual selecionado (para compatibilidade com código existente)
        self.caminhos = {
            "input": "",
            "output": "",
            "gatilho_ativo": False,
            "lote": False,
            "execucao_automatica": False,
            "tempo_execucao": 60
        }
        
        # Variáveis de controle
        self.observer = None
        self.monitoramento_ativo = False
        self.caminho_atual_index = 0  # Índice do caminho atual sendo processado
        
        # Criar interface
        self.criar_interface()
        
        # Carregar configurações se existirem
        self.carregar_configuracoes()
        
        # Iniciar monitoramento automaticamente se a execução automática estiver ativada
        self.after(1000, self.iniciar_automaticamente)
        
    def criar_interface(self):
        # Criar notebook (abas)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Aba 1: Configurações
        self.aba_config = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_config, text="🛠️ Configurações")
        
        # Aba 2: Cadastro de Caminhos
        self.aba_caminhos = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_caminhos, text="📁 Cadastro de Caminhos")
        
        # Aba 3: Logs
        self.aba_logs = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_logs, text="📋 Logs")
        
        # Configurar conteúdo das abas
        self.configurar_aba_config()
        self.configurar_aba_caminhos()
        self.configurar_aba_logs()
        
    def configurar_aba_config(self):
        # Frame principal com padding
        frame = ttk.Frame(self.aba_config, padding=10)
        frame.pack(fill=BOTH, expand=True)
        
        # Título
        ttk.Label(frame, text="Configurações de Requisições", font=("TkDefaultFont", 14, "bold")).pack(pady=(0, 20))
        
        # Grid para os campos
        grid_frame = ttk.Frame(frame)
        grid_frame.pack(fill=X, expand=True)
        
        # URL Base
        ttk.Label(grid_frame, text="URL Base:").grid(row=0, column=0, sticky=W, pady=5)
        self.url_base_entry = ttk.Entry(grid_frame, width=50)
        self.url_base_entry.grid(row=0, column=1, sticky=EW, padx=5, pady=5)
        
        # Username
        ttk.Label(grid_frame, text="Username:").grid(row=1, column=0, sticky=W, pady=5)
        self.username_entry = ttk.Entry(grid_frame, width=50)
        self.username_entry.grid(row=1, column=1, sticky=EW, padx=5, pady=5)
        
        # Password
        ttk.Label(grid_frame, text="Password:").grid(row=2, column=0, sticky=W, pady=5)
        self.password_entry = ttk.Entry(grid_frame, width=50, show="*")
        self.password_entry.grid(row=2, column=1, sticky=EW, padx=5, pady=5)
        
        # Token
        ttk.Label(grid_frame, text="Token/Access Token:").grid(row=3, column=0, sticky=W, pady=5)
        self.token_entry = ttk.Entry(grid_frame, width=50)
        self.token_entry.grid(row=3, column=1, sticky=EW, padx=5, pady=5)
        
        # Client ID
        ttk.Label(grid_frame, text="Client ID:").grid(row=4, column=0, sticky=W, pady=5)
        self.client_id_entry = ttk.Entry(grid_frame, width=50)
        self.client_id_entry.grid(row=4, column=1, sticky=EW, padx=5, pady=5)
        
        # Client Secret
        ttk.Label(grid_frame, text="Client Secret:").grid(row=5, column=0, sticky=W, pady=5)
        self.client_secret_entry = ttk.Entry(grid_frame, width=50, show="*")
        self.client_secret_entry.grid(row=5, column=1, sticky=EW, padx=5, pady=5)
        
        # Timeout
        ttk.Label(grid_frame, text="Timeout (s):").grid(row=6, column=0, sticky=W, pady=5)
        self.timeout_entry = ttk.Spinbox(grid_frame, from_=1, to=300, width=10)
        self.timeout_entry.set(30)
        self.timeout_entry.grid(row=6, column=1, sticky=W, padx=5, pady=5)
        
        # Fila de processamento
        ttk.Label(grid_frame, text="Fila de processamento:").grid(row=7, column=0, sticky=W, pady=5)
        self.fila_entry = ttk.Entry(grid_frame, width=50)
        self.fila_entry.grid(row=7, column=1, sticky=EW, padx=5, pady=5)
        
        # Configurar grid para expandir
        grid_frame.columnconfigure(1, weight=1)
        
        # Botões
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=X, pady=20)
        
        # Botão para minimizar para a bandeja
        ttk.Button(btn_frame, text="Minimizar para Bandeja", command=self.minimize_to_tray, style="info.TButton").pack(side=LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Salvar Configurações", command=self.salvar_configuracoes, style="success.TButton").pack(side=RIGHT, padx=5)
        ttk.Button(btn_frame, text="Limpar Campos", command=self.limpar_config, style="warning.TButton").pack(side=RIGHT, padx=5)
        
    def configurar_aba_caminhos(self):
        # Frame principal com padding
        frame = ttk.Frame(self.aba_caminhos, padding=10)
        frame.pack(fill=BOTH, expand=True)
        
        # Título e botão de adicionar caminho
        titulo_frame = ttk.Frame(frame)
        titulo_frame.pack(fill=X, pady=(0, 20))
        
        ttk.Label(titulo_frame, text="Cadastro de Caminhos", font=("TkDefaultFont", 14, "bold")).pack(side=LEFT)
        
        # Botões de ação para caminhos
        botoes_frame = ttk.Frame(titulo_frame)
        botoes_frame.pack(side=RIGHT)
        
        ttk.Button(botoes_frame, text="+", width=3, command=self.adicionar_caminho, style="success.TButton").pack(side=RIGHT, padx=5)
        ttk.Button(botoes_frame, text="Salvar", width=8, command=self.salvar_caminho_atual, style="primary.TButton").pack(side=RIGHT, padx=5)
        
        # Frame para lista de caminhos com altura máxima definida
        lista_frame_container = ttk.LabelFrame(frame, text="Caminhos Cadastrados")
        lista_frame_container.pack(fill=X, expand=False, pady=10)
        
        # Definir altura máxima para a lista de caminhos
        self.lista_caminhos_frame = ttk.Frame(lista_frame_container)
        self.lista_caminhos_frame.pack(fill=X, expand=True, padx=5, pady=5)
        
        # Frame para formulário de caminho com borda para melhor visualização
        self.form_frame = ttk.LabelFrame(frame, text="Detalhes do Caminho", padding=10)
        self.form_frame.pack(fill=X, expand=True, pady=10)
        
        # Grid para os campos do formulário com melhor organização
        grid_frame = ttk.Frame(self.form_frame)
        grid_frame.pack(fill=X, expand=True, padx=5, pady=5)
        
        # Nome do Caminho
        ttk.Label(grid_frame, text="Nome do Caminho:").grid(row=0, column=0, sticky=W, pady=5)
        self.nome_entry = ttk.Entry(grid_frame, width=50)
        self.nome_entry.grid(row=0, column=1, sticky=EW, padx=5, pady=5)
        
        # Caminho Input
        ttk.Label(grid_frame, text="Caminho Input:").grid(row=1, column=0, sticky=W, pady=5)
        self.input_frame = ttk.Frame(grid_frame)
        self.input_frame.grid(row=1, column=1, sticky=EW, padx=5, pady=5)
        self.input_frame.columnconfigure(0, weight=1)  # Entrada expande para preencher espaço
        self.input_entry = ttk.Entry(self.input_frame, width=50)
        self.input_entry.grid(row=0, column=0, sticky=EW)
        ttk.Button(self.input_frame, text="Selecionar", command=self.selecionar_input).grid(row=0, column=1, padx=5)
        
        # Caminho Output
        ttk.Label(grid_frame, text="Caminho Output:").grid(row=2, column=0, sticky=W, pady=5)
        self.output_frame = ttk.Frame(grid_frame)
        self.output_frame.grid(row=2, column=1, sticky=EW, padx=5, pady=5)
        self.output_frame.columnconfigure(0, weight=1)  # Entrada expande para preencher espaço
        self.output_entry = ttk.Entry(self.output_frame, width=50)
        self.output_entry.grid(row=0, column=0, sticky=EW)
        ttk.Button(self.output_frame, text="Selecionar", command=self.selecionar_output).grid(row=0, column=1, padx=5)
        
        # Tempo de execução
        ttk.Label(grid_frame, text="Tempo de execução (s):").grid(row=3, column=0, sticky=W, pady=5)
        self.tempo_execucao_entry = ttk.Spinbox(grid_frame, from_=1, to=3600, width=10)
        self.tempo_execucao_entry.set(60)
        self.tempo_execucao_entry.grid(row=3, column=1, sticky=W, padx=5, pady=5)
        
        # Checkboxes
        self.gatilho_var = tk.BooleanVar()
        self.lote_var = tk.BooleanVar()
        self.execucao_automatica_var = tk.BooleanVar()
        
        # Criar frame para checkboxes com melhor organização
        checkbox_frame = ttk.Frame(grid_frame)
        checkbox_frame.grid(row=4, column=0, columnspan=2, sticky=W, padx=5, pady=10)
        
        # Organizar checkboxes em uma linha com espaçamento adequado
        ttk.Label(checkbox_frame, text="Opções:").pack(side=LEFT, padx=(0, 10))
        ttk.Checkbutton(checkbox_frame, text="Ativar Gatilho", variable=self.gatilho_var).pack(side=LEFT, padx=(0, 15))
        ttk.Checkbutton(checkbox_frame, text="Requisições em Lote", variable=self.lote_var).pack(side=LEFT, padx=(0, 15))
        ttk.Checkbutton(checkbox_frame, text="Execução Automática", variable=self.execucao_automatica_var).pack(side=LEFT)
        
        # Configurar grid para expandir
        grid_frame.columnconfigure(1, weight=1)
        
        # Botões
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=X, pady=20)
        
        self.btn_monitorar = ttk.Button(btn_frame, text="Iniciar Monitoramento", command=self.alternar_monitoramento, style="success.TButton")
        self.btn_monitorar.pack(side=RIGHT, padx=5)
        
        ttk.Button(btn_frame, text="Executar Agora", command=self.executar_agora, style="info.TButton").pack(side=RIGHT, padx=5)
        
    def configurar_aba_logs(self):
        # Frame principal com padding
        frame = ttk.Frame(self.aba_logs, padding=10)
        frame.pack(fill=BOTH, expand=True)
        
        # Título
        ttk.Label(frame, text="Logs de Execução", font=("TkDefaultFont", 14, "bold")).pack(pady=(0, 10))
        
        # Área de logs
        self.log_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=20, width=80)
        self.log_area.pack(fill=BOTH, expand=True, pady=10)
        self.log_area.config(state=tk.DISABLED)
        
        # Botões
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=X, pady=10)
        
        # Botão para minimizar para a bandeja
        ttk.Button(btn_frame, text="Minimizar para Bandeja", command=self.minimize_to_tray, style="info.TButton").pack(side=LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Limpar Logs", command=self.limpar_logs, style="warning.TButton").pack(side=RIGHT, padx=5)
        
    def selecionar_input(self):
        diretorio = filedialog.askdirectory(title="Selecione o diretório de entrada")
        if diretorio:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, diretorio)
    
    def selecionar_output(self):
        diretorio = filedialog.askdirectory(title="Selecione o diretório de saída")
        if diretorio:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, diretorio)
    
    def salvar_configuracoes(self):
        self.config["url_base"] = self.url_base_entry.get()
        self.config["username"] = self.username_entry.get()
        self.config["password"] = self.password_entry.get()
        self.config["token"] = self.token_entry.get()
        self.config["client_id"] = self.client_id_entry.get()
        self.config["client_secret"] = self.client_secret_entry.get()
        
        try:
            self.config["timeout"] = int(self.timeout_entry.get())
        except ValueError:
            self.config["timeout"] = 30
            self.timeout_entry.delete(0, tk.END)
            self.timeout_entry.insert(0, "30")
        
        self.config["fila"] = self.fila_entry.get()
        
        # Salvar em arquivo
        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=4)
        
        self.adicionar_log("Configurações salvas com sucesso!")
    
    def adicionar_caminho(self):
        """Adiciona um novo caminho à lista"""
        # Limpar os campos do formulário
        self.nome_entry.delete(0, tk.END)
        self.input_entry.delete(0, tk.END)
        self.output_entry.delete(0, tk.END)
        self.tempo_execucao_entry.delete(0, tk.END)
        self.tempo_execucao_entry.insert(0, "60")
        self.gatilho_var.set(False)
        self.lote_var.set(False)
        self.execucao_automatica_var.set(False)
        
        # Criar nome padrão para o novo caminho
        nome_padrao = f"Caminho {len(self.lista_caminhos) + 1}"
        self.nome_entry.insert(0, nome_padrao)
        
        # Atualizar o caminho atual para um novo caminho vazio
        self.caminhos = {
            "input": "",
            "output": "",
            "gatilho_ativo": False,
            "lote": False,
            "execucao_automatica": False,
            "tempo_execucao": 60,
            "nome": nome_padrao
        }
        
        # Adicionar log para debug
        self.adicionar_log(f"Novo caminho criado: {self.caminhos['nome']}")
        
        # Atualizar a interface para mostrar os checkboxes desmarcados
        self.gatilho_var.set(False)
        self.lote_var.set(False)
        self.execucao_automatica_var.set(False)
        
        # Salvar o novo caminho automaticamente
        self.salvar_caminho_atual()
        
        # Atualizar a interface
        self.atualizar_lista_caminhos()
    
    def salvar_caminho_atual(self):
        """Salva o caminho atual no formulário"""
        # Atualizar o caminho atual com os valores do formulário
        self.caminhos["nome"] = self.nome_entry.get()
        self.caminhos["input"] = self.input_entry.get()
        self.caminhos["output"] = self.output_entry.get()
        self.caminhos["gatilho_ativo"] = self.gatilho_var.get()
        self.caminhos["lote"] = self.lote_var.get()
        self.caminhos["execucao_automatica"] = self.execucao_automatica_var.get()
        
        try:
            self.caminhos["tempo_execucao"] = int(self.tempo_execucao_entry.get())
        except ValueError:
            self.caminhos["tempo_execucao"] = 60
            self.tempo_execucao_entry.delete(0, tk.END)
            self.tempo_execucao_entry.insert(0, "60")
        
        # Garantir que o caminho tenha um nome
        if not self.caminhos["nome"]:
            nome_padrao = f"Caminho {len(self.lista_caminhos) + 1}"
            self.caminhos["nome"] = nome_padrao
            self.nome_entry.delete(0, tk.END)
            self.nome_entry.insert(0, nome_padrao)
        
        # Verificar se este caminho já existe na lista
        caminho_existente = False
        for i, caminho in enumerate(self.lista_caminhos):
            if caminho.get("nome") == self.caminhos.get("nome"):
                # Atualizar caminho existente
                self.lista_caminhos[i] = self.caminhos.copy()
                caminho_existente = True
                break
        
        # Se não existir, adicionar à lista
        if not caminho_existente:
            self.lista_caminhos.append(self.caminhos.copy())
        
        # Salvar todos os caminhos em arquivo
        self.salvar_caminhos()
        
        # Atualizar a interface
        self.atualizar_lista_caminhos()
        
        self.adicionar_log(f"Caminho '{self.caminhos.get('nome')}' salvo com sucesso!")
    
    def salvar_caminhos(self):
        """Salva todos os caminhos em arquivo"""
        with open("caminhos.json", "w") as f:
            json.dump({
                "caminhos": self.lista_caminhos,
                "caminho_atual": self.caminhos
            }, f, indent=4)
        
        self.adicionar_log("Todos os caminhos foram salvos com sucesso!")
    
    def carregar_caminho(self, index):
        """Carrega um caminho da lista para o formulário"""
        if 0 <= index < len(self.lista_caminhos):
            # Atualizar o caminho atual
            self.caminhos = self.lista_caminhos[index].copy()
            
            # Atualizar os campos do formulário
            self.nome_entry.delete(0, tk.END)
            self.nome_entry.insert(0, self.caminhos.get("nome", f"Caminho {index+1}"))
            
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.caminhos.get("input", ""))
            
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, self.caminhos.get("output", ""))
            
            self.gatilho_var.set(self.caminhos.get("gatilho_ativo", False))
            self.lote_var.set(self.caminhos.get("lote", False))
            self.execucao_automatica_var.set(self.caminhos.get("execucao_automatica", False))
            
            self.tempo_execucao_entry.delete(0, tk.END)
            self.tempo_execucao_entry.insert(0, str(self.caminhos.get("tempo_execucao", 60)))
            
            self.adicionar_log(f"Caminho '{self.caminhos.get('nome')}' carregado.")
    
    def excluir_caminho(self, index):
        """Exclui um caminho da lista"""
        if 0 <= index < len(self.lista_caminhos):
            nome_caminho = self.lista_caminhos[index].get("nome", f"Caminho {index+1}")
            del self.lista_caminhos[index]
            
            # Salvar a lista atualizada
            self.salvar_caminhos()
            
            # Atualizar a interface
            self.atualizar_lista_caminhos()
            
            self.adicionar_log(f"Caminho '{nome_caminho}' excluído.")
    
    def atualizar_lista_caminhos(self):
        """Atualiza a interface com a lista de caminhos"""
        # Limpar o frame da lista
        for widget in self.lista_caminhos_frame.winfo_children():
            widget.destroy()
        
        # Se não houver caminhos, mostrar mensagem
        if not self.lista_caminhos:
            ttk.Label(self.lista_caminhos_frame, text="Nenhum caminho cadastrado. Clique no botão + para adicionar.").pack(pady=10)
            return
        
        # Criar cabeçalho
        header_frame = ttk.Frame(self.lista_caminhos_frame)
        header_frame.pack(fill=X, pady=(0, 5))
        
        ttk.Label(header_frame, text="Nome", width=15).pack(side=LEFT, padx=5)
        ttk.Label(header_frame, text="Input", width=25).pack(side=LEFT, padx=5)
        ttk.Label(header_frame, text="Output", width=25).pack(side=LEFT, padx=5)
        ttk.Label(header_frame, text="Gatilho", width=8).pack(side=LEFT, padx=5)
        ttk.Label(header_frame, text="Lote", width=8).pack(side=LEFT, padx=5)
        ttk.Label(header_frame, text="Auto", width=8).pack(side=LEFT, padx=5)
        ttk.Label(header_frame, text="Tempo", width=8).pack(side=LEFT, padx=5)
        ttk.Label(header_frame, text="Ações", width=15).pack(side=LEFT, padx=5)
        
        # Adicionar separador
        ttk.Separator(self.lista_caminhos_frame, orient="horizontal").pack(fill=X, pady=5)
        
        # Criar lista scrollable com altura fixa
        canvas = tk.Canvas(self.lista_caminhos_frame, height=150)  # Altura fixa para a lista
        scrollbar = ttk.Scrollbar(self.lista_caminhos_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configurar o canvas para permitir rolagem com a roda do mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Adicionar cada caminho à lista
        for i, caminho in enumerate(self.lista_caminhos):
            row_frame = ttk.Frame(scrollable_frame)
            row_frame.pack(fill=X, pady=2)
            
            nome = caminho.get("nome", f"Caminho {i+1}")
            input_path = caminho.get("input", "")
            output_path = caminho.get("output", "")
            gatilho = "Sim" if caminho.get("gatilho_ativo", False) else "Não"
            lote = "Sim" if caminho.get("lote", False) else "Não"
            auto = "Sim" if caminho.get("execucao_automatica", False) else "Não"
            tempo = str(caminho.get("tempo_execucao", 60))
            
            # Truncar caminhos longos
            if len(input_path) > 25:
                input_path = input_path[:22] + "..."
            if len(output_path) > 25:
                output_path = output_path[:22] + "..."
            
            ttk.Label(row_frame, text=nome, width=15).pack(side=LEFT, padx=5)
            ttk.Label(row_frame, text=input_path, width=25).pack(side=LEFT, padx=5)
            ttk.Label(row_frame, text=output_path, width=25).pack(side=LEFT, padx=5)
            ttk.Label(row_frame, text=gatilho, width=8).pack(side=LEFT, padx=5)
            ttk.Label(row_frame, text=lote, width=8).pack(side=LEFT, padx=5)
            ttk.Label(row_frame, text=auto, width=8).pack(side=LEFT, padx=5)
            ttk.Label(row_frame, text=tempo, width=8).pack(side=LEFT, padx=5)
            
            # Botões de ação
            action_frame = ttk.Frame(row_frame)
            action_frame.pack(side=LEFT, padx=5)
            
            ttk.Button(
                action_frame, 
                text="Editar", 
                width=8,
                command=lambda idx=i: self.carregar_caminho(idx)
            ).pack(side=LEFT, padx=2)
            
            ttk.Button(
                action_frame, 
                text="Excluir", 
                width=8,
                style="danger.TButton",
                command=lambda idx=i: self.excluir_caminho(idx)
            ).pack(side=LEFT, padx=2)
    
    def carregar_configuracoes(self):
        # Carregar configurações
        try:
            with open("config.json", "r") as f:
                self.config = json.load(f)
                
                self.url_base_entry.delete(0, tk.END)
                self.url_base_entry.insert(0, self.config.get("url_base", ""))
                
                self.username_entry.delete(0, tk.END)
                self.username_entry.insert(0, self.config.get("username", ""))
                
                self.password_entry.delete(0, tk.END)
                self.password_entry.insert(0, self.config.get("password", ""))
                
                self.token_entry.delete(0, tk.END)
                self.token_entry.insert(0, self.config.get("token", ""))
                
                self.client_id_entry.delete(0, tk.END)
                self.client_id_entry.insert(0, self.config.get("client_id", ""))
                
                self.client_secret_entry.delete(0, tk.END)
                self.client_secret_entry.insert(0, self.config.get("client_secret", ""))
                
                self.timeout_entry.delete(0, tk.END)
                self.timeout_entry.insert(0, str(self.config.get("timeout", 30)))
                
                self.fila_entry.delete(0, tk.END)
                self.fila_entry.insert(0, self.config.get("fila", ""))
        except FileNotFoundError:
            pass
        
        # Carregar caminhos
        try:
            with open("caminhos.json", "r") as f:
                dados = json.load(f)
                
                # Verificar se o arquivo está no novo formato (com lista de caminhos)
                if "caminhos" in dados:
                    self.lista_caminhos = dados.get("caminhos", [])
                    self.caminhos = dados.get("caminho_atual", {})
                else:
                    # Formato antigo - converter para o novo formato
                    self.caminhos = dados
                    # Adicionar o caminho atual à lista se não estiver vazio
                    if self.caminhos.get("input") or self.caminhos.get("output"):
                        # Adicionar um nome ao caminho antigo
                        self.caminhos["nome"] = "Caminho 1"
                        self.lista_caminhos = [self.caminhos.copy()]
                
                # Preencher o formulário com o caminho atual
                self.nome_entry.delete(0, tk.END)
                self.nome_entry.insert(0, self.caminhos.get("nome", "Caminho 1"))
                
                self.input_entry.delete(0, tk.END)
                self.input_entry.insert(0, self.caminhos.get("input", ""))
                
                self.output_entry.delete(0, tk.END)
                self.output_entry.insert(0, self.caminhos.get("output", ""))
                
                self.gatilho_var.set(self.caminhos.get("gatilho_ativo", False))
                self.lote_var.set(self.caminhos.get("lote", False))
                self.execucao_automatica_var.set(self.caminhos.get("execucao_automatica", False))
                
                self.tempo_execucao_entry.delete(0, tk.END)
                self.tempo_execucao_entry.insert(0, str(self.caminhos.get("tempo_execucao", 60)))
                
                # Atualizar a interface com a lista de caminhos
                self.atualizar_lista_caminhos()
        except FileNotFoundError:
            pass
    
    def limpar_config(self):
        self.url_base_entry.delete(0, tk.END)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.token_entry.delete(0, tk.END)
        self.client_id_entry.delete(0, tk.END)
        self.client_secret_entry.delete(0, tk.END)
        self.timeout_entry.delete(0, tk.END)
        self.timeout_entry.insert(0, "30")
        self.fila_entry.delete(0, tk.END)
    
    def limpar_logs(self):
        # Limpar área visual de logs
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state=tk.DISABLED)
        
        # Limpar arquivo de log atual se existir
        if hasattr(self, 'arquivo_log') and os.path.exists(self.arquivo_log):
            try:
                with open(self.arquivo_log, "w", encoding="utf-8") as f:
                    f.write(f"=== Log limpo em {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')} ===\n")
                self.adicionar_log("Arquivo de log limpo.")
            except Exception as e:
                print(f"Erro ao limpar arquivo de log: {str(e)}")
    
    def inicializar_arquivo_log(self):
        """Inicializa o arquivo de log com a data atual"""
        # Criar pasta log se não existir
        if not os.path.exists("log"):
            os.makedirs("log")
            
        # Nome do arquivo com data atual
        data_atual = datetime.datetime.now().strftime("%d%m%y")
        self.arquivo_log = os.path.join("log", f"log_{data_atual}.txt")
        
        # Adicionar cabeçalho ao arquivo
        with open(self.arquivo_log, "a", encoding="utf-8") as f:
            f.write(f"=== Log iniciado em {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')} ===\n")
    
    # Dicionário para rastrear logs já registrados (evitar duplicações)
    _logs_registrados = {}
    
    # Dicionário para rastrear processamentos em andamento por caminho
    _processamentos_ativos = {}
    
    def adicionar_log(self, mensagem, log_id=None):
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        log_entry = f"[{timestamp}] {mensagem}\n"
        
        # Se um log_id foi fornecido, verificar se já foi registrado para evitar duplicação
        if log_id is not None:
            # Se este log_id já foi registrado com a mesma mensagem, ignorar
            if log_id in self._logs_registrados and self._logs_registrados[log_id] == mensagem:
                return
            # Registrar este log_id e mensagem
            self._logs_registrados[log_id] = mensagem
            
            # Limitar o tamanho do dicionário para evitar crescimento excessivo
            if len(self._logs_registrados) > 1000:
                # Remover os itens mais antigos
                keys_to_remove = list(self._logs_registrados.keys())[:500]
                for key in keys_to_remove:
                    del self._logs_registrados[key]
        
        # Usar after para garantir que a atualização da UI ocorra na thread principal
        def atualizar_ui():
            # Adicionar ao componente visual
            self.log_area.config(state=tk.NORMAL)
            self.log_area.insert(tk.END, log_entry)
            self.log_area.see(tk.END)  # Rolar para o final
            self.log_area.config(state=tk.DISABLED)
        
        # Se estamos na thread principal, atualizar diretamente
        # Caso contrário, agendar para a thread principal
        try:
            self.after(0, atualizar_ui)
        except RuntimeError:
            # Se ocorrer erro (thread não principal), apenas registrar no arquivo
            print(f"Log (thread não-principal): {log_entry.strip()}")
        
        # Adicionar ao arquivo de log
        try:
            # Verificar se o arquivo de log foi inicializado
            if not hasattr(self, 'arquivo_log'):
                self.inicializar_arquivo_log()
                
            # Escrever no arquivo
            with open(self.arquivo_log, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Erro ao escrever no arquivo de log: {str(e)}")
            # Não propagar o erro para não interromper a aplicação
    
    def alternar_monitoramento(self):
        if self.monitoramento_ativo:
            self.parar_monitoramento()
        else:
            self.iniciar_monitoramento()
            
    # Dicionário para armazenar os IDs dos agendamentos por caminho
    _agendamentos_por_caminho = {}
    
    def verificacao_automatica(self, caminho_especifico=None):
        """Função para verificar periodicamente a pasta de entrada quando execução automática estiver ativada
        
        Args:
            caminho_especifico: Se fornecido, verifica apenas este caminho específico
        """
        if not self.monitoramento_ativo:
            return
            
        # Criar um ID único para esta verificação
        verif_id = f"verif_{time.time()}"
        
        # Determinar quais caminhos verificar
        if caminho_especifico:
            caminhos_para_verificar = [caminho_especifico]
        else:
            # Na primeira execução, configurar verificações individuais para cada caminho
            caminhos_para_verificar = [self.caminhos] + self.lista_caminhos
            
            # Cancelar agendamentos existentes
            for after_id in self._agendamentos_por_caminho.values():
                if after_id:
                    self.after_cancel(after_id)
            
            # Limpar dicionário de agendamentos
            self._agendamentos_por_caminho = {}
            
            # Configurar verificações individuais para cada caminho com execução automática
            for caminho in caminhos_para_verificar:
                if caminho.get("execucao_automatica", False):
                    nome_caminho = caminho.get("nome", "atual")
                    tempo_execucao = caminho.get("tempo_execucao", 60)
                    
                    # Agendar primeira verificação para este caminho
                    after_id = self.after(tempo_execucao * 1000, 
                                         lambda c=caminho: self.verificacao_automatica(c))
                    
                    # Armazenar o ID do agendamento
                    self._agendamentos_por_caminho[nome_caminho] = after_id
            
            # Retornar após configurar os agendamentos individuais
            return
        
        # A partir daqui, estamos verificando um caminho específico
        nome_caminho = caminho_especifico.get("nome", "atual")
        
        # Verificar se o caminho tem execução automática
        if not caminho_especifico.get("execucao_automatica", False):
            return
        
        # ID único para este caminho na verificação
        caminho_verif_id = f"{verif_id}_{nome_caminho}"
        
        # Verificar se existem arquivos para processar
        arquivos = [f for f in os.listdir(caminho_especifico["input"]) if f.lower().endswith(".json")]
        
        # Verificar se o gatilho está ativo e se os arquivos de gatilho existem
        if caminho_especifico.get("gatilho_ativo", False):
            gatilho_ini_path = os.path.join(caminho_especifico["input"], "gatilho_ini.json")
            gatilho_fim_path = os.path.join(caminho_especifico["input"], "gatilho_fim.json")
            
            # Se não existirem os arquivos de gatilho, não processar
            if not os.path.isfile(gatilho_ini_path) or not os.path.isfile(gatilho_fim_path):
                self.adicionar_log(f"Verificação automática do caminho {nome_caminho}: arquivos de gatilho não encontrados.", log_id=caminho_verif_id+"_sem_gatilho")
            else:
                # Processar se houver arquivos
                if arquivos:
                    self.adicionar_log(f"Verificação automática do caminho {nome_caminho}: {len(arquivos)} arquivos encontrados.", log_id=caminho_verif_id+"_arquivos")
                    threading.Thread(target=self.processar_arquivos, args=(caminho_especifico,)).start()
                else:
                    self.adicionar_log(f"Verificação automática do caminho {nome_caminho}: nenhum arquivo encontrado.", log_id=caminho_verif_id+"_vazio")
        else:
            # Processar se houver arquivos (sem verificar gatilhos)
            if arquivos:
                self.adicionar_log(f"Verificação automática do caminho {nome_caminho}: {len(arquivos)} arquivos encontrados.", log_id=caminho_verif_id+"_arquivos")
                threading.Thread(target=self.processar_arquivos, args=(caminho_especifico,)).start()
            else:
                self.adicionar_log(f"Verificação automática do caminho {nome_caminho}: nenhum arquivo encontrado.", log_id=caminho_verif_id+"_vazio")
        
        # Agendar próxima verificação para este caminho específico
        tempo_execucao = caminho_especifico.get("tempo_execucao", 60)
        self.adicionar_log(f"Próxima verificação automática do caminho {nome_caminho} em {tempo_execucao} segundos.", log_id=caminho_verif_id+"_proxima")
        
        # Criar novo agendamento e armazenar seu ID
        after_id = self.after(tempo_execucao * 1000, 
                             lambda c=caminho_especifico: self.verificacao_automatica(c))
        self._agendamentos_por_caminho[nome_caminho] = after_id
    
    def iniciar_monitoramento(self):
        # Criar um ID único para este monitoramento
        monitor_id = f"monitor_{time.time()}"
        
        # Inicializar arquivo de log
        self.inicializar_arquivo_log()
        
        # Lista para armazenar todos os caminhos a serem monitorados
        caminhos_para_monitorar = [self.caminhos] + self.lista_caminhos
        diretorios_observados = set()
        
        # Verificar todos os caminhos
        for caminho in caminhos_para_monitorar:
            nome_caminho = caminho.get("nome", "atual")
            # ID único para este caminho no monitoramento
            caminho_monitor_id = f"{monitor_id}_{nome_caminho}"
            
            # Verificar se os caminhos estão configurados
            if not caminho.get("input") or not caminho.get("output"):
                self.adicionar_log(f"ERRO: Configure os caminhos de entrada e saída para o caminho {nome_caminho}!", log_id=caminho_monitor_id+"_erro_config")
                continue
            
            # Verificar se os diretórios existem
            if not os.path.isdir(caminho["input"]):
                self.adicionar_log(f"ERRO: Diretório de entrada não existe para o caminho {nome_caminho}: {caminho['input']}", log_id=caminho_monitor_id+"_erro_input")
                continue
            
            if not os.path.isdir(caminho["output"]):
                self.adicionar_log(f"ERRO: Diretório de saída não existe para o caminho {nome_caminho}: {caminho['output']}", log_id=caminho_monitor_id+"_erro_output")
                continue
            
            # Adicionar o diretório à lista de diretórios observados
            diretorios_observados.add(caminho["input"])
        
        # Se não houver diretórios válidos para monitorar, abortar
        if not diretorios_observados:
            self.adicionar_log("ERRO: Nenhum diretório válido para monitorar!", log_id=monitor_id+"_erro_sem_dir")
            return
        
        # Iniciar monitoramento
        self.monitoramento_ativo = True
        self.btn_monitorar.config(text="Parar Monitoramento", style="danger.TButton")
        
        self.adicionar_log(f"Iniciando monitoramento de {len(diretorios_observados)} diretórios!", log_id=monitor_id+"_inicio")
        
        # Configurar e iniciar o observer para cada diretório único
        event_handler = FileSystemEventHandler()
        event_handler.on_created = self.on_file_created
        
        self.observer = Observer()
        for diretorio in diretorios_observados:
            self.observer.schedule(event_handler, diretorio, recursive=False)
        self.observer.start()
        
        # Verificar se há caminhos com execução automática ativada
        caminhos_automaticos = [c for c in caminhos_para_monitorar if c.get("execucao_automatica", False)]
        
        if caminhos_automaticos:
            # Alternar para a aba de logs (índice 2)
            self.notebook.select(2)
            self.adicionar_log(f"Execução automática ativada para {len(caminhos_automaticos)} caminhos. Iniciando verificação periódica...", log_id=monitor_id+"_auto_inicio")
            # Iniciar verificação automática com configuração individual para cada caminho
            self.verificacao_automatica()
    
    def parar_monitoramento(self):
        # Criar um ID único para esta operação
        parar_id = f"parar_{time.time()}"
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        
        # Cancelar todos os agendamentos de verificação automática
        for after_id in self._agendamentos_por_caminho.values():
            if after_id:
                self.after_cancel(after_id)
        
        # Limpar dicionário de agendamentos
        self._agendamentos_por_caminho = {}
        
        self.monitoramento_ativo = False
        self.btn_monitorar.config(text="Iniciar Monitoramento", style="success.TButton")
        
        self.adicionar_log("Monitoramento parado.", log_id=parar_id)
        
    def iniciar_automaticamente(self):
        """Função para iniciar o monitoramento automaticamente para todos os caminhos com execução automática ativada"""
        # Criar um ID único para esta operação
        auto_id = f"auto_{time.time()}"
        
        if not self.monitoramento_ativo:
            # Verificar se há caminhos com execução automática ativada
            caminhos_automaticos = [c for c in self.lista_caminhos if c.get("execucao_automatica", False)]
            
            # Verificar também o caminho atual (para compatibilidade)
            if self.caminhos.get("execucao_automatica", False):
                caminhos_automaticos.append(self.caminhos)
            
            # Se houver pelo menos um caminho com execução automática, iniciar o monitoramento
            if caminhos_automaticos:
                self.adicionar_log(f"Iniciando monitoramento automático para {len(caminhos_automaticos)} caminhos...", log_id=auto_id)
                self.notebook.select(2)  # Alternar para a aba de logs (índice 2)
                self.iniciar_monitoramento()
    
    def on_file_created(self, event):
        # Verificar se é um arquivo
        if not os.path.isfile(event.src_path):
            return
        
        # Verificar se é um arquivo JSON
        if not event.src_path.lower().endswith(".json"):
            return
        
        # Verificar qual caminho corresponde ao evento
        caminho_correspondente = None
        
        # Primeiro verificar o caminho atual (para compatibilidade)
        if event.src_path.startswith(self.caminhos["input"]):
            caminho_correspondente = self.caminhos
        else:
            # Verificar na lista de caminhos
            for caminho in self.lista_caminhos:
                if event.src_path.startswith(caminho["input"]):
                    caminho_correspondente = caminho
                    break
        
        # Se não encontrou um caminho correspondente, ignorar o evento
        if not caminho_correspondente:
            return
            
        # Verificar se o gatilho está ativo para este caminho
        if not caminho_correspondente.get("gatilho_ativo", False):
            return
        
        # Verificar se é um arquivo de gatilho
        filename = os.path.basename(event.src_path)
        
        nome_caminho = caminho_correspondente.get("nome", "atual")
        # Criar um ID único para este evento
        evento_id = f"evento_{nome_caminho}_{filename}_{time.time()}"
        
        if filename == "gatilho_ini.json":
            self.adicionar_log(f"Arquivo gatilho_ini.json detectado no caminho {nome_caminho}. Iniciando processamento...", log_id=evento_id)
            threading.Thread(target=self.processar_arquivos, args=(caminho_correspondente,)).start()
    
    def executar_agora(self):
        # Criar um ID único para esta execução
        exec_id = f"exec_{time.time()}"
        
        # Se não houver caminhos cadastrados, usar o caminho atual
        if not self.lista_caminhos:
            # Verificar se os caminhos estão configurados
            if not self.caminhos["input"] or not self.caminhos["output"]:
                self.adicionar_log("ERRO: Configure os caminhos de entrada e saída primeiro!", log_id=exec_id+"_erro_config")
                return
            
            # Verificar se os diretórios existem
            if not os.path.isdir(self.caminhos["input"]):
                self.adicionar_log(f"ERRO: Diretório de entrada não existe: {self.caminhos['input']}", log_id=exec_id+"_erro_input")
                return
            
            if not os.path.isdir(self.caminhos["output"]):
                self.adicionar_log(f"ERRO: Diretório de saída não existe: {self.caminhos['output']}", log_id=exec_id+"_erro_output")
                return
            
            # Iniciar processamento em uma thread separada
            self.adicionar_log("Iniciando processamento do caminho atual...", log_id=exec_id+"_inicio")
            threading.Thread(target=self.processar_arquivos, args=(self.caminhos,)).start()
        else:
            # Processar todos os caminhos cadastrados
            self.adicionar_log(f"Iniciando processamento de {len(self.lista_caminhos)} caminhos cadastrados...", log_id=exec_id+"_inicio_todos")
            threading.Thread(target=self.processar_todos_caminhos).start()
    
    def processar_todos_caminhos(self):
        """Processa todos os caminhos cadastrados sequencialmente"""
        # Criar um ID único para este processamento em lote
        todos_id = f"todos_{time.time()}"
        
        for i, caminho in enumerate(self.lista_caminhos):
            nome = caminho.get("nome", f"Caminho {i+1}")
            # ID único para este caminho no processamento em lote
            caminho_id = f"{todos_id}_{nome}"
            
            self.adicionar_log(f"Processando caminho: {nome}", log_id=caminho_id+"_inicio")
            
            # Verificar se os caminhos estão configurados
            if not caminho.get("input") or not caminho.get("output"):
                self.adicionar_log(f"ERRO: Caminho {nome} não tem entrada ou saída configurada. Pulando...", log_id=caminho_id+"_erro_config")
                continue
            
            # Verificar se os diretórios existem
            if not os.path.isdir(caminho.get("input")):
                self.adicionar_log(f"ERRO: Diretório de entrada não existe: {caminho.get('input')}. Pulando...", log_id=caminho_id+"_erro_input")
                continue
            
            if not os.path.isdir(caminho.get("output")):
                self.adicionar_log(f"ERRO: Diretório de saída não existe: {caminho.get('output')}. Pulando...", log_id=caminho_id+"_erro_output")
                continue
            
            # Processar este caminho
            self.processar_arquivos(caminho)
            
            # Pequena pausa entre o processamento de cada caminho
            time.sleep(2)
        
        self.adicionar_log("Processamento de todos os caminhos concluído!", log_id=todos_id+"_concluido")

    
    def processar_arquivos(self, caminho=None):
        # Se não for fornecido um caminho, usar o caminho atual
        if caminho is None:
            caminho = self.caminhos
        
        nome_caminho = caminho.get("nome", "atual")
        
        # Verificar se já existe um processamento em andamento para este caminho
        if nome_caminho in self._processamentos_ativos and self._processamentos_ativos[nome_caminho]:
            # Já existe um processamento em andamento, não iniciar outro
            return
            
        # Marcar este caminho como em processamento
        self._processamentos_ativos[nome_caminho] = True
        
        # Registrar o tempo de início do processamento
        tempo_inicio = time.time()
        
        # Criar um ID único para este processamento
        processo_id = f"proc_{nome_caminho}_{tempo_inicio}"
        self.adicionar_log(f"Iniciando processamento de arquivos do caminho {nome_caminho}...", log_id=processo_id+"_inicio")
        
        # Verificar se existem os arquivos de gatilho
        gatilho_ini_path = os.path.join(caminho["input"], "gatilho_ini.json")
        gatilho_fim_path = os.path.join(caminho["input"], "gatilho_fim.json")
        
        # Se o gatilho estiver ativo, verificar se os arquivos existem
        if caminho["gatilho_ativo"]:
            if not os.path.isfile(gatilho_ini_path):
                self.adicionar_log(f"ERRO: Arquivo gatilho_ini.json não encontrado no caminho {nome_caminho}!", log_id=processo_id+"_erro_ini")
                return
            
            if not os.path.isfile(gatilho_fim_path):
                self.adicionar_log(f"ERRO: Arquivo gatilho_fim.json não encontrado no caminho {nome_caminho}!", log_id=processo_id+"_erro_fim")
                return
            
            # Enviar gatilho_ini.json
            status_ini = self.enviar_requisicao(gatilho_ini_path)
            
            if status_ini != 200:
                self.adicionar_log(f"ERRO: Falha ao enviar gatilho_ini.json do caminho {nome_caminho}. Status: {status_ini}", log_id=processo_id+"_erro_ini_status")
                return
            
            # Mover gatilho_ini.json para a pasta de saída
            timestamp = datetime.datetime.now().strftime("%d%m%y_%H%M%S")
            nome_saida_ini = f"gatilho_ini_{timestamp}.json"
            arquivo_saida_ini = os.path.join(caminho["output"], nome_saida_ini)
            
            try:
                with open(gatilho_ini_path, "r") as f_in:
                    conteudo = f_in.read()
                
                with open(arquivo_saida_ini, "w") as f_out:
                    f_out.write(conteudo)
                
                os.remove(gatilho_ini_path)
                self.adicionar_log(f"Arquivo gatilho_ini.json do caminho {nome_caminho} processado e movido para {nome_saida_ini}", log_id=processo_id+"_ini_movido")
            except Exception as e:
                self.adicionar_log(f"ERRO ao mover arquivo gatilho_ini.json do caminho {nome_caminho}: {str(e)}", log_id=processo_id+"_erro_ini_mover")
            
            self.adicionar_log(f"Gatilho inicial do caminho {nome_caminho} enviado com sucesso!", log_id=processo_id+"_ini_sucesso")
        
        # Listar todos os arquivos JSON no diretório de entrada
        arquivos = [f for f in os.listdir(caminho["input"]) if f.lower().endswith(".json") 
                   and f != "gatilho_ini.json" and f != "gatilho_fim.json"]
        
        # Ordenar arquivos pelo nome
        arquivos.sort()
        
        self.adicionar_log(f"Encontrados {len(arquivos)} arquivos para processar no caminho {nome_caminho}.", log_id=processo_id+"_contagem")
        
        # Processar arquivos
        if caminho["lote"]:
            # Processamento em lote
            try:
                # Determinar o número de requisições simultâneas
                num_simultaneas = 1  # Padrão: uma por vez
                if self.config["fila"].isdigit():
                    num_simultaneas = int(self.config["fila"])
                    if num_simultaneas < 1:
                        num_simultaneas = 1
                
                self.adicionar_log(f"Processando em lote com {num_simultaneas} requisições simultâneas no caminho {nome_caminho}", log_id=processo_id+"_lote_inicio")
                
                # Processar arquivos em lotes
                for i in range(0, len(arquivos), num_simultaneas):
                    # Registrar o tempo de início do processamento do lote
                    tempo_inicio_lote = time.time()
                    
                    lote_atual = arquivos[i:i+num_simultaneas]
                    threads = []
                    
                    # Criar threads para cada arquivo no lote
                    for arquivo in lote_atual:
                        arquivo_path = os.path.join(caminho["input"], arquivo)
                        thread = threading.Thread(
                            target=self.processar_arquivo_individual,
                            args=(arquivo_path, arquivo, caminho, False)  # Não enviar gatilho_fim
                        )
                        threads.append(thread)
                        thread.start()
                    
                    # Aguardar todas as threads do lote terminarem
                    for thread in threads:
                        thread.join()
                    
                    # Calcular o tempo total de processamento do lote
                    tempo_fim_lote = time.time()
                    tempo_total_lote = round(tempo_fim_lote - tempo_inicio_lote, 2)  # Tempo em segundos com 2 casas decimais
                    
                    self.adicionar_log(f"Lote de {len(lote_atual)} arquivos processado no caminho {nome_caminho} em {tempo_total_lote}s", log_id=processo_id+f"_lote_{i}")
            except Exception as e:
                self.adicionar_log(f"ERRO no processamento em lote do caminho {nome_caminho}: {str(e)}", log_id=processo_id+"_erro_lote")
        else:
            # Processamento sequencial
            for i, arquivo in enumerate(arquivos):
                arquivo_path = os.path.join(caminho["input"], arquivo)
                self.processar_arquivo_individual(arquivo_path, arquivo, caminho, False)  # Não enviar gatilho_fim
                time.sleep(1)  # Pequena pausa entre requisições sequenciais
        
        # Após processar todos os arquivos, verificar se há mais arquivos na pasta além do gatilho_fim
        arquivos_restantes = [f for f in os.listdir(caminho["input"]) if f.lower().endswith(".json") 
                            and f != "gatilho_fim.json"]
        
        # Se não houver mais arquivos e o gatilho estiver ativo, enviar o gatilho_fim
        if not arquivos_restantes and caminho["gatilho_ativo"] and os.path.isfile(gatilho_fim_path):
            self.adicionar_log(f"Todos os arquivos processados. Enviando gatilho_fim para o caminho {nome_caminho}...", log_id=processo_id+"_fim_inicio")
            
            # Enviar gatilho_fim.json
            status_fim = self.enviar_requisicao(gatilho_fim_path, log_id=processo_id+"_gatilho_fim")
            
            # Mover gatilho_fim.json para a pasta de saída
            timestamp = datetime.datetime.now().strftime("%d%m%y_%H%M%S")
            nome_saida_fim = f"gatilho_fim_{timestamp}.json"
            arquivo_saida_fim = os.path.join(caminho["output"], nome_saida_fim)
            
            try:
                with open(gatilho_fim_path, "r") as f_in:
                    conteudo = f_in.read()
                
                with open(arquivo_saida_fim, "w") as f_out:
                    f_out.write(conteudo)
                
                os.remove(gatilho_fim_path)
                self.adicionar_log(f"Arquivo gatilho_fim.json do caminho {nome_caminho} processado e movido para {nome_saida_fim}", log_id=processo_id+"_fim_movido")
            except Exception as e:
                self.adicionar_log(f"ERRO ao mover arquivo gatilho_fim.json do caminho {nome_caminho}: {str(e)}", log_id=processo_id+"_erro_fim_mover")
            
            if status_fim != 200:
                self.adicionar_log(f"ERRO: Falha ao enviar gatilho_fim.json do caminho {nome_caminho}. Status: {status_fim}", log_id=processo_id+"_erro_fim_status")
            else:
                self.adicionar_log(f"Gatilho final do caminho {nome_caminho} enviado com sucesso!", log_id=processo_id+"_fim_sucesso")
        
        # Calcular o tempo total de processamento
        tempo_fim = time.time()
        tempo_total = round(tempo_fim - tempo_inicio, 2)  # Tempo em segundos com 2 casas decimais
        
        self.adicionar_log(f"Processamento de arquivos do caminho {nome_caminho} concluído! Tempo total: {tempo_total}s", log_id=processo_id+"_conclusao")
        
        # Marcar este caminho como não mais em processamento
        self._processamentos_ativos[nome_caminho] = False
    
    def processar_arquivo_individual(self, arquivo_path, arquivo_nome, caminho=None, enviar_gatilho_fim=True):
        """Processa um arquivo individual, enviando requisição e movendo para saída
        
        Args:
            arquivo_path: Caminho completo do arquivo a ser processado
            arquivo_nome: Nome do arquivo (sem o caminho)
            caminho: Dicionário com as configurações do caminho (input, output, etc.)
            enviar_gatilho_fim: Se True, envia o gatilho_fim após processar o arquivo (padrão: True)
        """
        # Registrar o tempo de início do processamento individual
        tempo_inicio_individual = time.time()
        
        # Se não for fornecido um caminho, usar o caminho atual
        if caminho is None:
            caminho = self.caminhos
            
        nome_caminho = caminho.get("nome", "atual")
        # Criar um ID único para este arquivo
        arquivo_id = f"arq_{nome_caminho}_{arquivo_nome}_{tempo_inicio_individual}"
        
        # Enviar requisição
        status = self.enviar_requisicao(arquivo_path, log_id=arquivo_id)
        
        # Gerar nome do arquivo de saída
        timestamp = datetime.datetime.now().strftime("%d%m%y_%H%M%S")
        nome_saida = f"{os.path.splitext(arquivo_nome)[0]}_{timestamp}.json"
        arquivo_saida = os.path.join(caminho["output"], nome_saida)
        
        # Mover arquivo para a pasta de saída
        try:
            with open(arquivo_path, "r") as f_in:
                conteudo = f_in.read()
            
            with open(arquivo_saida, "w") as f_out:
                f_out.write(conteudo)
            
            os.remove(arquivo_path)
            self.adicionar_log(f"Arquivo {arquivo_nome} do caminho {nome_caminho} processado e movido para {nome_saida}", log_id=arquivo_id+"_movido")
        except Exception as e:
            self.adicionar_log(f"ERRO ao mover arquivo {arquivo_nome} do caminho {nome_caminho}: {str(e)}", log_id=arquivo_id+"_erro_mover")
        
        # Se o gatilho estiver ativo e enviar_gatilho_fim for True, enviar gatilho_fim.json
        # Essa lógica foi movida para o método processar_arquivos para ser executada apenas uma vez
        # após todos os arquivos terem sido processados
        if enviar_gatilho_fim:
            gatilho_fim_path = os.path.join(caminho["input"], "gatilho_fim.json")
            if caminho["gatilho_ativo"] and os.path.isfile(gatilho_fim_path):
                # Verificar se há outros arquivos na pasta além do gatilho_fim
                arquivos_restantes = [f for f in os.listdir(caminho["input"]) if f.lower().endswith(".json") 
                                    and f != "gatilho_fim.json"]
                
                # Só enviar o gatilho_fim se não houver mais arquivos na pasta
                if not arquivos_restantes:
                    status_fim = self.enviar_requisicao(gatilho_fim_path, log_id=arquivo_id+"_gatilho_fim")
                    
                    # Mover gatilho_fim.json para a pasta de saída
                    timestamp = datetime.datetime.now().strftime("%d%m%y_%H%M%S")
                    nome_saida_fim = f"gatilho_fim_{timestamp}.json"
                    arquivo_saida_fim = os.path.join(caminho["output"], nome_saida_fim)
                    
                    try:
                        with open(gatilho_fim_path, "r") as f_in:
                            conteudo = f_in.read()
                        
                        with open(arquivo_saida_fim, "w") as f_out:
                            f_out.write(conteudo)
                        
                        os.remove(gatilho_fim_path)
                        self.adicionar_log(f"Arquivo gatilho_fim.json do caminho {nome_caminho} processado e movido para {nome_saida_fim}", log_id=arquivo_id+"_gatilho_fim_movido")
                    except Exception as e:
                        self.adicionar_log(f"ERRO ao mover arquivo gatilho_fim.json do caminho {nome_caminho}: {str(e)}", log_id=arquivo_id+"_erro_gatilho_fim_mover")
                    
                    if status_fim != 200:
                        self.adicionar_log(f"ERRO: Falha ao enviar gatilho_fim.json do caminho {nome_caminho}. Status: {status_fim}", log_id=arquivo_id+"_erro_gatilho_fim_status")
                    else:
                        self.adicionar_log(f"Gatilho final do caminho {nome_caminho} enviado com sucesso!", log_id=arquivo_id+"_gatilho_fim_sucesso")
                else:
                    self.adicionar_log(f"Ainda existem {len(arquivos_restantes)} arquivos para processar. Gatilho final não será enviado agora.", log_id=arquivo_id+"_gatilho_fim_adiado")
        
        # Calcular o tempo total de processamento individual
        tempo_fim_individual = time.time()
        tempo_total_individual = round(tempo_fim_individual - tempo_inicio_individual, 2)  # Tempo em segundos com 2 casas decimais
        self.adicionar_log(f"Arquivo {arquivo_nome} do caminho {nome_caminho} processado em {tempo_total_individual}s", log_id=arquivo_id+"_tempo_processamento")
        
        # Remover a mensagem de conclusão, pois ela já é exibida no método processar_arquivos
    
    def enviar_requisicao(self, arquivo_path, log_id=None):
        try:
            # Ler o conteúdo do arquivo JSON
            with open(arquivo_path, "r") as f:
                dados = json.load(f)
            
            # Preparar headers
            headers = {}
            
            # Adicionar token se disponível
            if self.config["token"]:
                headers["Authorization"] = f"Bearer {self.config['token']}"
            
            # Configurar autenticação básica se disponível
            auth = None
            if self.config["username"] and self.config["password"]:
                auth = (self.config["username"], self.config["password"])
            
            # Configurar timeout
            timeout = self.config["timeout"]
            
            # Construir URL completa
            url = self.config["url_base"]
            if self.config["fila"]:
                url = f"{url}/{self.config['fila']}"
            
            # Enviar requisição POST - Usar um identificador único para o log
            arquivo_nome = os.path.basename(arquivo_path)
            if log_id is None:
                log_id = f"{arquivo_nome}_{time.time()}"
            self.adicionar_log(f"Enviando requisição para `{url}` com arquivo {arquivo_nome}", log_id=log_id)
            
            # Medir o tempo de execução da requisição
            inicio = time.time()
            response = requests.post(
                url=url,
                json=dados,
                headers=headers,
                auth=auth,
                timeout=timeout
            )
            fim = time.time()
            tempo_execucao = round(fim - inicio, 2)  # Tempo em segundos com 2 casas decimais
            
            # Registrar resposta com o mesmo identificador, incluindo o tempo de execução
            self.adicionar_log(f"Resposta: Status {response.status_code} - Tempo de execução: {tempo_execucao}s (Timeout configurado: {timeout}s)", log_id=log_id)
            
            return response.status_code
        
        except requests.exceptions.Timeout as e:
            self.adicionar_log(f"ERRO de TIMEOUT na requisição: {str(e)} - Timeout configurado: {timeout}s", log_id=log_id+"_erro_timeout")
            return 408  # Request Timeout
        except Exception as e:
            self.adicionar_log(f"ERRO na requisição: {str(e)}", log_id=log_id+"_erro")
            return 500

    def create_icon_image(self):
        # Carregar a imagem do ícone a partir do arquivo na raiz do projeto
        try:
            # Caminho para o arquivo de ícone na raiz do projeto
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
            self.adicionar_log(f"Tentando carregar ícone de: {icon_path}")
            
            # Verificar se o arquivo existe
            if os.path.exists(icon_path):
                # Carregar a imagem do arquivo
                image = Image.open(icon_path)
                # Redimensionar para um tamanho adequado para ícone de bandeja
                image = image.resize((64, 64), Image.LANCZOS)
                # Converter para o formato correto para pystray
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                self.adicionar_log("Ícone carregado com sucesso")
                return image
            else:
                self.adicionar_log(f"Arquivo de ícone não encontrado: {icon_path}")
                # Criar uma imagem padrão como fallback
                return self._create_default_icon()
        except Exception as e:
            self.adicionar_log(f"Erro ao carregar ícone: {str(e)}")
            # Criar uma imagem padrão como fallback
            return self._create_default_icon()
    
    def _create_default_icon(self):
        # Criar uma imagem simples para o ícone da bandeja como fallback
        width = 64
        height = 64
        color1 = (255, 128, 0)  # Laranja
        
        # Criar uma imagem com fundo transparente
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        
        # Desenhar um círculo preenchido
        dc.ellipse((4, 4, width-4, height-4), fill=color1)
        
        # Desenhar um "P" como texto
        dc.text((width//2-10, height//2-10), "P", fill=(0, 0, 0))
        
        return image
    
    def setup_tray_icon(self):
        try:
            # Criar o menu de contexto para o ícone da bandeja
            menu = pystray.Menu(
                pystray.MenuItem('Restaurar', self.show_window),
                pystray.MenuItem('Fechar', self.quit_app)
            )
            
            # Obter a imagem do ícone
            icon_image = self.create_icon_image()
            self.adicionar_log("Imagem do ícone criada, configurando ícone da bandeja")
            
            # Criar o ícone da bandeja
            self.icon = pystray.Icon("postman_automatizado", icon_image, "Postman Automatizado", menu)
            
            # Iniciar o ícone em uma thread separada
            threading.Thread(target=self.icon.run, daemon=True).start()
            
            # Adicionar mensagem de log
            self.adicionar_log("Aplicativo minimizado para a bandeja do sistema")
        except Exception as e:
            self.adicionar_log(f"Erro ao criar ícone na bandeja: {str(e)}")
            # Tentar uma abordagem alternativa
            try:
                # Criar um ícone mais simples
                self.adicionar_log("Tentando criar ícone alternativo")
                image = Image.new('RGBA', (64, 64), (255, 128, 0, 255))
                self.icon = pystray.Icon("postman_automatizado", image, "Postman Automatizado")
                self.icon.run_detached()
                self.adicionar_log("Ícone alternativo criado na bandeja do sistema")
            except Exception as e2:
                self.adicionar_log(f"Erro ao criar ícone alternativo: {str(e2)}")
                return False
        return True
    
    def on_close(self):
        # Quando o usuário tenta fechar a janela, minimizar para a bandeja
        self.withdraw()  # Esconder a janela
        self.is_minimized = True
        
        # Criar o ícone na bandeja se ainda não existir
        if self.icon is None:
            success = self.setup_tray_icon()
            if not success:
                # Em caso de erro, mostrar mensagem e fechar normalmente
                self.adicionar_log("Não foi possível minimizar para a bandeja. Fechando o aplicativo.")
                self.destroy()
                return
        
        # Mostrar uma dica na bandeja do sistema
        try:
            import ctypes
            ctypes.windll.user32.MessageBeep(0)
        except:
            pass
        
        # Adicionar mensagem de log
        self.adicionar_log("Aplicativo minimizado para a bandeja do sistema. Clique no ícone para restaurar.")
    
    def show_window(self, icon=None, item=None):
        # Restaurar a janela quando solicitado pelo menu da bandeja ou quando outra instância tenta abrir
        self.deiconify()  # Mostrar a janela
        self.is_minimized = False
        self.focus_force()  # Trazer a janela para o primeiro plano
        self.adicionar_log("Aplicativo restaurado da bandeja do sistema")
        
        # Trazer a janela para o primeiro plano (Windows)
        try:
            import ctypes
            hwnd = ctypes.windll.user32.FindWindowW(None, self.title())
            # Restaurar a janela se estiver minimizada
            ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE = 9
            # Trazer para frente
            ctypes.windll.user32.SetForegroundWindow(hwnd)
        except Exception as e:
            self.adicionar_log(f"Erro ao tentar focar janela: {str(e)}")
            pass
    
    def quit_app(self, icon=None, item=None):
        # Fechar completamente o aplicativo quando solicitado pelo menu da bandeja
        self.adicionar_log("Fechando o aplicativo a partir da bandeja do sistema")
        
        # Parar o ícone da bandeja
        if self.icon:
            try:
                self.icon.stop()
            except:
                pass
        
        # Destruir a janela principal
        self.destroy()
    
    def minimize_to_tray(self):
        # Método para minimizar manualmente para a bandeja
        self.on_close()

class SingleInstanceApp:
    """ Limita a aplicação a uma única instância """

    def __init__(self):
        self.mutex_name = "PostmanAutomatizado_{D0E858DF-985E-4907-B7FB-8D732C3FC3B9}"
        self.mutex = CreateMutex(None, False, self.mutex_name)
        self.last_error = GetLastError()
    
    def already_running(self):
        return (self.last_error == ERROR_ALREADY_EXISTS)
        
    def __del__(self):
        if self.mutex:
            CloseHandle(self.mutex)


def find_and_focus_existing_window():
    """ Encontra e traz para frente a janela existente do aplicativo """
    try:
        import ctypes
        # Encontrar a janela pelo título
        hwnd = ctypes.windll.user32.FindWindowW(None, "Postman Automatizado")
        if hwnd:
            # Restaurar a janela se estiver minimizada
            ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE = 9
            # Trazer para frente
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            return True
        return False
    except Exception as e:
        print(f"Erro ao tentar focar janela existente: {str(e)}")
        return False


def check_pywin32_installed():
    """ Verifica se o pacote pywin32 está instalado """
    try:
        import win32api
        return True
    except ImportError:
        return False


if __name__ == "__main__":
    # Verificar se o pywin32 está instalado para a funcionalidade de instância única
    if check_pywin32_installed():
        # Verificar se já existe uma instância em execução
        app_instance = SingleInstanceApp()
        
        if app_instance.already_running():
            # Se já estiver em execução, tenta encontrar e focar a janela existente
            print("Outra instância do Postman Automatizado já está em execução.")
            if find_and_focus_existing_window():
                print("Janela existente encontrada e trazida para frente.")
            else:
                print("Não foi possível encontrar a janela existente.")
            sys.exit(0)
    else:
        print("Pacote pywin32 não encontrado. A funcionalidade de instância única não estará disponível.")
    
    # Se não estiver em execução ou se o pywin32 não estiver instalado, inicia normalmente
    app = PostmanAutomatizado()
    app.mainloop()