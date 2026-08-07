from abc import ABC, abstractmethod

class IService(ABC):

    @abstractmethod
    def info(self):
        pass

    @abstractmethod
    def status(self):
        pass

    @abstractmethod
    def health(self):
        pass

    @abstractmethod
    def execute(self, action=None, params=None):
        pass

    @abstractmethod
    def config(self):
        pass
