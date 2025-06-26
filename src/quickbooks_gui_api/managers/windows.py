# src\invoice_saver\tools\window_manager.py

import logging

from pywinauto import Application, Desktop
from typing import List, Dict, Tuple, Any, Final, overload

from ..models import Window



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


    @staticmethod
    def attempt_focus_window(window: Window) -> bool:
        """
        Attempts to focus on the window with the provided name. 

        :param window: The window entity to focus.
        :type window: Window
        :returns: `True` Attempt was successful. `False` Attempt failed.
        """
        
    @staticmethod
    def active_window() -> Window:
        """ Returns a window model instance of the currently active window """

    
    @staticmethod
    def active_dialog() -> Window:
        """ Returns the name of the dialog that is currently focused. """  

    @staticmethod
    def get_all_windows() -> List[Window]:
        """ Returns a list of window model instances. """
            
    @staticmethod
    def get_all_dialogs (filter: Window | None = None) -> List[Window]:
        """
        Returns a list of window model instances for all dialogs.

        :param filter: Limits the return for only dialogs open under that window.
        :type filter: Window | None = None
        """

    @staticmethod
    def is_window(window: Window) -> bool:
        """
        If the provided window model instance is a window and not a dialog.

        :param window: The window model instance to examine.
        :type window: Window
        """
    
    @staticmethod
    def is_dialog(window: Window) -> bool:
        """
        If the provided window model instance is a window and not a dialog.
        
        :param window: The window model instance to examine.
        :type window: Window
        """

    @staticmethod    
    def is_focused(window: Window) -> bool:
        """
        If the provided window model instance is currently focused. 

        :param window: The window model instance to examine.
        :type window: Window
        """

    # def window_control(
    #         self,
    #         target: str,
    #         trigger: List[str],
    #         attempt_focus: bool = True,
    #         expected_load_time: float = 0,
    #         retries: int = 0
    #     ):
    #     """
        

    #     :param target:
    #     :type target:
    #     :param trigger:
    #     :type trigger:
    #     :param attempt_focus:
    #     :type attempt_focus:
    #     :param expected_load_time:
    #     :type expected_load_time:
    #     :param retries:
    #     :type retries:
    #     """
    

    def send_input(
            self,
            keys: str | List[str] | None = None,
            send_count: int = 1,
            *,
            string: str | None = None, 
            delay: float = 0
        ) -> None:
        """
        Send the the specified input, the specified number of times, with a specified delay.  

        :param keys: The keys to 'press'. Single character can be sent as a string, lists are used for multi-key presses.
        :type keys: str | List[str] | None = None
        :param send_count: How many time the provided input should be sent.
        :type send_count: int = 1
        :param string: Indicates a whole string should be sent, not just a character or a hotkey.
        :type string: str | None = None
        :param delay: Delay for repeated sends.
        :type delay: float = 0
        """
        pass

    def mouse(
            self, 
            x: int | None = None, 
            y: int | None = None, 
            *,
            position: Tuple[int, int] | None = None,
            click: bool = True
        ) -> None:
        """
        Move the mouse to ort click at the specified coordinates.

        :param x: X coordinate to be clicked.  
        :type x: int | None = None
        :param y: Y coordinate to be clicked.
        :type y: int | None = None
        :param position: Alternative input method, x,y tuple. 
        :type position: Tuple[int, int] | None = None
        """

        if position is not None:
            x = position[0]
            y = position[1]


        pass


    