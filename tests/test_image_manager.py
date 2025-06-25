# --- BOILER -----------------------------------------------------------------------
from pathlib import Path
from datetime import datetime, timedelta

from typing import List, Dict, Final, Literal, overload, Any

import logging
GLOBAL_FMT = "%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - line %(lineno)d: %(message)s"
logging.basicConfig(
    level    = logging.DEBUG,    # global minimum level
    format   = GLOBAL_FMT,       # global format
    handlers = [logging.StreamHandler()]  # you can omit handlers if you just want the default stream
)
logger = logging.getLogger(__name__)
# --- BOILER -----------------------------------------------------------------------

from quickbooks_gui_api.managers import ImageManager, Color
from quickbooks_gui_api.models import Image

# --- Test Image ---
logger.info("=== Image load test ===")
TEST_IMG_PATH = Path(r"tests\Test Case - Image Manager.png")
start = datetime.now()
img = Image((0, 0), (500, 500)).load(TEST_IMG_PATH)
stop = datetime.now()
logger.info(f"Previous operation time: `{stop - start}`.\n")


red =   Color(hex_val="ed1c24")
blue =  Color(hex_val="3f48cc")
white = Color(hex_val="ffffff")


manager = ImageManager(logger=logger)

logger.info("=== Color conversion test ===")
start = datetime.now()
logger.debug(f"White HEX:`{white.hex}`, RGB:`{white.rgb}`")
stop = datetime.now()
logger.info(f"Previous operation time: `{stop - start}`.\n")

logger.info("=== Crop test ===")
start = datetime.now()
temp = manager.crop(img, from_top=200, from_bottom=200, from_left=200, from_right=200)
stop = datetime.now()
file_name = "test-crop.png"
temp.save(Path(file_name))
logger.debug(f"Saved crop test file as `{file_name}`")
logger.info(f"Previous operation time: `{stop - start}`.\n")

logger.info("=== Single region isolation test ===")
start = datetime.now()
temp = manager.isolate_region(img, red)
stop = datetime.now()
file_name = "test-single_isolation.png"
temp.save(Path(file_name))
logger.debug(f"Saved single region isolation test file as `{file_name}`.")
logger.info(f"Previous operation time: `{stop - start}`.\n")

logger.info("=== Single region isolation test ===")
start = datetime.now()
regions = manager.isolate_multiple_regions(img, blue)
stop = datetime.now()
logger.debug(f"Found `{len(regions)}` regions.")
for i, region in enumerate(regions):
    file_name = f"test-multi_isolation_{i}.png"
    region.save(Path(file_name))
    logger.debug(f"Saved multi region isolation test file as `{file_name}`.")
logger.info(f"Previous operation time: `{stop - start}`.\n")

logger.info("=== Modify color test - whitelist ===")
start = datetime.now()
temp = manager.modify_color(img, red, blue)
stop = datetime.now()
file_name = "test-modify_color_whitelist.png"
temp.save(Path(file_name))
logger.debug(f"Saved modify color test file as `{file_name}`.")
logger.info(f"Previous operation time: `{stop - start}`.\n")

logger.info("=== Modify color test - blacklist ===")
start = datetime.now()
temp = manager.modify_color(img, white, Color(hex_val="#000000"))
stop = datetime.now()
file_name = "test-modify_color_blacklist.png"
temp.save(Path(file_name))
logger.debug(f"Saved modify color test file as `{file_name}`.")
logger.info(f"Previous operation time: `{stop - start}`.\n")

logger.info("=== Line test ===")
start = datetime.now()
temp = manager.line_test(img)
stop = datetime.now()
file_name = "test-line_test.png"
temp.save(Path(file_name))
logger.debug(f"Saved line test file as `{file_name}`.")
logger.info(f"Previous operation time: `{stop - start}`.\n")