# src/tree_manager.py
import tkinter as tk
from tkinter import simpledialog, messagebox
from pathlib import Path

from .ui_dialogs import CreateFileDialog

class TreeManager:
    """Gerencia todas as operações do widget Treeview."""

    def __init__(self, tree_widget: tk.Widget, folder_icon: tk.Image, file_icon: tk.Image):
        self.tree = tree_widget
        self.folder_icon = folder_icon
        self.file_icon = file_icon
        self.drag_data = {"item": None}

        # Bind de eventos
        self.tree.bind("<ButtonPress-1>", self._on_drag_start)
        self.tree.bind("<B1-Motion>", self._on_drag_motion)
        self.tree.bind("<ButtonRelease-1>", self._on_drag_stop)

    def _is_file(self, item_text: str) -> bool:
        """Verifica se um item é um arquivo baseado no texto (se contém '.')."""
        return '.' in Path(item_text).name

    def add_folder(self):
        parent = self.tree.selection()[0] if self.tree.selection() else ""
        item_id = self.tree.insert(parent, tk.END, text="Nova Pasta", image=self.folder_icon, open=True)
        self.tree.selection_set(item_id)
        self.rename_item()

    def add_file(self):
        parent = self.tree.selection()[0] if self.tree.selection() else ""
        if parent and self._is_file(self.tree.item(parent, "text")):
            messagebox.showwarning("Ação Inválida", "Não é possível adicionar um item dentro de um arquivo.")
            return

        dialog = CreateFileDialog(self.tree, title="Criar Novo Arquivo")
        if dialog.result:
            item_id = self.tree.insert(parent, tk.END, text=dialog.result, image=self.file_icon)
            self.tree.selection_set(item_id)

    def rename_item(self):
        if not self.tree.selection():
            return
        item_id = self.tree.selection()[0]
        current_name = self.tree.item(item_id, "text")
        new_name = simpledialog.askstring("Renomear Item", "Novo nome:", initialvalue=current_name)
        if new_name and new_name.strip():
            self.tree.item(item_id, text=new_name.strip())
            is_file = self._is_file(new_name.strip())
            self.tree.item(item_id, image=self.file_icon if is_file else self.folder_icon)

    def delete_item(self):
        if not self.tree.selection():
            return
        if messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir o(s) item(ns) selecionado(s)?"):
            for item_id in self.tree.selection():
                self.tree.delete(item_id)

    def clear_tree(self):
        self.tree.delete(*self.tree.get_children())

    def get_structure(self, parent_id=""):
        structure = {}
        for item_id in self.tree.get_children(parent_id):
            text = self.tree.item(item_id, "text")
            children_structure = self.get_structure(item_id)
            structure[text] = children_structure if children_structure else None
        return structure

    def build_from_structure(self, structure: dict, parent_id=""):
        if not structure:
            return
        for name, children in structure.items():
            is_file = self._is_file(name) or children is None
            icon = self.file_icon if is_file else self.folder_icon
            
            item_id = self.tree.insert(parent_id, tk.END, text=name, image=icon, open=True)
            if children:
                self.build_from_structure(children, parent_id=item_id)

    def _on_drag_start(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.drag_data["item"] = item

    def _on_drag_motion(self, event):
        if not self.drag_data["item"]:
            return
        target_item = self.tree.identify_row(event.y)
        if target_item and not self._is_file(self.tree.item(target_item, "text")):
            self.tree.move(self.drag_data["item"], target_item, tk.END)

    def _on_drag_stop(self, event):
        self.drag_data["item"] = None