from abc import ABC, abstractmethod


class APIBase(ABC):

    @abstractmethod
    def api_connection(self):
        pass

    @abstractmethod
    def get_data(self):
        pass
