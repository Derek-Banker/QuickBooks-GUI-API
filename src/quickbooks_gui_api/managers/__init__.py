# src\quickbooks_gui_api\managers\__init__.py

from src.quickbooks_gui_api.managers.image      import ImageManager
from src.quickbooks_gui_api.managers.ocr        import OCRManager
from src.quickbooks_gui_api.managers.processes  import ProcessManager
from src.quickbooks_gui_api.managers.windows    import WindowManager


__all__ = [
           "ImageManager",
           "OCRManager",
           "ProcessManager",
           "WindowManager"
          ] 
