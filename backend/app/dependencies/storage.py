from app.domain.interfaces.storage import IStorageProvider
from app.storage.local_storage import LocalStorageProvider

_storage_instance: IStorageProvider = LocalStorageProvider()

def get_storage_provider() -> IStorageProvider:
    return _storage_instance
