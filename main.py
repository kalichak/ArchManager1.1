# main.py
from src.main_window import ProjectBuilderApp
from src.app_config import PRESETS_DIR
import sys
import os

def main():
    # Configuração do diretório de presets
    PRESETS_DIR.mkdir(parents=True, exist_ok=True)
    
    app = ProjectBuilderApp()
    app.mainloop()

if __name__ == "__main__":
    # Adiciona o diretório src ao path do Python para que possamos importar de 'src'
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
    main()