# src\quickbooks_gui_api\models\image.py
from __future__ import annotations

from typing import Literal


class Window:
    """
    Represents an image with source coordinates, size, and path.
    Attributes:
        source (tuple[int, int]): The source coordinates (x, y) of the image.
        size (tuple[int, int]): The size of the image (width, height).
        path (Path | None): The file path of the image.
    """
    def __init__(self, 
                 name: str,
                 position: tuple[int, int],
                 size: tuple[int, int],
                 ) -> None:
        self._name:         str = name
        self._position_x:   int = position[0]
        self._position_y:   int = position[1]
        self._width:        int = size[0]
        self._height:       int = size[1]

    @property
    def name(self) -> str:
        return self._name

    @property
    def position(self) -> tuple[int, int]:
        return (self._position_x, self._position_y)
    
    @property
    def size(self) -> tuple[int, int]:
        return (self._width, self._height)
    

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

