# src/ui_dialogs.py
import tkinter as tk
from tkinter import simpledialog
import ttkbootstrap as ttk
from .app_config import FILE_EXTENSIONS

class CreateFileDialog(simpledialog.Dialog):
    """Caixa de diálogo para criar um novo arquivo com seleção de extensão."""
    def __init__(self, parent, title=None):
        self.result = None
        super().__init__(parent, title=title)

    def body(self, master):
        ttk.Label(master, text="Nome do Arquivo:", justify="left").grid(row=0, padx=5, pady=5, sticky="w")
        self.entry_name = ttk.Entry(master, width=30)
        self.entry_name.grid(row=1, padx=5, sticky="ew")

        ttk.Label(master, text="Extensão:", justify="left").grid(row=2, padx=5, pady=5, sticky="w")
        self.combo_ext = ttk.Combobox(master, values=FILE_EXTENSIONS, state="readonly")
        self.combo_ext.grid(row=3, padx=5, sticky="ew")
        self.combo_ext.set(FILE_EXTENSIONS[0]) # Padrão
        return self.entry_name # Foco inicial

    def apply(self):
        filename = self.entry_name.get().strip()
        extension = self.combo_ext.get()
        if filename:
            self.result = f"{filename}{extension}"