
import logging
import pytomlpp

from pathlib import Path
from pywinauto import Application, WindowSpecification

from quickbooks_gui_api.managers import WindowManager, FileManager
from quickbooks_gui_api.models import Report, Element

from quickbooks_gui_api.apis.api_exceptions import ConfigFileNotFound


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

        # self.img_man = ImageManager() 
        # self.str_man = StringManager()
        # self.ocr_man = OCRManager()
        # self.helper = Helper()
        self.window_manager = WindowManager()
        self.file_manager    = FileManager()
            
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
            self.MAX_REPORT_SAVE_TIME:      float   = config["MAX_REPORT_SAVE_TIME"]
            self.QUICKBOOKS_WINDOW_NAME:    str     = config["QUICKBOOKS_WINDOW_NAME"]
            self.ACCEPTABLE_FILE_AGE:       float   = config["ACCEPTABLE_FILE_AGE"]
            self.HOME_TRIES:                int     = 10

            self.REPORT_NAME_MATCH_THRESHOLD: float   = config["REPORT_NAME_MATCH_THRESHOLD"]

        except Exception as e:
            self.logger.error(e)
            raise e

    def _handle_global_popups(self):
        all_titles = self.window_manager.get_all_dialog_titles(self.app)

        if HAVE_ANY_QUESTIONS.title in all_titles:
            self.logger.debug("Unwanted dialog detected. `%s` Closing...",HAVE_ANY_QUESTIONS.title)
            HAVE_ANY_QUESTIONS.as_element(self.window).close()

        if NEW_FEATURE.title in all_titles:
            self.logger.debug("Unwanted dialog detected. `%s` Closing...",NEW_FEATURE.title)
            NEW_FEATURE.as_element(self.window).set_focus()
            self.window_manager.send_input('enter')

        if QUICKBOOKS_PAYMENTS.title in all_titles:
            self.logger.debug("Unwanted dialog detected. `%s` Closing...",QUICKBOOKS_PAYMENTS.title)
            QUICKBOOKS_PAYMENTS.as_element(self.window).set_focus()
            self.window_manager.send_input('esc')

    def home(self, true_home: bool = False) -> None:
        self.window.set_focus()
        
        def attempt_close(i: int):
            top_title = self.window_manager.top_dialog(self.app)
            try:
                self.window.child_window(control_type = "Window", title = top_title).close()
                self.logger.debug("Closed window `%s`. Attempt `%i`/`%i`.", top_title, i+1, self.HOME_TRIES)
            except Exception:
                self.logger.exception("Error attempting to close targeted window, `%s`",top_title)

        def memorized_list_and_base(titles: list[str]) -> bool:
            base: bool = False
            memorized_list: bool = False
            number_of_titles = len(titles)


            for title in titles:
                if self.QUICKBOOKS_WINDOW_NAME in title:
                    base = True
                if title == MEMORIZED_REPORTS_WINDOW.title:
                    memorized_list = True

                if number_of_titles == 1 and base:
                    return True
                elif number_of_titles == 2 and base and memorized_list:
                    return True

            return False

        if true_home:
            for i in range(self.HOME_TRIES):
                titles = self.window_manager.get_all_dialog_titles(self.app)
                if len(titles) == 1 and self.QUICKBOOKS_WINDOW_NAME in titles[0]:
                    return
                else:
                    attempt_close(i)
                    

        else:
            for i in range(self.HOME_TRIES):
                titles = self.window_manager.get_all_dialog_titles(self.app)
                if memorized_list_and_base(titles):
                    return
                else:
                    attempt_close(i)

    


    def save(
        self, 
        reports: Report | list[Report],
        # save_directory: Path,
    ) -> None:

        queue: list[Report] = []

        if isinstance(reports, Report):
            queue.append(reports)
            self.logger.debug("Single report detected, appending to queue.")
        else:
            queue = reports
            self.logger.debug("List detected. Appending `%i` to queue for processing.", len(reports))

        self._handle_global_popups()
        self.home(True)

        self.window.set_focus()

        def _memorized_reports():
            self.window.set_focus()
            self.window_manager.send_input(['alt', 'R'])
            self.window_manager.send_input('z')
            self.window_manager.send_input('enter')
        
        def _find_report():
            self.window.set_focus()

            report_name = queue[0].name

            if report_name in self.window_manager.get_all_dialog_titles(self.app):
                self.logger.warning("The report `%s` is already open, calling home function to close everything...", report_name)
                self.home(True) 
            
            self.window_manager.send_input(string=report_name, char_at_a_time=True)

            self.window_manager.send_input(["alt","s"])

            if self.window_manager.top_dialog(self.app) == report_name:
                self.logger.info("The intended report, `%s`, has been successfully opened.", report_name)
            else:
                self.logger.info("The attempt to open, `%s`, has has failed. THe current top window is `%s`.", report_name,self.window_manager.top_dialog(self.app))

        def _save_as_new_worksheet():
            self.window.set_focus()
            EXCEL_BUTTON.as_element(self.window).click_input()
            self.window_manager.send_input('n')

        def _save_as_csv():
            self.window.set_focus()
            AS_CSV_BUTTON.as_element(self.window).click_input()
            self.window_manager.send_input(['alt', 'x'])

        def _save_file(path: Path):
            self.window.set_focus()
            FILE_NAME_FIELD.as_element(self.window).set_text(str(path))
            self.window_manager.send_input(keys='enter') 

        def _handle_unwanted_dialog():
            self.window.set_focus()
            top_dialog_title = self.window_manager.top_dialog(self.app)

            def focus():
                self.logger.debug("Unwanted dialog detected. `%s` Accommodating...",top_dialog_title)
                unwanted_dialog = self.window.child_window(control_type= "Window", title = top_dialog_title)
                unwanted_dialog.set_focus()    

            if top_dialog_title == CONFIRM_SAVE_AS.title:
                focus()
                self.window_manager.send_input(keys=['y'])

            self._handle_global_popups()

        

        self.logger.info("Entering save loop...")
        while len(queue) != 0:  
            _memorized_reports()

            report_path = queue[0].export_path() 
            pre_existing_file = report_path.exists()


            if self.window_manager.top_dialog(self.app) == MEMORIZED_REPORTS_WINDOW.title:
                self.logger.debug("Memorized report list is detected and focused...") 
                _find_report()
                _handle_unwanted_dialog()
            else:
                _memorized_reports()

            if self.window_manager.is_element_active(EXCEL_BUTTON.as_element(self.window), timeout=self.WINDOW_LOAD_DELAY):
                self.logger.debug("Selected report is detected and focused...")
                _save_as_new_worksheet()
                _handle_unwanted_dialog()
            
            if self.window_manager.is_element_active(AS_CSV_BUTTON.as_element(self.window), timeout=self.WINDOW_LOAD_DELAY):
                self.logger.debug("`%s` Button is detected and focused...",AS_CSV_BUTTON.title)
                _save_as_csv()
                _handle_unwanted_dialog()

            if self.window_manager.is_element_active(FILE_NAME_FIELD.as_element(self.window), timeout=self.WINDOW_LOAD_DELAY):
                self.logger.debug("`%s` Window is detected and focused...",SAVE_FILE_AS_WINDOW.title)
                _save_file(report_path)
                _handle_unwanted_dialog()
            else:
                print("NOT DETECTED")
             
            # if self.window_manager.is_element_active(CANCEL_BUTTON.as_element(self.window), timeout=self.WINDOW_LOAD_DELAY):
            #     loading = True
            #     while loading:
            #         if self.window_manager.is_element_active(CANCEL_BUTTON.as_element(self.window), timeout=0.1):
            #             self.logger.debug("The report `%s` is saving...", self.window_manager.top_dialog(self.app))
            #             time.sleep(1)
            #         else:
            #             loading = False

            if self.file_manager.wait_for_file(report_path, self.MAX_REPORT_SAVE_TIME):
                self.logger.debug("The report file, `%s`, exists.", report_path.name)
                self.file_manager.wait_till_stable(report_path, self.MAX_REPORT_SAVE_TIME)
                self.logger.debug("The report file, `%s`, is stable.", report_path.name)
                if pre_existing_file:
                    file_age = self.file_manager.time_since_modified(report_path)
                    self.logger.warning("the file `%s` existed before the report was saved. The file was last modified `%.2f` second ago.", report_path.name, file_age)
                    if  file_age >= self.ACCEPTABLE_FILE_AGE:
                        error = ValueError(f"The report file is `{file_age}` seconds old. Which is older than ACCEPTABLE_FILE_AGE, `{self.ACCEPTABLE_FILE_AGE}`. This may indicate the file was already there and was not saved correctly.")
                        self.logger.error(error)
                        raise error
                
                _handle_unwanted_dialog()
                self.home()
                queue.remove(queue[0])    

        self.home(True)

