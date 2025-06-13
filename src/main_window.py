# src/main_window.py
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from pathlib import Path

# Importando nossos módulos customizados
from . import app_config
from .preset_manager import PresetManager
from .tree_manager import TreeManager

class ProjectBuilderApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Criador de Estrutura de Projetos")
        self.geometry("1000x700")
        
        try:
            self.iconbitmap(app_config.ICON_APP)
            self.folder_icon = ttk.PhotoImage(file=app_config.ICON_FOLDER)
            self.file_icon = ttk.PhotoImage(file=app_config.ICON_FILE)
        except tk.TclError:
            messagebox.showerror("Erro de Ícone", "Não foi possível carregar os arquivos de ícone. Verifique se eles existem na pasta 'assets' com os nomes corretos.")
            self.folder_icon = None
            self.file_icon = None
            # Você pode fechar o app se os ícones forem essenciais
            # self.destroy() 
            # return

        self.preset_manager = PresetManager(app_config.PRESETS_DIR)
        self.current_preset = tk.StringVar()

        self._create_toolbar()
        self._create_main_panels()
        self._create_context_menu()
        
        # O TreeManager é inicializado após o treeview ser criado
        self.tree_manager = TreeManager(self.tree, self.folder_icon, self.file_icon)

        self._load_presets_to_combobox()

    def _create_toolbar(self):
        toolbar = ttk.Frame(self, bootstyle=SECONDARY)
        toolbar.pack(fill=X, padx=10, pady=5)
        
        ttk.Button(toolbar, text="Novo", command=self.new_preset).pack(side=LEFT, padx=3)
        ttk.Button(toolbar, text="Salvar", command=self.save_preset).pack(side=LEFT, padx=3)
        ttk.Button(toolbar, text="Gerar Estrutura", bootstyle="success", command=self.generate_structure_on_disk).pack(side=LEFT, padx=3)
        
        ttk.Label(toolbar, text="Presets:", padding=(20, 0, 5, 0)).pack(side=LEFT)
        self.cmb_presets = ttk.Combobox(toolbar, textvariable=self.current_preset, state="readonly")
        self.cmb_presets.pack(side=LEFT, fill=X, expand=True, padx=3)
        self.cmb_presets.bind("<<ComboboxSelected>>", self.load_preset_from_combobox)

    def _create_main_panels(self):
        main_panel = ttk.PanedWindow(self, orient=HORIZONTAL)
        main_panel.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))
        
        tree_frame = ttk.Frame(main_panel)
        self.tree = ttk.Treeview(tree_frame, show='tree', selectmode='extended')
        self.tree.pack(fill=BOTH, expand=True)
        main_panel.add(tree_frame, weight=3)
        
        edit_panel = ttk.Frame(main_panel)
        self._create_edit_controls(edit_panel)
        main_panel.add(edit_panel, weight=1)

    def _create_edit_controls(self, parent):
        frame = ttk.Labelframe(parent, text="Informações do Preset", bootstyle=INFO, padding=10)
        frame.pack(fill=BOTH, expand=True, padx=(5, 0))
        
        ttk.Label(frame, text="Nome do Preset:").grid(row=0, column=0, sticky=W, pady=(0, 2))
        self.ent_name = ttk.Entry(frame)
        self.ent_name.grid(row=1, column=0, columnspan=2, sticky=EW, pady=(0, 10))
        
        ttk.Label(frame, text="Descrição:").grid(row=2, column=0, sticky=W, pady=(0, 2))
        self.txt_desc = tk.Text(frame, height=8, wrap="word", relief="solid", borderwidth=1)
        self.txt_desc.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(0, 15))
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2)
        
        add_folder_btn = ttk.Button(btn_frame, text=" Add Pasta", command=lambda: self.tree_manager.add_folder())
        if self.folder_icon:
            add_folder_btn.config(image=self.folder_icon, compound=LEFT)
        add_folder_btn.pack(side=LEFT, padx=5)

        add_file_btn = ttk.Button(btn_frame, text=" Add Arquivo", command=lambda: self.tree_manager.add_file())
        if self.file_icon:
            add_file_btn.config(image=self.file_icon, compound=LEFT)
        add_file_btn.pack(side=LEFT, padx=5)

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(3, weight=1)

    def _create_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Nova Pasta", command=lambda: self.tree_manager.add_folder())
        self.context_menu.add_command(label="Novo Arquivo", command=lambda: self.tree_manager.add_file())
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Renomear", command=lambda: self.tree_manager.rename_item())
        self.context_menu.add_command(label="Excluir", command=lambda: self.tree_manager.delete_item())
        self.tree.bind("<Button-3>", self._show_context_menu)

    def _show_context_menu(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            if item_id not in self.tree.selection():
                self.tree.selection_set(item_id)
            self.context_menu.post(event.x_root, event.y_root)

    def _load_presets_to_combobox(self):
        presets = self.preset_manager.list_presets()
        self.cmb_presets["values"] = presets
        if not presets:
            self.current_preset.set("")

    def new_preset(self):
        self.tree_manager.clear_tree()
        self.current_preset.set("")
        self.ent_name.delete(0, END)
        self.txt_desc.delete("1.0", END)
        self.ent_name.focus_set()

    def save_preset(self):
        name = self.ent_name.get().strip()
        desc = self.txt_desc.get("1.0", END).strip()
        structure = self.tree_manager.get_structure()
        
        if self.preset_manager.save(name, desc, structure):
            self._load_presets_to_combobox()
            self.current_preset.set(name)

    def load_preset_from_combobox(self, event=None):
        preset_name = self.current_preset.get()
        if not preset_name: return
        
        preset_data = self.preset_manager.load(preset_name)
        if preset_data:
            self.tree_manager.clear_tree()
            self.ent_name.delete(0, END)
            self.txt_desc.delete("1.0", END)
            self.ent_name.insert(0, preset_data["metadata"].get("name", ""))
            self.txt_desc.insert("1.0", preset_data["metadata"].get("description", ""))
            self.tree_manager.build_from_structure(preset_data.get("structure", {}))

    def generate_structure_on_disk(self):
        if not self.tree.get_children():
            messagebox.showwarning("Aviso", "A estrutura está vazia. Adicione pastas ou arquivos primeiro.")
            return
        
        base_dir = filedialog.askdirectory(title="Selecione o diretório base para criar a estrutura")
        if not base_dir: return
            
        try:
            self._create_recursive(Path(base_dir), "")
            messagebox.showinfo("Sucesso", f"Estrutura criada com sucesso em:\n{base_dir}")
        except Exception as e:
            messagebox.showerror("Erro ao Criar Estrutura", f"Ocorreu um erro:\n{e}")

    def _create_recursive(self, base_path: Path, parent_item_id: str):
        for item_id in self.tree.get_children(parent_item_id):
            name = self.tree.item(item_id, "text")
            current_path = base_path / name
            
            if self.tree.get_children(item_id):
                current_path.mkdir(parents=True, exist_ok=True)
                self._create_recursive(current_path, item_id)
            else:
                current_path.touch(exist_ok=True)