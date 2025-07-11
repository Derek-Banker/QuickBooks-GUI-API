# --- BOILER --------------------------------------------------------------------
from pathlib import Path
from datetime import datetime

from typing import List, Dict

import logging
GLOBAL_FMT = "%(asctime)s | %(levelname)s | %(module)s:%(funcName)s:%(lineno)d | %(message)s"
logging.basicConfig(
    level    = logging.DEBUG,
    format   = GLOBAL_FMT,
    handlers = [logging.StreamHandler()]  # you can omit handlers if you just want the default stream
)
logger = logging.getLogger(__name__)
# --- BOILER --------------------------------------------------------------------

from quickbooks_gui_api.managers import FileManager

file_manager = FileManager(logger=logger)

file_path = Path(r"samples\file_manager\Test Case - File Manager.txt")
not_file = Path(r"samples\file_manager\NOT Test Case - File Manager.txt")

logger.info("=== is_locked test ===")
start = datetime.now()
result = file_manager.is_locked(file_path)
stop = datetime.now()
logger.debug(f"Result: `{result}`")
logger.info(f"Previous operation time: `{stop - start}`.\n")

logger.info("=== wait_for_file test ===")
start = datetime.now()
result = file_manager.wait_for_file(file_path)
stop = datetime.now()
logger.debug(f"Result: `{result}`")
logger.info(f"Previous operation time: `{stop - start}`.\n")


logger.info("=== wait_for_file test ===")
start = datetime.now()
result = file_manager.wait_for_file(not_file, 1)
stop = datetime.now()
logger.debug(f"Result: `{result}`")
logger.info(f"Previous operation time: `{stop - start}`.\n")

logger.info("=== wait_till_stable test ===")
start = datetime.now()
result = file_manager.wait_till_stable(file_path)
stop = datetime.now()
logger.debug(f"Result: `{result}`")
logger.info(f"Previous operation time: `{stop - start}`.\n")

logger.info("=== time_since_modified test ===")
start = datetime.now()
result = file_manager.time_since_modified(file_path)
stop = datetime.now()
logger.debug(f"Result: `{result}`")
logger.info(f"Previous operation time: `{stop - start}`.\n")