class OperationLogger: def init(self, dir): log_path = os.path.join(dir, 'operations.log') logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s - %(message)s')
def log(self, msg): logging.info(msg)
def log_error(self, msg): logging.error(msg)