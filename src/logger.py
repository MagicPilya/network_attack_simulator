import logging
import os

LOG_MAX_LINES = 3000

def setup_logger(log_dir, log_name):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, log_name)
    
    # Создаем логгер
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)
    
    # Создаем обработчик файла
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setLevel(logging.DEBUG)
    
    # Создаем обработчик консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    # Создаем форматтер и добавляем его к обработчикам
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Добавляем обработчики к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Добавляем функцию очистки логов после записи
    logger.addFilter(LogFilter(log_file))
    
    return logger

class LogFilter(logging.Filter):
    def __init__(self, log_file):
        self.log_file = log_file

    def filter(self, record):
        self.check_log_file_size()
        return True

    def check_log_file_size(self):
        with open(self.log_file, 'r') as f:
            lines = f.readlines()
        if len(lines) > LOG_MAX_LINES:
            with open(self.log_file, 'w') as f:
                f.truncate(0)

