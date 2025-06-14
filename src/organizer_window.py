# src/organizer_window.py
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import filedialog, messagebox
from pathlib import Path
import shutil
import os
from datetime import datetime

# (A importação incorreta foi removida daqui)

# Dicionário de mapeamento de extensões para pastas
EXT_MAP = {
    "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "documents": [".pdf", ".docx", ".doc", ".txt", ".pptx", ".xlsx", ".csv", ".md"],
    "audio": [".mp3", ".wav", ".flac", ".m4a"],
    "video": [".mp4", ".mov", ".avi", ".mkv"],
    "archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "code": [".py", ".js", ".html", ".css", ".java", ".c", ".cpp"],
    "executables": [".exe", ".msi", ".bat", ".sh"]
}
# Criar um mapa reverso para busca rápida de extensão -> tipo
REVERSE_EXT_MAP = {ext: type for type, exts in EXT_MAP.items() for ext in exts}

class FolderOrganizerWindow(ttk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Organizador de Pastas Avançado")
        self.geometry("750x550")
        self.transient(parent)
        self.grab_set()

        self.target_dir = tk.StringVar()
        self.delete_empty = tk.BooleanVar(value=True)
        self.organize_mode = tk.StringVar(value="Por Tipo de Arquivo")

        self._create_widgets()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, expand=False, pady=(0, 10))
        top_frame.columnconfigure(0, weight=1)

        dir_frame = ttk.Labelframe(top_frame, text="1. Selecione a Pasta", padding=10)
        dir_frame.grid(row=0, column=0, sticky="ew")
        dir_frame.columnconfigure(0, weight=1)
        entry = ttk.Entry(dir_frame, textvariable=self.target_dir, state="readonly")
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        btn_select = ttk.Button(dir_frame, text="Procurar...", command=self.select_directory)
        btn_select.grid(row=0, column=1)

        mode_frame = ttk.Labelframe(top_frame, text="2. Escolha o Modo", padding=10)
        mode_frame.grid(row=0, column=1, sticky="ns", padx=(10, 0))
        modes = ["Por Tipo de Arquivo", "Por Data (Ano/Mês)", "Por Letra Inicial"]
        mode_cb = ttk.Combobox(mode_frame, textvariable=self.organize_mode, values=modes, state="readonly")
        mode_cb.pack()
        mode_cb.bind("<<ComboboxSelected>>", lambda e: self.run_preview())

        log_frame = ttk.Labelframe(main_frame, text="3. Pré-visualização das Ações", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=10, state="disabled")
        self.log_text.pack(fill=tk.BOTH, expand=True)

        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, expand=False)
        ttk.Checkbutton(action_frame, text="Excluir pastas vazias após organizar", variable=self.delete_empty).pack(side=tk.LEFT)
        self.btn_organize = ttk.Button(action_frame, text="Organizar Agora!", bootstyle="success", state="disabled", command=self.run_organize)
        self.btn_organize.pack(side=tk.RIGHT)

    def _log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def _clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state="disabled")

    def select_directory(self):
        path = filedialog.askdirectory(title="Selecione uma pasta")
        if path:
            self.target_dir.set(path)
            self.btn_organize.config(state="normal")
            self.run_preview()

    def run_preview(self):
        if self.target_dir.get():
            self._organize_directory(dry_run=True)
    
    def run_organize(self):
        if messagebox.askyesno("Confirmar Organização", "Isso moverá os arquivos permanentemente. Tem certeza?"):
            self._organize_directory(dry_run=False)
            messagebox.showinfo("Sucesso", "A pasta foi organizada com sucesso!")

    def _organize_directory(self, dry_run=True):
        self._clear_log()
        path = Path(self.target_dir.get())
        if not path.is_dir(): return
        mode = self.organize_mode.get()
        self._log(f"Analisando '{path.name}' | Modo: {mode}\n")
        
        files_to_move = [f for f in path.iterdir() if f.is_file()]
        if not files_to_move: self._log("Nenhum arquivo encontrado para organizar."); return

        for file_path in files_to_move:
            dest_path = None
            
            if mode == "Por Tipo de Arquivo":
                ext = file_path.suffix.lower()
                dest_folder_name = REVERSE_EXT_MAP.get(ext, "other")
                dest_path = path / dest_folder_name
            elif mode == "Por Data (Ano/Mês)":
                try:
                    mtime = file_path.stat().st_mtime
                    dt_obj = datetime.fromtimestamp(mtime)
                    dest_path = path / str(dt_obj.year) / dt_obj.strftime("%Y-%m")
                except Exception:
                    dest_path = path / "unknown_date"
            elif mode == "Por Letra Inicial":
                first_letter = file_path.name[0].upper()
                if not first_letter.isalnum(): first_letter = "#"
                dest_path = path / first_letter

            if dest_path:
                if not dry_run:
                    dest_path.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(file_path), str(dest_path))
                relative_dest = dest_path.relative_to(path)
                self._log(f"Mover: '{file_path.name}'  ->  '\\{relative_dest}\\'")
        
        if self.delete_empty.get() and not dry_run: self._delete_empty_subfolders(path)
        self._log("\nAnálise concluída.")
    
    def _delete_empty_subfolders(self, search_path: Path):
        for dirpath, dirnames, filenames in os.walk(search_path, topdown=False):
            if not dirnames and not filenames:
                try: os.rmdir(dirpath); self._log(f"Excluindo pasta vazia: {dirpath}")
                except OSError: pass