
import time
import logging
import pytomlpp
from pathlib import Path

from dataclasses import dataclass
from typing import List, Dict, Any, overload, Final
from pywinauto import Application, WindowSpecification


from quickbooks_gui_api.managers import WindowManager, ImageManager, Color, OCRManager, StringManager, ProcessManager, Helper
from quickbooks_gui_api.models import Report, Image, Element

from quickbooks_gui_api.apis.api_exceptions import ConfigFileNotFound, ExpectedDialogNotFound, InvalidPrinter


# Shortened window and dialog names:
# Element Name                        Control   Title                                           Auto ID
MEMORIZED_REPORTS_WINDOW    = Element("Window", "Memorized Report List",                        65281)
REPORT_WINDOW               = Element("Window",  None,                                          65282)
EXCEL_BUTTON                = Element("Pane",   "Excel",                                        7)
EXPORT_AS_WINDOW            = Element("Window", "Send Report to Excel",                         None)
AS_CSV_BUTTON               = Element("Pane",   "Create a comma separated values (.csv) file",  1841)
SAVE_FILE_AS_WINDOW         = Element("Window", "Create Disk File",                             None)
FILE_NAME_FIELD             = Element("Edit",   "File name:",                                   1148)
CANCEL_BUTTON               = Element("Button", "Cancel",                                       2)

CONFIRM_SAVE_AS             = Element("Window", "Confirm Save As",                              None)
HAVE_ANY_QUESTIONS          = Element("Window", None,                                           "FloatingViewerFrame")
NEW_FEATURE                 = Element("Pane",  "QB WPF Host",                                   None)
QUICKBOOKS_PAYMENTS         = Element("Window",'QuickBooks Payments',                           None)




class Reports:
    """
    Handles the control logic and process for saving reports
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
            self.HOME_TRIES:                int     = 10

            self.REPORT_NAME_MATCH_THRESHOLD: float   = config["REPORT_NAME_MATCH_THRESHOLD"]

        except Exception as e:
            self.logger.error(e)
            raise e

    def _handle_global_popups(self):
        all_titles = self.win_man.get_all_dialog_titles(self.app)

        if HAVE_ANY_QUESTIONS.title in all_titles:
            self.logger.debug("Unwanted dialog detected. `%s` Closing...",HAVE_ANY_QUESTIONS.title)
            HAVE_ANY_QUESTIONS.as_element(self.window).close()

        if NEW_FEATURE.title in all_titles:
            self.logger.debug("Unwanted dialog detected. `%s` Closing...",NEW_FEATURE.title)
            NEW_FEATURE.as_element(self.window).set_focus()
            self.win_man.send_input('enter')

        if QUICKBOOKS_PAYMENTS.title in all_titles:
            self.logger.debug("Unwanted dialog detected. `%s` Closing...",QUICKBOOKS_PAYMENTS.title)
            QUICKBOOKS_PAYMENTS.as_element(self.window).set_focus()
            self.win_man.send_input('esc')

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
        reports: Report | List[Report],
        # save_directory: Path,
    ) -> None:

        queue: List[Report] = []

        if isinstance(reports, Report):
            queue.append(reports)
            self.logger.debug("Single report detected, appending to queue.")
        else:
            queue = reports
            self.logger.debug("List detected. Appending `%i` to queue for processing.", len(reports))

        self._handle_global_popups()
        self.home()

        self.window.set_focus()

        def _memorized_reports():
            self.window.set_focus()
            self.win_man.send_input(['alt', 'R'])
            self.win_man.send_input('z')
            self.win_man.send_input('enter')
        
        def _find_report():
            self.window.set_focus()
            report_name = queue[0].name 
            length = len(report_name)

            for i in range(length):
                char = report_name[i]
                self.win_man.send_input(string=char)

            valid_match, pulled_text, match_confidence = self.helper.capture_isolate_ocr_match(
                self.window,
                single_or_multi= "single",
                color= Color(hex_val="4e9e19"),
                tolerance= 5.0,
                target_text= report_name,
                match_threshold= self.REPORT_NAME_MATCH_THRESHOLD
            )

            if valid_match:
                self.win_man.send_input(["alt","s"])
                self.logger.info("The selected report `%s` matched the intended report, `%s`, with a confidence of `%s`.",pulled_text,report_name,match_confidence)
            else:
                self.logger.error(f"The selected report, `{pulled_text}`, only matched the intended report, `{report_name}`, with a confidence of `{match_confidence}`. This is below the configured threshold")

        def _save_as_new_worksheet():
            self.window.set_focus()
            EXCEL_BUTTON.as_element(self.window).click_input()
            self.win_man.send_input('n')

        def _save_as_csv():
            self.window.set_focus()
            AS_CSV_BUTTON.as_element(self.window).click_input()
            self.win_man.send_input(['alt', 'x'])

        def _save_file():
            self.window.set_focus()
            FILE_NAME_FIELD.as_element(self.window).set_text(str(queue[0].export_path()))
            self.win_man.send_input(keys='enter')

        def _close_report():
            self.window.set_focus()
            self.win_man.send_input(keys=['esc'])

        def _handle_unwanted_dialog():
            self.window.set_focus()
            top_dialog_title = self.win_man.top_dialog(self.app)

            def focus():
                self.logger.debug("Unwanted dialog detected. `%s` Accommodating...",top_dialog_title)
                unwanted_dialog = self.window.child_window(control_type= "Window", title = top_dialog_title)
                unwanted_dialog.set_focus()    

            if top_dialog_title == CONFIRM_SAVE_AS.title:
                focus()
                self.win_man.send_input(keys=['y'])

            self._handle_global_popups()

        

        self.logger.info("Entering save loop...")
        while len(queue) != 0:  
            _memorized_reports()

            if self.win_man.top_dialog(self.app) == MEMORIZED_REPORTS_WINDOW.title:
                self.logger.debug("Memorized report list is detected and focused...") 
                _find_report()
                _handle_unwanted_dialog()
            else:
                _memorized_reports()

            if self.win_man.is_element_active(EXCEL_BUTTON.as_element(self.window), timeout=self.WINDOW_LOAD_DELAY):
                self.logger.debug("Selected report is detected and focused...")
                _save_as_new_worksheet()
                _handle_unwanted_dialog()
            
            if self.win_man.is_element_active(AS_CSV_BUTTON.as_element(self.window), timeout=self.WINDOW_LOAD_DELAY):
                self.logger.debug("`%s` Button is detected and focused...",AS_CSV_BUTTON.title)
                _save_as_csv()
                _handle_unwanted_dialog()

            if self.win_man.is_element_active(FILE_NAME_FIELD.as_element(self.window), timeout=self.WINDOW_LOAD_DELAY):
                self.logger.debug("`%s` Window is detected and focused...",SAVE_FILE_AS_WINDOW.title)
                _save_file()
                _handle_unwanted_dialog()
            else:
                print("NOT DETECTED")
             
            if self.win_man.is_element_active(CANCEL_BUTTON.as_element(self.window), timeout=self.WINDOW_LOAD_DELAY):
                loading = True
                while loading:
                    if self.win_man.is_element_active(CANCEL_BUTTON.as_element(self.window), timeout=0.1):
                        self.logger.debug("The report `%s` is saving...", self.win_man.top_dialog(self.app))
                        time.sleep(1)
                    else:
                        loading = False
                
                _handle_unwanted_dialog()
                self.home()
                queue.remove(queue[0])    



