from ppap.context import Context
from ppap.function_wrapper import FunctionWrapper
from ppap.policy_assertion_exception import PolicyAssertionError
from ppap.policy import Policy

class Container():
    def __init__(self, data, policy: Policy):
        self.__data = data
        self.__policy = policy

    def invoke(self, funcWrapper: FunctionWrapper):
        if self.__policy.check_policy(Context(), funcWrapper.flag):
            funcWrapper.func(self.__data)
        else:
            raise PolicyAssertionError(self.__policy)
