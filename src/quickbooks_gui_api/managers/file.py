# src\quickbooks_gui_api\managers\file.py

import logging

import time

from pathlib import Path
from typing import Any


class FileManager:

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
            
    def is_locked(
            self, 
            path: Path
        ) -> bool:
        """
        Detects if the file at the provided path is locked, i.e. in use.

        :param path: Path instance pointing to the file. 
        :type  path: Path
        """
        
    def wait_for_file(
            self,
            path: Path, 
            max_time: float = 60.0, 
            poll_frequency: float = 0.5
        ) -> bool:
        """
        Waits for a file to exist.
        
        :param path: Path instance pointing to the file. 
        :type  path: Path
        :param max_time: The maximum amount of time the function is allowed to wait. 
        :type  max_time: float = 60.0
        :param poll_frequency: How often the to check for the file.
        :type  poll_frequency: float = 0.5
        """

    def wait_till_stable(
            self, 
            path: Path, 
            max_time: float = 60.0, 
            poll_frequency: float = 1.0
        ) -> None:
        """
        Waits for a file to be stable. Not locked or being changed.

        :param path: Path instance pointing to the file. 
        :type  path: Path
        :param max_time: The maximum amount of time the function is allowed to wait. 
        :type  max_time: float = 60.0
        :param poll_frequency: How often the to check the file.
        :type  poll_frequency: float = 0.5
        """
        if not path.is_file():
            raise TypeError("The provided path does not pass Path.is_file().")
        if not path.exists():
            raise TypeError("The provided path does not pass Path.exists().")