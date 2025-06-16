# src\quickbooks_gui_api\managers\manager_exceptions.py

class ManagerException(Exception):
    """An exception relating to an Manager level module."""
    pass


# --- Window Manager  ------------------------------------------------------------------

class WindowFocusFail(ManagerException):
    """A window was unable to be focused"""
    def __init__(self, target: str, current: str) -> None:
        super().__init__("Attempt to focus the window `%s` failed. The window `%s` is currently focused.", target, current)    
    pass

class UnexpectedState(ManagerException):
    pass

# --- Image Manager   ------------------------------------------------------------------

class CaptureFailed(ManagerException):
    """Attempted Capture Failed"""
    pass

# --- Process Manager ------------------------------------------------------------------
# --- OCR Manager     ------------------------------------------------------------------



