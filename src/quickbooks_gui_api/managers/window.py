# src\quickbooks_gui_api\managers\windows.py

import time
import logging
import win32gui
from ctypes.wintypes import RECT
import pyautogui
import pywinauto.mouse
import pywinauto.timings

from typing                         import List, Tuple, overload, Dict, Any
from pywinauto                      import Application, WindowSpecification
from pywinauto.controls.uiawrapper  import UIAWrapper


class WindowManager:
    """
    Manages windows in Windows. 
    Attributes:
        logger (logging.Logger): Logger instance for logging operations.
    """
    

    def __init__(self, logger: logging.Logger | None = None) -> None:
        if logger is None:
            self.logger = logging.getLogger(__name__)
        elif isinstance(logger, logging.Logger):
            self.logger = logger
        else:
            raise TypeError("Provided parameter `logger` is not an instance of `logging.Logger`.")
        
    @staticmethod
    def rect_to_size_pos(rect: RECT) -> tuple[tuple[int, int], tuple[int, int]]:
        """ 
        Converts the winType RECT into a two size and pos tuples
        :returns: (int(width), int(height))(size), (int(x), int(y))(pos)
        """
        return (rect.width(), rect.height()), (rect.left, rect.top)


    def get_all_dialog_titles(self, app: Application) -> List[str]:
        """
        Return every caption of every UIA “Dialog” under `app`.
        """
        # 1) Locate and wrap the main window
        main_spec = app.window(title_re=".*QuickBooks.*")
        try:
            main_wrap: UIAWrapper = (
                main_spec
                if isinstance(main_spec, UIAWrapper)
                else main_spec.wrapper_object()
            )
        except Exception as e:
            raise RuntimeError(f"Could not wrap main QuickBooks window: {e}")

        titles: List[str] = []
        seen = set()

        # 2) Include the main window itself *if* it's a Dialog
        if main_wrap.friendly_class_name() == "Dialog":
            text = main_wrap.window_text().strip()
            if text:
                titles.append(text)
                seen.add(text)

        # 3) Walk all Window controls beneath it
        for win in main_wrap.descendants(control_type="Window"):
            # 4) Filter by the friendly class name
            if win.friendly_class_name() != "Dialog":
                continue
            # 5) Grab its text
            text = win.window_text().strip()
            if not text or text in seen:
                continue
            titles.append(text)
            seen.add(text)

        return titles
        

    def is_element_active(
            self,
            element: UIAWrapper | WindowSpecification | None = None,
            *,
            root: pywinauto.WindowSpecification | None = None,
            timeout: float = 5,
            attempt_focus: bool = False,
            retry_interval: float = 0.25,
            **child_kwargs: Dict[str, Any],
        ) -> bool:
        """
        Return True only if `element` is present, visible, enabled, and
        not obscured by any other window.

        You must pass *either*:
        - `element`: a UIAWrapper (or WindowSpecification) you already have, **or**
        - `root` + any number of child_window keyword args
            (e.g. auto_id="foo", control_type="Button", title="OK", etc.)
        """
        # 1) resolve element if necessary
        if element is None:
            if root is None or not child_kwargs:
                raise ValueError(
                    "Must provide either `element` or (`root` + child_window criteria)"
                )
            element = root.child_window(**child_kwargs)

        # 2) obtain a concrete wrapper to avoid repeated lookups
        if isinstance(element, WindowSpecification):
            try:
                element = element.wrapper_object()
            except Exception:
                # fall back to waiting if the control isn't ready yet
                if timeout > 0:
                    try:
                        element = element.wait(
                            "exists visible enabled ready",
                            timeout=timeout,
                            retry_interval=retry_interval,
                        )
                    except pywinauto.timings.TimeoutError:
                        return False
                else:
                    return False
        else:
            if timeout > 0:
                try:
                    pywinauto.timings.wait_until(
                        timeout,
                        retry_interval,
                        lambda: (
                            getattr(element, "exists", lambda: True)()
                            and getattr(element, "is_visible", lambda: True)()
                            and getattr(element, "is_enabled", lambda: True)()
                        ),
                    )
                except pywinauto.timings.TimeoutError:
                    return False
            else:
                if not (
                    getattr(element, "exists", lambda: True)()
                    and getattr(element, "is_visible", lambda: True)()
                    and getattr(element, "is_enabled", lambda: True)()
                ):
                    return False

        if element is None:
            return False


        # 3) optionally focus it
        if attempt_focus:
            try:
                element.set_focus()
            except Exception:
                pass

        # 4) pick a point in the middle of its bounding rectangle
        rect = element.rectangle()
        cx = (rect.left + rect.right) // 2
        cy = (rect.top + rect.bottom) // 2

        # 5) Win32 hit-test at that point
        hwnd_at_point = win32gui.WindowFromPoint((cx, cy))
        return hwnd_at_point == element.handle
    
    def top_dialog(self, app: Application) -> str:
        """
        Return the title of the topmost modal dialog in the given
        ``Application``.  If no dialog is found an empty string is
        returned.
        """

        main_spec = app.window(title_re=".*QuickBooks.*")
        try:
            main_wrap: UIAWrapper = (
                main_spec
                if isinstance(main_spec, UIAWrapper)
                else main_spec.wrapper_object()
            )
        except Exception as e:
            raise RuntimeError(f"Could not wrap main QuickBooks window: {e}")

        dialogs: list[tuple[int, UIAWrapper]] = []

        def _collect(node: UIAWrapper, depth: int) -> None:
            for child in node.children():
                try:
                    if child.friendly_class_name() == "Dialog" and child.window_text().strip():
                        dialogs.append((depth + 1, child))
                except Exception:
                    pass
                _collect(child, depth + 1)

        _collect(main_wrap, 0)

        dialogs.sort(key=lambda t: t[0], reverse=True)

        for _, dlg in dialogs:
            if self.is_element_active(dlg, timeout=0.2, retry_interval=0.05):
                return dlg.window_text()

        return dialogs[0][1].window_text() if dialogs else ""
    
    @overload
    def send_input(self, keys: str | List[str] | None = None, *, send_count: int = 1, delay: float = 0) -> None:...
    @overload
    def send_input(self, *, string: str | None = None, char_at_a_time: bool = False, delay: float = 0) -> None:...

    def send_input(
            self,
            keys: str | List[str] | None = None,
            *,
            string: str | None = None,
            send_count: int = 1,
            char_at_a_time: bool = False,
            delay: float = 0.0,
        ) -> None:
        """Send keyboard input to the active window.

        :param  keys:           Individual keys or hotkeys to press.
                                If a nested list is passed, each sublist will be treated as a batch and delay will be used in-between each.
        :type   keys:           str | List[str] | None = None
        :param  string:         Optional string to type/paste.
        :type   string:         str | None = None
        :param  send_count:     Number of times to repeat the send.
        :type   send_count:     int = 1
        :param  char_at_a_time: When ``True`` characters of ``string`` are sent individually.
        :param  delay:          Delay between repeated sends or batches.
        :type   delay:          float = 0.0 
        :raises ValueError:     If neither ``keys`` nor ``string`` is provided.
        """
        if keys is None and string is None:
            raise ValueError("Either 'keys' or 'string' must be provided.")

        # Handle keys
        if keys is not None:
            for _ in range(send_count):
                # Single string (e.g., "enter" or "a")
                if isinstance(keys, str):
                    self.logger.debug("Sending single key input: `%s`.", keys)
                    pyautogui.press(keys)
                # Flat list (e.g., ["ctrl", "a"])
                elif isinstance(keys, list) and all(isinstance(k, str) for k in keys):
                    # Send all as a hotkey (simultaneous press)
                    self.logger.debug("Sending key input as hotkey: `%s`.", keys)
                    pyautogui.hotkey(*keys)
                else:
                    raise ValueError("Invalid format for 'keys'. Must be str or List[str].")
                if delay and not (isinstance(keys, list) and all(isinstance(k, list) for k in keys)):
                    time.sleep(delay)
            # If keys was provided, don't send string (even if not None)
            return

        # Handle string input
        if string is not None:
            for _ in range(send_count):
                if char_at_a_time:
                    self.logger.debug("Sending string `%s` char at a time with a delay of `%f`.", string, delay)
                    for char in string:
                        pyautogui.typewrite(char)
                        if delay:
                            time.sleep(delay)
                else:
                    self.logger.debug("Sending string `%s` all at once a delay after of `%f`.", string, delay)
                    pyautogui.typewrite(string)
                    if delay:
                        time.sleep(delay)



    @overload
    def mouse(self, x: int | None = None, y: int | None = None, *, click: bool = True) -> None:...
    @overload
    def mouse(self, *, position: Tuple[int, int] | None = None, click: bool = True) -> None:...

    def mouse(
            self, 
            x: int | None = None, 
            y: int | None = None, 
            *,
            position: Tuple[int, int] | None = None,
            click: bool = True
        ) -> None:
        """
        Move the mouse to and or click at the specified coordinates.

        :param  x:          X coordinate to be clicked.  
        :type   x:          int | None = None
        :param  y:          Y coordinate to be clicked.
        :type   y:          int | None = None
        :param  position:   Alternative input method, x,y tuple. 
        :type   position:   Tuple[int, int] | None = None
        """

        if position is not None:
            x = position[0]
            y = position[1]

        if x is None or y is None:
            raise ValueError("x and y coordinates are required")

        coords = (x, y)
        if click:
            pywinauto.mouse.click(coords=coords)
        else:
            pywinauto.mouse.move(coords=coords)
    
