# src\quickbooks_gui_api\managers\__init__.py

from .image     import ImageManager, Color
from .ocr       import OCRManager
from .processes import ProcessManager
from .window    import WindowManager
from .string    import StringManager
from .file      import FileManager
from .helper    import Helper


__all__ = [
           "ImageManager",
           "Color",
           "OCRManager",
           "ProcessManager",
           "WindowManager",
           "StringManager",
           "FileManager",
           "Helper",
          ] 
