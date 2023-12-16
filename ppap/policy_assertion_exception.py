from ppap.policy import Policy

class PolicyAssertionError(Exception):
    def __init__(self, policy: Policy):
        super().__init__(f"Invocation with the provided context does not satisfy policy rules: {policy.name}")