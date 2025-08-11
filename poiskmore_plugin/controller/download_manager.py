import os
import shutil
class DownloadManager:
def __init__(self, data_path):
self.data_path = data_path
self.descriptor = None
self.subscription = None
@property
def descriptor(self):
if self.descriptor is None:
self.descriptor = SerializationHelper.deserialize_file("DataCenter_Requests", os.path.join(self.data_path, "RequestXml"))
return self.descriptor
@property
def subscription(self):
if self.subscription is None:
self.subscription = SerializationHelper.deserialize_file("Saved_Weather_Download_Subscription", os.path.join(self.data_path, "SubscriptionXml"))
return self.subscription
@property
def exists(self):
return os.path.exists(os.path.join(self.data_path, "RequestXml"))
def delete(self):
if os.path.exists(self.data_path):
shutil.rmtree(self.data_path)
self.descriptor = None
self.subscription = None
def copy_to(self, path):
os.makedirs(path, exist_ok=True)
for file in os.listdir(self.data_path):
shutil.copy(os.path.join(self.data_path, file), path)