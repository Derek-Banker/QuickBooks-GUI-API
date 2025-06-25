# --- BOILER --------------------------------------------------------------------
from pathlib import Path
from datetime import datetime

from typing import List, Dict

import logging
GLOBAL_FMT = "%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - line %(lineno)d: %(message)s"
logging.basicConfig(
    level    = logging.DEBUG,
    format   = GLOBAL_FMT,
    handlers = [logging.StreamHandler()]  # you can omit handlers if you just want the default stream
)
logger = logging.getLogger(__name__)
# --- BOILER --------------------------------------------------------------------

from quickbooks_gui_api.managers import OCRManager, ImageManager
from quickbooks_gui_api.models import Image

# --- Test Image ---
logger.info("=== Image load test ===")
TEST_IMG_PATH = Path(r"tests\Test Case - Image Manager.png")
start = datetime.now()
img = Image((0, 0), (500, 500)).load(TEST_IMG_PATH)
stop = datetime.now()
logger.info(f"Previous operation time: `{stop - start}`.\n")

ocr_manager = OCRManager(logger=logger)
image_manager = ImageManager(logger=logger)

logger.info("=== OCR single image test ===")
start = datetime.now()
text = ocr_manager.get_text(img)
stop = datetime.now()
logger.debug(f"Detected text: {text}")
logger.info(f"Previous operation time: `{stop - start}`.\n")

logger.info("=== OCR multiple images test ===")
start = datetime.now()
width, height = img.size
half_height = height // 2
crop_top = image_manager.crop(img, from_bottom=half_height)
crop_bottom = image_manager.crop(img, from_top=half_height)
results = ocr_manager.get_multi_text([crop_top, crop_bottom])
stop = datetime.now()
for i, (_, result_text) in enumerate(results.items()):
    logger.debug(f"Result {i}: {result_text}")
logger.info(f"Previous operation time: `{stop - start}`.\n")
