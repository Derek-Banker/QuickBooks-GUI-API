# src\quickbooks_gui_api\apis\invoices.py

import time
import logging
import pytomlpp

from typing import Any
from pathlib import Path
from datetime import datetime

from pywinauto import Application, WindowSpecification


from quickbooks_gui_api.managers import WindowManager, FileManager, Color, Helper
from quickbooks_gui_api.models import Invoice, Element

from quickbooks_gui_api.apis.api_exceptions import ConfigFileNotFound, InvalidPrinter

# Shortened window and dialog names:
NEW_INVOICE_WINDOW:         Element = Element("Window", "Create Invoices - Accounts Receivable (Editing Transaction...) ",  65280)
VIEWING_INVOICE_WINDOW:     Element = Element("Window", "Create Invoices - Accounts Receivable",                            65280)
FIND_INVOICE_WINDOW:        Element = Element("Window", "Find Invoices",                                                    None)
INVOICE_NUMBER_FIELD:       Element = Element("Edit",    None,                                                              3636)
FIND_BUTTON:                Element = Element("Pane",   "Find",                                                             51)
PRINT_INVOICE_WINDOW:       Element = Element("Window", "Print One Invoice",                                                None)
SAVE_PRINT_AS_WINDOW:       Element = Element("Window", "Save Print Output As",                                             None)
FILE_NAME_FIELD:            Element = Element("Edit",   "File name:",                                                       1001)
OVERWRITE_FILE_POPUP:       Element = Element("Window", "Confirm Save As",                                                  None)
DATE_ERROR_POPUP:           Element = Element("Window", "Warning",                                                          None)
AVAILABLE_CREDITS_POPUP:    Element = Element("Window", "Available Credits",                                                None)
CHANGED_TRANSACTION_POPUP:  Element = Element("Window", "Recording Transaction",                                            None)
ESTIMATE_LINKED_POPUP:      Element = Element("Window", "Recording Transaction",                                            None)
DATE_LOCKED_WINDOW:         Element = Element("Window", "QuickBooks",                                                       None)
# CANCEL_UNLOCK:              Element = Element("Pane",   "Cancel",                                                           52)
REVERT_BUTTON:              Element = Element("Pane",   "Revert",                                                           64)



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
                 logger: Any = logging.getLogger(__name__)
                 ) -> None:
        self.logger = logger
            
        if config_path is None:
            if Path(r"configs\config.toml").is_file():
                self.config_path = Path(r"configs\config.toml")
            else:
                raise

        self.load_config(config_path) 
        
        self.app    = application
        self.window = window

        self.window_manager = WindowManager()
        self.file_manager = FileManager()
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
                raise TypeError(f"Provided config path `{path}` is not an instance of Path.")

        try:
            config = pytomlpp.load(self.config_path)["QuickBooksGUIAPI"]

            self.SHOW_TOASTS:               bool    = config["SHOW_TOASTS"] 
            self.WINDOW_LOAD_DELAY:         float   = config["WINDOW_LOAD_DELAY"]
            self.DIALOG_LOAD_DELAY:         float   = config["DIALOG_LOAD_DELAY"]
            self.NAVIGATION_DELAY:          float   = config["NAVIGATION_DELAY"]
            self.STRING_MATCH_THRESHOLD:    float   = config["STRING_MATCH_THRESHOLD"]
            self.MAX_INVOICE_SAVE_TIME:     float   = config["MAX_INVOICE_SAVE_TIME"]
            self.ACCEPTABLE_FILE_AGE:       float   = config["ACCEPTABLE_FILE_AGE"]
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
                    self.logger.debug(f"Closed window `{top_title}`. Attempt `{i+1}`/`{self.HOME_TRIES}`.")
                except Exception:
                    self.logger.exception(f"Error attempting to close targeted window, `{top_title}`")
        

    def save(
        self, 
        invoices: Invoice | list[Invoice],
        # save_directory: Path,
    ) -> None:

        queue: list[Invoice] = []
        number_of_invoices: int

        if isinstance(invoices, Invoice):
            queue.append(invoices)
            number_of_invoices = 1
            self.logger.debug("Single invoice detected, added to queue.")
        else:
            queue = invoices
            number_of_invoices = len(queue)
            self.logger.debug(f"List detected. Appended `{number_of_invoices}` record to queue for processing.")

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
                    self.logger.warning(f"Unable to initially focus on the invoice number field, reattempting. Attempts remaining `{remaining_attempts}`.")
                    self.window_manager.send_input('tab')
                    remaining_attempts -= 1

                self.logger.debug("Invoice number field is active, inserting number.")
                self.window_manager.send_input(string=queue[0].number)
                FIND_BUTTON.as_element(self.window).click_input()
            else:
                error = ValueError(f"Unable to ascertain that the find_invoice_dialog is active in the set interval of DIALOG_LOAD_DELAY = `{self.DIALOG_LOAD_DELAY}`. Current dialog is `{self.window_manager.top_dialog(self.app)}`.")
                self.logger.error(error)
                raise error

        
        def _print_to_pdf():
            self.window.set_focus()
            self.window_manager.send_input(keys=["ctrl","p"])
            
            if self.window_manager.is_element_active(PRINT_INVOICE_WINDOW.as_element(self.window), timeout=self.DIALOG_LOAD_DELAY, retry_interval=0.05, attempt_focus=True):
                self.logger.debug("The print_invoice_dialog was found and determined to be active. Proceeding to verify and select printer...")

                valid_printer = self.helper.capture_isolate_ocr_match(
                                    PRINT_INVOICE_WINDOW.as_element(self.window),
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
                self.logger.debug(f"Unwanted dialog detected. `{top_dialog_title}` Accommodating...")
                unwanted_dialog = self.window.child_window(control_type= "Window", title = top_dialog_title)
                unwanted_dialog.set_focus()    

            if top_dialog_title == AVAILABLE_CREDITS_POPUP.title:
                focus()
                self.window_manager.send_input(keys=['alt', 'n'])

            elif top_dialog_title == CHANGED_TRANSACTION_POPUP.title:
                focus()
                self.window_manager.send_input(keys=['alt', 'n'])

            elif top_dialog_title == ESTIMATE_LINKED_POPUP.title:
                focus()
                self.window_manager.send_input(keys=['alt', 'n'])

            elif top_dialog_title == OVERWRITE_FILE_POPUP.title:
                focus()
                self.window_manager.send_input(keys=['y'])

            elif top_dialog_title == DATE_LOCKED_WINDOW.title:
                focus()
                self.window_manager.send_input(keys=['esc'])
                REVERT_BUTTON.as_element(self.window).click_input()

# --- HELPERS END --------------------------------------------------------------------------

        pre_existing_file_hash: str = ""

        loop_start = datetime.now()
        while len(queue) != 0:      
            self.logger.info(f"Now saving invoice `{((number_of_invoices-len(queue)) + 1)}`/`{ number_of_invoices}`...")
            self.window.set_focus()
            
            save_path = queue[0].export_path() 
            pre_existing_file = save_path.exists()

            if pre_existing_file:
                pre_existing_file_hash = self.file_manager.hash_file(save_path)

            start = datetime.now()
            if self.window_manager.top_dialog(self.app) == NEW_INVOICE_WINDOW.title or self.window_manager.top_dialog(self.app) == VIEWING_INVOICE_WINDOW.title:
                _find_invoice()
                _handle_unwanted_dialog()

            if self.window_manager.top_dialog(self.app) == VIEWING_INVOICE_WINDOW.title:
                _print_to_pdf()
                _handle_unwanted_dialog()
            

            if  self.window_manager.top_dialog(self.app) == SAVE_PRINT_AS_WINDOW.title:
                _save_pdf_file()
                _handle_unwanted_dialog()



            if self.file_manager.wait_for_file(save_path, self.MAX_INVOICE_SAVE_TIME):
                time.sleep(0.15) # Annoyingly necessary delay. Break without it.
                self.logger.debug(f"The report file, `{save_path.name}`, exists.")
                self.file_manager.wait_till_stable(save_path, self.MAX_INVOICE_SAVE_TIME)
                self.logger.debug(f"The report file, `{save_path.name}`, is stable.")
               
                if pre_existing_file:
                    self.logger.warning(f"The file `{save_path.name}` existed before the report was saved. Comparing the file hashes and inspecting 'last modified' time...")
                    hashes_match = pre_existing_file_hash == self.file_manager.hash_file(save_path)
                    time_since_modified = self.file_manager.time_since_modified(save_path)    

                    if not hashes_match and (time_since_modified > self.ACCEPTABLE_FILE_AGE):
                        error = ValueError(f"The files hash match `{hashes_match}` and the file's age `{time_since_modified}` is higher than the configured threshold `self.ACCEPTABLE_FILE_AGE`.")
                        self.logger.error(error)
                        raise error

                _handle_unwanted_dialog() 
                stop = datetime.now()
                self.logger.info(f"Invoice number `{queue[0].number}` saved in: `{stop - start}`.\n")
                queue.remove(queue[0]) 

        self.home()
        
        loop_end = datetime.now()
        self.logger.info(f"All invoices saved in: `{loop_end - loop_start}`.")



                


    
        
        
