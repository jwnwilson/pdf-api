from ports.db import DbAdapter
from ports.storage import StorageAdapter, StorageData


def upload_asset(storage_adapter: StorageAdapter, db_adapter: DbAdapter) -> StorageData:
    """[summary]

    Args:
        html (str): [description]
        file_path (str): [description]

    Returns:
        [type]: [description]
    """
    upload_data = storage_adapter.upload_url()
    return upload_data
