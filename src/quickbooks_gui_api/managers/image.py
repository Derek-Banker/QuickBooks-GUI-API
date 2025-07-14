# src\quickbooks_gui_api\managers\image.py

from __future__ import annotations

import cv2
import mss
import numpy
import logging

from PIL import Image as PILImage
from typing import Literal, List, overload, Tuple

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
        :type   size:   Tuple[int(width), int(height)]
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
        arr = numpy.array(image.img.convert("RGB"))
        distances = self.color_distance_array(arr, color.rgb)
        mask = distances <= tolerance

        if not mask.any():
            error = ValueError("Target color not found in image (within tolerance).")
            self.logger.error(error)
            raise error

        coords = numpy.argwhere(mask)
        top_left = coords.min(axis=0)
        bottom_right = coords.max(axis=0)

        crop_box = (
            int(top_left[1]),
            int(top_left[0]),
            int(bottom_right[1]) + 1,
            int(bottom_right[0]) + 1,
        )
        cropped_img = image.img.crop(crop_box)

        new_source = (
            image.source[0] + crop_box[0] if image._source_x is not None else crop_box[0],
            image.source[1] + crop_box[1] if image._source_y is not None else crop_box[1],
        )
        new_size = (crop_box[2] - crop_box[0], crop_box[3] - crop_box[1])

        return Image(source=new_source, size=new_size, img=cropped_img)


    def isolate_multiple_regions(
            self,
            image: Image,
            target_color: Color,
            tolerance: float = 0.0,
            min_area: int | None = None,
            min_size: Tuple[int | None, int | None] = (None, None),
        ) -> List[Image]:
        """
        Locate all regions of ``image`` matching ``target_color`` with optional minimum area and size filtering.

        :param image: Image to analyse.
        :type image: Image
        :param target_color: Colour to search for.
        :type target_color: Color
        :param tolerance: Allowed deviation for each channel when matching the colour.
        :type tolerance: float = 0.0
        :param min_area: Minimum area (in px) for a region to be returned.
        :type min_area: int | None
        :param min_size: Minimum width and height as (min_width, min_height).
        :type min_size: Tuple[int | None, int | None]
        :returns: A list of images cropped to the matching regions.
        :rtype: list[Image]
        """

        arr = numpy.array(image.img.convert("RGB"))
        distances = self.color_distance_array(arr, target_color.rgb)
        mask = (distances <= tolerance).astype('uint8')

        if not mask.any():
            return []

        num_labels, labels = cv2.connectedComponents(mask, connectivity=8)
        regions: list[Image] = []
        min_width, min_height = min_size if min_size else (None, None)

        for label in range(1, num_labels):
            ys, xs = numpy.where(labels == label)
            if ys.size == 0 or xs.size == 0:
                continue
            top = ys.min()
            bottom = ys.max()
            left = xs.min()
            right = xs.max()

            crop_box = (left, top, right + 1, bottom + 1)
            cropped_img = image.img.crop(crop_box)

            new_source = (
                image.source[0] + left if image._source_x is not None else left,
                image.source[1] + top if image._source_y is not None else top,
            )
            new_size = (right - left + 1, bottom - top + 1)

            region_img = Image(source=new_source, size=new_size, img=cropped_img)
            area_ok = min_area is None or region_img.area >= min_area
            width_ok = min_width is None or region_img.size[0] >= min_width
            height_ok = min_height is None or region_img.size[1] >= min_height

            if area_ok and width_ok and height_ok:
                regions.append(region_img)

        return regions

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
        :param  tolerance:      The percent variance of color allowed in a sample. Useful for more reliable anti-aliasing and compression handling.
        :type   tolerance:      float = 0.0
        :param  mode:           If ``whitelist`` only pixels matching
                                ``target_color`` are replaced. If ``blacklist``
                                all other pixels are replaced.
        :type   mode:           Literal["blacklist", "whitelist"]
        :returns: Modified image instance.
        :rtype: Image
        """

        if mode not in ("whitelist", "blacklist"):
            raise ValueError("mode must be 'blacklist' or 'whitelist'")

        arr = numpy.array(image.img.convert("RGB"))
        distances = self.color_distance_array(arr, target_color.rgb)
        mask = distances <= tolerance
        if mode == "blacklist":
            mask = ~mask

        arr = arr.copy()
        arr[mask] = numpy.array(end_color.rgb, dtype=arr.dtype)

        new_img = PILImage.fromarray(arr.astype('uint8'))

        return Image(source=image.source, size=image.size, img=new_img)

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

        Columns on the left and right edges that are a uniform colour (within
        ``tolerance``) are removed from the image.

        :param  image:      Image to operate on.
        :type   image:      Image
        :param  tolerance:  The percent variance of color allowed in a sample. Useful for more reliable anti-aliasing and compression handling.
        :type   tolerance:  float = 0.0
        """

        arr = numpy.array(image.img.convert("RGB"))
        height, width = arr.shape[:2]

        left = 0
        while left < width:
            col = arr[:, left]
            if numpy.all(numpy.abs(col - col[0]) <= tolerance):
                left += 1
            else:
                break

        right = width - 1
        while right >= left:
            col = arr[:, right]
            if numpy.all(numpy.abs(col - col[0]) <= tolerance):
                right -= 1
            else:
                break

        crop_box = (left, 0, right + 1, height)
        cropped_img = image.img.crop(crop_box)

        new_source = (
            image.source[0] + left if image._source_x is not None else left,
            image.source[1] if image._source_y is not None else 0,
        )
        new_size = (crop_box[2] - crop_box[0], crop_box[3] - crop_box[1])

        return Image(source=new_source, size=new_size, img=cropped_img)
    def _horizontal_line_test(
            self,
            image: Image,
            tolerance: float = 0.0
        ) -> Image:
        """
        Runs a vertical line test on the provided image, allows for a variance tolerance.

        Rows on the top and bottom edges that are a uniform colour (within
        ``tolerance``) are removed from the image.

        :param image: Image to operate on.
        :type image: Image
        :param tolerance: The percent variance of color allowed in a sample. Useful for more reliable anti-aliasing and compression handling.
        :type tolerance: float = 0.0
        """

        arr = numpy.array(image.img.convert("RGB"))
        height, width = arr.shape[:2]

        top = 0
        while top < height:
            row = arr[top]
            if numpy.all(numpy.abs(row - row[0]) <= tolerance):
                top += 1
            else:
                break

        bottom = height - 1
        while bottom >= top:
            row = arr[bottom]
            if numpy.all(numpy.abs(row - row[0]) <= tolerance):
                bottom -= 1
            else:
                break

        crop_box = (0, top, width, bottom + 1)
        cropped_img = image.img.crop(crop_box)

        new_source = (
            image.source[0] if image._source_x is not None else 0,
            image.source[1] + top if image._source_y is not None else top,
        )
        new_size = (crop_box[2] - crop_box[0], crop_box[3] - crop_box[1])

        return Image(source=new_source, size=new_size, img=cropped_img)

    @staticmethod
    def color_distance(rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
        """
        Compute the Euclidean (L2) distance between two RGB colors.

        :param rgb1: First RGB color as (R, G, B) tuple.
        :param rgb2: Second RGB color as (R, G, B) tuple.
        :return: Euclidean distance between the two colors.
        """
        arr1 = numpy.array(rgb1, dtype=numpy.int32)
        arr2 = numpy.array(rgb2, dtype=numpy.int32)
        return float(numpy.linalg.norm(arr1 - arr2))

    @staticmethod
    def color_distance_array(arr: numpy.ndarray, rgb: tuple[int, int, int]) -> numpy.ndarray:
        """
        Compute the Euclidean distance from every pixel in `arr` to the target `rgb` color.
        :param arr: Numpy array of shape (height, width, 3).
        :param rgb: Target color as (R, G, B) tuple.
        :return: Numpy array of distances, shape (height, width).
        """
        arr = arr.astype('int32')
        target = numpy.array(rgb, dtype='int32')
        return numpy.linalg.norm(arr - target, axis=-1)
    

    @staticmethod
    def largest (images: List[Image]) -> Image:
        """ Given a list of images, returns the one with the largest area. Does not recognize equals. """

        if len(images) == 0:
            raise ValueError("Invalid parameter: Empty list provided, cannot rank.")

        largest: Image = images[0]    
        for image in images:
            if largest.area < image.area:
                largest = image
        
        return largest
    
    @staticmethod
    def smallest (images: List[Image]) -> Image:
        """ Given a list of images, returns the one with the smallest area. Does not recognize equals. """

        if len(images) == 0:
            raise ValueError("Invalid parameter: Empty list provided, cannot rank.")

        smallest: Image = images[0]    
        for image in images:
            if smallest.area < image.area:
                smallest = image
        
        return smallest 
    
    