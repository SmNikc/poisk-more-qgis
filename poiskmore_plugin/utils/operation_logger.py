import logging
class OperationLogger:
def __init__(self, dir):
self.logger = logging.getLogger('operation')
handler = logging.FileHandler(os.path.join(dir, 'operations.log'))
self.logger.addHandler(handler)
self.logger.setLevel(logging.INFO)
def log(self, message):
self.logger.info(message)