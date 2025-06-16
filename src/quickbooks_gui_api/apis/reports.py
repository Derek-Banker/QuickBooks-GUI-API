import logging
from pathlib import Path

from typing import List, Dict, Any, overload

from src.quickbooks_gui_api.managers import WindowManager, ImageManager, OCRManager 

class Reports:
    """
    Handles the control logic for saving reports.
    Attributes:
        logger (logging.Logger): Logger instance for logging operations.
    """

    def __init__(self,
                 logger: logging.Logger | None = None
                 ) -> None:
        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            if isinstance(logger, logging.Logger):
                self.logger = logger 
            else:
                raise TypeError("Provided parameter `logger` is not an instance of `logging.Logger`.")
            

    def save ()