import time
import logging
import pytomlpp
from pathlib import Path

from typing import List, Dict, Any, overload, Final

from src.quickbooks_gui_api.managers import WindowManager, ImageManager, OCRManager, StringManager
from src.quickbooks_gui_api.models import Invoice, Image, Window

from src.quickbooks_gui_api.apis.api_exceptions import ConfigFileNotFound, ExpectedDialogNotFound, InvalidPrinter

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
                 config_path: Path | None = Path(r"configs\config.toml"),
                 logger: logging.Logger | None = None
                 ) -> None:
        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            if isinstance(logger, logging.Logger):
                self.logger = logger 
            else:
                raise TypeError("Provided parameter `logger` is not an instance of `logging.Logger`.")
            
        if config_path is None:
            if Path(r"configs\config.toml").is_file():
                self.config_path = Path(r"configs\config.toml")
            else:
                raise

        self.load_config(config_path) 
        
        self.application = application

        self.window_man = WindowManager(self.application)
        image_man = ImageManager()
        ocr_man = OCRManager()
            
    def load_config(self, path) -> None:
        if path is None:
            if Path(r"configs\config.toml").is_file():
                self.config_path = Path(r"configs\config.toml")
            else:
                raise ConfigFileNotFound(path)
        else:
            if isinstance(path, Path):
                if path.is_file:
                    self.config_path = path
            else:
                raise TypeError("Provided config path `%s` is not an instance of Path.", path)

        try:
            config = pytomlpp.load(self.config_path)["QuickBooksInvoicesSaver"]

            self.SHOW_TOASTS:               bool    = config["SHOW_TOASTS"] 
            self.WINDOW_LOAD_DELAY:         float   = config["WINDOW_LOAD_DELAY"]
            self.DIALOG_LOAD_DELAY:         float   = config["DIALOG_LOAD_DELAY"]
            self.NAVIGATION_DELAY:          float   = config["NAVIGATION_DELAY"]
            self.VALID_INVOICE_PRINTER:     str     = config("VALID_INVOICE_PRINTER")
            self.STRING_MATCH_THRESHOLD:    float   = config("STRING_MATCH_THRESHOLD") 

        except Exception as e:
            self.logger.error(e)
            raise e


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

        window_man  = WindowManager(self.application)
        image_man   = ImageManager()
        ocr_man     = OCRManager()
        string_man  = StringManager()

        window_man.home()

        window_man.send_input(["ctrl", "i"])

        def _find_invoice():
            window_man.send_input(["ctrl", "f"])
            time.sleep(self.DIALOG_LOAD_DELAY)
            window_man.send_input("tab", 3)
            window_man.send_input(string=queue[0].number)
            window_man.send_input(["alt", "d"])

        
        def _print_to_pdf():
            window_man.send_input(["ctrl","p"])
            time.sleep(self.DIALOG_LOAD_DELAY)
            dialog = window_man.active_dialog()
            dialog_capture = image_man.capture(dialog.size, dialog.position)
            isolated_field = image_man.isolate_regions(dialog_capture, (78, 158, 25))
            selected_printer = ocr_man.get_text(isolated_field)
            
            if string_man.is_match(self.STRING_MATCH_THRESHOLD, input=selected_printer, target=self.VALID_INVOICE_PRINTER):
                window_man.send_input("enter")
            else:
                self.logger.error(InvalidPrinter)
                raise InvalidPrinter
            
        def _save_invoice():
            dialog = window_man.active_dialog()
            dialog_capture = image_man.capture(dialog.size, dialog.position)
            isolated_field = image_man.isolate_regions(dialog_capture, (78, 158, 25))
            selected_printer = ocr_man.get_text(isolated_field)
            
            if string_man.is_match(self.STRING_MATCH_THRESHOLD, input=selected_printer, target=self.VALID_INVOICE_PRINTER):
                window_man.send_input("enter")
            else:
                self.logger.error(InvalidPrinter)
                raise InvalidPrinter



        index: int = 0
        while len(queue) != 0:  

            if window_man.active_dialog().name == CREATE_INVOICES:
                _find_invoice()
                
            if window_man.active_dialog().name == DATE_ERROR:
                _find_invoice()

            if window_man.active_dialog().name == CREATE_INVOICES:
                _print_to_pdf()

            if window_man.active_dialog().name == SAVE_INVOICE:
                _save_invoice()


                


    
        
        
