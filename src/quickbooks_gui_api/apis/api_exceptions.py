# src\quickbooks_gui_api\apis\api_exceptions.py

class APIException(Exception):
    """An exception relating to an API level module."""
    pass

class ConfigFileNotFound(APIException):
    """The config file was not found."""
    def __init__(self, path) -> None:
        super().__init__("Unable to find config file at the following path `%s`.", path)
    pass

class ExpectedWindowNotFound(APIException):
    """The expected window was unable to be confidently found."""
    pass

class ExpectedDialogNotFound(APIException):    
    """The expected dialog window was unable to be confidently found."""
    pass

class InvalidPrinter(APIException):
    """The currently selected printed does not match the `VALID_INVOICE_PRINTER` defined in the config."""
