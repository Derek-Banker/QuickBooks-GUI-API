# --- BOILER -------------------------------------------------------------------
from datetime import datetime
import logging

GLOBAL_FMT = "%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - line %(lineno)d: %(message)s"
logging.basicConfig(
    level    = logging.DEBUG,
    format   = GLOBAL_FMT,
    handlers = [logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
# --- BOILER -------------------------------------------------------------------

from pywinauto import Application

from quickbooks_gui_api.managers import WindowManager

# Connect to QuickBooks by executable name
qb_app = Application(backend='uia').connect(path='QBW.EXE')
qb_window = qb_app.window(title_re=".*QuickBooks.*")
qb_window.set_focus()




window_manager = WindowManager(logger=logger)

logger.info("=== List windows ===")
start = datetime.now()
dialogs = window_manager.get_all_dialog_titles(qb_app)
stop = datetime.now()
logger.debug(f"Dialogs: `{dialogs}`")
logger.info(f"Previous operation time: `{stop - start}`.\n")
