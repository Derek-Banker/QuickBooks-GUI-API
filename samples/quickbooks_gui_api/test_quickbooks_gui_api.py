# --- BOILER --------------------------------------------------------------------
from pathlib import Path
from datetime import datetime
import time
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

from quickbooks_gui_api import QuickBookGUIAPI


gui_api = QuickBookGUIAPI()

gui_api.startup()
time.sleep(5)
gui_api.shutdown()
