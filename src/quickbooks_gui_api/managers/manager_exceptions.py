# src\quickbooks_gui_api\managers\manager_exceptions.py

class ManagerException(Exception):
    """An exception relating to an Manager level module."""
    pass


# --- Window Manager  ------------------------------------------------------------------

class WindowFocusFail(ManagerException):
    """A window was unable to be focused"""
    def __init__(self, target: str, current: str) -> None:
        message = (f"Attempt to focus the window '{target}' failed. The window '{current}' is currently focused.")
        super().__init__(message)


class WindowNotFound(ManagerException):
    """Raised when a window cannot be found within a timeout."""
    pass

class UnexpectedState(ManagerException):
    pass

# --- Image Manager   ------------------------------------------------------------------

class CaptureFailed(ManagerException):
    """Attempted Capture Failed"""
    pass

# --- Process Manager ------------------------------------------------------------------
# --- OCR Manager     ------------------------------------------------------------------



