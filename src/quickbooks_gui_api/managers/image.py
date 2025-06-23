from __future__ import annotations
import logging
from typing import BinaryIO, Literal, List
from PIL import Image as PILImage
import numpy
import mss

from pathlib import Path

from src.quickbooks_gui_api.models.image import Image

class ImageManager:
    """
    Manages image operations such as taking screenshots, cropping, isolating regions, and modifying colors.
    Attributes:
        logger (logging.Logger): Logger instance for logging operations.
    """

    def __init__(self, 
                 logger: logging.Logger | None = None
                 ) -> None:
        
        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            if isinstance(logger, logging.Logger):
                self.logger = logger 
            else:
                raise TypeError("Provided parameter `logger` is not an instance of `logging.Logger`.")

    def capture(self, 
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

    def isolate_region(self,
                        image: Image ,
                        color: str | tuple[int,int,int]
                        ) -> Image:
        return Image()
    
    def isolate_multiple_regions(self,
                        image: List[Image] | Image ,
                        color: str | tuple[int,int,int]
                        ) -> List[Image]:
        
        return List[Image]

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
