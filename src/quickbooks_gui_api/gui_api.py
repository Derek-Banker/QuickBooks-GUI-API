# src\quickbooks_gui_api\gui_api.py

import os
import logging
import pytomlpp
import toml_init
from toml_init import EncryptionManager
from pathlib import Path

from typing import List, Dict, Any, overload, Final
from pywinauto import Application, WindowSpecification


# from quickbooks_gui_api.apis import Invoices, Reports
from quickbooks_gui_api.managers import ImageManager, Color, OCRManager, ProcessManager, WindowManager, StringManager


COMPANY_NOT_LOADED: Final[str] = "No QuickBooks Company Loaded"
LOGIN:              Final[str] = "QuickBooks Desktop Login"

cwd = Path(os.getcwd())

DEFAULT_CONFIG_FOLDER_PATH: Final[Path] = cwd.joinpath("configs")
DEFAULT_CONFIG_DEFAULT_FOLDER_PATH: Final[Path] = DEFAULT_CONFIG_FOLDER_PATH.joinpath("defaults")
DEFAULT_CONFIG_FILE_NAME: Final[str] = "config.toml"

class QuickBookGUIAPI:

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

    def kill_avatax(self) -> None:

        pass

    def startup(self, 
            config_directory: Path = DEFAULT_CONFIG_FOLDER_PATH, 
            config_file_name: str = DEFAULT_CONFIG_FILE_NAME
        ):
        # tuple[Application, WindowSpecification, Dict[str, Any]]

        toml_init.ConfigManager().initialize()

        config = pytomlpp.load(config_directory.joinpath(config_file_name))
        
        pro_man = ProcessManager()

        try:
            exe_path            = config["QuickBooksGUIAPI"]["QB_EXE_PATH"]
            company_file_name   = config["QuickBooksGUIAPI"]["COMPANY_FILE_NAME"]    
        except KeyError:
            self.logger.error("KeyError Raised. These is a problem with the config file.")
            raise

        win_man = WindowManager()
        str_man = StringManager()
        
        try:
            qb_app = Application(backend='uia').connect(path='QBW.EXE')
            qb_window = qb_app.window(title_re=".*Intuit QuickBooks Enterprise Solutions: Manufacturing and Wholesale 24.0.*")
        except Exception as e:
            self.logger.error(e)
            raise e





        if str_man.is_match_in_list(COMPANY_NOT_LOADED, win_man.get_all_dialog_titles(qb_app), 95.0):
            qb_window.set_focus()

            img_man = ImageManager()
            orc_man = OCRManager()

            company_file_window = qb_window.child_window(title = "No QuickBooks Company Loaded", auto_id = "65280")
            win_dim = company_file_window.rectangle()
    
            selected_file_img   = img_man.capture((win_dim.width(), win_dim.height()), (win_dim.left, win_dim.top))
            isolated_regions    = img_man.isolate_multiple_regions(selected_file_img, Color(hex_val="4e9e19"), 5.0, min_area=5000)
            
            if len(isolated_regions) > 1:
                self.logger.error("Isolated regions for selected company file is greater than 1. Unable to accommodate.")
                raise ValueError
            
            selected_file_text = orc_man.get_text(isolated_regions[0])

            if str_man.is_match(90.0, input=selected_file_text, target=company_file_name):
                self.logger.info(f"ORC'd selected company `{selected_file_text}` file sufficiently matches target `{company_file_name}`.")
                win_man.send_input("enter")
            else:
                self.logger.error(f"Unrecognized company file `{selected_file_text}` currently selected. Match confidence is {str_man.match(selected_file_text,company_file_name)} with target `{company_file_name}`.")
                raise ValueError
            





            # selected_file_text = orc_man.get_text(selected_file)

            # print(selected_file_text)


        # if str_man.is_match_in_list(LOGIN, win_man.get_all_dialog_titles(qb_app), 95.0):    
        #     enc_man = EncryptionManager()   



        # return qb_app, qb_window
