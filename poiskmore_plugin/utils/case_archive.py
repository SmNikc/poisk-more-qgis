class CaseArchive: def init(self, dir): self.dir = dir
def archive_case(self, case_id, data): timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") archive_path = os.path.join(self.dir, f"archive_{case_id}_{timestamp}.json") with open(archive_path, 'w') as f: json.dump(data, f) return archive_path
def load_archived_case(self, path): with open(path, 'r') as f: return json.load(f)