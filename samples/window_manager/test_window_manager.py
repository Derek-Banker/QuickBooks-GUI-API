# --- BOILER -------------------------------------------------------------------
from datetime import datetime
import logging

GLOBAL_FMT = "%(asctime)s | %(levelname)s | %(module)s:%(funcName)s:%(lineno)d | %(message)s"
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
app = Application(backend='uia').connect(path='QBW.EXE')
window = app.window(title_re=".*QuickBooks.*")
window.set_focus()




window_manager = WindowManager(logger=logger)

logger.info("=== List windows ===")
start = datetime.now()
dialogs = window_manager.get_all_dialog_titles(app)
stop = datetime.now()
logger.debug(f"Dialogs: `{dialogs}`")
logger.info(f"Previous operation time: `{stop - start}`.\n")

logger.info("=== Send Input ===")
start = datetime.now()
window_manager.send_input(["ctrl","i"])
stop = datetime.now()
logger.info(f"Previous operation time: `{stop - start}`.\n")


logger.info("=== Is Element Active ===")
start = datetime.now()
dialogs = window_manager.is_element_active(root=window, control_type = "Window", auto_id = "65280")
stop = datetime.now()
logger.debug(f"Dialogs: `{dialogs}`")
logger.info(f"Previous operation time: `{stop - start}`.\n")

logger.info("=== Top Dialog ===")
start = datetime.now()
dialog = window_manager.top_dialog(app)
stop = datetime.now()
logger.debug(f"Top Dialog: `{dialog}`")
logger.info(f"Previous operation time: `{stop - start}`.\n")

logger.info("=== Mouse ===")
start = datetime.now()
window_manager.mouse(0,0)
stop = datetime.now()
logger.info(f"Previous operation time: `{stop - start}`.\n")