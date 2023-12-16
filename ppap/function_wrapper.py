from typing import Callable

Flag = int

class FunctionWrapper:

    def __init__(self, func: Callable, flag: Flag):
        self.flag = flag
        self.func = func