import shutil
import os
class CaseArchive:
def __init__(self, dir):
self.dir = dir
def archive_case(self, case_id, data):
archive_path = os.path.join(self.dir, f"archive_{case_id}")
os.makedirs(archive_path, exist_ok=True)
with open(os.path.join(archive_path, "data.txt"), 'w') as f:
f.write(str(data))