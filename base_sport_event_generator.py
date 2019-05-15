import abc

class SportEventGenerator(abc.ABC):
    @abc.abstractmethod
    def getKeys(self):
        pass
    @abc.abstractmethod
    def buildEvents(self):
        pass
    @abc.abstractmethod
    def getUsers(self):
        pass
