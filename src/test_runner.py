# tests/test_runner.py
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path do Python para que possamos importar de 'src'
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.tree_manager import TreeManager

def test_export_to_text():
    """Testa a função de exportação visual da árvore."""
    print("--- Testando export_to_text ---")
    
    # Simulação de um widget Treeview e ícones para o teste
    class MockTree:
        def get_children(self, parent_id=""):
            if parent_id == "": return ["item1"]
            if parent_id == "item1": return ["item2", "item3"]
            return []
        def item(self, item_id, key=None):
            return {"text": item_id}
            
    mock_tree = MockTree()
    mock_icons = {} # Não precisamos de ícones reais para este teste
    
    tm = TreeManager(mock_tree, mock_icons)
    
    # Simula a construção da árvore a partir de uma estrutura
    structure = {
        "src": {
            "main.py": None,
            "utils.py": None
        },
        "README.md": None
    }
    
    # Esta função não existe mais no TreeManager, então vamos simular o resultado
    # O teste real seria verificar a estrutura criada vs a esperada
    
    print("Teste de exportação visual (simulação):")
    # Para testar de verdade, precisaríamos de uma instância Tkinter rodando.
    # Mas podemos testar a lógica da estrutura.
    
    print("Teste de get_structure:")
    # Para testar get_structure, precisaríamos simular as chamadas `insert`
    # O que é complexo sem uma UI.
    
    print("\nEste arquivo demonstra como você pode chamar funções isoladamente.")
    print("Testes de UI completos geralmente requerem frameworks como PyTest com plugins de Tkinter.")


if __name__ == "__main__":
    test_export_to_text()