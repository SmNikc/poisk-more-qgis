import logging
class Logger:
def __init__(self, file_path):
logging.basicConfig(filename=file_path, level=logging.INFO)
def log(self, message):
logging.info(message)