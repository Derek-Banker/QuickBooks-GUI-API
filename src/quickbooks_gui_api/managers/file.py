# src\quickbooks_gui_api\managers\file.py

import time
import msvcrt
import logging

from pathlib import Path



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
            
    def is_locked(self, path: Path) -> bool:
        """
        Detects if the file at the provided path is locked (in use) on Windows.

        :param path: Path instance pointing to the file.
        :raises TypeError: if `path` is not a Path, doesn't exist, or isn't a file
        :returns: True if the file is locked (another process holds it open), False otherwise.
        """
        if not isinstance(path, Path):
            raise TypeError("path must be a pathlib.Path")

        if not path.exists() or not path.is_file():
            raise TypeError("The provided path does not exist or is not a file.")

        try:
            # open for append (so we don't truncate) and try to lock a single byte
            with open(path, "a") as fh:
                msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)  # acquire non-blocking lock
                msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)  # release it immediately
            return False
        except OSError:
            # locking failed, so the file must be in use by another process
            return True
        except Exception:
            # on any other unexpected error, assume locked for safety
            self.logger.exception("Failed checking lock state for %s", path)
            return True
        
    def wait_for_file(
            self,
            path: Path,
            max_time: float = 60.0,
            poll_frequency: float = 0.5
        ) -> bool:
        """Wait for ``path`` to exist.

        The call will repeatedly poll ``path`` until it exists or the timeout is
        reached.  ``True`` is returned if the file appeared before the timeout,
        otherwise ``False``.

        :param path: Path instance pointing to the expected file location.
        :type  path: Path
        :param max_time: Maximum time to wait in seconds.
        :type  max_time: float = 60.0
        :param poll_frequency: Interval between existence checks in seconds.
        :type  poll_frequency: float = 0.5
        :returns: ``True`` if the file was found, ``False`` otherwise.
        :rtype: bool
        """

        end_time = time.monotonic() + max_time
        while time.monotonic() < end_time:
            if path.exists():
                return True
            time.sleep(poll_frequency)

        return False

    def wait_till_stable(
            self,
            path: Path,
            max_time: float = 60.0,
            poll_frequency: float = 1.0
        ) -> None:
        """Block until ``path`` is stable.

        Stability means the file exists, is not locked by another process and
        its size and modification time remain unchanged for at least one poll
        interval.  If the timeout is exceeded without reaching a stable state a
        ``TimeoutError`` is raised.

        :param path: Path instance pointing to the file.
        :type  path: Path
        :param max_time: Maximum time to wait for stability.
        :type  max_time: float = 60.0
        :param poll_frequency: Interval between checks.
        :type  poll_frequency: float = 1.0
        :raises TimeoutError: If the file does not become stable in time.
        """

        if not path.exists() or not path.is_file():
            raise TypeError("The provided path does not pass Path.exists() and Path.is_file().")

        prev_stat = path.stat()
        end_time = time.monotonic() + max_time

        while time.monotonic() < end_time:
            if self.is_locked(path):
                time.sleep(poll_frequency)
                prev_stat = path.stat()
                continue

            current_stat = path.stat()
            if (
                current_stat.st_size == prev_stat.st_size
                and current_stat.st_mtime == prev_stat.st_mtime
            ):
                return

            prev_stat = current_stat
            time.sleep(poll_frequency)

        raise TimeoutError(f"File {path} did not become stable within {max_time} seconds")
    
    def time_since_modified(self, path: Path) -> float:
        """Return seconds elapsed since ``path`` was last modified.

        :param path: Path instance pointing to the file.
        :type  path: Path
        :returns: Time since last modification in seconds.
        :rtype: float
        """

        if not path.exists() or not path.is_file():
            raise TypeError(
                "The provided path does not pass Path.exists() and Path.is_file()."
            )

        return time.time() - path.stat().st_mtime