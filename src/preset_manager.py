# src/preset_manager.py
import json
from pathlib import Path
from datetime import datetime
from tkinter import messagebox

class PresetManager:
    """Gerencia o salvamento e carregamento de presets."""

    def __init__(self, presets_dir: Path):
        self.presets_dir = presets_dir
        self.presets_dir.mkdir(parents=True, exist_ok=True)

    def list_presets(self) -> list[str]:
        """Retorna uma lista ordenada com os nomes dos presets disponíveis."""
        return sorted([f.stem for f in self.presets_dir.glob("*.json")])

    def save(self, name: str, description: str, structure: dict):
        """Salva a estrutura atual como um preset JSON."""
        if not name:
            messagebox.showwarning("Aviso", "Informe um nome para o preset antes de salvar.")
            return False

        preset_data = {
            "metadata": {
                "name": name,
                "description": description,
                "created": datetime.now().isoformat()
            },
            "structure": structure
        }

        file_path = self.presets_dir / f"{name}.json"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(preset_data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Sucesso", f"Preset '{name}' salvo com sucesso.")
            return True
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o preset:\n{e}")
            return False

    def load(self, name: str) -> dict | None:
        """Carrega um preset a partir de um arquivo JSON."""
        file_path = self.presets_dir / f"{name}.json"
        if not file_path.exists():
            messagebox.showerror("Erro ao Carregar", f"O arquivo de preset '{name}.json' não foi encontrado.")
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            messagebox.showerror("Erro ao Carregar", f"Erro ao ler o arquivo de preset:\n{e}")
            return None