import time
import logging
import pytomlpp
from pathlib import Path

from typing import List, Dict, Any, overload, Final

from src.quickbooks_gui_api.managers import WindowManager, ImageManager, OCRManager, StringManager
from src.quickbooks_gui_api.models import Report, Image, Window

from src.quickbooks_gui_api.apis.api_exceptions import ConfigFileNotFound, ExpectedDialogNotFound, InvalidPrinter

# Shortened window and dialog names:
REPORT_LIST:        Final[str] = "Memorized Report List"
SAVE_AS_DATA_FILE:  Final[str] = "Send Report To Excel"
SAVE_FILE_AS:       Final[str] = "Create Disk File"
EXPORTING:          Final[str] = "Creating csv"



class Reports:
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
            config = pytomlpp.load(self.config_path)["QuickBooksGUIAPI"]

            self.SHOW_TOASTS:               bool    = config["SHOW_TOASTS"] 
            self.WINDOW_LOAD_DELAY:         float   = config["WINDOW_LOAD_DELAY"]
            self.DIALOG_LOAD_DELAY:         float   = config["DIALOG_LOAD_DELAY"]
            self.NAVIGATION_DELAY:          float   = config["NAVIGATION_DELAY"]

        except Exception as e:
            self.logger.error(e)
            raise e


    def save(
        self, 
        invoices: Report | List[Report],
        save_directory: Path,
    ) -> None:

        queue: List[Report] = []

        if isinstance(invoices, Report):
            queue.append(invoices)
            self.logger.debug("Single report detected, appending to queue.")
        else:
            queue = invoices
            self.logger.debug("List detected. Appending `%i` to queue for processing.", len(invoices))

        if save_directory.is_dir():
            self.logger.debug("Provided `save_directory`, `%s`, does exist. Proceeding...")
        else:
            error = ValueError("Provided `save_directory`, `%s`, does NOT exist. Raising value error.") 
            self.logger.error(error)
            raise error

        window_man  = WindowManager(self.application)
        image_man   = ImageManager()
        ocr_man     = OCRManager()
        string_man  = StringManager()

        window_man.home()

        
        def _memorized_reports():
            window_man.send_input(['alt', 'R'])
            window_man.send_input('z')
            window_man.send_input('enter')
        
        def _find_report():
            report_name = queue[0].name 
            length = len(report_name)

            for i in range(length):
                char = report_name[i]
                window_man.send_input(char)

        def _save_as_new_worksheet():
            window_man.send_input(['alt', 'x'])
            window_man.send_input(['alt', 'n'])

        def _save_as_csv():
            window_man.send_input('down', 3)
            window_man.send_input('space')
            window_man.send_input(['alt', 'x'])

        def _save_file():
            window_man.send_input(['alt','n'])
            abs_path = save_directory.joinpath(queue[0].file_name)
            window_man.send_input(string = str(abs_path))
            window_man.send_input(['alt','s'])

        def _close_report():
            window_man.send_input('esc')


        _memorized_reports()

        while len(queue) != 0:  
            if window_man.active_dialog().name == REPORT_LIST:
                _find_report()

            if window_man.active_dialog().name == queue[0].name:
                _save_as_new_worksheet()
            
            if window_man.active_dialog().name == SAVE_AS_DATA_FILE:
                _save_as_csv()

            if window_man.active_dialog().name == SAVE_FILE_AS:
                _save_file()
             
            if window_man.active_dialog().name == EXPORTING:
                loading = True
                while loading:
                    if window_man.active_dialog().name == EXPORTING:
                        time.sleep(1)
                    else:
                        loading = False
                
                _close_report()
                queue.remove(queue[0])    



