import os
import shutil
from .serialization_helper import SerializationHelper


class DownloadManager:
    """Manage download descriptor and subscription data."""

    def __init__(self, data_path):
        self.data_path = data_path
        self._descriptor = None
        self._subscription = None

    @property
    def descriptor(self):
        if self._descriptor is None:
            self._descriptor = SerializationHelper.deserialize_file(
                "DataCenter_Requests", os.path.join(self.data_path, "RequestXml")
            )
        return self._descriptor

    @property
    def subscription(self):
        if self._subscription is None:
            self._subscription = SerializationHelper.deserialize_file(
                "Saved_Weather_Download_Subscription",
                os.path.join(self.data_path, "SubscriptionXml"),
            )
        return self._subscription

    @property
    def exists(self):
        return os.path.exists(os.path.join(self.data_path, "RequestXml"))

    def delete(self):
        if os.path.exists(self.data_path):
            shutil.rmtree(self.data_path)
            self._descriptor = None
            self._subscription = None

    def copy_to(self, path):
        os.makedirs(path, exist_ok=True)
        for file in os.listdir(self.data_path):
            shutil.copy(os.path.join(self.data_path, file), path)
