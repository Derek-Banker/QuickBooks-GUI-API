import logging
from pathlib import Path
import psutil

class ProcessManager:
    """
    Manages Windows processes. Can start, stop, and detect.
    Attributes:
        logger (logging.Logger): Logger instance for logging operations.
    """

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

    def is_running(self, *,
                   name: str | None = None,
                   path: Path | None = None) -> bool:
        """
        Check if any process with the given name or executable path is running.

        :param name: The name of the process to target
        :type name: str
        :param location: The path to the process to target.
        :type location: Path

        :returns: The success status.  
        :rtype: bool


    
        """
        if not name and not path:
            self.logger.debug("No name or location provided to is_running()")
            return False

        name = name.lower() if name else None
        path = str(path).lower() if path else None

        for process in psutil.process_iter(['name', 'exe']):
            info = process.info
            try:
                if name and info.get('name') and info['name'].lower() == name:
                    self.logger.debug(f"Found running process by name: {name}")
                    return True
                if path and info.get('exe') and info['exe'].lower() == path:
                    self.logger.debug(f"Found running process by path: {path}")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # process exited or no permission, skip
                continue

        self.logger.debug(f"No matching process found (name={name}, path={path})")
        return False

    def start(self, location: Path | None) -> bool:
        """
        Attempts to start the process at the given location.

        :param location: The path to the process to target.
        :type location: Path

        :returns: The success status.  
        :rtype: bool        
        """
        if location is None:
            self.logger.error("No location provided to start()")
            return False

        exe = str(location)
        if not location.exists():
            self.logger.error(f"Executable not found: {exe}")
            return False

        try:
            proc = psutil.Popen([exe])
            self.logger.info(f"Started process {exe} (PID {proc.pid})")
            return True
        except Exception:
            self.logger.exception(f"Failed to start process: {exe}")
            return False

    def terminate(self,
                  name: str | None = None,
                  location: Path | None = None) -> bool:
        """
        Terminate all running processes matching the given name or path.
        Returns True if at least one process was terminated.

        :param name: The name of the process to target
        :type name: str
        :param location: The path to the process to target.
        :type location: Path

        :returns: The success status.  
        :rtype: bool         
        """
        if not name and not location:
            self.logger.debug("No name or location provided to terminate()")
            return False

        name = name.lower() if name else None
        path = str(location).lower() if location else None

        found_any = False
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            info = proc.info
            try:
                match = (
                    (name and info.get('name') and info['name'].lower() == name)
                    or
                    (path and info.get('exe') and info['exe'].lower() == path)
                )
                if not match:
                    continue

                found_any = True
                p = psutil.Process(info['pid'])
                self.logger.info(f"Terminating PID {p.pid} ({info.get('name')})")
                p.terminate()
                try:
                    p.wait(timeout=5)
                except psutil.TimeoutExpired:
                    self.logger.warning(f"PID {p.pid} did not exit; killing")
                    p.kill()
                    p.wait()

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # already gone or cannot terminate, skip
                continue
            except Exception:
                self.logger.exception(f"Error terminating PID {info.get('pid')}")
                continue

        if not found_any:
            self.logger.debug(f"No processes matched (name={name}, path={path})")
        return found_any
