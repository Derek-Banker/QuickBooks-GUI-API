

import os
from pathlib import Path
from typing import Any, Final
import logging

from toml_init import ConfigManager

UNINITIALIZED: Final[str] = "UNINITIALIZED"

cwd = Path(os.getcwd())

DEFAULT_CONFIG_FOLDER_PATH: Final[Path] = cwd.joinpath("configs")
DEFAULT_CONFIG_DEFAULT_FOLDER_PATH: Final[Path] = DEFAULT_CONFIG_FOLDER_PATH.joinpath("defaults")
DEFAULT_CONFIG_FILE_NAME: Final[str] = "config.toml"

class ConfigInit:

    def __init__(
            self,
            base_path: Path | None = None,
            defaults_path: Path | None = None,
            master_filename: str | None = None,
            logger: Any = logging.getLogger(__name__)
        ) -> None:
        
        self.logger = logger

        # Build dict only with non-None overrides
        kwargs = {}
        if base_path is not None:
            kwargs['base_path'] = base_path
        if defaults_path is not None:
            kwargs['defaults_path'] = defaults_path
        if master_filename is not None:
            kwargs['master_filename'] = master_filename
        if logger is not None:
            kwargs['logger'] = logger

        ConfigManager(**kwargs).initialize()
