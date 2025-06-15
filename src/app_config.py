# src/app_config.py
from pathlib import Path

# Define o caminho raiz do projeto de forma robusta
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Diretórios principais
ASSETS_DIR = PROJECT_ROOT / "assets"
PRESETS_DIR = PROJECT_ROOT / "presets"

# Lista de ícones que a aplicação tentará carregar
# A extensão .png é preferível para ícones de UI, .ico para o ícone da janela
ICON_NAMES = [
    "folder", "file", "python", "html", "css", "javascript", "json",
    "image", "archive", "text", "app"
]

# Extensões de arquivo para o diálogo de criação
FILE_EXTENSIONS = [
    ".txt", ".md", ".json", ".py", ".js", ".html", ".css", ".xml", ".gitignore",
    ".xls", ".xlsx", ".csv", ".doc", ".docx", ".pdf"
]