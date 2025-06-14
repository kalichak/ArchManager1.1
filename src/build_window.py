# src/build_window.py
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import filedialog, messagebox
from pathlib import Path
import subprocess
import threading
import queue

class BuildWindow(ttk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Construtor de Executável (PyInstaller)")
        self.geometry("800x600")
        self.transient(parent)
        self.grab_set()

        # Variáveis de UI
        self.script_path = tk.StringVar()
        self.is_onefile = tk.BooleanVar(value=True)
        self.is_windowed = tk.BooleanVar(value=True)
        self.icon_path = tk.StringVar()
        self.data_to_add = tk.StringVar(value="assets;assets")

        self.queue = queue.Queue()
        self._create_widgets()
        self.after(100, self.process_queue)

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Configurações
        settings_frame = ttk.Labelframe(main_frame, text="Configurações da Compilação", padding=10)
        settings_frame.pack(fill=tk.X, expand=False, pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)

        ttk.Label(settings_frame, text="Script Principal (.py):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        entry_script = ttk.Entry(settings_frame, textvariable=self.script_path, state="readonly")
        entry_script.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(settings_frame, text="Procurar...", command=self.select_script).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(settings_frame, text="Ícone do .exe:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        entry_icon = ttk.Entry(settings_frame, textvariable=self.icon_path, state="readonly")
        entry_icon.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(settings_frame, text="Procurar...", command=self.select_icon).grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(settings_frame, text="Adicionar Dados (pasta;nome):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        entry_data = ttk.Entry(settings_frame, textvariable=self.data_to_add)
        entry_data.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        options_frame = ttk.Frame(settings_frame)
        options_frame.grid(row=3, column=1, sticky="w", pady=5)
        ttk.Checkbutton(options_frame, text="Arquivo Único (.exe)", variable=self.is_onefile).pack(side=tk.LEFT)
        ttk.Checkbutton(options_frame, text="Sem Console (App de Janela)", variable=self.is_windowed).pack(side=tk.LEFT, padx=10)

        # Log de compilação
        log_frame = ttk.Labelframe(main_frame, text="Log de Compilação", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, state="disabled", bg="#2b2b2b", fg="white")
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Botão de ação
        self.btn_build = ttk.Button(main_frame, text="Compilar!", bootstyle="success", state="disabled", command=self.run_build)
        self.btn_build.pack(pady=10, fill=tk.X)

    def select_script(self):
        path = filedialog.askopenfilename(title="Selecione o script .py principal", filetypes=[("Python Files", "*.py")])
        if path:
            self.script_path.set(path)
            self.btn_build.config(state="normal")
    
    def select_icon(self):
        path = filedialog.askopenfilename(title="Selecione o ícone .ico", filetypes=[("Icon Files", "*.ico")])
        if path: self.icon_path.set(path)

    def run_build(self):
        script = self.script_path.get()
        if not script:
            messagebox.showerror("Erro", "Selecione o script principal.")
            return

        command = ["pyinstaller", Path(script).name]
        if self.is_onefile.get(): command.append("--onefile")
        if self.is_windowed.get(): command.append("--windowed")
        if self.icon_path.get(): command.extend(["--icon", self.icon_path.get()])
        if self.data_to_add.get():
            for data in self.data_to_add.get().split(','):
                command.extend(["--add-data", data.strip()])

        self.btn_build.config(state="disabled")
        self._clear_log()
        self._log("Iniciando a compilação...")
        self._log(f"Comando: {' '.join(command)}\n")

        # Roda o processo em uma thread para não travar a UI
        thread = threading.Thread(target=self.execute_command, args=(command, Path(script).parent), daemon=True)
        thread.start()

    def execute_command(self, command, workdir):
        try:
            process = subprocess.Popen(command, cwd=workdir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
            for line in iter(process.stdout.readline, ''):
                self.queue.put(line)
            process.stdout.close()
            process.wait()
        except Exception as e:
            self.queue.put(f"\nERRO CRÍTICO: {e}")
        finally:
            self.queue.put(None) # Sinal de fim

    def process_queue(self):
        try:
            while True:
                line = self.queue.get_nowait()
                if line is None:
                    self._log("\nCompilação concluída!")
                    self.btn_build.config(state="normal")
                    return
                self._log(line.strip())
        except queue.Empty:
            pass
        self.after(100, self.process_queue)

    def _log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def _clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state="disabled")