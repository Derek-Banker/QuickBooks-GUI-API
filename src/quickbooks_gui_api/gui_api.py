# src\quickbooks_gui_api\gui_api.py

import os
import time
import logging
import pytomlpp
import toml_init
from toml_init  import EncryptionManager
from pathlib    import Path

from typing     import Final, Any
from pywinauto  import Application, WindowSpecification, findwindows, timings, win32functions, win32defines

from quickbooks_gui_api.models      import Invoice, Report, Element
from quickbooks_gui_api.managers    import Color, ProcessManager, WindowManager, StringManager, Helper


COMPANY_NOT_LOADED: Final[str] = "No QuickBooks Company Loaded"
LOGIN:              Final[str] = "QuickBooks Desktop Login"

cwd = Path(os.getcwd())

DEFAULT_CONFIG_FOLDER_PATH:         Final[Path] = cwd.joinpath("configs")
DEFAULT_CONFIG_DEFAULT_FOLDER_PATH: Final[Path] = DEFAULT_CONFIG_FOLDER_PATH.joinpath("defaults")
DEFAULT_CONFIG_FILE_NAME:           Final[str]  = "config.toml"

COMPANY_FILE_WINDOW:    Element = Element("Window",     "No QuickBooks Company Loaded",     65280)
USERNAME_FIELD:         Element = Element("Edit",       None,                               15922)
PASSWORD_FIELD:         Element = Element("Edit",       None,                               15924)
MULTI_USER_FILE:        Element = Element("Window",     "QuickBooks Desktop Information",   None)
SERVICE_UPDATE:         Element = Element("Window",     "QuickBooks Update Service",        None)

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
                 logger: Any = logging.getLogger(__name__)
                 ) -> None:
        self.logger = logger
        
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
        
    def _start_quickbooks(self) -> bool:
        self.logger.debug("Starting QuickBooks if not already running...")
        
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
                error = f"QuickBooks unable to be started. Error thrown: `{e}`"
                self.logger.error(error)
                raise e
        else:
            self.logger.debug("QuickBook was already running.")
            return True


    def _handle_startup_popups(self, app: Application) -> None:
        dialog_titles = self.window_manager.get_all_dialog_titles(app)
        
        if SERVICE_UPDATE.title in dialog_titles:
            self.logger.debug(f"Unwanted dialog detected. `{SERVICE_UPDATE.title}` Accommodating...")
            self.window_manager.send_input('enter')

    def _focus_popup(self, title: str):
        self.logger.debug(f"Unwanted dialog detected. `{title}` Accommodating...")
        unwanted_dialog = self.window.child_window(control_type= "Window", title = title)
        unwanted_dialog.set_focus()

    def _handle_running_popups(self):
        top_dialog_title = self.window_manager.top_dialog(self.app)

        if top_dialog_title == MULTI_USER_FILE.title:
            self._focus_popup(top_dialog_title)
            self.window_manager.send_input(keys=['alt', 'n'])

    def _kill_avatax(self) -> None:
        self._terminate_processes(AVATAX_PROCESSES)
    
    def _connect_to_app(self) -> tuple[Application, WindowSpecification]:
        self.logger.debug("Attempting to connect pywinauto to application...")
        try:
            self.app = Application(backend='uia').connect(path=self.exe_path)
            self.window = self.app.window(title_re=".*QuickBooks.*")
        except Exception:
            self.logger.exception
            raise

        return self.app, self.window

    
    def _select_company_file(self, window: WindowSpecification) -> None:
        self.logger.debug("Company file selection step detected...")
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
            self.logger.debug(f"ORC'd selected company `{selected_company}` file sufficiently matches target `{self.company_file_name}`.")
            self.window_manager.send_input("enter")
            time.sleep(self.company_file_load_delay)
        else:
            self.logger.error(f"Unrecognized company file `{selected_company}` currently selected. Match confidence is {match_confidence} with target `{self.company_file_name}`.")
            raise ValueError

    def _login(self, window: WindowSpecification, username: str, password: str) -> None:
            self.logger.debug("User login step detected...")
        
            window.set_focus()
            self.window_manager.send_input(["alt","u"])
            self.helper.safely_set_text(username, root=window, control_type = "Edit", auto_id = "15922") # type: ignore



            self.window_manager.send_input(["alt","p"])
            self.helper.safely_set_text(password, root=window, control_type = "Edit", auto_id = "15924") # type: ignore
            
            self.window_manager.send_input("enter")

            self._handle_running_popups()
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
            username: str,
            password: str,
            config_directory: Path = DEFAULT_CONFIG_FOLDER_PATH, 
            config_file_name: str = DEFAULT_CONFIG_FILE_NAME,
            kill_avatax: bool = True
        ) -> tuple[Application, WindowSpecification]:  
        self.logger.info("Entering startup routine...")

        config = self._load_config_basic(config_directory, config_file_name)

        self._start_quickbooks()
        app, window = self._connect_to_app()

        window.set_focus()

        self._handle_startup_popups(app)

        main_window_spec = app.window(title_re=".*QuickBooks Enterprise Solutions.*")
        try:
            main_window_wrapper = main_window_spec.wait('exists')

            if main_window_wrapper.is_minimized():
                self.logger.info("QuickBooks window is minimized. Restoring it...")
                # The UIA restore() can fail with a COMError. Using the lower-level
                # ShowWindow function is more reliable for this operation.
                win32functions.ShowWindow(main_window_wrapper.handle, win32defines.SW_RESTORE)
                time.sleep(0.5)  # Give a moment for the window to draw

            main_window_wrapper.set_focus()
            self.logger.debug("Main window is ready and focused.")

            # Update self.window and the local `window` to the spec we know works.
            self.window = window = main_window_spec

        except Exception as e:
            self.logger.error(f"Could not find or restore the main QuickBooks window: {e}")
            raise e

        if self.string_manager.is_match_in_list(COMPANY_NOT_LOADED, self.window_manager.get_all_dialog_titles(app), 95.0):
           self._select_company_file(window)
            
        if self.string_manager.is_match_in_list(LOGIN, self.window_manager.get_all_dialog_titles(app), 95.0):    
            self._login(window, username, password)

        if kill_avatax:
            self._kill_avatax()

        window.set_focus()
        
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