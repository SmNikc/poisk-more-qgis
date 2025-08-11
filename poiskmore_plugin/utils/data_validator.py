class DataValidator:
def validate_datetime(self, dt):
return dt.isValid()
def validate_coords(self, coords):
try:
lat, lon = map(float, coords.split(','))
return -90 <= lat <= 90 and -180 <= lon <= 180
except:
return False