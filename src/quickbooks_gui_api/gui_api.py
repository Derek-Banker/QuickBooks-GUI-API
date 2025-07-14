# src\quickbooks_gui_api\gui_api.py

import os
import time
import logging
import pytomlpp
import toml_init
from toml_init  import EncryptionManager
from pathlib    import Path

from typing     import Final, Any
from pywinauto  import Application, WindowSpecification

from quickbooks_gui_api.models      import Invoice, Report
from quickbooks_gui_api.managers    import Color, ProcessManager, WindowManager, StringManager, Helper


COMPANY_NOT_LOADED: Final[str] = "No QuickBooks Company Loaded"
LOGIN:              Final[str] = "QuickBooks Desktop Login"

cwd = Path(os.getcwd())

DEFAULT_CONFIG_FOLDER_PATH: Final[Path] = cwd.joinpath("configs")
DEFAULT_CONFIG_DEFAULT_FOLDER_PATH: Final[Path] = DEFAULT_CONFIG_FOLDER_PATH.joinpath("defaults")
DEFAULT_CONFIG_FILE_NAME: Final[str] = "config.toml"

QUICKBOOKS_PROCESSES:   list[str] = [
                                     "QBW.EXE", 
                                     "qbw32.exe", 
                                     "qbupdate.exe",
                                     "qbhelp.exe", 
                                     "QBUpdateService.exe",
                                     "QBFDT.exe",
                                    ]

AVATAX_PROCESSES:       list[str] = [
                                     "AvalaraEventCallBack.exe"
                                    ]

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
        
        self.process_manager = ProcessManager()
        self.string_manager = StringManager()
        self.window_manager = WindowManager()
        self.helper = Helper()

        self.app:       Application
        self.window:    WindowSpecification
    
    def _load_config_basic(self,
            config_directory: Path, 
            config_file_name: str
        ) -> dict[str, Any]:

        toml_init.ConfigManager().initialize()

        config = pytomlpp.load(config_directory.joinpath(config_file_name))

        try:
            self.exe_path                   = config["QuickBooksGUIAPI"]["QB_EXE_PATH"]
            self.company_file_name          = config["QuickBooksGUIAPI"]["COMPANY_FILE_NAME"]
            self.process_start_delay        = config["QuickBooksGUIAPI"]["PROCESS_START_DELAY"]
            self.company_file_load_delay    = config["QuickBooksGUIAPI"]["COMPANY_FILE_LOAD_DELAY"]            
            self.login_delay                = config["QuickBooksGUIAPI"]["LOGIN_DELAY"]
        except KeyError:
            e = KeyError("KeyError Raised when attempting to retrieve `QuickBooksGUIAPI` config data. There is a problem with the config file.")
            self.logger.error(e)
            raise e
        
        return config

    def _load_config_sensitive(self, config: dict[str, Any]) -> tuple[str, str]:
        self.logger.info("Attempting to load in sensitive data points in from config...")

        try:
            key_name   = config["QuickBooksGUIAPI.secrets"]["KEY_NAME"]
            hash       = config["QuickBooksGUIAPI.secrets"]["HASH"]
            salt       = config["QuickBooksGUIAPI.secrets"]["SALT"]
            username   = config["QuickBooksGUIAPI.secrets"]["USERNAME"]
            password   = config["QuickBooksGUIAPI.secrets"]["PASSWORD"]
        except KeyError:
            e = KeyError("KeyError raised when attempting to retrieve `QuickBooksGUIAPI.secrets`. There is a problem with the config file. If you have not already, use setup to set the encrypted secrets.")
            self.logger.error(e)
            raise e

        import dotenv
        dotenv.load_dotenv()

        try:
            key = os.getenv(key_name)
        except KeyError:
            e = KeyError(f"KeyError raised when attempting to the retrieve 'KEY_NAME' environmental variable, set as `{key_name}` in the config file.")
            self.logger.error(e)
            raise e
        
        confidential_data = [key, hash, salt, username, password]

        if ("UNINITIALIZED" in confidential_data) or (None in confidential_data) or key is None:
            error = ValueError("At lease one of the confidential references is `UNINITIALIZED` or `None`.")
            self.logger.error(error)
            raise error

        em = EncryptionManager()

    
        if em.hash(key,salt) != hash:
            error = ValueError(f"The `HASH` value pulled from the config file is not a hash of the `{key_name}` environmental variable.")
            self.logger.error(error)
            raise error

        else:
            self.logger.info("Stored hash matches that of the environment key, proceeding with decryption...")
            fer_key = em.derive_key(key,salt)

            return em.decrypt(username,fer_key), em.decrypt(password,fer_key)
        
    def _start_quickbooks(self) -> bool:
        self.logger.info("Starting QuickBooks if not already running...")
        
        if not self.process_manager.is_running(path = Path(self.exe_path)):
            self.logger.debug("QuickBook was not running. Attempting to start...")
            try:
                self.process_manager.start(path = Path(self.exe_path))
                time.sleep(self.process_start_delay)
                if self.process_manager.is_running(path = Path(self.exe_path)):
                    self.logger.debug("Attempt successful.")
                    return True
                else:
                    return False
            except Exception as e:
                error = "QuickBooks unable to be started. Error thrown: `%s`",e
                self.logger.error(error)
                raise e
        else:
            self.logger.debug("QuickBook was already running.")
            return True




    def _kill_avatax(self) -> None:
        self._terminate_processes(AVATAX_PROCESSES)
    
    def _connect_to_app(self) -> tuple[Application, WindowSpecification]:
        self.logger.info("Attempting to connect pywinauto to application...")
        try:
            self.app = Application(backend='uia').connect(path=self.exe_path)
            self.window = self.app.window(title_re=".*Intuit QuickBooks Enterprise Solutions: Manufacturing and Wholesale 24.0.*")
        except Exception:
            self.logger.exception
            raise

        return self.app, self.window

    
    def _select_company_file(self, window: WindowSpecification) -> None:
        self.logger.info("Company file selection step detected...")
        window.set_focus()

        company_file_window = window.child_window(title = "No QuickBooks Company Loaded", auto_id = "65280")

        correct_company, selected_company, match_confidence =   self.helper.capture_isolate_ocr_match(
                                                                    company_file_window, 
                                                                    single_or_multi="multi", 
                                                                    color=Color(hex_val="4e9e19"), 
                                                                    tolerance= 5.0, 
                                                                    min_area= 5000, 
                                                                    target_text=self.company_file_name, 
                                                                    match_threshold= 90.0
                                                                )

        if correct_company:
            self.logger.info(f"ORC'd selected company `{selected_company}` file sufficiently matches target `{self.company_file_name}`.")
            self.window_manager.send_input("enter")
            time.sleep(self.company_file_load_delay)
        else:
            self.logger.error(f"Unrecognized company file `{selected_company}` currently selected. Match confidence is {match_confidence} with target `{self.company_file_name}`.")
            raise ValueError

    def _login(self, window: WindowSpecification, config: dict[str, Any]) -> None:
            self.logger.info("User login step detected...")
            username, password = self._load_config_sensitive(config)

            window.set_focus()
            self.window_manager.send_input(["alt","u"])
            self.helper.safely_set_text(username, root=window, control_type = "Edit", auto_id = "15922") # type: ignore

            self.window_manager.send_input(["alt","p"])
            self.helper.safely_set_text(password, root=window, control_type = "Edit", auto_id = "15924") # type: ignore
            
            self.window_manager.send_input("enter")
            time.sleep(self.login_delay)

    def _terminate_processes(self, processes: list[str]) -> None:
        for process in processes:
            try:
                self.process_manager.terminate(name= process)
            except Exception:
                self.logger.exception(f"Error occurred while attempting to terminate the following process: `{process}`.")
                continue
       
        self.logger.info("All provided processes have been terminated.")

    def startup(self, 
            config_directory: Path = DEFAULT_CONFIG_FOLDER_PATH, 
            config_file_name: str = DEFAULT_CONFIG_FILE_NAME,
            kill_avatax: bool = True
        ) -> tuple[Application, WindowSpecification]:
        self.logger.info("Entering startup routine...")

        config = self._load_config_basic(config_directory, config_file_name)

        self._start_quickbooks()

        app, window = self._connect_to_app()

        if self.string_manager.is_match_in_list(COMPANY_NOT_LOADED, self.window_manager.get_all_dialog_titles(app), 95.0):
           self._select_company_file(window)
            
        if self.string_manager.is_match_in_list(LOGIN, self.window_manager.get_all_dialog_titles(app), 95.0):    
            self._login(window, config)

        if kill_avatax:
            self._kill_avatax()
        
        return app, window

    def shutdown(self) -> None:
        self.logger.info("Entering shutdown routine...")
        
        self._terminate_processes(QUICKBOOKS_PROCESSES)

    def save_invoices(self, invoices: Invoice | list[Invoice]):
        from quickbooks_gui_api.apis import Invoices

        if self.app is not None and self.window is not None:
            Invoices(self.app,self.window).save(invoices)

    def save_reports (self, reports: Report | list[Report]):
        from quickbooks_gui_api.apis import Reports

        if self.app is not None and self.window is not None:
            Reports(self.app,self.window).save(reports)