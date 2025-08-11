class SavedWeatherDownloadSubscription:
def __init__(self):
self.subscriptions = []
@property
def subscriptions(self):
return self._subscriptions
@subscriptions.setter
def subscriptions(self, value):
self._subscriptions = value