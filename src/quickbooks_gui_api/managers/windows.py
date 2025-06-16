# src\invoice_saver\tools\window_manager.py

import logging
from rapidfuzz import fuzz
from pywinauto import Application, Desktop
from typing import List, Dict, Tuple, Any, Final, overload



class WindowManager:
    """
    Manages windows in Windows. 
    Attributes:
        logger (logging.Logger): Logger instance for logging operations.
    """


    def __init__(self, 
                 logger: logging.Logger | None  = None
                 ) -> None:

        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            if isinstance(logger, logging.Logger):
                self.logger = logger 
            else:
                raise TypeError("Provided parameter `logger` is not an instance of `logging.Logger`.")

    def best_string_match(self, options: List[str], target: str, match_threshold: float = 100, return_on_match: bool = False) -> Dict[str,float] | None:
        max_result: float = 0.0
        best_string: str = ""
        
        for item in options:
            temp = fuzz.ratio(item,target)
            self.logger.debug("Comparing '%s' to '%s': Score = %f", item, target, temp)
            if (temp == 100) or (return_on_match and (temp >= match_threshold)):
                return {item: temp}
            else:
                if temp >= match_threshold and temp > max_result:
                    max_result = temp
                    best_string = item

        if max_result == 0.0:
            return None
        else:
            return {best_string: max_result}



    def attempt_focus_window(self, title: str) -> bool:
        """
        Attempts to focus on the window with the provided name.

        :param title: The exact name of the window.
        :type title: str
        :returns bool: True: Attempt successful. False: Attempt failed. 
        """
        return False

    def get_active_window(self) -> str:
        """ Returns the name of the window that is currently focused. """
        return ""

    def get_all_windows_(self, ) -> List[str]:
        return [""]

    def window_control(self,
                       target_title: str,
                        trigger: List[str],
                        attempt_focus: bool = True,
                        expected_load_time: float = 0,
                        retries: int = 0
                        ):
        pass

    def get_window_size(self, window: Application) -> Tuple[int, int]:
        rect = window.rectangle()
        return (rect.width(), rect.height())

    def get_window_origin(self, window: Application) -> tuple[int, int]:
        rect = window.rectangle()
        return (rect.left, rect.top)

    def get_window_title(self, window: Application) -> str:
        return window.window_text()

    def is_dialog(self, window: Application) -> bool:
        return window.friendly_class_name().lower() in ["dialog", "window"]


    def is_focused(self, window: Application) -> bool:
        focused = Desktop(backend=window.backend.name).get_active()
        return focused.handle == window.handle
    
    def find_active_quickbooks_dialog(self):
        windows = Desktop(backend="uia").windows()
        for w in windows:
            title = w.window_text()
            if "QuickBooks" in title or w.class_name().startswith("Intuit"):
                if w.is_visible() and w.is_enabled():
                    return w
        return None
    
    def get_dialogs(self) -> List[str]:
        return [""]
    

    def send_input(
        self,
        keys: str | List[str],
        send_count: int = 1,
        delay: float = 0
    ) -> None:
        pass

    # --- Top level functions --------------------------------------------------

    def home(self, max_tries = 10) -> None:

        while max_tries != 0:
            if len(self.get_dialogs()) > 0:
                self.send_input("esc")
                max_tries -= 1 
            else:
                return
        
        raise:

    


    