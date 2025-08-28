# logger_factory.py

# utilities
import os
from datetime import datetime
from loguru import logger as _logger
from loguru._logger import Logger
from typing import Literal

class LogManager:
    _configured = False

    @classmethod
    def _configure(
        cls,
        file_name: str,
        log_dir: str,
        archive_subdir: str,
        archive_retention: int,
        log_level: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"] = "DEBUG",
    ) -> None:
        archive_dir = os.path.join(log_dir, archive_subdir)
        os.makedirs(archive_dir, exist_ok=True)

        for fn in os.listdir(log_dir):
            if fn.startswith(f"LATEST_{file_name}_") and fn.endswith(".log"):
                os.remove(os.path.join(log_dir, fn))

        now = datetime.now()
        ts  = now.strftime("%Y-%m-%d_%H-%M-%S_") + f"{now.microsecond//1000:03d}"

        _logger.add(
            os.path.join(
                archive_dir,
                f"{file_name}" + "_{time:YYYY-MM-DD_HH-mm-ss}.log"
            ),
            retention=archive_retention,
            compression=None,
            level=log_level
        )
        _logger.add(
            os.path.join(log_dir, f"LATEST_{file_name}_{ts}.log"),
            mode="w",
            backtrace=True,
            diagnose=False,
            level=log_level
        )
        cls._configured = True

    @classmethod
    def get_logger(
        cls,
        module_name: str | None = None,
        *,
        log_level: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"] = "DEBUG",   
        file_name: str = "Log",
        log_dir: str = "Logs",
        archive_subdir: str = "Old Logs",
        archive_retention: int = 5,
    ) -> Logger:
        if not cls._configured:
            cls._configure(file_name, log_dir, archive_subdir, archive_retention, log_level)
        return _logger.bind(module=module_name) if module_name else _logger # type: ignore