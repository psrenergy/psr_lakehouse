class LakehouseError(Exception):
    """Custom exception for Lakehouse client errors."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"LakehouseError: {self.message}"


class LakehouseAuthError(LakehouseError):
    """Exception for failures to authenticate against a lakehouse that requires a token.

    Unlike its siblings this does not prepend its own class name in `__str__`:
    a traceback already prints the class, so doing it again reads as
    "LakehouseAuthError: LakehouseAuthError: ..." in the one place a user is
    most likely to be reading carefully.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class LakehouseInputError(LakehouseError):
    """Exception for invalid input errors in Lakehouse client."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"LakehouseInputError: {self.message}"


class LakehouseGroupByFunctionError(LakehouseError):
    """Exception for invalid group by function errors in Lakehouse client."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"LakehouseGroupByFunctionError: {self.message}"
