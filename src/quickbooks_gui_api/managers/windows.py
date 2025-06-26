# src\quickbooks_gui_api\managers\windows.py

import logging

from pywinauto import Application, Desktop
from pywinauto import keyboard, mouse
from typing import List, Tuple

from quickbooks_gui_api.models import Window



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
        """Attempt to focus ``window``.

        The method will query :class:`pywinauto.Desktop` for the window with
        the provided title and call ``set_focus`` on it. Any failure is
        suppressed and logged and ``False`` is returned.

        :param window: The window entity to focus.
        :type window: Window
        :returns: ``True`` if the focus attempt succeeded, ``False`` otherwise.
        :rtype: bool
        """
        try:
            Desktop(backend="uia").window(title=window.name).set_focus()
            return True
        except Exception as e:  # pragma: no cover - depends on OS specific libs
            logging.getLogger(__name__).error(
                "Failed to focus window '%s': %s", window.name, e
            )
            return False
        
    @staticmethod
    def active_window() -> Window:
        """Return a :class:`Window` instance for the currently focused window."""
        active = Desktop(backend="uia").get_active()
        rect = active.rectangle()
        return Window(
            active.window_text(),
            (rect.left, rect.top),
            (rect.width(), rect.height()),
        )

    
    @staticmethod
    def active_dialog() -> Window:
        """Return the active dialog as a :class:`Window` instance."""
        win = WindowManager.active_window()
        if WindowManager.is_dialog(win):
            return win
        # fall back to searching all dialogs and returning the focused one
        for dialog in WindowManager.get_all_dialogs():
            if WindowManager.is_focused(dialog):
                return dialog
        return win

    @staticmethod
    def get_all_windows() -> List[Window]:
        """Return a list of all top level windows as :class:`Window` objects."""
        windows = []
        for win in Desktop(backend="uia").windows():
            if win.friendly_class_name() != "Dialog":
                rect = win.rectangle()
                windows.append(
                    Window(
                        win.window_text(),
                        (rect.left, rect.top),
                        (rect.width(), rect.height()),
                    )
                )
        return windows
            
    @staticmethod
    def get_all_dialogs (filter: Window | None = None) -> List[Window]:
        """
        Returns a list of :class:`Window` instances for all dialogs.

        :param filter: Limits the return for only dialogs open under that window.
        :type filter: Window | None = None
        """
        dialogs = []
        if filter is not None:
            try:
                app = Application(backend="uia").connect(title=filter.name)
                candidates = app.windows()
            except Exception:
                candidates = []
        else:
            candidates = Desktop(backend="uia").windows()

        for win in candidates:
            if win.friendly_class_name() == "Dialog":
                rect = win.rectangle()
                dialogs.append(
                    Window(
                        win.window_text(),
                        (rect.left, rect.top),
                        (rect.width(), rect.height()),
                    )
                )

        return dialogs

    @staticmethod
    def is_window(window: Window) -> bool:
        """
        If the provided :py:class:`Window` instance represents a top level window.

        :param window: The window model instance to examine.
        :type window: Window
        """
        try:
            wrapper = Desktop(backend="uia").window(title=window.name)
            return wrapper.friendly_class_name() != "Dialog"
        except Exception:
            return False
    
    @staticmethod
    def is_dialog(window: Window) -> bool:
        """
        If the provided :class:`Window` instance represents a dialog.

        :param window: The window model instance to examine.
        :type window: Window
        """
        try:
            wrapper = Desktop(backend="uia").window(title=window.name)
            return wrapper.friendly_class_name() == "Dialog"
        except Exception:
            return False

    @staticmethod    
    def is_focused(window: Window) -> bool:
        """
        If the provided :class:`Window` instance is currently focused.

        :param window: The window model instance to examine.
        :type window: Window
        """
        try:
            active = Desktop(backend="uia").get_active()
            return active.window_text() == window.name
        except Exception:
            return False

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
        if keys is None and string is None:
            raise ValueError("Either 'keys' or 'string' must be provided")

        if string is not None:
            for _ in range(send_count):
                keyboard.send_keys(string, with_spaces=True, pause=delay)
            return

        sequence: str
        if isinstance(keys, list):
            sequence = ''.join(f'{{{k}}}' if len(k) > 1 else k for k in keys)
        else:
            sequence = f'{{{keys}}}' if keys and len(keys) > 1 else str(keys)

        for _ in range(send_count):
            keyboard.send_keys(sequence, pause=delay)

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

        if x is None or y is None:
            raise ValueError("x and y coordinates are required")

        coords = (x, y)
        if click:
            mouse.click(coords=coords)
        else:
            mouse.move(coords=coords)
    