class LakehouseError(Exception):
    """Custom exception for Lakehouse client errors."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"LakehouseError: {self.message}"