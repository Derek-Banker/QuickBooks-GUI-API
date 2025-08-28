# --- BOILER --------------------------------------------------------------------
import time
from pathlib import Path

from quickbooks_gui_api.utilities import LogManager
logger = LogManager.get_logger(__name__)
# --- BOILER --------------------------------------------------------------------

from quickbooks_gui_api import QuickBookGUIAPI

USERNAME = ""
PASSWORD = ""

# If you have not already initalized the config you have to run this before the first run or after any config directory changes. 
# ConfigInit(logger=logger)

gui_api = QuickBookGUIAPI(logger=logger)

try:
    logger.info("Attempting pre-test shutdown to clean up old processes...")
    gui_api.shutdown()
    time.sleep(1)
except Exception:
    logger.debug("No existing QuickBooks process found to shut down (which is normal).")

try:
    logger.info("Starting the main test...")
    gui_api.startup(USERNAME, PASSWORD)
    logger.info("Startup successful. Waiting for 5 seconds...")
    time.sleep(5)
finally:
    logger.info("Test finished. Shutting down QuickBooks.")
    # gui_api.shutdown()
