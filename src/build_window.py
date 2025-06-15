
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import filedialog, messagebox
from pathlib import Path
import subprocess, threading, queue, os, sys

class BuildWindow(ttk.Toplevel):
    def __init__(self, parent):

        """Janela de Build para compilar projetos Python em executáveis."""
        if not hasattr(sys, 'frozen') or not sys.frozen:  # Verifica se está rodando como executável
            sys.path.append(str(Path(__file__).resolve().parent))
        ttk.Style().theme_use("morph")  # Define o tema escuro

        # Inicializa a janela
        super().__init__(parent); self.title("BuildExE");
        self.transient(parent); self.grab_set()
        self.geometry("980x800"); self.resizable(True, True)
        
        # UI Variables
        self.project_root_path = tk.StringVar(); self.python_exe_path = tk.StringVar()
        self.script_path = tk.StringVar(); self.output_name = tk.StringVar()
        self.icon_path = tk.StringVar(); self.package_type = tk.StringVar(value="onefile")
        self.clean_build = tk.BooleanVar(value=True); self.create_installer = tk.BooleanVar(value=False)
        self.app_version = tk.StringVar(value="1.0.0"); self.app_publisher = tk.StringVar(value="Sua Empresa")
        
        self.queue = queue.Queue(); self._create_widgets(); self.after(100, self.process_queue)
        
    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=20); main_frame.pack(fill=tk.BOTH, expand=True)
        config_frame = ttk.Labelframe(main_frame, text="Configurações de Build", padding=10)
        config_frame.pack(fill=tk.X, pady=(0, 10)); config_frame.columnconfigure(1, weight=1)

        ttk.Label(config_frame, text="Pasta Raiz do Projeto:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(config_frame, textvariable=self.project_root_path, state="readonly").grid(row=0, column=1, sticky="ew")
        ttk.Button(config_frame, text="Procurar...", command=self.select_project_root).grid(row=0, column=2, padx=5)
        
        ttk.Label(config_frame, text="Interpretador Python:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(config_frame, textvariable=self.python_exe_path, state="readonly").grid(row=1, column=1, sticky="ew")
        
        ttk.Label(config_frame, text="Script Principal:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(config_frame, textvariable=self.script_path, state="readonly").grid(row=2, column=1, sticky="ew")

        ttk.Label(config_frame, text="Nome do App:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(config_frame, textvariable=self.output_name).grid(row=3, column=1, columnspan=2, sticky="ew")
        
        ttk.Label(config_frame, text="Ícone (.ico):").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(config_frame, textvariable=self.icon_path, state="readonly").grid(row=4, column=1, sticky="ew")
        ttk.Button(config_frame, text="Procurar...", command=self.select_icon).grid(row=4, column=2, padx=5)

        options_frame = ttk.Labelframe(main_frame, text="Opções", padding=10)
        options_frame.pack(fill=tk.X, pady=(0, 15)); options_frame.columnconfigure(1, weight=1)
        ttk.Radiobutton(options_frame, text="Arquivo Único (.exe)", variable=self.package_type, value="onefile").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Radiobutton(options_frame, text="Pasta com Arquivos", variable=self.package_type, value="onedir").grid(row=1, column=0, sticky="w", padx=5)
        ttk.Checkbutton(options_frame, text="Limpar cache antes do build (--clean)", variable=self.clean_build).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        
        installer_check = ttk.Checkbutton(options_frame, text="Criar instalador após o build", variable=self.create_installer, bootstyle="success-round-toggle")
        installer_check.grid(row=0, column=1, rowspan=3, sticky="w", padx=20)
        
        log_frame = ttk.Labelframe(main_frame, text="Log de Saída", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, state="disabled", bg="#2b2b2b", fg="white", font=("Courier New", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        log_frame.pack(fill=tk.BOTH, expand=True)
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, state="disabled", bg="#2b2b2b", fg="white", font=("Courier New", 9))
        self.log_text.grid(row=0, column=0, sticky="nsew")  # Use grid para expandir corretamente

        
        
        self.btn_build = ttk.Button(main_frame, text="Iniciar Processo Completo de Build", bootstyle="success", state="disabled", command=self.run_full_process)
        self.btn_build.pack(fill=tk.X, pady=(15, 0), ipady=10)
        main_frame.rowconfigure(2, weight=1)  # Deixe espaço expansível para log_frame
        main_frame.columnconfigure(0, weight=1)

        
        
    def select_project_root(self):
        path = filedialog.askdirectory(title="Selecione a Pasta Raiz do seu Projeto")
        if not path: return
        root = Path(path); self.project_root_path.set(path)
        venv_path = next((p for p in [root/"venv", root/".venv"] if (p/"Scripts"/"python.exe").exists()), None)
        python_exe = str(venv_path/"Scripts"/"python.exe") if venv_path else ""
        self.python_exe_path.set(python_exe)
        main_py = next(root.glob("main.py"), None) or next(root.glob("*.py"), None)
        self.script_path.set(str(main_py) if main_py else "")
        self.output_name.set(root.name)
        if all([self.project_root_path.get(), self.python_exe_path.get(), self.script_path.get()]):
            self.btn_build.config(state="normal")
        else:
            messagebox.showwarning("Atenção", "Não foi possível detectar 'python.exe' ou um arquivo '.py' principal. Verifique a estrutura e a presença de uma venv.")
            self.btn_build.config(state="disabled")

    def _run_pyinstaller(self, force_onedir=False):
        python_exe_path = Path(self.python_exe_path.get())
        workdir = Path(self.project_root_path.get())

        # --- ABORDAGEM FINAL E ROBUSTA ---
        # Procura pelo executável do pyinstaller na pasta Scripts da venv
        pyinstaller_exe = python_exe_path.parent / "pyinstaller.exe"
        if not pyinstaller_exe.exists():
            self.queue.put(("log", f"ERRO FATAL: '{pyinstaller_exe}' não encontrado. A preparação do ambiente pode ter falhado."))
            return False

        # O comando agora chama o pyinstaller.exe diretamente
        command = [str(pyinstaller_exe), self.script_path.get(), "--noconfirm"]
        
        if force_onedir or self.package_type.get() == 'onedir': command.append("--onedir")
        else: command.append("--onefile")
        
        command.append("--windowed")
        if self.output_name.get(): command.extend(["--name", self.output_name.get()])
        if self.icon_path.get(): command.extend(["--icon", self.icon_path.get()])
        if self.clean_build.get(): command.extend(["--clean"])
        
        assets_path = workdir / "assets"
        if assets_path.is_dir(): command.extend(["--add-data", f"{assets_path}{os.pathsep}assets"])
        
        return self.execute_command(command, workdir)
        
    def execute_command(self, command, workdir):
        self.queue.put(("log", f"\nComando: {' '.join(command)}\nEm: {workdir}\n" + "-"*50))
        try:
            process = subprocess.Popen(command, cwd=workdir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
            for line in iter(process.stdout.readline, ''):
                self.queue.put(("log", line.strip()))
            ret_code = process.wait()
            self.queue.put(("log", "-"*50 + f"\n---> Código de Saída: {ret_code} <---"))
            return ret_code == 0
        except Exception as e:
            self.queue.put(("log", f"\nERRO CRÍTICO: {e}"))
            return False
            
    # O resto das funções (run_full_process, _build_thread, etc.) permanecem,
    # mas a lógica interna foi simplificada para ser mais direta.
    def select_icon(self):
        path = filedialog.askopenfilename(title="Selecione o ícone .ico", filetypes=[("Icon Files", "*.ico")]);
        if path: self.icon_path.set(path)
    def run_full_process(self):
        if not all([self.project_root_path.get(), self.python_exe_path.get(), self.script_path.get()]):
            messagebox.showerror("Erro", "Campos essenciais não preenchidos."); return
        self.btn_build.config(state="disabled"); self._clear_log()
        threading.Thread(target=self._build_thread, daemon=True).start()
    def _build_thread(self):
        python_exe = self.python_exe_path.get(); workdir = Path(self.project_root_path.get())
        req_file = workdir / "requirements.txt"
        self.queue.put(("log", "--- [ETAPA 1/3] Preparando Ambiente ---"))
        install_commands = [[python_exe, "-m", "pip", "install", "--upgrade", "pip", "pyinstaller", "wheel"]]
        if req_file.exists(): install_commands.append([python_exe, "-m", "pip", "install", "-r", str(req_file)])
        for cmd in install_commands:
            if not self.execute_command(cmd, workdir):
                self.queue.put(("end", "ERRO FATAL: Falha na instalação de dependências.")); return
        self.queue.put(("log", "Ambiente preparado com sucesso."))
        
        self.queue.put(("log", "\n--- [ETAPA 2/3] Compilando com PyInstaller ---"))
        if not self._run_pyinstaller(force_onedir=self.create_installer.get()):
            self.queue.put(("end", "ERRO FATAL: Falha na compilação.")); return
        self.queue.put(("log", "Executável criado com sucesso."))
        
        if self.create_installer.get():
            self.queue.put(("log", "\n--- [ETAPA 3/3] Criando Instalador ---"))
            if not self._run_inno_setup(): self.queue.put(("end", "ERRO: Falha na criação do instalador."))
            else: self.queue.put(("end", "SUCESSO: Processo concluído! Instalador criado."))
        else:
            self.queue.put(("end", "SUCESSO: Processo concluído! Executável criado."))
    def process_queue(self):
        try:
            while True:
                msg_type, value = self.queue.get_nowait()
                if msg_type == "log": self._log(value)
                elif msg_type == "end":
                    self.btn_build.config(state="normal")
                    if "ERRO" in value: messagebox.showerror("Processo Falhou", value)
                    else: messagebox.showinfo("Processo Finalizado", value)
                    return
        except queue.Empty: pass; self.after(100, self.process_queue)
    def _log(self, m):
        self.log_text.config(state="normal"); self.log_text.insert(tk.END, str(m) + "\n"); self.log_text.see(tk.END); self.log_text.config(state="disabled")
    def _clear_log(self):
        self.log_text.config(state="normal"); self.log_text.delete("1.0", tk.END); self.log_text.config(state="disabled")
    def _run_inno_setup(self):
        inno_path = Path("C:/Program Files (x86)/Inno Setup 6/ISCC.exe")
        if not inno_path.exists(): self.queue.put(("log", f"ERRO: Inno Setup não encontrado.")); return False
        script_content = self._generate_inno_script()
        workdir = Path(self.project_root_path.get()); iss_path = workdir / "installer_script.iss"
        with open(iss_path, "w", encoding="utf-8") as f: f.write(script_content)
        return self.execute_command([str(inno_path), str(iss_path)], workdir)
    def _generate_inno_script(self):
        app_name = self.output_name.get(); workdir = Path(self.project_root_path.get())
        dist_folder = workdir / "dist" / (app_name if self.create_installer.get() or self.package_type.get() == 'onedir' else "")
        source_files = str(dist_folder).replace("/", "\\")
        main_exe = app_name + ".exe"
        if self.package_type.get() == 'onedir': source_files += "\\*" # Copia tudo da pasta
        else: source_files += f"\\{main_exe}" # Copia só o exe
        
        return f"""
[Setup]
AppName={app_name}
AppVersion={self.app_version.get()}
AppPublisher={self.app_publisher.get()}
DefaultDirName={{autopf}}\\{app_name}
OutputBaseFilename={app_name}-{self.app_version.get()}-setup
OutputDir={workdir}
Compression=lzma2
SolidCompression=yes
[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\\BrazilianPortuguese.isl"
[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}";
[Files]
Source: "{source_files}"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{{group}}\\{app_name}"; Filename: "{{app}}\\{main_exe}"
Name: "{{autodesktop}}\\{app_name}"; Filename: "{{app}}\\{main_exe}"; Tasks: desktopicon
[Run]
Filename: "{{app}}\\{main_exe}"; Description: "{{cm:LaunchProgram,{app_name}}}"; Flags: nowait postinstall skipifsilent
"""