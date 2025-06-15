# src/tree_manager.py
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import simpledialog, messagebox
from pathlib import Path
import logging
from .ui_dialogs import CreateFileDialog

log = logging.getLogger(__name__)

class TreeManager:
    def __init__(self, tree_widget: ttk.Treeview, icons: dict):
        self.tree = tree_widget
        self.icons = icons
        self.clipboard = None
        self.drag_data = {"item": None}
        self.on_update_callback = None
        self._bind_events()

    def set_on_update_callback(self, callback):
        self.on_update_callback = callback
    
    def add_folder(self):
        parent_id = self.get_selected_item_as_folder()
        folder_name = simpledialog.askstring("Nova Pasta", "Digite o nome da nova pasta:")
        if folder_name and folder_name.strip():
            name = folder_name.strip()
            item_id = self._insert_item(parent_id, name, is_folder=True)
            self.tree.selection_set(item_id); self.tree.see(item_id)
            self._notify_update(f"Pasta '{name}' criada.")

    def add_file(self):
        parent_id = self.get_selected_item_as_folder()
        dialog = CreateFileDialog(self.tree, title="Criar Novo Arquivo")
        if dialog.result:
            name = dialog.result
            item_id = self._insert_item(parent_id, name)
            self.tree.selection_set(item_id); self.tree.see(item_id)
            self._notify_update(f"Arquivo '{name}' criado.")

    def rename_item(self):
        item_id = self.get_selected_item()
        if not item_id: return
        current_name = self.tree.item(item_id, "text")
        new_name = simpledialog.askstring("Renomear", "Novo nome:", initialvalue=current_name)
        if new_name and new_name.strip():
            name = new_name.strip()
            self.tree.item(item_id, text=name); self._update_icon(item_id)
            self._notify_update(f"'{current_name}' renomeado para '{name}'.")

    def delete_selected_items(self):
        selected_ids = self.tree.selection()
        if not selected_ids: return
        item_names = [f"'{self.tree.item(i, 'text')}'" for i in selected_ids]
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir {', '.join(item_names)}?"):
            for item_id in selected_ids: self.tree.delete(item_id)
            self._notify_update(f"{len(item_names)} item(s) excluído(s).")
            
    def copy_item(self):
        item_id = self.get_selected_item()
        if not item_id: return
        item_text = self.tree.item(item_id, "text")
        self.clipboard = {item_text: self.get_structure(item_id)}
        self._notify_update(f"Item '{item_text}' copiado.")

    def paste_item(self):
        if not self.clipboard: return
        parent_id = self.get_selected_item_as_folder()
        self.build_from_structure(self.clipboard, parent_id=parent_id)

    def find_item(self):
        search_term = simpledialog.askstring("Localizar", "Digite o nome do item:")
        if not search_term: return
        found_item = self._find_recursive(search_term.lower())
        if found_item:
            self.tree.selection_set(found_item); self.tree.see(found_item); self.tree.focus(found_item)
        else: messagebox.showinfo("Não Encontrado", f"Nenhum item contendo '{search_term}' foi encontrado.")

    def clear_tree(self):
        self.tree.delete(*self.tree.get_children()); self._notify_update("Árvore limpa.")
        
    def get_structure(self, parent_id=""):
        return {self.tree.item(i, "text"): self.get_structure(i) or None for i in self.tree.get_children(parent_id)}
        
    def build_from_structure(self, structure: dict, parent_id=""):
        if not structure: return
        for name, children in structure.items():
            is_folder = bool(children)
            item_id = self._insert_item(parent_id, name, is_folder=is_folder)
            if children: self.build_from_structure(children, parent_id=item_id)
        self._notify_update("Estrutura carregada do preset.")
        
    def export_to_text(self, project_name="MeuProjeto"):
        if not self.tree.get_children(): return f"{project_name}/"
        lines = [f"{project_name}/"]; children = self.tree.get_children()
        for i, item_id in enumerate(children):
            self._export_recursive(item_id, "    ", i == len(children) - 1, lines)
        return "\n".join(lines)
    
    def get_selected_item(self):
        selection = self.tree.selection(); return selection[0] if selection else None
        
    def get_selected_item_as_folder(self):
        item_id = self.get_selected_item()
        if not item_id: return ""
        return item_id if self.is_folder_node(item_id) else self.tree.parent(item_id)

    def is_folder_node(self, item_id):
        if not item_id: return True
        if self.tree.get_children(item_id): return True
        item_text = self.tree.item(item_id, "text")
        # Um arquivo sem extensão ainda é tratado como pasta (ex: 'LICENSE')
        return not Path(item_text).suffix
        
    def _bind_events(self):
        self.tree.bind("<ButtonPress-1>", self._on_drag_start)
        self.tree.bind("<B1-Motion>", self._on_drag_motion)
        self.tree.bind("<ButtonRelease-1>", self._on_drag_stop)

    def _notify_update(self, message: str):
        log.info(message)
        if self.on_update_callback: self.on_update_callback()

    def _get_icon_for_file(self, filename: str):
        ext = Path(filename).suffix.lower()
        mapping = { ".py": "python", ".html": "html", ".css": "css", ".js": "javascript", ".json": "json",
                    ".txt": "text", ".md": "text", ".zip": "archive", ".rar": "archive",
                    ".png": "image", ".jpg": "image", ".svg": "image", ".ico": "image"}
        return self.icons.get(mapping.get(ext, "file"))

    def _insert_item(self, parent_id, text, is_folder=False):
        icon = self.icons.get("folder") if is_folder else self._get_icon_for_file(text)
        opts = {"text": text, "open": True};
        if icon: opts["image"] = icon
        return self.tree.insert(parent_id, tk.END, **opts)

    def _update_icon(self, item_id):
        is_folder = self.is_folder_node(item_id)
        icon_key = "folder" if is_folder else self._get_icon_for_file(self.tree.item(item_id, "text"))
        if self.icons.get(icon_key): self.tree.item(item_id, image=self.icons.get(icon_key))
            
    def _find_recursive(self, search_term, parent_item=""):
        for item_id in self.tree.get_children(parent_item):
            if search_term in self.tree.item(item_id, "text").lower(): return item_id
            found = self._find_recursive(search_term, item_id)
            if found: return found
        return None

    def _export_recursive(self, item_id, prefix, is_last, lines):
        lines.append(f"{prefix}{'└── ' if is_last else '├── '}{self.tree.item(item_id, 'text')}")
        children = self.tree.get_children(item_id)
        if children:
            new_prefix = prefix + ("    " if is_last else "│   ")
            for i, child_id in enumerate(children): self._export_recursive(child_id, new_prefix, i == len(children) - 1, lines)
                
    def _on_drag_start(self, event):
        item = self.tree.identify_row(event.y);
        if item: self.drag_data["item"] = item
    def _on_drag_motion(self, event):
        if not self.drag_data["item"]: return
        target = self.tree.identify_row(event.y)
        if not target: self.tree.move(self.drag_data["item"], "", tk.END); return
        descendants = self._get_all_descendants(self.drag_data["item"])
        if target != self.drag_data["item"] and target not in descendants:
            if self.is_folder_node(target): self.tree.move(self.drag_data["item"], target, tk.END)
            else: self.tree.move(self.drag_data["item"], self.tree.parent(target), tk.END)
    def _get_all_descendants(self, item_id):
        descendants = []; children = self.tree.get_children(item_id)
        descendants.extend(children)
        for child in children: descendants.extend(self._get_all_descendants(child))
        return descendants
    def _on_drag_stop(self, event):
        if self.drag_data["item"]: self.drag_data["item"] = None; self._notify_update("Item movido.")