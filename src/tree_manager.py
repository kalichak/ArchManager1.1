# src/tree_manager.py
import tkinter as tk
from tkinter import simpledialog, messagebox
from pathlib import Path

from .ui_dialogs import CreateFileDialog

class TreeManager:
    # MUDANÇA: Adicionado on_update_callback
    def __init__(self, tree_widget: tk.Widget, icons: dict, on_update_callback=None):
        self.tree = tree_widget
        self.icons = icons
        self.clipboard = None
        self.drag_data = {"item": None}
        self.on_update_callback = on_update_callback # <-- NOVO

        # Bind do drag-and-drop
        self.tree.bind("<ButtonPress-1>", self._on_drag_start)
        self.tree.bind("<B1-Motion>", self._on_drag_motion)
        self.tree.bind("<ButtonRelease-1>", self._on_drag_stop)

    # Função auxiliar que chama o callback
    def _notify_update(self):
        if self.on_update_callback:
            self.on_update_callback()

    # --- Funções do CRUD agora chamam o _notify_update ---
    def add_folder(self):
        # ... (código existente)
        parent = self.tree.selection()[0] if self.tree.selection() else ""
        item_id = self._insert_item(parent, "Nova Pasta", is_folder=True)
        self.tree.selection_set(item_id)
        self.rename_item() # Renomear já notifica a atualização

    def add_file(self):
        # ... (código existente)
        parent = self.tree.selection()[0] if self.tree.selection() else ""
        # ...
        dialog = CreateFileDialog(self.tree, title="Criar Novo Arquivo")
        if dialog.result:
            item_id = self._insert_item(parent, dialog.result)
            self.tree.selection_set(item_id)
            self._notify_update() # <-- MUDANÇA

    def rename_item(self):
        # ... (código existente)
        # ...
        if new_name and new_name.strip():
            # ...
            self.tree.item(item_id, text=new_name.strip())
            # ...
            self._notify_update() # <-- MUDANÇA

    def delete_item(self):
        if not self.tree.selection(): return
        if messagebox.askyesno("Confirmar Exclusão", "Tem certeza?"):
            for item_id in self.tree.selection():
                self.tree.delete(item_id)
            self._notify_update() # <-- MUDANÇA

    def paste_item(self):
        if not self.clipboard: return
        # ... (código existente)
        parent = self.tree.selection()[0] if self.tree.selection() else ""
        # ...
        self.build_from_structure(self.clipboard, parent_id=parent)
        # build_from_structure já notifica a atualização

    def clear_tree(self):
        self.tree.delete(*self.tree.get_children())
        self._notify_update() # <-- MUDANÇA

    def build_from_structure(self, structure: dict, parent_id=""):
        if not structure: return
        for name, children in structure.items():
            is_folder = bool(children)
            item_id = self._insert_item(parent_id, name, is_folder=is_folder)
            if children:
                self.build_from_structure(children, parent_id=item_id)
        self._notify_update() # Notifica após construir tudo

    def _on_drag_stop(self, event):
        # MUDANÇA: Notifica quando o drag-and-drop termina
        if self.drag_data["item"]:
            self.drag_data["item"] = None
            self._notify_update()
            
    # O resto das funções (get_icon, insert_item, copy, find, export, etc.) pode ser mantido
    # da versão anterior, pois a lógica principal não muda.
    def _get_icon_for_file(self, filename: str):
        ext = Path(filename).suffix.lower()
        if ext in ['.py', '.pyw']: return self.icons.get("python")
        if ext in ['.html', '.htm']: return self.icons.get("html")
        if ext == '.css': return self.icons.get("css")
        if ext == '.js': return self.icons.get("javascript")
        if ext == '.json': return self.icons.get("json")
        if ext in ['.txt', '.md', '.log']: return self.icons.get("text")
        if ext in ['.zip', '.rar', '.7z', '.gz']: return self.icons.get("archive")
        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico']: return self.icons.get("image")
        return self.icons.get("file")

    def _insert_item(self, parent, text, is_folder=False):
        icon = self.icons.get("folder") if is_folder else self._get_icon_for_file(text)
        options = {"text": text}
        if is_folder: options["open"] = True
        if icon: options["image"] = icon
        return self.tree.insert(parent, tk.END, **options)

    def copy_item(self):
        if not self.tree.selection(): return
        item_id = self.tree.selection()[0]
        structure = {self.tree.item(item_id, "text"): self.get_structure(item_id)}
        self.clipboard = structure

    def find_item(self):
        search_term = simpledialog.askstring("Localizar Item", "Digite o nome (ou parte) do item:")
        if not search_term: return
        found_item = self._find_recursive(search_term.lower())
        if found_item: self.tree.selection_set(found_item); self.tree.see(found_item)
        else: messagebox.showinfo("Não Encontrado", f"Nenhum item contendo '{search_term}' foi encontrado.")

    def _find_recursive(self, search_term, parent_item=""):
        for item_id in self.tree.get_children(parent_item):
            if search_term in self.tree.item(item_id, "text").lower(): return item_id
            found = self._find_recursive(search_term, item_id)
            if found: return found
        return None
        
    def get_structure(self, p_id=""): return {self.tree.item(i,"text"):self.get_structure(i) or None for i in self.tree.get_children(p_id)}

    def export_to_text(self, project_name="Meu Projeto"):
        if not self.tree.get_children(): return ""
        lines = [f"{project_name}/"]
        children = self.tree.get_children()
        for i, item_id in enumerate(children):
            self._export_recursive(item_id, "    ", i == len(children) - 1, lines)
        return "\n".join(lines)
        
    def _export_recursive(self, item_id, prefix, is_last, lines):
        lines.append(f"{prefix}{'└── ' if is_last else '├── '}{self.tree.item(item_id, 'text')}")
        children = self.tree.get_children(item_id)
        if children:
            new_prefix = prefix + ("    " if is_last else "│   ")
            for i, child_id in enumerate(children):
                self._export_recursive(child_id, new_prefix, i == len(children) - 1, lines)
    
    # Drag-and-drop
    def _on_drag_start(self, event): self.drag_data["item"] = self.tree.identify_row(event.y)
    def _on_drag_motion(self, event):
        if not self.drag_data["item"]: return
        target = self.tree.identify_row(event.y)
        is_folder_target = target and not bool(Path(self.tree.item(target, "text")).suffix)
        if is_folder_target: self.tree.move(self.drag_data["item"], target, tk.END)