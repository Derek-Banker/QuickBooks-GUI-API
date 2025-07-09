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

from quickbooks_gui_api import QuickBookGUIAPI
from quickbooks_gui_api.apis import Invoices
from quickbooks_gui_api.models import Invoice

invoices: list =    [
                     1254,
                     2016,
                     4313,
                     7617,
                     8929,
                     10226,
                     15312,
                     15895,
                     15898,
                     15887,
                     16867,
                     17185,
                     17936,
                     17487,
                     17575,
                     17756,
                     17754,
                     17718,
                     17928
                    ]

main = QuickBookGUIAPI() 
app, window = main.startup()
main._kill_avatax()

invoice_objects: List[Invoice] = []

for invoice in invoices:
    invoice_objects.append(Invoice(str(invoice), None, Path(r"C:\Users\Derek\CFS - Derek\Holding")))

invoice_saver = Invoices(app, window)
invoice_saver.save(invoice_objects)

