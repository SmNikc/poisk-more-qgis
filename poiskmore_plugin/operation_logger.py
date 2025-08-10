# operation_logger.py (логгер операций для отладки)
# Комментарий: Настройка системы логирования для плагина. Создает файл plugin.log 
# в директории плагина для записи отладочной информации и ошибок.
import logging
import os

def setup_logger(plugin_dir):
    logger = logging.getLogger('poiskmore_plugin')
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(os.path.join(plugin_dir, 'plugin.log'))
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

# Пример использования: logger = setup_logger(plugin_dir)
# logger.info("Plugin loaded")