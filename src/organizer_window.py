# src/organizer_window.py
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import filedialog, messagebox
from pathlib import Path
import shutil, os

# Dicionário principal de categorias por extensão
EXT_MAP = {
    "Imagens": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "Documentos": [".pdf", ".docx", ".doc", ".txt", ".pptx", ".xlsx", ".csv", ".md", ".odt"],
    "Apresentações": [".ppt", ".pptx"], "Planilhas": [".xls", ".xlsx"],
    "PDFs": [".pdf"], "Textos": [".txt", ".md", ".log"], "Arquivos de Código": [".py", ".js", ".html", ".css", ".java", ".c", ".cpp"],
    "Audio": [".mp3", ".wav", ".flac", ".m4a"], "video": [".mp4", ".mov", ".avi", ".mkv"],
    "Arquivos": [".zip", ".rar", ".7z", ".tar", ".gz"], "code": [".py", ".js", ".html", ".css"],
}
REVERSE_EXT_MAP = {ext: type for type, exts in EXT_MAP.items() for ext in exts}

# --- NOVO: REGRAS DE SUBPASTAS POR PALAVRA-CHAVE ---
# Formato: CategoriaPrincipal: { NomeDaSubpasta: [lista_de_palavras_chave_em_minúsculo] }
KEYWORD_MAP = {
    "Documentos": {
        "Invoices": ["invoice", "nota fiscal", "nf", "fatura"],
        "Reports": ["report", "relatorio", "relatório"],
        "Resumes": ["resume", "cv", "curriculo", "currículo"],
        "Contracts": ["contract", "contrato"]
    },
    "Imagens": {
        "Screenshots": ["screenshot", "captura de tela"],
        "Logos": ["logo"]
    },
    "Audio": {
        "Podcasts": ["podcast"],
        "Music": ["music", "musica", "canção", "canção"]
    },
    # Você pode adicionar mais categorias e regras aqui!
}

class FolderOrganizerWindow(ttk.Toplevel):
    # O __init__ e _create_widgets podem ser mantidos, a mudança principal é na lógica.
    def __init__(self, parent):
        super().__init__(parent); self.title("Organizador de Pastas Avançado"); self.geometry("750x550")
        self.transient(parent); self.grab_set()
        self.target_dir = tk.StringVar(); self.organize_mode = tk.StringVar(value="Por Tipo e Palavra-Chave")
        self._create_widgets()
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=15); main_frame.pack(fill=tk.BOTH, expand=True)
        top_frame = ttk.Frame(main_frame); top_frame.pack(fill=tk.X, expand=False, pady=(0, 10))
        top_frame.columnconfigure(0, weight=1)
        dir_frame = ttk.Labelframe(top_frame, text="1. Selecione a Pasta", padding=10); dir_frame.grid(row=0, column=0, sticky="ew")
        dir_frame.columnconfigure(0, weight=1)
        ttk.Entry(dir_frame, textvariable=self.target_dir, state="readonly").grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ttk.Button(dir_frame, text="Procurar...", command=self.select_directory).grid(row=0, column=1)
        mode_frame = ttk.Labelframe(top_frame, text="2. Modo de Organização", padding=10); mode_frame.grid(row=0, column=1, sticky="ns", padx=(10, 0))
        modes = ["Por Tipo e Palavra-Chave"]; ttk.Combobox(mode_frame, textvariable=self.organize_mode, values=modes, state="readonly").pack()
        log_frame = ttk.Labelframe(main_frame, text="3. Pré-visualização das Ações", padding=10); log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=10, state="disabled"); self.log_text.pack(fill=tk.BOTH, expand=True)
        action_frame = ttk.Frame(main_frame); action_frame.pack(fill=tk.X, expand=False)
        self.btn_organize = ttk.Button(action_frame, text="Organizar Agora!", bootstyle="success", state="disabled", command=self.run_organize); self.btn_organize.pack(side=tk.RIGHT)

    def _organize_directory(self, dry_run=True):
        self._clear_log(); path = Path(self.target_dir.get())
        if not path.is_dir(): return
        self._log(f"Analisando '{path.name}'...\n")
        
        files_to_move = [f for f in path.iterdir() if f.is_file()]
        if not files_to_move: self._log("Nenhum arquivo encontrado para organizar."); return

        for file_path in files_to_move:
            file_name_lower = file_path.name.lower()
            main_category = REVERSE_EXT_MAP.get(file_path.suffix.lower(), "Outros")
            
            # --- NOVA LÓGICA DE SUBPASTA ---
            subfolder = None
            if main_category in KEYWORD_MAP:
                for subfolder_name, keywords in KEYWORD_MAP[main_category].items():
                    if any(keyword in file_name_lower for keyword in keywords):
                        subfolder = subfolder_name
                        break # Encontrou a primeira regra, para aqui
            
            # Monta o caminho final
            if subfolder:
                dest_path = path / main_category / subfolder
            else:
                dest_path = path / main_category
            
            if not dry_run:
                dest_path.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file_path), str(dest_path))
            relative_dest = dest_path.relative_to(path)
            self._log(f"Mover: '{file_path.name}'  ->  '\\{relative_dest}\\'")
        
        self._log("\nAnálise concluída.")

    # O resto das funções (select_directory, run_preview, run_organize, log, etc.) permanece o mesmo.
    def select_directory(self):
        path = filedialog.askdirectory(title="Selecione uma pasta")
        if path:
            self.target_dir.set(path); self.btn_organize.config(state="normal"); self.run_preview()
    def run_preview(self):
        if self.target_dir.get(): self._organize_directory(dry_run=True)
    def run_organize(self):
        if messagebox.askyesno("Confirmar Organização", "Isso moverá os arquivos permanentemente. Tem certeza?"):
            self._organize_directory(dry_run=False); messagebox.showinfo("Sucesso", "A pasta foi organizada com sucesso!")
    def _log(self, message):
        self.log_text.config(state="normal"); self.log_text.insert(tk.END, message + "\n"); self.log_text.see(tk.END); self.log_text.config(state="disabled")
    def _clear_log(self):
        self.log_text.config(state="normal"); self.log_text.delete("1.0", tk.END); self.log_text.config(state="disabled")