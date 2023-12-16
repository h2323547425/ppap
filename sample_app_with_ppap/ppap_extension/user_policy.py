from ppap.policy import Policy
from ppap.function_wrapper import Flag

class UserFlag(Flag):
    USERNAME = 0

class UserPolicy(Policy):
    def __init__(self, userId, userDB):
        self.userId = userId
        self.userDB = userDB
        super().__init__("UserPolicy")

    def check_policy(self, context, flag):
        if flag == UserFlag.USERNAME:
            # print("\n\nchecking username")
            # print(context.user)
            # print(self.userId)
            # print(context.user == self.userId)
            return context.user and context.user == self.userId
        return False