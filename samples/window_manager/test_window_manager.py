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

qb_window.set_focus()
save_file_dialog = qb_window.child_window(control_type = "Window", title = "Save Print Output As")
save_file_dialog.set_focus()
file_name_field = qb_window.child_window(control_type = "Edit", auto_id= '1001')
print(window_manager.is_element_active(file_name_field, timeout=0.0, retry_interval=0.05, attempt_focus=True))

file_name_field.set_text("TEST")