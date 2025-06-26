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

from quickbooks_gui_api.managers import WindowManager

window_manager = WindowManager(logger=logger)

logger.info("=== Active window ===")
start = datetime.now()
active = window_manager.active_window()
stop = datetime.now()
logger.debug(f"Active window: {active.name} at {active.position} size {active.size}")
logger.info(f"Previous operation time: `{stop - start}`.\n")

logger.info("=== List all windows ===")
start = datetime.now()
windows = window_manager.get_all_windows()
stop = datetime.now()
for win in windows:
    logger.debug(f"Window: {win.name}")
logger.info(f"Previous operation time: `{stop - start}`.\n")

logger.info("=== List all dialogs ===")
start = datetime.now()
dialogs = window_manager.get_all_dialogs()
stop = datetime.now()
for dlg in dialogs:
    logger.debug(f"Dialog: {dlg.name}")
logger.info(f"Previous operation time: `{stop - start}`.\n")

logger.info("=== Focus active window again ===")
start = datetime.now()
window_manager.attempt_focus_window(active)
stop = datetime.now()
logger.info(f"Previous operation time: `{stop - start}`.\n")

logger.info("=== Send input test ===")
start = datetime.now()
window_manager.send_input(string="Hello world!")
stop = datetime.now()
logger.info(f"Previous operation time: `{stop - start}`.\n")

logger.info("=== Mouse move test ===")
start = datetime.now()
center_pos = active.center("absolute")
window_manager.mouse(position=center_pos, click=False)
stop = datetime.now()
logger.info(f"Previous operation time: `{stop - start}`.\n")
