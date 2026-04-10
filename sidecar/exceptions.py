# ipcha/exceptions.py

class ModelDiversityError(ValueError):
    """
    Raised when the Proponent and Ipcha Agent are configured with models
    from the same family, which is not allowed.
    """
    def __init__(self, message: str, family: str):
        self.family = family
        super().__init__(message)


class DoWDefenseError(Exception):
    """Base exception for Denial-of-Wallet errors."""
    def __init__(self, message, user_id, observed_value, limit_value):
        self.user_id = user_id
        self.observed_value = observed_value
        self.limit_value = limit_value
        super().__init__(message)


class InvocationCostExceededError(DoWDefenseError):
    """Raised when a single claim's estimated cost is too high."""
    pass


class BudgetLimitExceededError(DoWDefenseError):
    """Raised when a user's rolling budget is exhausted."""
    pass
