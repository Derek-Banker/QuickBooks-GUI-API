# src\invoice_saver\tools\window_manager.py

from typing import List, Dict
from rapidfuzz import fuzz

import logging

class WindowManager:

    def __init__(self, logger = None) -> None:

        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger


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
        pass

    def get_active_window(self) -> str:
        """ Returns the name of the window that is currently focused. """

        pass

    def get_all_windows_(self, ) -> List[str]:
        pass

    # def window_control(target_title: str,
    #                     trigger: List[str],
    #                     attempt_focus: bool = True,
    #                     expected_load_time: float = 0,
    #                     retries: int = 0
    #                     ):
    #     pass



