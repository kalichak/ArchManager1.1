Documentação do Projeto: ArchManager

## 1. Visão Geral

**ArchManager** é uma aplicação de desktop desenvolvida em Python com Tkinter e ttkbootstrap. Sua finalidade é auxiliar desenvolvedores e usuários a automatizar tarefas comuns de gerenciamento de projetos e arquivos. Suas principais funcionalidades incluem:

- **Criação de Estruturas de Projeto:** Permite desenhar visualmente a estrutura de pastas e arquivos de um projeto.
- **Gerenciamento de Presets:** Salva e carrega templates de estruturas de projeto para reutilização.
- **Geração em Disco:** Cria a estrutura de pastas e arquivos definida diretamente no sistema de arquivos.
- **Compilador Integrado:** Oferece uma interface gráfica para o PyInstaller, facilitando a compilação de aplicações Python em executáveis (`.exe`) e a criação de instaladores com Inno Setup.
- **Organizador de Pastas:** Automatiza a organização de arquivos em subpastas com base em sua extensão e em palavras-chave no nome.

## 2. Estrutura de Diretórios

O projeto está organizado da seguinte forma:

```
ArchManager/
├── assets/
│   ├── archive.png
│   ├── css.png
│   ├── file.png
│   ├── folder.png
│   ├── html.png
│   ├── image.png
│   ├── javascript.png
│   ├── json.png
│   ├── python.png
│   └── text.png
│   └── app.ico
├── presets/
│   └── (arquivos .json de presets salvos)
├── src/
│   ├── __init__.py
│   ├── app_config.py
│   ├── build_window.py
│   ├── logger_setup.py
│   ├── main_window.py
│   ├── organizer_window.py
│   ├── preset_manager.py
│   ├── project_templates.py
│   ├── test_runner.py
│   ├── tree_manager.py
│   └── ui_dialogs.py
└── main.py
```

## 3. Análise Detalhada dos Módulos

### `main.py` (Ponto de Entrada)

Este é o script principal que inicia a aplicação.

| Função / Método     | Descrição Detalhada                                                                                                                                                                                                                                                                                                                            |
| :--------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `(script principal)` | Importa a classe `ProjectBuilderApp` de `main_window.py` e o módulo `sys`. Adiciona o diretório pai ao `sys.path` para garantir que as importações relativas a partir de `src` funcionem corretamente. Instancia a classe `ProjectBuilderApp` e chama seu método `run()` para iniciar o loop principal da interface gráfica. |

---

### `src/app_config.py`

Este módulo centraliza todas as constantes e configurações globais da aplicação para fácil manutenção.

| Constante           | Tipo             | Descrição                                                                                                                                                                     |
| :------------------ | :--------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `PROJECT_ROOT`    | `pathlib.Path` | Define o caminho absoluto para a pasta raiz do projeto, garantindo que os caminhos para outros recursos sejam sempre corretos, independentemente de onde o script é executado. |
| `ASSETS_DIR`      | `pathlib.Path` | Aponta para o diretório `assets`, onde os ícones e outras mídias são armazenados.                                                                                         |
| `PRESETS_DIR`     | `pathlib.Path` | Aponta para o diretório `presets`, onde as estruturas de projeto salvas (em formato JSON) são guardadas.                                                                    |
| `ICON_NAMES`      | `list[str]`    | Uma lista com os nomes base dos ícones que a aplicação tentará carregar. Usado para popular a interface com ícones visuais.                                                |
| `FILE_EXTENSIONS` | `list[str]`    | Uma lista de extensões de arquivo comuns oferecidas no diálogo de criação de novos arquivos.                                                                                |

---

### `src/build_window.py`

Implementa a janela "Build Master", que fornece uma interface gráfica para compilar a aplicação Python em um executável e, opcionalmente, criar um instalador.

#### Classe: `BuildWindow(ttk.Toplevel)`

| Função / Método                          | Parâmetros                                  | Retorno             | Descrição Detalhada                                                                                                                                                                                                                                                                                                                                                                                                          |
| :------------------------------------------ | :------------------------------------------- | :------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `__init__(self, parent)`                  | `parent`: A janela pai.                    | `None`            | Inicializa a janela, define seu título e geometria. Declara todas as variáveis de controle do Tkinter (`tk.StringVar`, `tk.BooleanVar`). Cria uma `queue.Queue` para comunicação thread-safe com a UI e chama `_create_widgets()` para construir a interface.                                                                                                                                                      |
| `_create_widgets(self)`                   | `None`                                     | `None`            | Constrói todos os elementos da interface gráfica (widgets), como frames, labels, entradas de texto, botões e a área de log, organizando-os em um grid.                                                                                                                                                                                                                                                                     |
| `select_project_root(self)`               | `None`                                     | `None`            | Abre um diálogo para o usuário selecionar a pasta raiz do projeto. Após a seleção, tenta detectar automaticamente o interpretador Python em um ambiente virtual (`venv` ou `.venv`) e o script principal (`main.py`). Habilita o botão de build se os caminhos essenciais forem encontrados.                                                                                                                       |
| `select_icon(self)`                       | `None`                                     | `None`            | Abre um diálogo para o usuário selecionar um arquivo de ícone (`.ico`).                                                                                                                                                                                                                                                                                                                                                   |
| `run_full_process(self)`                  | `None`                                     | `None`            | Ponto de entrada para o processo de build. Desabilita o botão de build para evitar execuções múltiplas, limpa o log e inicia a função `_build_thread` em uma nova thread para não congelar a UI.                                                                                                                                                                                                                      |
| `_build_thread(self)`                     | `None`                                     | `None`            | Executa a lógica de build em segundo plano. Orquestra o processo em três etapas: 1.**Preparação do Ambiente:** Instala `pyinstaller`, `wheel` e as dependências do `requirements.txt`. 2. **Compilação:** Chama `_run_pyinstaller`. 3. **Criação do Instalador:** Se a opção estiver marcada, chama `_run_inno_setup`. Envia mensagens de log e status para a UI através da `queue`. |
| `_run_pyinstaller(self, force_onedir)`    | `force_onedir`: `bool`                   | `bool`            | Constrói e executa o comando do PyInstaller com base nas opções definidas na UI (onefile/onedir, nome, ícone, etc.). Retorna `True` em caso de sucesso.                                                                                                                                                                                                                                                                  |
| `_run_inno_setup(self)`                   | `None`                                     | `bool`            | Gera o script do Inno Setup (`.iss`) através de `_generate_inno_script`, salva-o em um arquivo temporário e executa o compilador do Inno Setup. Retorna `True` em caso de sucesso. **(Nota: Esta função não estava no código fornecido, mas a lógica de geração do script sim)**                                                                                                                          |
| `execute_command(self, command, workdir)` | `command`: `list`, `workdir`: `Path` | `bool`            | Função genérica para executar comandos de sistema (como `pip` ou `pyinstaller`) usando `subprocess.Popen`. Captura a saída (stdout/stderr) em tempo real e a envia para a `queue` para ser exibida no log da UI. Retorna `True` se o comando for executado com sucesso (código de saída 0).                                                                                                                    |
| `process_queue(self)`                     | `None`                                     | `None`            | Método que executa periodicamente (`after(100, ...)`). Verifica se há novas mensagens na `queue`. Se houver uma mensagem do tipo "log", atualiza o texto do log. Se for "end", reabilita o botão de build e exibe uma mensagem de sucesso ou erro.                                                                                                                                                                      |
| `_log(self, m)`                           | `m`: `str`                               | `None`            | Helper para adicionar uma mensagem à caixa de texto de log na UI.                                                                                                                                                                                                                                                                                                                                                             |
| `_clear_log(self)`                        | `None`                                     | `None`            | Helper para limpar todo o conteúdo da caixa de texto de log.                                                                                                                                                                                                                                                                                                                                                                  |
| `_generate_inno_script(self)`             | `None`                                     | `str` \| `None` | Gera o conteúdo de um script Inno Setup (`.iss`) como uma string formatada. Ele usa os valores dos widgets da UI (nome do app, versão, etc.) para preencher o template do script. Valida se a pasta de distribuição do PyInstaller existe antes de prosseguir.                                                                                                                                                           |

---

### `src/logger_setup.py`

Configura um sistema de logging centralizado para a aplicação.

#### Classe: `StatusBarHandler(logging.Handler)`

| Função / Método                  | Parâmetros                       | Retorno  | Descrição Detalhada                                                                                                                                                                                  |
| :---------------------------------- | :-------------------------------- | :------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `__init__(self, status_callback)` | `status_callback`: `function` | `None` | Inicializa o handler, armazenando a função de callback que será chamada para atualizar a barra de status.                                                                                           |
| `emit(self, record)`              | `record`: `LogRecord`         | `None` | Método chamado pelo sistema de logging sempre que uma nova mensagem é registrada. Ele formata a mensagem e a envia para a função de callback da UI de forma thread-safe, usando `after(0, ...)`. |

#### Funções Globais

| Função                                  | Parâmetros                              | Retorno  | Descrição Detalhada                                                                                                                                                                                                          |
| :---------------------------------------- | :--------------------------------------- | :------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `setup_logging(status_update_callback)` | `status_update_callback`: `function` | `None` | Configura o logger raiz da aplicação. Cria dois handlers: um `FileHandler` para salvar logs detalhados em `app.log` e o `StatusBarHandler` customizado para enviar mensagens para a UI. Adiciona ambos ao logger raiz. |

---

### `src/main_window.py`

É o coração da aplicação, definindo a janela principal, seus painéis, menus e a lógica de interação central.

#### Classe: `ProjectBuilderApp(ttk.Window)`

| Função / Método                                     | Parâmetros                                          | Retorno  | Descrição Detalhada                                                                                                                                                                                                                                                       |
| :----------------------------------------------------- | :--------------------------------------------------- | :------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `__init__(self)`                                     | `None`                                             | `None` | Construtor da classe. Define o tema, título e geometria da janela. Inicializa o sistema de logging, carrega ícones, instancia `PresetManager` e `TreeManager`, cria os widgets e associa os atalhos de teclado.                                                       |
| `_create_widgets(self)`                              | `None`                                             | `None` | Orquestra a criação dos componentes principais da UI: a barra de ferramentas (`_create_toolbar`), os painéis principais (`_create_main_panels`), o menu de contexto (`_create_context_menu`) e a barra de status (`_create_status_bar`).                         |
| `_create_main_panels(self)`                          | `None`                                             | `None` | Cria o layout de dois painéis (esquerda e direita). O painel esquerdo contém a árvore de arquivos (`ttk.Treeview`) com um estilo visual customizado. O painel direito contém um `ttk.Notebook` com abas para "Detalhes do Projeto" e "Visualização da Estrutura". |
| `_create_details_controls(self, parent)`             | `parent`: `widget`                               | `None` | Popula a aba "Detalhes" com controles para nome e descrição do preset, e botões para adicionar pastas/arquivos.                                                                                                                                                          |
| `_create_visual_controls(self, parent)`              | `parent`: `widget`                               | `None` | Popula a aba "Visualização" com uma caixa de texto (`tk.Text`) para exibir a representação textual da árvore de diretórios.                                                                                                                                         |
| `update_visual_tree_export(self, *args)`             | `*args`                                            | `None` | Obtém a estrutura de árvore do `TreeManager`, formata-a como texto e a exibe na aba de visualização. É chamada sempre que a árvore é modificada.                                                                                                                   |
| `_load_icons(self)`                                  | `None`                                             | `dict` | Carrega os arquivos de imagem (`.png`, `.ico`) do diretório `assets`, redimensiona-os e os converte para objetos `ImageTk.PhotoImage` para uso na UI. Retorna um dicionário de ícones.                                                                           |
| `_create_toolbar(self)`                              | `None`                                             | `None` | Cria a barra de ferramentas superior com botões para salvar preset, gerar estrutura, compilar app, organizar pasta e comboboxes para selecionar presets e templates.                                                                                                       |
| `_create_context_menu(self)`                         | `None`                                             | `None` | Cria o menu de contexto (clique com o botão direito) para a árvore de arquivos, com opções como Nova Pasta, Renomear, Excluir, Copiar e Colar.                                                                                                                          |
| `_create_status_bar(self)`                           | `None`                                             | `None` | Cria a barra de status na parte inferior da janela para exibir mensagens de log.                                                                                                                                                                                            |
| `_bind_shortcuts(self)`                              | `None`                                             | `None` | Associa atalhos de teclado (e.g., Ctrl+S, F2, Delete) a suas respectivas funções.                                                                                                                                                                                         |
| `_on_tree_select(self, event)`                       | `event`: `tk.Event`                              | `None` | Callback para o evento de seleção de item na árvore. Atualiza o log com o item selecionado.                                                                                                                                                                              |
| `_notify_update(self, message)`                      | `message`: `str`                                 | `None` | Função de callback passada ao `TreeManager`. É chamada quando a árvore é modificada para atualizar a visualização em texto e o log.                                                                                                                                |
| `update_status_from_log(self, message)`              | `message`: `str`                                 | `None` | Callback passada ao `setup_logging`. Atualiza o texto da barra de status.                                                                                                                                                                                                 |
| `_show_context_menu(self, event)`                    | `event`: `tk.Event`                              | `None` | Exibe o menu de contexto na posição do cursor quando o botão direito do mouse é clicado sobre a árvore.                                                                                                                                                                |
| `on_project_type_change(self, event)`                | `event`: `tk.Event`                              | `None` | Chamada quando um template de projeto (e.g., "App Python Básico") é selecionado. Carrega a estrutura do template correspondente na árvore.                                                                                                                               |
| `_load_presets_to_combobox(self)`                    | `None`                                             | `None` | Lista os presets salvos usando `PresetManager` e popula o combobox de presets na toolbar.                                                                                                                                                                                 |
| `new_preset(self)`                                   | `None`                                             | `None` | Limpa a árvore e os campos de texto para iniciar a criação de uma nova estrutura.                                                                                                                                                                                        |
| `save_preset(self)`                                  | `None`                                             | `None` | Pega a estrutura atual da árvore, o nome e a descrição e os salva como um novo preset JSON usando `PresetManager`.                                                                                                                                                     |
| `load_preset_from_combobox(self, event)`             | `event`: `tk.Event`                              | `None` | Carrega os dados de um preset selecionado no combobox e reconstrói a árvore com sua estrutura.                                                                                                                                                                            |
| `generate_structure_on_disk(self)`                   | `None`                                             | `None` | Pede ao usuário para selecionar um diretório base e, em seguida, chama `_create_recursive` para criar fisicamente as pastas e arquivos da árvore nesse diretório.                                                                                                     |
| `_create_recursive(self, base_path, parent_item_id)` | `base_path`: `Path`, `parent_item_id`: `str` | `None` | Função recursiva que percorre a árvore de itens da UI e cria as pastas e arquivos correspondentes no sistema de arquivos.                                                                                                                                                |
| `run(self)`                                          | `None`                                             | `None` | Inicia o loop principal da aplicação (`mainloop`), tornando a janela visível e interativa.                                                                                                                                                                             |

---

### `src/organizer_window.py`

Implementa a janela "Organizador de Pastas", que move arquivos para subpastas com base em regras.

#### Classe: `FolderOrganizerWindow(ttk.Toplevel)`

| Função / Método                     | Parâmetros            | Retorno  | Descrição Detalhada                                                                                                                                                                                                                                                                                                                                                                     |
| :------------------------------------- | :--------------------- | :------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `__init__(self, parent)`             | `parent`: `widget` | `None` | Inicializa a janela do organizador, definindo título, geometria e variáveis de controle. Chama `_create_widgets`.                                                                                                                                                                                                                                                                     |
| `_create_widgets(self)`              | `None`               | `None` | Constrói a interface do organizador: campo para selecionar o diretório, combobox para o modo de organização, área de texto para a pré-visualização e o botão "Organizar Agora!".                                                                                                                                                                                                 |
| `_organize_directory(self, dry_run)` | `dry_run`: `bool`  | `None` | O núcleo da lógica. Itera sobre os arquivos no diretório alvo. Para cada arquivo, determina a categoria principal pela extensão (usando `REVERSE_EXT_MAP`) e, em seguida, procura por palavras-chave no nome do arquivo para determinar uma subpasta (usando `KEYWORD_MAP`). Se `dry_run` for `True`, apenas exibe as ações no log. Se `False`, move os arquivos de fato. |
| `select_directory(self)`             | `None`               | `None` | Abre um diálogo para o usuário selecionar a pasta a ser organizada. Após a seleção, chama `run_preview`.                                                                                                                                                                                                                                                                           |
| `run_preview(self)`                  | `None`               | `None` | Chama `_organize_directory` com `dry_run=True` para mostrar ao usuário o que será feito sem mover nenhum arquivo.                                                                                                                                                                                                                                                                   |
| `run_organize(self)`                 | `None`               | `None` | Exibe uma mensagem de confirmação. Se o usuário concordar, chama `_organize_directory` com `dry_run=False` para executar a organização.                                                                                                                                                                                                                                          |
| `_log(self, message)`                | `message`: `str`   | `None` | Helper para adicionar uma mensagem à caixa de texto de log/preview.                                                                                                                                                                                                                                                                                                                      |
| `_clear_log(self)`                   | `None`               | `None` | Helper para limpar a caixa de texto de log/preview.                                                                                                                                                                                                                                                                                                                                       |

---

### `src/preset_manager.py`

Classe responsável por toda a lógica de manipulação de arquivos de preset.

#### Classe: `PresetManager`

| Função / Método                           | Parâmetros                                                          | Retorno              | Descrição Detalhada                                                                                                                                                                                                                                   |
| :------------------------------------------- | :------------------------------------------------------------------- | :------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `__init__(self, presets_dir)`              | `presets_dir`: `Path`                                            | `None`             | Inicializa o gerenciador, definindo o diretório onde os presets serão armazenados e garantindo que ele exista.                                                                                                                                        |
| `list_presets(self)`                       | `None`                                                             | `list[str]`        | Escaneia o diretório de presets e retorna uma lista ordenada com os nomes (sem a extensão `.json`) de todos os presets encontrados.                                                                                                                 |
| `save(self, name, description, structure)` | `name`: `str`, `description`: `str`, `structure`: `dict` | `bool`             | Cria um dicionário contendo metadados (nome, descrição, data de criação) e a estrutura da árvore. Serializa este dicionário em formato JSON e o salva em um arquivo `nome.json` no diretório de presets. Retorna `True` em caso de sucesso. |
| `load(self, name)`                         | `name`: `str`                                                    | `dict` \| `None` | Encontra o arquivo `nome.json`, o abre, e desserializa seu conteúdo JSON de volta para um dicionário Python. Retorna o dicionário ou `None` em caso de erro.                                                                                     |

---

### `src/project_templates.py`

Define estruturas de projeto pré-configuradas e o conteúdo de arquivos comuns.

| Constante / Função               | Descrição                                                                                                       |
| :--------------------------------- | :---------------------------------------------------------------------------------------------------------------- |
| `PYTHON_BASIC_APP`               | Um dicionário que define a estrutura de pastas e arquivos para uma aplicação Python simples.                   |
| `PYTHON_WEB_APP`, etc.           | Outros dicionários definindo diferentes tipos de projetos.                                                       |
| `PROJECT_TEMPLATES`              | Um dicionário que mapeia nomes amigáveis (e.g., "Python Basic App") para as constantes de estrutura de projeto. |
| `GITIGNORE_CONTENT`, etc.        | Strings multi-linha contendo o conteúdo padrão para arquivos como `.gitignore` e `README.md`.               |
| `get_template_content(filename)` | Função que recebe um nome de arquivo e retorna o conteúdo padrão para ele, se houver, ou uma string vazia.    |

---

### `src/tree_manager.py`

Gerencia todas as operações relacionadas ao widget `ttk.Treeview`, abstraindo a complexidade da manipulação de seus itens.

#### Classe: `TreeManager`

| Função / Método                                   | Parâmetros                                            | Retorno        | Descrição Detalhada                                                                                                                                                                       |
| :--------------------------------------------------- | :----------------------------------------------------- | :------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `__init__(self, tree_widget, icons)`               | `tree_widget`: `ttk.Treeview`, `icons`: `dict` | `None`       | Inicializa o gerenciador com a instância do Treeview e o dicionário de ícones. Associa os eventos de arrastar e soltar (`_bind_events`).                                               |
| `set_on_update_callback(self, callback)`           | `callback`: `function`                             | `None`       | Armazena a função de callback que será chamada sempre que a árvore for modificada.                                                                                                      |
| `add_folder(self)` / `add_file(self)`            | `None`                                               | `None`       | Adiciona um novo item (pasta ou arquivo) à árvore. Pede um nome ao usuário através de um diálogo e insere o item no local apropriado.                                                  |
| `rename_item(self)`                                | `None`                                               | `None`       | Permite ao usuário renomear o item selecionado.                                                                                                                                            |
| `delete_selected_items(self)`                      | `None`                                               | `None`       | Remove todos os itens atualmente selecionados da árvore após uma confirmação.                                                                                                           |
| `copy_item(self)` / `paste_item(self)`           | `None`                                               | `None`       | Implementa a funcionalidade de copiar e colar.`copy_item` armazena a estrutura do item selecionado no `self.clipboard`. `paste_item` reconstrói essa estrutura no local selecionado. |
| `find_item(self)`                                  | `None`                                               | `None`       | Procura por um item na árvore e o seleciona se encontrado.                                                                                                                                 |
| `clear_tree(self)`                                 | `None`                                               | `None`       | Remove todos os itens da árvore.                                                                                                                                                           |
| `get_structure(self, parent_id)`                   | `parent_id`: `str`                                 | `dict`       | Função recursiva que "lê" a árvore da UI e a converte em uma estrutura de dicionário aninhado, ideal para salvar em JSON.                                                              |
| `build_from_structure(self, structure, parent_id)` | `structure`: `dict`, `parent_id`: `str`        | `None`       | Função recursiva que recebe um dicionário de estrutura e "desenha" os itens correspondentes na árvore da UI.                                                                            |
| `export_to_text(self, project_name)`               | `project_name`: `str`                              | `str`        | Gera uma representação de texto formatada da árvore, semelhante à saída do comando `tree`.                                                                                           |
| `_bind_events(self)`                               | `None`                                               | `None`       | Associa os eventos de clique e movimento do mouse (`<ButtonPress-1>`, `<B1-Motion>`, `<ButtonRelease-1>`) às funções de arrastar e soltar.                                         |
| `_on_drag_start / _on_drag_motion / _on_drag_stop` | `event`: `tk.Event`                                | `None`       | Implementam a lógica de arrastar e soltar (Drag and Drop), permitindo que o usuário reorganize os itens na árvore com o mouse.                                                           |
| `_insert_item(self, parent_id, text, is_folder)`   | ...                                                    | `str`        | Helper interno para inserir um item na árvore, definindo seu texto, ícone e retornando seu ID.                                                                                            |
| `_get_icon_for_file(self, filename)`               | `filename`: `str`                                  | `PhotoImage` | Determina qual ícone usar para um arquivo com base em sua extensão.                                                                                                                       |

---

### `src/ui_dialogs.py`

Contém classes de diálogo customizadas para a aplicação.

#### Classe: `CreateFileDialog(simpledialog.Dialog)`

| Função / Método                | Parâmetros                                | Retorno    | Descrição Detalhada                                                                                                                           |
| :-------------------------------- | :----------------------------------------- | :--------- | :---------------------------------------------------------------------------------------------------------------------------------------------- |
| `__init__(self, parent, title)` | `parent`: `widget`, `title`: `str` | `None`   | Inicializa o diálogo.                                                                                                                          |
| `body(self, master)`            | `master`: `widget`                     | `widget` | Cria o corpo do diálogo: uma entrada para o nome do arquivo e um combobox para selecionar a extensão a partir da lista `FILE_EXTENSIONS`.   |
| `apply(self)`                   | `None`                                   | `None`   | Chamado quando o botão "OK" é pressionado. Concatena o nome do arquivo com a extensão selecionada e armazena o resultado em `self.result`. |

---

### `src/test_runner.py`

Um script simples para executar testes unitários ou de integração.

| Função / Método        | Descrição                                                                                                                                                                                                                                      |
| :------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test_export_to_text()` | Um exemplo de função de teste. Atualmente, ela demonstra como as funções do `TreeManager` poderiam ser chamadas isoladamente. Para testes de UI reais e completos, seriam necessários frameworks mais avançados como `pytest-tkinter`. |
