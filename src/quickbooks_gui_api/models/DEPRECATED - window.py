# src\quickbooks_gui_api\models\window.py
from __future__ import annotations

from typing import Literal, Any

"""
NOTICE: 
This model was deprecated due to pivoting approach. 
"""

class Window:
    """Represents a generic application window."""

    def __init__(
        self,
        name: str,
        position: tuple[int, int],
        size: tuple[int, int],
        *,
        hwnd: int | None = None,
        pid: int | None = None,
        wrapper: Any | None = None,
        parent: Window | None = None,
    ) -> None:
        """Create a :class:`Window` model instance."""

        self._name: str = name  
        self._position_x: int = position[0]
        self._position_y: int = position[1]
        self._width: int = size[0]
        self._height: int = size[1]
        self._hwnd: int | None = hwnd
        self._pid: int | None = pid
        self._wrapper: Any | None = wrapper
        self._parent: Window | None = parent

    @property
    def name(self) -> str:
        return self._name

    @property
    def position(self) -> tuple[int, int]:
        return (self._position_x, self._position_y)
    
    @property
    def size(self) -> tuple[int, int]:
        return (self._width, self._height)

    @property
    def hwnd(self) -> int | None:
        return self._hwnd

    @property
    def pid(self) -> int | None:
        return self._pid

    @property
    def wrapper(self) -> Any | None:
        return self._wrapper

    @property
    def parent(self) -> Window | None:
        return self._parent
    

    def center(self, mode: Literal["absolute", "relative"] = "absolute") -> tuple[int, int]:
        """
        Returns the coordinates for the center of the window.

        :param mode:    `relative`: The center of the window, relative to the window.
                        `absolute`: The center of the window, relative to the display.
        :type mode:     Literal["absolute", "relative"] = "absolute"
        """

        if mode == "absolute":
            return ((self._position_x + self._width) // 2, ((self._position_y + self._height) // 2))
        elif mode == "relative":
            return (self._width // 2, self._height // 2)

    def __repr__(self) -> str:
        return f"Window(name={self._name!r}, position={self.position}, size={self.size})"

    @classmethod
    def from_pywinauto(cls, wrapper: Any, parent: Window | None = None) -> Window:
        """Create a :class:`Window` model from a pywinauto wrapper object."""
        rect = wrapper.rectangle()
        return cls(
            wrapper.window_text(),
            (rect.left, rect.top),
            (rect.width(), rect.height()),
            hwnd=getattr(wrapper, "handle", None),
            pid=getattr(wrapper, "process_id", lambda: None)(),
            wrapper=wrapper,
            parent=parent,
        )

