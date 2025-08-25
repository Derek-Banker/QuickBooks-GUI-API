# --- BOILER --------------------------------------------------------------------
import time
import logging
GLOBAL_FMT = "%(asctime)s | %(levelname)s | %(module)s:%(funcName)s:%(lineno)d | %(message)s"
logging.basicConfig(
    level    = logging.DEBUG,
    format   = GLOBAL_FMT,
    handlers = [logging.StreamHandler()]  # you can omit handlers if you just want the default stream
)
logger = logging.getLogger(__name__)
# --- BOILER --------------------------------------------------------------------

from quickbooks_gui_api import QuickBookGUIAPI
from quickbooks_gui_api.utilities import LogManager


gui_api = QuickBookGUIAPI(logger=LogManager.get_logger(__name__))

try:
    logger.info("Attempting pre-test shutdown to clean up old processes...")
    gui_api.shutdown()
    time.sleep(1)
except Exception:
    logger.debug("No existing QuickBooks process found to shut down (which is normal).")

try:
    logger.info("Starting the main test...")
    gui_api.startup()
    logger.info("Startup successful. Waiting for 5 seconds...")
    time.sleep(5)
finally:
    logger.info("Test finished. Shutting down QuickBooks.")
    # gui_api.shutdown()
