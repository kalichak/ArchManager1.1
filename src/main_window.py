# src/main_window.py
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from pathlib import Path
import logging

try: from PIL import Image, ImageTk
except ImportError: Image = ImageTk = None

from . import app_config, project_templates
from .preset_manager import PresetManager
from .tree_manager import TreeManager
from .organizer_window import FolderOrganizerWindow
from .build_window import BuildWindow
from .logger_setup import setup_logging

class ProjectBuilderApp(ttk.Window):
    def __init__(self):
        # MUDANÇA: Usando o tema Cyborg e um título mais impactante
        super().__init__(themename="morph")
        self.title("ArchManager - Construtor de Projetos e Automação")
        self.geometry("1200x800")
        
        # O resto da inicialização permanece o mesmo...
        self.status_text = tk.StringVar()
        setup_logging(self.update_status_from_log)

        self.icons = self._load_icons()
        if self.icons.get("app"): self.iconphoto(True, self.icons.get("app"))
        
        self.preset_manager = PresetManager(app_config.PRESETS_DIR)
        self.current_preset = tk.StringVar()
        self.project_type = tk.StringVar(value="Vazio")

        self._create_widgets()
        
        self.tree_manager = TreeManager(self.tree, self.icons)
        self.tree_manager.set_on_update_callback(self._notify_update)

        self._bind_shortcuts()
        self._load_presets_to_combobox()
        self.update_visual_tree_export()

    def _create_widgets(self):
        self._create_toolbar()
        self._create_main_panels()
        self._create_context_menu()
        self._create_status_bar()

    def _create_main_panels(self):
        main_panel = ttk.PanedWindow(self, orient=HORIZONTAL); main_panel.pack(fill=BOTH, expand=True, padx=10, pady=(5,10))
        
        # --- MELHORIA VISUAL PRINCIPAL ---
        # Painel Esquerdo: A Árvore com fundo claro
        tree_frame = ttk.Frame(main_panel, padding=1, bootstyle="primary") # Borda sutil
        
        # 1. Cria um objeto de Estilo
        style = ttk.Style()
        
        # 2. Configura nosso novo estilo customizado "Light.Treeview"
        light_bg = "#D8E8FF"  # Um cinza muito claro e neutro
        dark_text = "#020F1C" # Quase preto
        select_bg = "#D8E8FF"  # Um azul primário agradável
        
        style.configure("Light.Treeview", 
                        background=light_bg, 
                        fieldbackground=light_bg, 
                        foreground=dark_text,
                        rowheight=24, # Mais espaçamento
                        indent=22) # Maior recuo para sub-itens
                        
        # 3. Mapeia a cor de seleção para o nosso estilo
        style.map("Light.Treeview", 
                  background=[('selected', select_bg)],
                  foreground=[('selected', 'white')])

        # 4. Aplica o estilo customizado ao criar o Treeview
        self.tree = ttk.Treeview(tree_frame, show='tree', selectmode='extended', style="Light.Treeview")
        self.tree.pack(fill=BOTH, expand=True)
        main_panel.add(tree_frame, weight=3)
        # ----------------------------------------------------

        # Painel Direito: Abas para Detalhes e Visualização
        right_panel = ttk.Labelframe(main_panel, text="  Detalhes e Visualização  ", padding=(15, 10), bootstyle="primary")
        self.notebook = ttk.Notebook(right_panel, bootstyle="primary")
        self.notebook.pack(fill=BOTH, expand=True)
        self.details_tab = ttk.Frame(self.notebook, padding=10)
        self.details_tab.columnconfigure(0, weight=1)
        self.details_tab.rowconfigure(0, weight=1)
        self.visual_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.details_tab, text=" Detalhes do Projeto ")
        self.notebook.add(self.visual_tab, text=" Visualização da Estrutura ")
        
        self._create_details_controls(self.details_tab)
        self._create_visual_controls(self.visual_tab)
        
        main_panel.add(right_panel, weight=2)
        style.configure("Light.TLabelframe", background=light_bg, foreground=dark_text)
        style.configure("Light.TFrame", background=light_bg)
        style.configure("Light.TNotebook", background=light_bg)
        style.configure("Light.TNotebook.Tab", background=light_bg, foreground=dark_text)
        
    def _create_details_controls(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(3, weight=1) # Faz a descrição expandir
        
        ttk.Label(parent, text="Nome do Preset:").pack(fill=X, pady=(5,2), anchor="w")
        self.ent_name = ttk.Entry(parent); self.ent_name.pack(fill=X, pady=(0, 10))
        self.ent_name.bind("<KeyRelease>", lambda e: self.update_visual_tree_export())

        ttk.Label(parent, text="Descrição:").pack(fill=X, pady=(5,2), anchor="w")
        self.txt_desc = tk.Text(parent, height=5, wrap="word"); self.txt_desc.pack(fill=BOTH, expand=True, pady=(0, 15))
        
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=X)
        ttk.Button(btn_frame, text="Add Pasta", bootstyle="primary", command=lambda: self.tree_manager.add_folder()).pack(side=LEFT)            
        ttk.Button(btn_frame, text="Add Arquivo", bootstyle="primary", command=lambda: self.tree_manager.add_file()).pack(side=LEFT, padx=5)

        
    def _create_visual_controls(self, parent):
        parent.rowconfigure(0, weight=1); parent.columnconfigure(0, weight=1)
        self.visual_tree_text = tk.Text(parent, wrap="none", font=("Courier New", 10), background="#D8E8FF", foreground="#061641", insertbackground="#D8E8FF")
        self.visual_tree_text.pack(fill=BOTH, expand=True)
        self.visual_tree_text.config(state="disabled")

    def update_visual_tree_export(self, *args):
        project_name = self.ent_name.get().strip() or "MeuProjeto"
        tree_text = self.tree_manager.export_to_text(project_name)
        self.visual_tree_text.config(state="normal"); self.visual_tree_text.delete("1.0", tk.END)
        self.visual_tree_text.insert("1.0", tree_text); self.visual_tree_text.config(state="disabled")

    # O resto das funções (toolbar, context menu, etc.) permanece o mesmo.
    # Colei tudo abaixo por segurança.
    
    def _load_icons(self):
        if not ImageTk: messagebox.showerror("Dependência Faltando", "'Pillow' é necessária."); return {}
        loaded_icons = {}; icon_size = (16, 16)
        for name in app_config.ICON_NAMES:
            try:
                path = app_config.ASSETS_DIR / f"{name}{'.ico' if name == 'app' else '.png'}"
                if path.exists():
                    if name == "app": loaded_icons[name] = ttk.PhotoImage(file=path)
                    else:
                        with Image.open(path) as img: loaded_icons[name] = ImageTk.PhotoImage(img.resize(icon_size, Image.Resampling.LANCZOS))
            except Exception as e: print(f"Erro ao carregar '{path.name}': {e}")
        return loaded_icons
    
    def _create_toolbar(self):
        toolbar = ttk.Frame(self, padding=(10, 5)); toolbar.pack(fill=X, side=TOP)
        ttk.Button(toolbar, text="Salvar Preset", command=self.save_preset, bootstyle="primary").pack(side=LEFT, padx=3)
        self.cmb_presets = ttk.Combobox(toolbar, textvariable=self.current_preset, state="readonly", width=20); self.cmb_presets.pack(side=LEFT, padx=3); self.cmb_presets.bind("<<ComboboxSelected>>", self.load_preset_from_combobox)
        ttk.Label(toolbar, text="Template:", padding=(15,0,5,0)).pack(side=LEFT)
        type_cb = ttk.Combobox(toolbar, textvariable=self.project_type, values=["Vazio", "App Python Básico"], state="readonly", width=20); type_cb.pack(side=LEFT, padx=3); type_cb.bind("<<ComboboxSelected>>", self.on_project_type_change)
        ttk.Button(toolbar, text="Gerar Estrutura", bootstyle="primary", command=self.generate_structure_on_disk).pack(side=LEFT, padx=(10, 3))
        ttk.Button(toolbar, text="Compilar App", bootstyle="primary", command=lambda: BuildWindow(self)).pack(side=RIGHT, padx=(0, 10))
        ttk.Button(toolbar, text="Organizar Pasta", bootstyle="primary", command=lambda: FolderOrganizerWindow(self)).pack(side=RIGHT, padx=5)

    def _create_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Nova Pasta", command=lambda: self.tree_manager.add_folder())
        self.context_menu.add_command(label="Novo Arquivo", command=lambda: self.tree_manager.add_file())
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Copiar", accelerator="Ctrl+C", command=lambda: self.tree_manager.copy_item())
        self.context_menu.add_command(label="Colar", accelerator="Ctrl+V", command=lambda: self.tree_manager.paste_item())
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Renomear", accelerator="F2", command=lambda: self.tree_manager.rename_item())
        self.context_menu.add_command(label="Excluir", accelerator="Del", command=lambda: self.tree_manager.delete_selected_items())
        self.tree.bind("<Button-3>", self._show_context_menu)
        
    def _create_status_bar(self):
        status_frame = ttk.Frame(self, bootstyle="primary"); status_frame.pack(side=BOTTOM, fill=X)
        self.status_label = ttk.Label(status_frame, textvariable=self.status_text, padding=(10, 5), anchor="w")
        self.status_label.pack(side=LEFT, fill=X, expand=True)

    def _bind_shortcuts(self):
        self.bind_all("<Control-n>", lambda e: self.new_preset()); self.bind_all("<Control-s>", lambda e: self.save_preset())
        self.tree.bind("<F2>", lambda e: self.tree_manager.rename_item()); self.tree.bind("<Delete>", lambda e: self.tree_manager.delete_selected_items())
        self.tree.bind("<Control-c>", lambda e: self.tree_manager.copy_item()); self.tree.bind("<Control-v>", lambda e: self.tree_manager.paste_item())
        self.tree.bind("<Control-f>", lambda e: self.tree_manager.find_item()); self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        
    def _on_tree_select(self, event=None):
        self.tree.focus_set()
        item_id = self.tree_manager.get_selected_item()
        if item_id: logging.info(f"Selecionado: {self.tree.item(item_id, 'text')}")
        
    def _notify_update(self, message="Estrutura atualizada."):
        self.update_visual_tree_export()
        logging.info(message)
        
    def update_status_from_log(self, message):
        self.status_text.set(message)
    
    def _show_context_menu(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            if item_id not in self.tree.selection(): self.tree.selection_set(item_id)
            self.context_menu.post(event.x_root, event.y_root)
            
    def on_project_type_change(self, event=None):
        ptype = self.project_type.get()
        if ptype == "Vazio": self.new_preset()
        elif ptype == "App Python Básico":
            if not self.tree.get_children() or messagebox.askyesno("Confirmar", "Isso substituirá a estrutura. Continuar?"):
                self.tree_manager.clear_tree(); self.ent_name.delete(0, tk.END); self.ent_name.insert(0, "Meu App Python")
                self.tree_manager.build_from_structure(project_templates.PYTHON_BASIC_APP)
                
    def _load_presets_to_combobox(self):
        presets = self.preset_manager.list_presets(); self.cmb_presets["values"] = [""] + presets
        self.current_preset.set("")
    def new_preset(self):
        self.tree_manager.clear_tree(); self.current_preset.set(""); self.project_type.set("Vazio")
        self.ent_name.delete(0, tk.END); self.txt_desc.delete("1.0", tk.END); self.ent_name.focus_set()
    def save_preset(self):
        name = self.ent_name.get().strip()
        if not name: messagebox.showwarning("Aviso", "O nome do preset não pode ser vazio."); return
        if self.preset_manager.save(name, self.txt_desc.get("1.0", tk.END).strip(), self.tree_manager.get_structure()):
            self._load_presets_to_combobox(); self.current_preset.set(name)
    def load_preset_from_combobox(self, event=None):
        preset_name = self.current_preset.get()
        if not preset_name: return
        preset_data = self.preset_manager.load(preset_name)
        if preset_data:
            self.tree_manager.clear_tree(); self.project_type.set("Vazio")
            meta = preset_data.get("metadata", {}); struct = preset_data.get("structure", {})
            self.ent_name.delete(0, tk.END); self.ent_name.insert(0, meta.get("name", ""))
            self.txt_desc.delete("1.0", tk.END); self.txt_desc.insert("1.0", meta.get("description", ""))
            self.tree_manager.build_from_structure(struct)

    def generate_structure_on_disk(self):
        if not self.tree.get_children(): messagebox.showwarning("Aviso", "Estrutura vazia."); return
        base_dir = filedialog.askdirectory(title="Selecione o diretório base")
        if not base_dir: return
        try:
            self._create_recursive(Path(base_dir), "")
            messagebox.showinfo("Sucesso", f"Estrutura criada em:\n{base_dir}")
        except Exception as e:
            logging.error(f"Erro ao gerar estrutura: {e}", exc_info=True)
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

    def _create_recursive(self, base_path: Path, parent_item_id):
        for item_id in self.tree.get_children(parent_item_id):
            name = self.tree.item(item_id, "text")
            current_path = base_path / name
            if self.tree_manager.is_folder_node(item_id):
                current_path.mkdir(parents=True, exist_ok=True)
                self._create_recursive(current_path, item_id)
            else:
                content = project_templates.get_template_content(name) if self.project_type.get() == "App Python Básico" else ""
                current_path.write_text(content, encoding="utf-8")
        self._notify_update(f"Estrutura '{base_path.name}' criada com sucesso.")
    def run(self):  
        """Inicia o loop principal da aplicação."""
        self.mainloop()
                