from abc import ABC, abstractmethod


class DataStorageInterface(ABC):
    @abstractmethod
    async def get_data_by_id(self, *args, **kwargs) -> dict:
        pass

    @abstractmethod
    async def search_data(self, *args, **kwargs) -> list:
        pass
