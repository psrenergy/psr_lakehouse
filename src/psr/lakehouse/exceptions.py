class LakehouseError(Exception):
    """Custom exception for Lakehouse client errors."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"LakehouseError: {self.message}"

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