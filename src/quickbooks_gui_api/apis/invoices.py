# src\quickbooks_gui_api\apis\invoices.py

import time
import logging
import pytomlpp
from pathlib import Path

from typing import List, Dict, Any, overload, Final
from pywinauto import Application, WindowSpecification


from quickbooks_gui_api.managers import WindowManager, ImageManager, Color, OCRManager, StringManager, ProcessManager, Helper
from quickbooks_gui_api.models import Invoice, Image

from quickbooks_gui_api.apis.api_exceptions import ConfigFileNotFound, ExpectedDialogNotFound, InvalidPrinter

# Shortened window and dialog names:
BLANK_INVOICE:          Final[str] = "Create Invoices - Accounts Receivable (Editing Transaction...) "
VIEWING_INVOICE:        Final[str] = "Create Invoices - Accounts Receivable"
FIND_INVOICE_DIALOG:    Final[str] = "Find Invoices"
PRINT_INVOICE_DIALOG:   Final[str] = "Print One Invoice"
SAVE_PRINT_AS:          Final[str] = "Save Print Output As"
OVERWRITE_FILE:         Final[str] = "Confirm Save As"
DATE_ERROR:             Final[str] = "Warning"
CREDITS:                Final[str] = "Available Credits"
CHANGED_TRANSACTION:    Final[str] = "Recording Transaction"





class Invoices:
    """
    Handles the control logic and process for saving invoices
    Attributes:
        logger (logging.Logger): Logger instance for logging operations.
    """


    def __init__(self,
                 application: Application,
                 window: WindowSpecification,
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
        
        self.app    = application
        self.window = window

        # self.pro_man = ProcessManager()
        self.img_man = ImageManager() 
        self.str_man = StringManager()
        self.win_man = WindowManager()
        self.ocr_man = OCRManager()
        self.helper = Helper()
            
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
            config = pytomlpp.load(self.config_path)["QuickBooksGUIAPI"]

            self.SHOW_TOASTS:               bool    = config["SHOW_TOASTS"] 
            self.WINDOW_LOAD_DELAY:         float   = config["WINDOW_LOAD_DELAY"]
            self.DIALOG_LOAD_DELAY:         float   = config["DIALOG_LOAD_DELAY"]
            self.NAVIGATION_DELAY:          float   = config["NAVIGATION_DELAY"]
            self.VALID_INVOICE_PRINTER:     str     = config["VALID_INVOICE_PRINTER"]
            self.STRING_MATCH_THRESHOLD:    float   = config["STRING_MATCH_THRESHOLD"]
            self.HOME_TRIES:                int     = 10

        except Exception as e:
            self.logger.error(e)
            raise e

    def home(self) -> None:
        self.window.set_focus()
        counter = self.HOME_TRIES
        while len(self.win_man.get_all_dialog_titles(self.app)) > 1 and counter > 0:
            self.logger.debug("More than one dialog window detected, attempting to get to the base level aka 'Home'")
            self.win_man.send_input('esc')
            counter -= 1
            time.sleep(1)

    def save(
        self, 
        invoices: Invoice | List[Invoice],
        # save_directory: Path,
    ) -> None:

        queue: List[Invoice] = []

        if isinstance(invoices, Invoice):
            queue.append(invoices)
            self.logger.debug("Single invoice detected, appending to queue.")
        else:
            queue = invoices
            self.logger.debug("List detected. Appending `%i` to queue for processing.", len(invoices))

        # if save_directory.is_dir():
        #     self.logger.debug("Provided `save_directory`, `%s`, does exist. Proceeding...", save_directory)
        # else:
        #     error = ValueError("Provided `save_directory`, `%s`, does NOT exist. Raising value error.", save_directory) 
        #     self.logger.error(error)
        #     raise error

        self.home()

        self.window.set_focus()
        self.win_man.send_input(["ctrl", "i"])

# --- HELPERS START --------------------------------------------------------------------------

        def _find_invoice():
            self.window.set_focus()

            self.win_man.send_input(keys=["ctrl", "f"])
            find_invoice_dialog = self.window.child_window(control_type = "Window", title = FIND_INVOICE_DIALOG)

            if self.win_man.is_element_active(find_invoice_dialog, timeout=self.DIALOG_LOAD_DELAY, retry_interval=0.05, attempt_focus=True):
                self.logger.debug("The find_invoice_dialog was found and determined to be active. Proceeding to enter invoice number...")

                # send the initial navigation inputs
                self.win_man.send_input(keys=["tab"], send_count=3)

                invoice_number_field = self.window.child_window(control_type = "Edit", auto_id = "3636")

                remaining_attempts = 10
                # loop until the field is active or attempts run out
                while not self.win_man.is_element_active(invoice_number_field, timeout= 0.2, retry_interval=0.05, attempt_focus=True) and remaining_attempts > 0:
                    self.logger.warning("Unable to initially focus on the invoice number field, reattempting. Attempts remaining `%i`.", remaining_attempts)
                    self.win_man.send_input('tab')
                    remaining_attempts -= 1

                self.logger.info("Invoice number field is active, inserting number.")
                self.win_man.send_input(string=queue[0].number)
                self.window.child_window(title = "Find", auto_id='51').click_input()
            else:
                error = ValueError(f"Unable to ascertain that the find_invoice_dialog is active in the set interval of DIALOG_LOAD_DELAY = `{self.DIALOG_LOAD_DELAY}`. Current dialog is `{self.win_man.top_dialog(self.app)}`.")
                self.logger.error(error)
                raise error

        
        def _print_to_pdf():
            self.window.set_focus()
            self.win_man.send_input(keys=["ctrl","p"])
            print_invoice_dialog = self.window.child_window(control_type = "Window", title = PRINT_INVOICE_DIALOG)
            if self.win_man.is_element_active(print_invoice_dialog, timeout=self.DIALOG_LOAD_DELAY, retry_interval=0.05, attempt_focus=True):
                self.logger.debug("The print_invoice_dialog was found and determined to be active. Proceeding to verify and select printer...")

                valid_printer = self.helper.capture_isolate_ocr_match(
                                    print_invoice_dialog,
                                    single_or_multi="single",
                                    color = Color(hex_val="4e9e19"),
                                    target_text= self.VALID_INVOICE_PRINTER,
                                    match_threshold= self.STRING_MATCH_THRESHOLD
                                )

                if valid_printer:
                    self.win_man.send_input(keys=["enter"])
                else:
                    self.logger.error(InvalidPrinter)
                    raise InvalidPrinter
            
            else:
                error = ValueError(f"Unable to ascertain that the print_invoice_dialog is active in the set interval of DIALOG_LOAD_DELAY = `{self.DIALOG_LOAD_DELAY}`. Current dialog is `{self.win_man.top_dialog(self.app)}`.")
                self.logger.error(error)
                raise error


        def _save_pdf_file():
            self.window.set_focus()
            save_file_dialog = self.window.child_window(control_type = "Window", title = SAVE_PRINT_AS)
            file_name_field = self.window.child_window(control_type = "Edit", auto_id= '1001')
            
            if self.win_man.is_element_active(file_name_field, timeout=self.DIALOG_LOAD_DELAY, retry_interval=0.05, attempt_focus=True):
                # abs_path = save_directory.joinpath(queue[0].file_name)
                self.helper.safely_set_text(str(queue[0].export_path()), file_name_field)
                self.win_man.send_input(['alt','s'])
            else:
                error = ValueError(f"Unable to ascertain that the save_file_dialog is active in the set interval of DIALOG_LOAD_DELAY = `{self.DIALOG_LOAD_DELAY}`. Current dialog is `{self.win_man.top_dialog(self.app)}`.")
                self.logger.error(error)
                raise error

            
        def _handle_unwanted_dialog():
            # time.sleep(self.DIALOG_LOAD_DELAY)
            top_dialog_title = self.win_man.top_dialog(self.app)

            def focus():
                self.logger.debug("Unwanted dialog detected. `%s` Accommodating...",top_dialog_title)
                unwanted_dialog = self.window.child_window(control_type= "Window", title = top_dialog_title)
                unwanted_dialog.set_focus()    

            if top_dialog_title == CREDITS:
                focus()
                self.win_man.send_input(keys=['alt', 'n'])

            elif top_dialog_title == CHANGED_TRANSACTION:
                focus()
                self.win_man.send_input(keys=['alt', 'n'])

            elif top_dialog_title == OVERWRITE_FILE:
                focus()
                self.win_man.send_input(keys=['y'])


            # elif top_dialog_title == DATE_ERROR:
            #     self.win_man.send_input(keys=['enter'])
            #     self.win_man.send_input(keys=['esc'])
            #     _find_invoice()

# --- HELPERS END --------------------------------------------------------------------------

        index: int = 0
        while len(queue) != 0:  
            self.logger.debug("Saving invoice in queue. Current index is `%i`.", index)
            self.window.set_focus()
            self.logger.debug("Current top_dialog = `%s`.", self.win_man.top_dialog(self.app))
            if self.win_man.top_dialog(self.app) == BLANK_INVOICE or self.win_man.top_dialog(self.app) == VIEWING_INVOICE:
                _find_invoice()
                _handle_unwanted_dialog()

            if self.win_man.top_dialog(self.app) == VIEWING_INVOICE:
                _print_to_pdf()
                _handle_unwanted_dialog()

            # if self.win_man.top_dialog(self.app) == PRINT_INVOICE_DIALOG:
            #     _save_invoice()
            #     _handle_unwanted_dialog()

            if  self.win_man.top_dialog(self.app) == SAVE_PRINT_AS:
                _save_pdf_file()
                queue.remove(queue[0]) 
                _handle_unwanted_dialog() 



                


    
        
        
