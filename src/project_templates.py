# src/project_templates.py

# Estrutura do Dicionário: Nome do Arquivo/Pasta: { sub-arquivos } ou None para arquivo
PYTHON_BASIC_APP = {
    "app": {
        "__init__.py": None,
        "main.py": None,
        "utils.py": None,
    },
    "tests": {
        "__init__.py": None,
        "test_main.py": None,
    },
    ".gitignore": None,
    "README.md": None,
    "requirements.txt": None,
}

PYTHON_WEB_APP = {
    "web_app": {
        "__init__.py": None,
        "app.py": None,
        "routes.py": None,
        "models.py": None,
    },
    "static": {
        "css": {},
        "js": {},
        "images": {},
    },
    "templates": {
        "index.html": None,
        "layout.html": None,
    },
    ".gitignore": None,
    "README.md": None,
    "requirements.txt": None,
}

PYTHON_BASIC_APP_WITH_TESTS = {
    "meu_app": {
        "__init__.py": None,
        "main.py": None,
        "utils.py": None,
    },
    "tests": {
        "__init__.py": None,
        "test_main.py": None,
    },
    ".gitignore": None,
    "README.md": None,
    "requirements.txt": None,
}

SQLITE_APP = {
    "database": {
        "db.sqlite3": None,
        "__init__.py": None,
    },
    "app": {
        "__init__.py": None,
        "main.py": None,
        "models.py": None,
    },
    ".gitignore": None,
    "README.md": None,
    "requirements.txt": None,
}

# Dicionário de templates de projeto
PROJECT_TEMPLATES = {
    "Python Basic App": PYTHON_BASIC_APP,
    "Python Web App": PYTHON_WEB_APP,   
    "Python Basic App with Tests": PYTHON_BASIC_APP_WITH_TESTS,
    "SQLite App": SQLITE_APP,
}

# Conteúdo dos arquivos do template
GITIGNORE_CONTENT = """
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE settings
.idea/
.vscode/
"""

README_CONTENT = """
# Meu App Python

Este projeto foi gerado automaticamente pelo ArchManager.

## Descrição

Uma breve descrição do que este projeto faz.

## Como Usar

1.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

2.  Execute o aplicativo:
    ```bash
    python meu_app/main.py
    ```
"""

MAIN_PY_CONTENT = """
def hello_world():
    \"\"\"Retorna uma saudação amigável.\"\"\"
    return "Olá, mundo do ArchManager!"

def main():
    \"\"\"Função principal do aplicativo.\"\"\"
    print(hello_world())

if __name__ == "__main__":
    main()
"""

# Função para obter o conteúdo baseado no nome do arquivo
def get_template_content(filename: str) -> str:
    if filename == ".gitignore":
        return GITIGNORE_CONTENT.strip()
    if filename == "README.md":
        return README_CONTENT.strip()
    if filename == "main.py":
        return MAIN_PY_CONTENT.strip()
    # Para outros arquivos como requirements.txt, __init__.py, etc., retorna vazio.
    return ""