# --- BOILER --------------------------------------------------------------------
import time
from pathlib import Path

from quickbooks_gui_api.utilities import LogManager
logger = LogManager.get_logger(__name__)
# --- BOILER --------------------------------------------------------------------

from quickbooks_gui_api import QuickBookGUIAPI
from quickbooks_gui_api.apis import Invoices
from quickbooks_gui_api.models import Invoice

USERNAME = ""
PASSWORD = ""

invoices: list =    [
                     5786,
                     8921,
                     11412,
                     15198,
                     16968,
                     17232,
                     17595,
                     17677,
                    ]

# If you have not already initalized the config you have to run this before the first run or after any config directory changes. 
# ConfigInit(logger=logger)

main = QuickBookGUIAPI() 
app, window = main.startup(USERNAME, PASSWORD)

invoice_objects: list[Invoice] = []

for invoice in invoices:
    invoice_objects.append(Invoice(str(invoice), None, Path(r"C:\Users\Derek\CFS - Derek\Holding")))

invoice_saver = Invoices(app, window, logger=logger)
invoice_saver.save(invoice_objects)

main.shutdown()

