import pyautogui
from PIL import Image, ImageOps
import numpy as np
import time
import mss
import easyocr
import pytesseract
from PIL import Image
import logging


class OCRManager:
    """
    Uses `pytesseract` to for OCR functionality. Used to Verify on scree information.
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
        

def screenshot_crop_to_color(region, target_color, tolerance=10, screenshot_path='screenshot.png', cropped_path='cropped.png'):
    with mss.mss() as sct:
        monitor = {
            "left": region[0],
            "top": region[1],
            "width": region[2],
            "height": region[3]
        }
        screenshot = sct.grab(monitor)
        img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
        img.save(screenshot_path)

    img_array = np.array(img)

    match_color = np.all(np.abs(img_array - target_color) <= tolerance, axis=-1)

    if not np.any(match_color):
        raise ValueError("Target color not found in image.")

    coords = np.argwhere(match_color)
    top_left = coords.min(axis=0)
    bottom_right = coords.max(axis=0)

    cropped_img = img.crop((top_left[1], top_left[0], bottom_right[1]+1, bottom_right[0]+1))
    cropped_img.save(cropped_path)

    return screenshot_path, cropped_path



def crop_blank_borders(image_path, cleaned_image_path='cleaned.png'):
    img = vertical_line_test(image_path)
    img.save(cleaned_image_path)

    img = horizontal_line_test(cleaned_image_path)
    img.save(cleaned_image_path)

    return cleaned_image_path

# # Example usage
# time.sleep(3)
# region = (1920, 0, 1920, 1080)  # x, y, width, height
# color_to_crop = (78, 158, 25)  # RGB for green 

# original, cropped = screenshot_crop_to_color(region, color_to_crop)
# cleaned = crop_blank_borders(cropped)

# # print(f"Original screenshot saved as {original}")
# # print(f"Cropped image saved as {cropped}")
# # print(f"Cleaned image saved as {cleaned}")

# img = Image.open(cleaned)
# text = pytesseract.image_to_string(img, config='--psm 6')
# print(f"pytesseract: '{text}'")

# reader = easyocr.Reader(['en'])
# result = reader.readtext(cleaned)
# print(f"easyocr: '{result}'")

# with mss.mss() as sct:
#         monitor = {
#             "left": region[0],
#             "top": region[1],
#             "width": region[2],
#             "height": region[3]
#         }
#         screenshot = sct.grab(monitor)
#         img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
#         img.save("test.png")