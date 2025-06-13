# src/app_config.py
from pathlib import Path

# Caminho raiz do projeto (a pasta 'Criador de Pastas')
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Diretórios principais
ASSETS_DIR = PROJECT_ROOT / "assets"
PRESETS_DIR = PROJECT_ROOT / "presets" # Salva presets dentro do projeto

# Caminhos para os ícones
ICON_APP = ASSETS_DIR / "icon_pasta.ico"
ICON_FOLDER = ASSETS_DIR / "icon_pasta.ico"
ICON_FILE = ASSETS_DIR / "icon_arquivo.ico"

# Extensões de arquivo para a caixa de diálogo de criação
FILE_EXTENSIONS = [
    ".txt", ".py", ".js", ".html", ".css", ".md", ".json", ".xml", ".gitignore"
]