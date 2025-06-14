# src/main_window.py
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from pathlib import Path

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = ImageTk = None

from . import app_config, project_templates
from .preset_manager import PresetManager
from .tree_manager import TreeManager
from .organizer_window import FolderOrganizerWindow
from .build_window import BuildWindow

class ProjectBuilderApp(ttk.Window):

    def __init__(self):
        super().__init__(themename="morph", title="ArchManager 1.0")
        self.title("ArchManager 1.0")
        self.geometry("1366x768")
        self.resizable(True, True)
        
        self.icons = self._load_icons()
        if self.icons.get("app"): self.iconphoto(True, self.icons.get("app"))
        
        self.preset_manager = PresetManager(app_config.PRESETS_DIR)
        self.current_preset = tk.StringVar()
        self.project_type = tk.StringVar(value="Vazio")

        self._create_toolbar()
        self._create_main_panels()
        self._create_context_menu()
        self._create_status_bar()
        
        # MUDANÇA: Passando a função de update como callback
        self.tree_manager = TreeManager(self.tree, self.icons, on_update_callback=self.update_visual_tree_export)

        self._bind_shortcuts()
        self._load_presets_to_combobox()
        self.update_status("Pronto.")
        self.update_visual_tree_export() # Primeira atualização

    def _load_icons(self):
        if not ImageTk: messagebox.showerror("Dependência Faltando", "'Pillow' é necessária. Execute: pip install Pillow"); return {}

        icon_names = ["folder", "file", "python", "html", "css", "javascript", "json", "image", "archive", "text", "app"]
        loaded_icons = {}
        icon_size = (16, 16)

        for name in icon_names:
            try:
                ext = ".ico" if name == "app" else ".png"
                path = app_config.ASSETS_DIR / f"{name}{ext}"
                if not path.exists():
                    print(f"Aviso: Arquivo de ícone não encontrado em '{path}'")
                    continue
                
                if name == "app":
                    loaded_icons[name] = ttk.PhotoImage(file=path)
                else:
                    with Image.open(path) as img:
                        resized_img = img.resize(icon_size, Image.Resampling.LANCZOS)
                        loaded_icons[name] = ImageTk.PhotoImage(resized_img)
            except Exception as e:
                print(f"Erro ao carregar '{name}{ext}': {e}")
        
        print(f"Ícones carregados com sucesso: {list(loaded_icons.keys())}") # <-- NOVO LOG DE DEBUG
        return loaded_icons

    def _create_toolbar(self):
        toolbar = ttk.Frame(self, bootstyle=SECONDARY, padding=(10, 5))
        toolbar.pack(fill=X)
        # ... (código existente)
        ttk.Button(toolbar, text="Salvar Preset", bootstyle= "light", command=self.save_preset).pack(side=LEFT, padx=3)
        self.cmb_presets = ttk.Combobox(toolbar, textvariable=self.current_preset, state="readonly", width=20)
        self.cmb_presets.pack(side=LEFT, padx=3)
        self.cmb_presets.bind("<<ComboboxSelected>>", self.load_preset_from_combobox)
        ttk.Label(toolbar, text="Tipo de Projeto:", padding=(15,0,5,0)).pack(side=LEFT)
        type_cb = ttk.Combobox(toolbar, textvariable=self.project_type, values=["Vazio", "App Python Básico"], state="readonly", width=20)
        type_cb.pack(side=LEFT, padx=3)
        type_cb.bind("<<ComboboxSelected>>", self.on_project_type_change)
        ttk.Button(toolbar, text="Gerar Estrutura", bootstyle="light", command=self.generate_structure_on_disk).pack(side=LEFT, padx=(10, 3))
        # Botão de exportar removido
        ttk.Button(toolbar, text="Compilar (.exe)", bootstyle="light", command=lambda: BuildWindow(self)).pack(side=RIGHT, padx=(0, 10))
        ttk.Button(toolbar, text="Organizar Pasta", bootstyle="light", command=lambda: FolderOrganizerWindow(self)).pack(side=RIGHT, padx=5)

    def _create_edit_controls(self, parent):
        frame = ttk.Labelframe(parent, text="Detalhes e Visualização", padding=15)
        frame.pack(fill=BOTH, expand=True, padx=(10, 0))
        frame.rowconfigure(5, weight=1) # Faz a área de texto crescer
        frame.columnconfigure(0, weight=1)
        
        ttk.Label(frame, text="Nome do Preset:").grid(row=0, column=0, sticky=W, pady=(0, 5))
        self.ent_name = ttk.Entry(frame)
        self.ent_name.grid(row=1, column=0, sticky=EW, pady=(0, 15))
        self.ent_name.bind("<KeyRelease>", self.update_visual_tree_export) # Atualiza ao digitar
        
        ttk.Label(frame, text="Descrição:").grid(row=2, column=0, sticky=W, pady=(0, 5))
        self.txt_desc = tk.Text(frame, height=5, wrap="word", relief="solid", borderwidth=1)
        self.txt_desc.grid(row=3, column=0, sticky=EW, pady=(0, 15))

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, sticky="w", pady=(0, 15))
        ttk.Button(btn_frame, text="Add Pasta", command=lambda: self.tree_manager.add_folder()).pack(side=LEFT, padx=0)
        ttk.Button(btn_frame, text="Add Arquivo", command=lambda: self.tree_manager.add_file()).pack(side=LEFT, padx=5)

        # --- NOVO: Painel de visualização ---
        ttk.Label(frame, text="Visualização da Estrutura:").grid(row=5, column=0, sticky=NW, pady=(0, 5))
        self.visual_tree_text = tk.Text(frame, height=20, wrap="none", relief="solid", borderwidth=1, state="disabled", font=("Courier New", 10))
        self.visual_tree_text.grid(row=6, column=0, sticky="nsew")
        # ------------------------------------

    def update_visual_tree_export(self, event=None):
        """Atualiza a caixa de texto com a estrutura visual."""
        project_name = self.ent_name.get().strip() or "MeuProjeto"
        tree_text = self.tree_manager.export_to_text(project_name)
        
        self.visual_tree_text.config(state="normal")
        self.visual_tree_text.delete("1.0", tk.END)
        self.visual_tree_text.insert("1.0", tree_text)
        self.visual_tree_text.config(state="disabled")

    def _create_main_panels(self):
        main_panel = ttk.PanedWindow(self, orient=HORIZONTAL, bootstyle="light")
        main_panel.pack(fill=BOTH, expand=True, padx=10, pady=5)
        tree_frame = ttk.Frame(main_panel)
        style = ttk.Style(); style.configure("Treeview", rowheight=22, Indent=20)
        self.tree = ttk.Treeview(tree_frame, show='tree', selectmode='extended', style="Treeview")
        self.tree.pack(fill=BOTH, expand=True)
        main_panel.add(tree_frame, weight=3)
        edit_panel = ttk.Frame(main_panel); self._create_edit_controls(edit_panel)
        main_panel.add(edit_panel, weight=2)
    def _create_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        
        # --- A CORREÇÃO ESTÁ AQUI ---
        # Usando 'lambda' para garantir que self.tree_manager seja
        # procurado apenas no momento do clique, e não na criação do menu.
        self.context_menu.add_command(label="Copiar (Ctrl+C)", command=lambda: self.tree_manager.copy_item())
        self.context_menu.add_command(label="Colar (Ctrl+V)", command=lambda: self.tree_manager.paste_item())
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Renomear (F2)", command=lambda: self.tree_manager.rename_item())
        self.context_menu.add_command(label="Excluir (Del)", command=lambda: self.tree_manager.delete_item())
        # ---------------------------
        
        self.tree.bind("<Button-3>", self._show_context_menu)
    def _create_status_bar(self):
        status_frame = ttk.Frame(self, bootstyle=SECONDARY); status_frame.pack(side=BOTTOM, fill=X, padx=1, pady=1)
        self.status_label = ttk.Label(status_frame, text="Pronto.", padding=(10, 5)); self.status_label.pack(side=LEFT)
    def _bind_shortcuts(self):
        self.tree.bind("<F2>", lambda e: self.tree_manager.rename_item())
        self.tree.bind("<Delete>", lambda e: self.tree_manager.delete_item())
        self.tree.bind("<Control-c>", lambda e: self.tree_manager.copy_item())
        self.tree.bind("<Control-v>", lambda e: self.tree_manager.paste_item())
        self.tree.bind("<Control-f>", lambda e: self.tree_manager.find_item())
    def update_status(self, message):
        self.status_label.config(text=message); self.after(5000, lambda: self.status_label.config(text="Pronto."))
    def _show_context_menu(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            if item_id not in self.tree.selection(): self.tree.selection_set(item_id)
            self.context_menu.post(event.x_root, event.y_root)
    def on_project_type_change(self, event=None):
        ptype = self.project_type.get()
        if ptype == "Vazio": self.new_preset()
        elif ptype == "App Python Básico":
            if not self.tree.get_children() or messagebox.askyesno("Confirmar", "Isso substituirá a estrutura atual. Continuar?"):
                self.tree_manager.clear_tree()
                template = project_templates.PYTHON_BASIC_APP
                self.ent_name.delete(0, END); self.ent_name.insert(0, "Meu App Python")
                self.tree_manager.build_from_structure(template)
                self.update_status("Template de App Python Básico carregado.")
    def _load_presets_to_combobox(self):
        presets = self.preset_manager.list_presets()
        self.cmb_presets["values"] = [""] + presets
        self.current_preset.set("")
    def new_preset(self):
        self.tree_manager.clear_tree(); self.current_preset.set(""); self.project_type.set("Vazio")
        self.ent_name.delete(0, END); self.txt_desc.delete("1.0", END)
        self.ent_name.focus_set(); self.update_status("Novo preset iniciado.")
    def save_preset(self):
        name = self.ent_name.get().strip()
        if not name: messagebox.showwarning("Aviso", "O nome do preset não pode ser vazio."); return
        desc = self.txt_desc.get("1.0", END).strip()
        structure = self.tree_manager.get_structure()
        if self.preset_manager.save(name, desc, structure):
            self._load_presets_to_combobox(); self.current_preset.set(name)
            self.update_status(f"Preset '{name}' salvo.")
    def load_preset_from_combobox(self, event=None):
        preset_name = self.current_preset.get();
        if not preset_name: return
        preset_data = self.preset_manager.load(preset_name)
        if preset_data:
            self.tree_manager.clear_tree(); self.project_type.set("Vazio")
            self.ent_name.delete(0, END); self.ent_name.insert(0, preset_data["metadata"].get("name", ""))
            self.txt_desc.delete("1.0", END); self.txt_desc.insert("1.0", preset_data["metadata"].get("description", ""))
            self.tree_manager.build_from_structure(preset_data.get("structure", {}))
            self.update_status(f"Preset '{preset_name}' carregado.")
    def generate_structure_on_disk(self):
        if not self.tree.get_children(): messagebox.showwarning("Aviso", "A estrutura está vazia."); return
        base_dir = filedialog.askdirectory(title="Selecione o diretório base")
        if not base_dir: return
        try:
            self._create_recursive(Path(base_dir), "")
            messagebox.showinfo("Sucesso", f"Estrutura criada com sucesso em:\n{base_dir}")
            self.update_status("Estrutura gerada no disco.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro:\n{e}")
    def _create_recursive(self, base_path: Path, parent_item_id: str):
        ptype = self.project_type.get()
        for item_id in self.tree.get_children(parent_item_id):
            name = self.tree.item(item_id, "text")
            current_path = base_path / name
            if self.tree.get_children(item_id):
                current_path.mkdir(parents=True, exist_ok=True)
                self._create_recursive(current_path, item_id)
            else:
                content = ""
                if ptype == "App Python Básico": content = project_templates.get_template_content(name)
                with open(current_path, "w", encoding="utf-8") as f: f.write(content)