# --- BOILER --------------------------------------------------------------------
from pathlib import Path
from datetime import datetime

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
from quickbooks_gui_api.apis import Invoices
from quickbooks_gui_api.models import Invoice



main = QuickBookGUIAPI() 
app, window = main.startup()
main._kill_avatax()

i1 = Invoice("12000","INVOICE - 12000")
i2 = Invoice("13000","INVOICE - 13000")
i3 = Invoice("14000","INVOICE - 14000")
i4 = Invoice("15000","INVOICE - 15000")

invoice_saver = Invoices(app, window)
invoice_saver.save([i1, i2, i3, i4],Path(r"C:\Users\Derek\CFS - Derek\Downloads"))

