import logging
from pathlib import Path

from typing import List, Dict, Any, overload

from .managers import ImageManager, OCRManager, ProcessManager, WindowManager



class QuickBookGUIAPI:

    def __init__(self,
                 logger: logging.Logger | None = None
                 ) -> None:
        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            if isinstance(logger, logging.Logger):
                self.logger = logger 
            else:
                raise TypeError("Provided parameter `logger` is not an instance of `logging.Logger`.")

    # def startup(self,
    #             username: str,
    #             password: str,
    #             exe_path: Path,
    #             version: str
    #            ) -> bool:
        

    # def kill_additional(self)
