# src\quickbooks_gui_api\models\image.py
from __future__ import annotations

import logging
from pathlib import Path
from typing import Literal
from PIL import Image as PILImage

logging.getLogger("PIL").setLevel(logging.WARNING)

class Image:
    """
    Represents an image with source coordinates, size, and path.
    Attributes:
        source (tuple[int, int]): The source coordinates (x, y) of the image.
        size (tuple[int, int]): The size of the image (width, height).
        path (Path | None): The file path of the image.
    """
    def __init__(self, 
                 source: tuple[int | None, int | None] = (None, None),
                 size: tuple[int | None, int | None] = (None, None),
                 img: PILImage.Image | None = None,
                 ) -> None:
        self._source_x: int | None = source[0]
        self._source_y: int | None = source[1]
        self._width:    int | None = size[0]
        self._height:   int | None = size[1]
        self._path:     Path| None = None
        self._area:     int | None = None

        self._img: PILImage.Image | None = img



    @property
    def source(self) -> tuple[int, int]:
        if self._source_x is None or self._source_y is None:
            raise ValueError("Source x and y must be set to get source.")
        return (self._source_x, self._source_y)
    @source.setter
    def source(self, value: tuple[int, int]):
        if not isinstance(value, tuple) or len(value) != 2:
            raise TypeError("Source must be a tuple of (x, y).")
        self._source_x, self._source_y = value
    
    @property
    def size(self) -> tuple[int, int]:
        if self._width is None or self._height is None:
            raise ValueError("Width and height must be set to get size.")
        return (self._width, self._height)
    @size.setter
    def size(self, value: tuple[int, int]):
        if not isinstance(value, tuple) or len(value) != 2:
            raise TypeError("Size must be a tuple of (width, height).")
        self._width, self._height = value

    @property
    def img(self) -> PILImage.Image:
        if self._img is None:
            if self._path is None:
                raise ValueError("Image is not loaded and path is not set.")
            else:
                self._img = self.load(self._path).img
        return self._img
    @img.setter
    def img(self, value: PILImage.Image | None):
        if value is not None and not isinstance(value, PILImage.Image):
            raise TypeError("Image must be a PIL Image object or None.")
        self._img = value

    @property
    def area(self) -> int:
        if self._area is None:
            if self._width is None or self._height is None:
                raise ValueError("Area calculation was attempted, but `height` and or `width` is None.")
            else:
                self._area = self._width * self._height
            
        return self._area

    @property
    def path(self) -> Path | None:
        return self._path
    @path.setter
    def path(self, value: Path | None):
        if value is not None and not isinstance(value, Path):
            raise TypeError("Path must be a Path object or None.")
        self._path = value

    def center(self, mode: Literal["absolute", "relative"] = "absolute") -> tuple[int, int]:
        if self._width is None or self._height is None:
            raise ValueError("Width and height must be set to calculate absolute center.")
        else:
            if mode == "absolute":
                if self._source_x is None or self._source_y is None:
                    raise ValueError("Source x and y must be set to calculate absolute center.")
                return ((self._source_x + self._width) // 2, ((self._source_y + self._height) // 2))
            elif mode == "relative":
                return (self._width // 2, self._height // 2)
            else:
                raise ValueError("Mode must be 'absolute' or 'relative'.")

    def save(self,  
             save_path: Path
             ) -> Path:
        if self._img is None:
            raise ValueError("Image is not loaded. Please load an image before saving.")
        if not isinstance(save_path, Path):
            raise TypeError("Save path must be a Path object.")
        if not save_path.parent.exists():
            raise FileNotFoundError(f"The directory {save_path.parent} does not exist.")
        if save_path.suffix.lower() not in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
            raise ValueError(f"The save path {save_path} is not a valid image format.")
        self._img.save(save_path)
        self._path = save_path
        return self._path

    def load(self,
             file_path: Path
             ) -> Image:
        if not file_path.exists():
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        if not file_path.is_file():
            raise ValueError(f"The path {file_path} is not a file.")
        if file_path.suffix.lower() not in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
            raise ValueError(f"The file {file_path} is not a valid image format.")

        self._img = PILImage.open(file_path)
        return self
