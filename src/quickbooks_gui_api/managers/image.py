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

    def capture(
            self, 
            size: tuple[int, int],
            source: tuple[int, int] = (0, 0),
        ) -> Image:
        """
        Capture a screenshot of the screen according to the parameters.

        :param size: Size of the capture region. Origin is top left. 
        :type size: tuple[int(height), int(width)]
        :param source: Offset of the capture region.
        :type source: tuple[int(x), int(y)] = (0, 0)
        """
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
        
    def crop(
            self,
            image:          Image,
            from_top:       int = 0,
            from_bottom:    int = 0,
            from_left:      int = 0,
            from_right:     int = 0,  
        ) -> Image:
        """
        Reduces the provided image by the provided dimensions.

        :param image: The provided image to crop.
        :type image: Image
        :param from_top: Rows of pixels removed from the image. Starting at the top going down.
        :type from_top: int = 0
        :param from_bottom: Rows of pixels removed from the image. Starting at the bottom going up.
        :type from_bottom: int = 0 
        :param from_left: Columns of pixels removed from the image. Starting from the left going right. 
        :type from_left: int = 0
        :param from_right: Columns of pixels removed from the image. Starting from the right going left.
        :type from_right: int = 0
        """

        if image.size[0] <= (from_bottom + from_bottom):
            error = ValueError("The provided parameters would remove more rows than are in the image.")
            self.logger.error(error)
            raise error
        
        if image.size[1] <= (from_left + from_right):
            error = ValueError("The provided parameters would remove more columns than are in the image.")
            self.logger.error(error)
            raise error
    
        if (from_top + from_bottom + from_right + from_left) == 0:
            self.logger.warning("No pixels were removed from the image. All parameters are `0`.")
            return image
        
        # TODO implement functionality. 

        return Image()

    def line_test(self,
             image: Image, 
             vertical: bool = True, 
             horizontal: bool = True
             ) -> Image:
        """
        Wrapper for the individual line test functions.

        :param image: The image instance to operate on.
        :type image: Image
        :param vertical: Run a vertical line test on the image.
        :type vertical: bool = True
        :param horizontal: Run a horizontal line test on the image.
        :type horizontal: bool = True
        """

        if not (vertical and horizontal):
            raise ValueError("At least one of vertical or horizontal must be True.")
        
        if vertical:
            image = self._vertical_line_test(image)
        if horizontal:
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
