# src\quickbooks_gui_api\managers\windows.py

import logging

from pywinauto import Application, Desktop
from pywinauto import keyboard, mouse
from typing import List, Tuple, Any
import time

from quickbooks_gui_api.models import Window
from .manager_exceptions import WindowFocusFail, WindowNotFound



class WindowManager:
    """
    Manages windows in Windows. 
    Attributes:
        logger (logging.Logger): Logger instance for logging operations.
    """
    

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.desktop = Desktop(backend="uia")

        if logger is None:
            self.logger = logging.getLogger(__name__)
        elif isinstance(logger, logging.Logger):
            self.logger = logger
        else:
            raise TypeError("Provided parameter `logger` is not an instance of `logging.Logger`.")


    def attempt_focus_window(self, window: Window) -> bool:
        """Attempt to focus ``window``.

        The method queries the Desktop for the provided window and attempts to
        set focus. On failure the currently focused window title is logged and a
        :class:`WindowFocusFail` is raised.

        :param window: The window entity to focus.
        :returns: ``True`` if the focus attempt succeeded.
        :raises WindowFocusFail: If the focus attempt fails.
        """
        try:
            if window.hwnd:
                self.desktop.window(handle=window.hwnd).set_focus()
            else:
                self.desktop.window(title=window.name).set_focus()
            return True
        except Exception as e:  # pragma: no cover - depends on OS specific libs
            current = self.desktop.get_active().window_text()
            self.logger.error(
                "Failed to focus window '%s'. '%s' is currently focused.",
                window.name,
                current,
            )
            raise WindowFocusFail(window.name, current) from e
        
    def active_window(self) -> Window:
        """Return a :class:`Window` instance for the currently focused window."""
        active = self.desktop.get_active()
        return Window.from_pywinauto(active)

    
    def active_dialog(self) -> Window:
        """Return the active dialog as a :class:`Window` instance."""
        win = self.active_window()
        if self.is_dialog(win):
            return win
        # fall back to searching all dialogs and returning the focused one
        for dialog in self.get_all_dialogs():
            if self.is_focused(dialog):
                return dialog
        return win

    def wait_for_window(
        self,
        title: str,
        timeout: float = 10.0,
        poll_interval: float = 0.1,
        *,
        raise_on_timeout: bool = True,
    ) -> Window | None:
        """Wait for a window to appear.

        Polls the desktop until a window with ``title`` is found or ``timeout``
        seconds have elapsed.

        :param title: Title of the desired window.
        :param timeout: Maximum seconds to wait.
        :param poll_interval: Interval between polling attempts.
        :param raise_on_timeout: When ``True`` a :class:`WindowNotFound` is
            raised if the window is not found.
        :returns: A :class:`Window` instance or ``None`` if ``raise_on_timeout``
            is ``False`` and no window is found.
        :raises WindowNotFound: If the window is not located in time.
        """

        end = time.time() + timeout
        while time.time() < end:
            try:
                wrapper = self.desktop.window(title=title)
                if wrapper.exists(timeout=0):
                    return Window.from_pywinauto(wrapper)
            except Exception:
                pass
            time.sleep(poll_interval)

        focused = self.desktop.get_active().window_text()
        self.logger.error(
            "Timed out waiting for window '%s'. '%s' is focused.", title, focused
        )
        if raise_on_timeout:
            raise WindowNotFound(title)
        return None

    def wait_for_dialog(
        self,
        title: str,
        timeout: float = 10.0,
        poll_interval: float = 0.1,
        *,
        raise_on_timeout: bool = True,
    ) -> Window | None:
        """Wait for a dialog with ``title`` to appear."""

        end = time.time() + timeout
        while time.time() < end:
            try:
                wrapper = self.desktop.window(title=title)
                if wrapper.exists(timeout=0) and wrapper.friendly_class_name() == "Dialog":
                    return Window.from_pywinauto(wrapper)
            except Exception:
                pass
            time.sleep(poll_interval)

        focused = self.desktop.get_active().window_text()
        self.logger.error(
            "Timed out waiting for dialog '%s'. '%s' is focused.", title, focused
        )
        if raise_on_timeout:
            raise WindowNotFound(title)
        return None

    def get_all_windows(self) -> List[Window]:
        """Return a list of all top level windows as :class:`Window` objects."""
        windows: List[Window] = []
        for win in self.desktop.windows():
            if win.friendly_class_name() != "Dialog":
                windows.append(Window.from_pywinauto(win))
        return windows
            
    def get_all_dialogs(self, filter: Window | None = None) -> List[Window]:
        """
        Returns a list of :class:`Window` instances for all dialogs.

        :param filter: Limits the return for only dialogs open under that window.
        :type filter: Window | None = None
        """
        dialogs: List[Window] = []
        if filter is not None:
            try:
                app = Application(backend="uia").connect(title=filter.name)
                candidates = app.windows()
            except Exception:
                candidates = []
        else:
            candidates = self.desktop.windows()

        for win in candidates:
            if win.friendly_class_name() == "Dialog":
                dialogs.append(Window.from_pywinauto(win))

        return dialogs

    def is_window(self, window: Window) -> bool:
        """
        If the provided :py:class:`Window` instance represents a top level window.

        :param window: The window model instance to examine.
        :type window: Window
        """
        try:
            wrapper = self.desktop.window(title=window.name)
            return wrapper.friendly_class_name() != "Dialog"
        except Exception:
            return False
    
    def is_dialog(self, window: Window) -> bool:
        """
        If the provided :class:`Window` instance represents a dialog.

        :param window: The window model instance to examine.
        :type window: Window
        """
        try:
            wrapper = self.desktop.window(title=window.name)
            return wrapper.friendly_class_name() == "Dialog"
        except Exception:
            return False

    def is_focused(self, window: Window) -> bool:
        """
        If the provided :class:`Window` instance is currently focused.

        :param window: The window model instance to examine.
        :type window: Window
        """
        try:
            active = self.desktop.get_active()
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
        *,
        keys: List[str] | None = None,
        string: str | None = None,
        send_count: int = 1,
        char_at_a_time: bool = False,
        delay: float = 0,
    ) -> None:
        """Send keyboard input to the active window.

        :param keys: List of keys to send simultaneously as a hotkey.
        :param string: Optional string to type/paste.
        :param send_count: Number of times to repeat the send.
        :param char_at_a_time: When ``True`` characters of ``string`` are sent
            individually.
        :param delay: Delay between repeated sends.
        :raises ValueError: If neither ``keys`` nor ``string`` is provided.
        """

        if keys is None and string is None:
            raise ValueError("Either 'keys' or 'string' must be provided")

        if keys is not None:
            sequence = ''.join(f'{{{k}}}' if len(k) > 1 else k for k in keys)
            for _ in range(send_count):
                keyboard.send_keys(sequence, pause=delay)
            return

        if string is not None:
            for _ in range(send_count):
                if char_at_a_time:
                    for char in string:
                        keyboard.send_keys(char, with_spaces=True, pause=delay)
                else:
                    keyboard.send_keys(string, with_spaces=True, pause=delay)

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
    
