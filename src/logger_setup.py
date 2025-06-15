# src/logger_setup.py
import logging
import tkinter as tk

class StatusBarHandler(logging.Handler):
    """Handler de log que envia registros para uma função de callback (status bar)."""
    def __init__(self, status_callback):
        super().__init__()
        self.status_callback = status_callback
    
    def emit(self, record):
        msg = self.format(record)
        # Usa after(0, ...) para garantir que a atualização da UI seja thread-safe
        self.status_callback.__self__.after(0, lambda: self.status_callback(msg))

def setup_logging(status_update_callback):
    """Configura o sistema de logging global da aplicação."""
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Handler para salvar logs detalhados em um arquivo 'app.log'
    file_handler = logging.FileHandler('app.log', mode='w', encoding='utf-8')
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO)

    # Handler para a barra de status da UI
    status_handler = StatusBarHandler(status_update_callback)
    status_handler.setLevel(logging.INFO) # Apenas mensagens INFO ou superiores vão para o status
    status_handler.setFormatter(logging.Formatter('%(message)s')) # Formato simples para a UI

    # Configura o logger raiz para usar os handlers
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Evita adicionar handlers duplicados se a função for chamada mais de uma vez
    if not root_logger.handlers:
        root_logger.addHandler(file_handler)
        root_logger.addHandler(status_handler)

    logging.info("Sistema de logging inicializado.")