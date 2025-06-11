from __future__ import annotations
import logging
from typing import BinaryIO, Literal
from PIL import Image as PILImage
import numpy
import mss

from pathlib import Path

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
                 path: Path | None = None
                 ) -> None:
        self._source_x = source[0]
        self._source_y = source[1]
        self._width = size[0]
        self._height = size[1]
        self._path = path

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


class ImageManager:
    """
    Manages image operations such as taking screenshots, cropping, isolating regions, and modifying colors.
    Attributes:
        logger (logging.Logger): Logger instance for logging operations.
    """

    def __init__(self, logger: logging.Logger | None = None) -> None:
        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger

    def screenshot(self, 
                   size: tuple[int, int],
                   source: tuple[int, int] = (0, 0),
                   ) -> Image:
        with mss.mss() as sct:
            monitor = {
                "left": source[0],
                "top": source[1],
                "width": size[0],
                "height": size[1]
            }
            screenshot = sct.grab(monitor)
            img = PILImage.frombytes('RGB', screenshot.size, screenshot.rgb)
            image = Image(source=source, size=size, img=img)
            return image
        
    def crop(self,
             image: Image, 
             test_vertical: bool = True, 
             test_horizontal: bool = True
             ) -> Image:
        
        if not (test_vertical and test_horizontal):
            raise ValueError("At least one of vertical or horizontal must be True.")
        
        if test_vertical:
            image = self._vertical_line_test(image)
        if test_horizontal:
            image = self._horizontal_line_test(image)
        return image

    def isolate_regions(self,
                        image: Image,
                        color: str | tuple[int,int,int]
                        ) -> list[tuple(Image,int)]:
        pass

    def modify_color(self,
                     image: Image,
                     target_color: str | tuple[int,int,int],
                     end_color: str | tuple[int,int,int],
                     mode: Literal["blacklist","whitelist"]
                    ) -> Image:       
        pass

    def _vertical_line_test(self, image: Image) -> Image:
        img = image.img
        img_array = numpy.array(img)

        left, right = 0, img_array.shape[1] - 1

        while left <= right and numpy.all(img_array[:, left] == img_array[0, left]):
            left += 1

        while right >= left and numpy.all(img_array[:, right] == img_array[0, right]):
            right -= 1

        cleaned_img = img.crop((left, 0, right + 1, img_array.shape[0]))

        image.img = cleaned_img
        return image

    def _horizontal_line_test(self, image: Image) -> Image:
        img = image.img
        img_array = numpy.array(img)

        top, bottom = 0, img_array.shape[0] - 1

        while top <= bottom and numpy.all(img_array[top, :] == img_array[top, 0]):
            top += 1

        while bottom >= top and numpy.all(img_array[bottom, :] == img_array[bottom, 0]):
            bottom -= 1

        cleaned_img = img.crop((0, top, img_array.shape[1], bottom + 1))

        image.img = cleaned_img
        return image

    @staticmethod        
    def _color(color: str | tuple[int,int,int]) -> tuple[int,int,int]:
        if isinstance(color, str):
            color = ImageManager._hex_to_rgb(color)
        return color
