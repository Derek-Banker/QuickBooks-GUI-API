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
from quickbooks_gui_api.apis import Reports
from quickbooks_gui_api.models import Report

reports: list = [
                 "Data Export - All Invoices - V 3",
                 "Data Export - All Customers - V 4",
                ]


main = QuickBookGUIAPI() 
app, window = main.startup()

report_objects: List[Report] = []

for report in reports:
    report_objects.append(Report(str(report), None, Path(r"C:\Users\Derek\CFS - Derek\Programming\Python\Collections-V4\Ingest Data")))

report_saver = Reports(app, window)
report_saver.save(report_objects)

