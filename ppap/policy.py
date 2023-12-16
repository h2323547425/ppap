from abc import ABC, abstractmethod
from ppap.context import Context
from ppap.function_wrapper import Flag

class Policy(ABC):
    @abstractmethod
    def __init__(self, name):
        self.name = name
        pass

    @abstractmethod
    def check_policy(self, context: Context, flag: Flag) -> bool:
        pass
