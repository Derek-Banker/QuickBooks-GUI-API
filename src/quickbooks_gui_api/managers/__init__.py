# src\quickbooks_gui_api\managers\__init__.py

from .image import ImageManager
from .ocr import OCRManager
from .processes import ProcessManager
from .windows import WindowManager
from .string import StringManager


__all__ = [
           "ImageManager",
           "OCRManager",
           "ProcessManager",
           "WindowManager",
           "StringManager",
          ] 
