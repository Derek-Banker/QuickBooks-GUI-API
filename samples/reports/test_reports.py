# --- BOILER --------------------------------------------------------------------
import time
from pathlib import Path

from quickbooks_gui_api.utilities import LogManager
logger = LogManager.get_logger(__name__)
# --- BOILER --------------------------------------------------------------------

from quickbooks_gui_api import ConfigInit
from quickbooks_gui_api import QuickBookGUIAPI
from quickbooks_gui_api.apis import Reports
from quickbooks_gui_api.models import Report

USERNAME = ""
PASSWORD = ""



save_path = Path(r"C:\Users\Derek\CFS - Derek\Programming\Python\Collections-V4\Ingest Data")

reports: list[Report] = [
                         Report("Data Export - All Invoices - 00001-11999", "STOPGAP - 1.CSV",                          save_path),
                         Report("Data Export - All Invoices - 12000-99999", "STOPGAP - 2.CSV",                          save_path),
                         Report("Data Export - All Customers - V 4",        "Data Export - All Customers & Jobs.CSV",   save_path)
                        ]

# If you have not already initalized the config you have to run this before the first run or after any config directory changes. 
# ConfigInit(logger=logger)

main = QuickBookGUIAPI() 
app, window = main.startup(USERNAME, PASSWORD)
report_saver = Reports(app, window, logger=logger)
report_saver.save(reports)


