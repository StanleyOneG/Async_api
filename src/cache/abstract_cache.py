from abc import ABC, abstractmethod


class AbstractBaseCache(ABC):
    """Abstract interface for cache services"""

    @abstractmethod
    def get(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def set(self, *args, **kwargs):
        pass