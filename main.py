# main.py
from src.main_window import ProjectBuilderApp

if __name__ == "__main__":
    # Garante que o diretório de presets exista antes de iniciar
    from src.app_config import PRESETS_DIR
    PRESETS_DIR.mkdir(parents=True, exist_ok=True)

    app = ProjectBuilderApp()
    app.mainloop()