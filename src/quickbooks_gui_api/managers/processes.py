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

    def is_running(self,
                   *,
                   name: str | None = None,
                   path: Path | None = None
                   ) -> bool:
        """
        Check if any process with the given name or executable path is running.

        :param name: The name of the process to target.
        :param path: The full executable path to target.
        :returns: True if running, False otherwise.
        """
        if not (name or path):
            self.logger.debug("No name or path provided to is_running()")
            return False

        name = name.lower() if name else None
        path_str = str(path).lower() if path else None

        for proc in psutil.process_iter(['name', 'exe']):
            try:
                info = proc.info
                proc_name = info.get('name', '') or ''
                proc_exe  = info.get('exe', '')  or ''

                if name and proc_name.lower() == name:
                    self.logger.debug("Found process by name: %s", name)
                    return True

                if path_str and proc_exe.lower() == path_str:
                    self.logger.debug("Found process by path: %s", path_str)
                    return True

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # that process disappeared or we can’t inspect it — skip it
                continue

        self.logger.debug("No matching process found (name=%s, path=%s)", name, path)
        return False

    def start(self, path: Path | None) -> bool:
        """
        Attempts to start the process at the given location.

        :param location: The path to the process to target.
        :type location: Path

        :returns: The success status.  
        :rtype: bool        
        """
        if path is None:
            self.logger.error("No location provided to start()")
            return False

        exe = str(path)
        if not path.exists():
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
                self.logger.debug(f"Terminating PID {p.pid} ({info.get('name')})")
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
