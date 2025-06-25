# src\quickbooks_gui_api\managers\image.py

from __future__ import annotations
import logging
from typing import Literal, List, overload, Tuple
from PIL import Image as PILImage
import numpy
import mss
import cv2

from pathlib import Path

from quickbooks_gui_api.models import Image

class Color:
    """
    Effective data class to allow for easier usage of hex and RGB values. 
    """
    @overload
    def __init__(self, *, hex_val: str) -> None: ...
    @overload
    def __init__(self, *, R: int, G: int, B: int) -> None: ...

    def __init__( 
        self,
        *,
        hex_val: str | None = None,
        R: int | None = None,
        G: int | None = None,
        B: int | None = None
    ) -> None:
        """
        :param  hex_value: Hex string representation. 
        :type   hex_value: str | None = None
        :param  R: Red color value.
        :type   R: int | None = None
        :param  G: Green color value.
        :type   G: int | None = None
        :param  B: Blue color value.
        :type   B: int | None = None
        """
        # Validate input
        if hex_val is not None:
            self._hex: str | None = self._normalize_hex(hex_val)
            self._rgb: Tuple[int, int, int] | None = None
        elif R is not None and G is not None and B is not None:
            self._hex = None
            self._rgb = (R, G, B)
        else:
            raise ValueError("Provide either hex_val or all of r, g, b.")

    @staticmethod
    def _normalize_hex(h: str) -> str:
        h = h.strip()
        if h.startswith('#'):
            h = h[1:]
        if len(h) not in (6, 3):
            raise ValueError("Hex color must be 3 or 6 characters long.")
        if len(h) == 3:
            h = ''.join(2 * c for c in h)
        return f"#{h.lower()}"

    @staticmethod
    def _hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
        h = hex_str.lstrip('#')
        r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
        return (r, g, b)

    @staticmethod
    def _rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        return "#{:02x}{:02x}{:02x}".format(*rgb)

    @property
    def hex(self) -> str:
        if self._hex is None and self._rgb is not None:
            self._hex = self._rgb_to_hex(self._rgb)
        if self._hex is None:
            raise ValueError("No color value set.")
        return self._hex

    @property
    def rgb(self) -> Tuple[int, int, int]:
        if self._rgb is None and self._hex is not None:
            self._rgb = self._hex_to_rgb(self._hex)
        if self._rgb is None:
            raise ValueError("No color value set.")
        return self._rgb

    def __repr__(self):
        return f"Color(hex={self.hex!r}, rgb={self.rgb!r})"  



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

        :param  size:   Size of the capture region. Origin is top left. 
        :type   size:   Tuple[int(height), int(width)]
        :param  source: Offset of the capture region.
        :type   source: Tuple[int(x), int(y)] = (0, 0)
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

        :param  image:          The provided image to crop.
        :type   image:          Image
        :param  from_top:       Rows of pixels removed from the image. Starting at the top going down.
        :type   from_top:       int = 0
        :param  from_bottom:    Rows of pixels removed from the image. Starting at the bottom going up.
        :type   from_bottom:    int = 0 
        :param  from_left:      Columns of pixels removed from the image. Starting from the left going right. 
        :type   from_left:      int = 0
        :param  from_right:     Columns of pixels removed from the image. Starting from the right going left.
        :type   from_right:     int = 0
        :returns: Cropped image instance.
        :rtype: Image
        """

        width, height = image.size

        if height <= (from_top + from_bottom):
            error = ValueError("The provided parameters would remove more rows than are in the image.")
            self.logger.error(error)
            raise error

        if width <= (from_left + from_right):
            error = ValueError("The provided parameters would remove more columns than are in the image.")
            self.logger.error(error)
            raise error
    
        if (from_top + from_bottom + from_right + from_left) == 0:
            self.logger.warning("No pixels were removed from the image. All parameters are `0`.")
            return image
        
        left = from_left
        top = from_top
        right = width - from_right
        bottom = height - from_bottom

        cropped = image.img.crop((left, top, right, bottom))

        new_source = (
            image.source[0] + left if image._source_x is not None else left,
            image.source[1] + top if image._source_y is not None else top,
        )
        new_size = (right - left, bottom - top)

        return Image(source=new_source, size=new_size, img=cropped)


    def isolate_region(
        self,
        image: Image,
        color: Color,
        tolerance: float = 0.0,
    ) -> Image:
        """Return a cropped image of the area matching ``color``.

        The method scans ``image`` for pixels whose values are within ``tolerance``
        of ``color`` and crops the image to the smallest rectangle containing all
        matching pixels.

        :param image: Image instance to search.
        :type image: Image
        :param color: Target color to locate in ``image``.
        :type color: Color
        :param tolerance: Allowed deviation for each color channel.
        :type tolerance: float = 0.0
        :returns: A new image cropped to the detected region.
        :rtype: Image
        :raises ValueError: If ``color`` is not found in ``image``.
        """

        
    
    def isolate_multiple_regions(
        self,
        image: Image,
        target_color: Color,
        tolerance: float = 0.0,
    ) -> List[Image]:
        """Locate all regions of ``image`` matching ``target_color``.

        Connected-component analysis is used to group neighboring pixels of the
        target color into individual regions.

        :param image: Image to analyse.
        :type image: Image
        :param target_color: Colour to search for.
        :type target_color: Color
        :param tolerance: Allowed deviation for each channel when matching the
            colour.
        :type tolerance: float = 0.0
        :returns: A list of images cropped to the matching regions.
        :rtype: list[Image]
        """
        

    def modify_color(
            self,
            image: Image,
            target_color: Color,
            end_color: Color,
            tolerance: float = 0.0,
            mode: Literal["blacklist","whitelist"] = "whitelist"
        ) -> Image:
        """
        Replace one color with another color.

        :param  image:          The image to operate on.
        :type   image:          Image
        :param  target_color:   The color to replace.  
        :type   target_color:   Color
        :param  end_color:      The color to replace the target with.
        :type   end_color:      Color
        :param  tolerance:  The percent variance of color allowed in a sample. Useful for more reliable anti-aliasing and compression handling. 
        :type   tolerance:  float = 0.0
        :param  mode:           If ``whitelist`` only pixels matching
                                ``target_color`` are replaced. If ``blacklist``
                                all other pixels are replaced.
        :type   mode:           Literal["blacklist", "whitelist"]
        :returns: Modified image instance.
        :rtype: Image
        """

    def line_test(self,
             image: Image, 
             vertical: bool = True, 
             horizontal: bool = True
             ) -> Image:
        """
        Wrapper for the individual line test functions.

        :param  image:      The image instance to operate on.
        :type   image:      Image
        :param  vertical:   Run a vertical line test on the image.
        :type   vertical:   bool = True
        :param  horizontal: Run a horizontal line test on the image.
        :type   horizontal: bool = True
        """

        if not (vertical and horizontal):
            raise ValueError("At least one of vertical or horizontal must be True.")
        
        if vertical:
            image = self._vertical_line_test(image)
        if horizontal:
            image = self._horizontal_line_test(image)
        return image

    def _vertical_line_test(
            self, 
            image: Image,
            tolerance: float = 0.0
        ) -> Image: 
        """
        Runs a vertical line test on the provided image, allows for a variance tolerance.

        :param  image:      Image to operate on. 
        :type   image:      Image
        :param  tolerance:  The percent variance of color allowed in a sample. Useful for more reliable anti-aliasing and compression handling. 
        :type   tolerance:  float = 0.0
        """
        

    def _horizontal_line_test(
            self, 
            image: Image, 
            tolerance: float = 0.0
        ) -> Image:
        """
        Runs a vertical line test on the provided image, allows for a variance tolerance.

        :param image: Image to operate on. 
        :type image: Image
        :param tolerance: The percent variance of color allowed in a sample. Useful for more reliable anti-aliasing and compression handling. 
        :type tolerance: float = 0.0
        """
       
    
