# --- BOILER --------------------------------------------------------------------
from pathlib import Path
from datetime import datetime

from typing import List, Dict

import logging
GLOBAL_FMT = "%(asctime)s | %(levelname)s | %(module)s:%(funcName)s:%(lineno)d | %(message)s"
logging.basicConfig(
    level    = logging.DEBUG,
    format   = GLOBAL_FMT,
    handlers = [logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
# --- BOILER --------------------------------------------------------------------

from quickbooks_gui_api import QuickBookGUIAPI
from quickbooks_gui_api.apis import Reports
from quickbooks_gui_api.models import Report

save_path = Path(r"C:\Users\Derek\CFS - Derek\Programming\Python\Collections-V4\Ingest Data")

reports: List[Report] = [
                         Report("Data Export - All Invoices - 00001-11999", "STOPGAP - 1.CSV",                          save_path),
                         Report("Data Export - All Invoices - 12000-99999", "STOPGAP - 2.CSV",                          save_path),
                         Report("Data Export - All Customers - V 4",        "Data Export - All Customers & Jobs.CSV",   save_path)
                        ]

main = QuickBookGUIAPI() 
app, window = main.startup()

report_saver = Reports(app, window)
report_saver.save(reports)

# main.startup()

