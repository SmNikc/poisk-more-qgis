class IncidentDirectory:
def __init__(self):
self.incidents = []
def add_incident(self, data):
self.incidents.append(data)
def get_incident(self, index):
return self.incidents[index]