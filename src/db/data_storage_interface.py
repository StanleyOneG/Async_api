from abc import ABC, abstractmethod


class DataStorageInterface(ABC):
    # def __init__(self, storage_client):
    #     self.storage_client = self.create_storage_client(storage_client)

    # def create_storage_client(self, storage_client):
    #     client = Depends(get_elastic_service)
    #     return client

    @abstractmethod
    async def get_data_by_id(self, *args, **kwargs) -> dict:
        pass

    @abstractmethod
    async def search_data(self, *args, **kwargs) -> list:
        pass
