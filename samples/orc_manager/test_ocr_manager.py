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

start = datetime.now()
img_one = Image((0,0),(200, 50)).load(Path(r"samples\orc_manager\Test Case - ORC Manager - 1.png"))
img_two = Image((0,0),(200, 50)).load(Path(r"samples\orc_manager\Test Case - ORC Manager - 2.png"))
stop = datetime.now()
logger.info(f"Previous operation time: `{stop - start}`.\n")

ocr_manager = OCRManager(logger=logger)

logger.info("=== OCR single image test ===")
start = datetime.now()
text = ocr_manager.get_text(img_one)
stop = datetime.now()
logger.debug(f"Detected text: `{text}`")
logger.info(f"Previous operation time: `{stop - start}`.\n")

logger.info("=== OCR multiple images test ===")
start = datetime.now()
results = ocr_manager.get_multi_text([img_one, img_two])
stop = datetime.now()
for i, (_, result_text) in enumerate(results.items()):
    logger.debug(f"Result {i}: {result_text}")
logger.info(f"Previous operation time: `{stop - start}`.\n")
