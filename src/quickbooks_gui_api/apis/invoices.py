import logging
from pathlib import Path

from typing import List, Dict, Any, overload, Final

from src.quickbooks_gui_api.managers import WindowManager, ImageManager, OCRManager 
from src.quickbooks_gui_api.models import Invoice

# Shortened window and dialog names:
CREATE_INVOICES: Final[str] = "Create Invoices - Accounts Receivable (Editing Transaction...)"
FIND_INVOICED: Final[str] = "Find Invoices"
PRINT_INVOICE: Final[str] = "Print One Invoice"
SAVE_INVOICE: Final[str] = "Save Print Output As"
OVERWRITE_FILE: Final[str] = "Confirm Save As"
DATE_ERROR: Final[str] = "Warning"
CREDITS: Final[str] = "Available Credits"
CHANGE_TRANSACTION: Final[str] = "Recording Transaction"



class Invoices:
    """
    Handles the control logic and process for saving invoices
    Attributes:
        logger (logging.Logger): Logger instance for logging operations.
    """

    def __init__(self,
                 application: Any,
                 logger: logging.Logger | None = None
                 ) -> None:
        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            if isinstance(logger, logging.Logger):
                self.logger = logger 
            else:
                raise TypeError("Provided parameter `logger` is not an instance of `logging.Logger`.")
            
        self.application = application
            
    def save(
        self, 
        invoices: Invoice | List[Invoice]
    ) -> None:

        queue: List[Invoice] = []

        if isinstance(invoices, Invoice):
            queue.append(invoices)
            self.logger.debug("Single invoice detected, appending to queue.")
        else:
            queue = invoices
            self.logger.debug("List detected. Appending `%i` to queue for processing.", len(invoices))

        window_man = WindowManager(self.application)
        image_man = ImageManager()
        ocr_man = OCRManager()

        window_man.home()

        window_man.send_input(["ctrl", "i"])

        index: int = 0
        while len(queue) != 0:  

            if window_man.current_dialog() == CREATE_INVOICES:

                window_man.send_input(["ctrl", "f"])



