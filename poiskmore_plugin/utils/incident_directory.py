def add_incident(self, data): self.incidents.append(data)
def get_incident(self, index): return self.incidents[index] if index < len(self.incidents) else None