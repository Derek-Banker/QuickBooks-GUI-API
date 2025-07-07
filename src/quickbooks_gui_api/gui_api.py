# src\quickbooks_gui_api\gui_api.py

import os
import time
import logging
import pytomlpp
import toml_init
from toml_init import EncryptionManager
from pathlib import Path

from typing import Final
from pywinauto import Application, WindowSpecification


# from quickbooks_gui_api.apis import Invoices, Reports
from quickbooks_gui_api.managers import ImageManager, Color, OCRManager, ProcessManager, WindowManager, StringManager, Helper


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
        
        self.pro_man = ProcessManager()
        # self.img_man = ImageManager() 
        self.str_man = StringManager()
        self.win_man = WindowManager()
        # self.ocr_man = OCRManager()
        self.helper = Helper()
    

    def kill_avatax(self) -> None:

        avatax_paths: list[Path] = [
                                    Path(r"C:\Program Files (x86)\Avalara\AvaTax Adapter\Bin\AvalaraEventCallBack.exe")
                                   ]
        
        for path in avatax_paths:
            if self.pro_man.is_running(path=path):
                self.logger.debug("Avatax process running, attempting to terminate process at `%s` ...", path)
                try:
                    if not self.pro_man.terminate(location=path):
                        error = ValueError(f"Unable to terminate Avatax process, `{path}`.")
                        self.logger.error(error)
                        raise error
                except Exception as e:
                    error = ValueError(f"Error when attempting to terminate Avatax process, `{path}`.")
                    self.logger.error(error)
                    raise error


    def startup(self, 
            config_directory: Path = DEFAULT_CONFIG_FOLDER_PATH, 
            config_file_name: str = DEFAULT_CONFIG_FILE_NAME
        ) -> tuple[Application, WindowSpecification]:

        toml_init.ConfigManager().initialize()

        config = pytomlpp.load(config_directory.joinpath(config_file_name))
        
        self.kill_avatax()

        try:
            exe_path            = config["QuickBooksGUIAPI"]["QB_EXE_PATH"]
            company_file_name   = config["QuickBooksGUIAPI"]["COMPANY_FILE_NAME"]    
        except KeyError:
            self.logger.error("KeyError Raised. These is a problem with the config file.")
            raise
        
        try:
            qb_app = Application(backend='uia').connect(path=exe_path)
            qb_window = qb_app.window(title_re=".*Intuit QuickBooks Enterprise Solutions: Manufacturing and Wholesale 24.0.*")
        except Exception as e:
            self.logger.error(e)
            raise e





        if self.str_man.is_match_in_list(COMPANY_NOT_LOADED, self.win_man.get_all_dialog_titles(qb_app), 95.0):
            qb_window.set_focus()

            

            company_file_window = qb_window.child_window(title = "No QuickBooks Company Loaded", auto_id = "65280")

            correct_company, selected_company, match_confidence =   self.helper.capture_isolate_ocr_match(
                                                                        company_file_window, 
                                                                        single_or_multi="multi", 
                                                                        color=Color(hex_val="4e9e19"), 
                                                                        tolerance= 5.0, 
                                                                        min_area= 5000, 
                                                                        target_text=company_file_name, 
                                                                        match_threshold= 90.0
                                                                    )

            if correct_company:
                self.logger.info(f"ORC'd selected company `{selected_company}` file sufficiently matches target `{company_file_name}`.")
                self.win_man.send_input("enter")
                time.sleep(config["QuickBooksGUIAPI"]["LOGIN_DELAY"])
            else:
                self.logger.error(f"Unrecognized company file `{selected_company}` currently selected. Match confidence is {match_confidence} with target `{company_file_name}`.")
                raise ValueError
            

        if self.str_man.is_match_in_list(LOGIN, self.win_man.get_all_dialog_titles(qb_app), 95.0):    
            import dotenv

            dotenv.load_dotenv()

            try:
                key = os.getenv("KEY")
            except KeyError:
                self.logger.error("KeyError raised when attempting to retrieve environmental variable.")
                raise KeyError

            try:
                hash        = config["QuickBooksGUIAPI.secrets"]["HASH"]
                salt        = config["QuickBooksGUIAPI.secrets"]["SALT"]
                username    = config["QuickBooksGUIAPI.secrets"]["USERNAME"]
                password    = config["QuickBooksGUIAPI.secrets"]["PASSWORD"]
            except KeyError:
                self.logger.error("KeyError raised when attempting to retrieve `QuickBooksGUIAPI.secrets`. There is a problem with the config file.")
                raise KeyError

            enc_man = EncryptionManager()

            confidential_data = [key, hash, salt, username, password]

            if ("UNINITIALIZED" in confidential_data) or (None in confidential_data) or key is None:
                error = ValueError("At lease of of the confidential references is `UNINITIALIZED` or `None`.")
                self.logger.error(error)
                raise error
        
            if enc_man.hash(key,salt) == hash:
                fer_key = enc_man.derive_key(key,salt)
                username_decrypted = enc_man.decrypt(username,fer_key) 
                password_decrypted = enc_man.decrypt(password,fer_key)

            else:
                error = ValueError("The `HASH` value pulled from the config file is not a hash of the `KEY` environmental variable.")
                self.logger.error(error)
                raise error

            qb_window.set_focus()
            self.win_man.send_input(["alt","u"])
            self.helper.safely_set_text(username_decrypted, root=qb_window, control_type = "Edit", auto_id = "15922") # type: ignore

            self.win_man.send_input(["alt","p"])
            self.helper.safely_set_text(password_decrypted, root=qb_window, control_type = "Edit", auto_id = "15924") # type: ignore
            
            self.win_man.send_input("enter")
            time.sleep(config["QuickBooksGUIAPI"]["LOGIN_DELAY"])

        return qb_app, qb_window
