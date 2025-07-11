# src\quickbooks_gui_api\apis\invoices.py

import time
import logging
import pytomlpp
from pathlib import Path

from typing import List, Final
from pywinauto import Application, WindowSpecification


from quickbooks_gui_api.managers import WindowManager, Color, Helper
from quickbooks_gui_api.models import Invoice, Element

from quickbooks_gui_api.apis.api_exceptions import ConfigFileNotFound, InvalidPrinter

# Shortened window and dialog names:
NEW_INVOICE_WINDOW: Element = Element("Window", "Create Invoices - Accounts Receivable (Editing Transaction...) ", 65280)
VIEWING_INVOICE_WINDOW: Element = Element("Window", "Create Invoices - Accounts Receivable", 65280)
FIND_INVOICE_WINDOW: Element = Element("Window", "Find Invoices", None)
INVOICE_NUMBER_FIELD: Element = Element("Edit", None, 3636)
FIND_BUTTON: Element = Element("Pane", "Find", 51)
PRINT_INVOICE_DIALOG: Element = Element("Window", "Print One Invoice", None)
SAVE_PRINT_AS: Element = Element("Window", "Save Print Output As", None)
FILE_NAME_FIELD: Element = Element("Edit", None, 1001)
OVERWRITE_FILE: Element = Element("Window", "Confirm Save As", None)
DATE_ERROR: Element = Element("Window", "Warning", None)
CREDITS: Element = Element("Window", "Available Credits", None)
CHANGED_TRANSACTION: Element = Element("Window", "Recording Transaction", None)




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

        self.window_manager = WindowManager()
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
            self.STRING_MATCH_THRESHOLD:    float   = config["STRING_MATCH_THRESHOLD"]
            self.VALID_INVOICE_PRINTER:     str     = config["VALID_INVOICE_PRINTER"]
            self.QUICKBOOKS_WINDOW_NAME:    str     = config["QUICKBOOKS_WINDOW_NAME"]
            self.HOME_TRIES:                int     = 10

        except Exception as e:
            self.logger.error(e)
            raise e

    def home(self) -> None:
        self.window.set_focus()
      
        for i in range(self.HOME_TRIES):
            titles = self.window_manager.get_all_dialog_titles(self.app)
            if len(titles) == 1 and self.QUICKBOOKS_WINDOW_NAME in titles[0]:
                return
            else:
                top_title = self.window_manager.top_dialog(self.app)
                try:
                    self.window.child_window(control_type = "Window", title = top_title).close()
                    self.logger.debug("Closed window `%s`. Attempt `%i`/`%i`.", top_title, i+1, self.HOME_TRIES)
                except Exception:
                    self.logger.exception("Error attempting to close targeted window, `%s`",top_title)
        

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

        self.home()

        self.window.set_focus()
        self.window_manager.send_input(["ctrl", "i"])

# --- HELPERS START --------------------------------------------------------------------------

        def _find_invoice():
            self.window.set_focus()

            self.window_manager.send_input(keys=["ctrl", "f"])

            if self.window_manager.is_element_active(FIND_INVOICE_WINDOW.as_element(self.window), timeout=self.DIALOG_LOAD_DELAY, retry_interval=0.05, attempt_focus=True):
                self.logger.debug("The find_invoice_dialog was found and determined to be active. Proceeding to enter invoice number...")

                # send the initial navigation inputs
                self.window_manager.send_input(keys=["tab"], send_count=3)

                remaining_attempts = 10
                # loop until the field is active or attempts run out
                while not self.window_manager.is_element_active(INVOICE_NUMBER_FIELD.as_element(self.window), timeout= 0.2, retry_interval=0.05, attempt_focus=True) and remaining_attempts > 0:
                    self.logger.warning("Unable to initially focus on the invoice number field, reattempting. Attempts remaining `%i`.", remaining_attempts)
                    self.window_manager.send_input('tab')
                    remaining_attempts -= 1

                self.logger.info("Invoice number field is active, inserting number.")
                self.window_manager.send_input(string=queue[0].number)
                FIND_BUTTON.as_element(self.window).click_input()
            else:
                error = ValueError(f"Unable to ascertain that the find_invoice_dialog is active in the set interval of DIALOG_LOAD_DELAY = `{self.DIALOG_LOAD_DELAY}`. Current dialog is `{self.window_manager.top_dialog(self.app)}`.")
                self.logger.error(error)
                raise error

        
        def _print_to_pdf():
            self.window.set_focus()
            self.window_manager.send_input(keys=["ctrl","p"])
            
            if self.window_manager.is_element_active(PRINT_INVOICE_DIALOG.as_element(self.window), timeout=self.DIALOG_LOAD_DELAY, retry_interval=0.05, attempt_focus=True):
                self.logger.debug("The print_invoice_dialog was found and determined to be active. Proceeding to verify and select printer...")

                valid_printer = self.helper.capture_isolate_ocr_match(
                                    PRINT_INVOICE_DIALOG.as_element(self.window),
                                    single_or_multi="single",
                                    color = Color(hex_val="4e9e19"),
                                    target_text= self.VALID_INVOICE_PRINTER,
                                    match_threshold= self.STRING_MATCH_THRESHOLD
                                )

                if valid_printer:
                    self.window_manager.send_input(keys=["enter"])
                else:
                    self.logger.error(InvalidPrinter)
                    raise InvalidPrinter
            
            else:
                error = ValueError(f"Unable to ascertain that the print_invoice_dialog is active in the set interval of DIALOG_LOAD_DELAY = `{self.DIALOG_LOAD_DELAY}`. Current dialog is `{self.window_manager.top_dialog(self.app)}`.")
                self.logger.error(error)
                raise error


        def _save_pdf_file():
            self.window.set_focus()
            # save_file_dialog = self.window.child_window(control_type = "Window", title = SAVE_PRINT_AS) # Throws error, multiple windows share title somehow?
            FILE_NAME_FIELD.as_element(self.window)
            
            if self.window_manager.is_element_active(FILE_NAME_FIELD.as_element(self.window), timeout=self.DIALOG_LOAD_DELAY, retry_interval=0.05, attempt_focus=True):
                # abs_path = save_directory.joinpath(queue[0].file_name)
                self.window_manager.send_input(['alt','n'])
                FILE_NAME_FIELD.as_element(self.window).set_text(str(queue[0].export_path()))
                self.window_manager.send_input(['alt','s'])
            else:
                error = ValueError(f"Unable to ascertain that the save_file_dialog is active in the set interval of DIALOG_LOAD_DELAY = `{self.DIALOG_LOAD_DELAY}`. Current dialog is `{self.window_manager.top_dialog(self.app)}`.")
                self.logger.error(error)
                raise error

            
        def _handle_unwanted_dialog():
            # time.sleep(self.DIALOG_LOAD_DELAY)
            top_dialog_title = self.window_manager.top_dialog(self.app)

            def focus():
                self.logger.debug("Unwanted dialog detected. `%s` Accommodating...",top_dialog_title)
                unwanted_dialog = self.window.child_window(control_type= "Window", title = top_dialog_title)
                unwanted_dialog.set_focus()    

            if top_dialog_title == CREDITS:
                focus()
                self.window_manager.send_input(keys=['alt', 'n'])

            elif top_dialog_title == CHANGED_TRANSACTION:
                focus()
                self.window_manager.send_input(keys=['alt', 'n'])

            elif top_dialog_title == OVERWRITE_FILE:
                focus()
                self.window_manager.send_input(keys=['y'])


            # elif top_dialog_title == DATE_ERROR:
            #     self.win_man.send_input(keys=['enter'])
            #     self.win_man.send_input(keys=['esc'])
            #     _find_invoice()

# --- HELPERS END --------------------------------------------------------------------------

        index: int = 0
        while len(queue) != 0:  
            self.logger.debug("Saving invoice in queue. Current index is `%i`.", index)
            self.window.set_focus()
            self.logger.debug("Current top_dialog = `%s`.", self.window_manager.top_dialog(self.app))
            if self.window_manager.top_dialog(self.app) == NEW_INVOICE_WINDOW or self.window_manager.top_dialog(self.app) == VIEWING_INVOICE_WINDOW:
                _find_invoice()
                _handle_unwanted_dialog()

            if self.window_manager.top_dialog(self.app) == VIEWING_INVOICE_WINDOW:
                _print_to_pdf()
                _handle_unwanted_dialog()

            # if self.win_man.top_dialog(self.app) == PRINT_INVOICE_DIALOG:
            #     _save_invoice()
            #     _handle_unwanted_dialog()

            if  self.window_manager.top_dialog(self.app) == SAVE_PRINT_AS:
                _save_pdf_file()
                _handle_unwanted_dialog() 
                queue.remove(queue[0]) 



                


    
        
        
