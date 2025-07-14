

import os
import dotenv
import pytomlpp
from pathlib import Path
from typing import Dict, Any, Final
import logging

from toml_init import EncryptionManager, ConfigManager

UNINITIALIZED: Final[str] = "UNINITIALIZED"

cwd = Path(os.getcwd())

DEFAULT_CONFIG_FOLDER_PATH: Final[Path] = cwd.joinpath("configs")
DEFAULT_CONFIG_DEFAULT_FOLDER_PATH: Final[Path] = DEFAULT_CONFIG_FOLDER_PATH.joinpath("defaults")
DEFAULT_CONFIG_FILE_NAME: Final[str] = "config.toml"

class Setup:



    def __init__(
        self, 
        config_index: str = "QuickBooksGUIAPI.secrets", 
        logger: logging.Logger | None = None
    ) -> None:
        if logger is None:
            self.logger = logging.getLogger(__name__)
        elif isinstance(logger, logging.Logger):
            self.logger = logger
        else:
            raise TypeError("Provided parameter `logger` is not an instance of `logging.Logger`.")
        self.config_index = config_index

    def _get_local_key(self, 
                       local_key_name: str | None, 
                       local_key_value: str | None
                       ) -> str:
        if (local_key_name is None) == (local_key_value is None):
            raise ValueError("Exactly one of `local_key_name` or `local_key_value` must be provided.")
        if local_key_value is not None:
            return local_key_value
        dotenv.load_dotenv()
        key = os.getenv(local_key_name) # type: ignore
        if key is None:
            raise ValueError(f"Unable to retrieve environmental variable by the name `{local_key_name}`")
        return key

    def set_credentials(
        self,
        username: str,
        password: str,
        *,
        local_key_name: str | None = None,
        local_key_value: str | None = None,
        config_path: Path = Path(r"configs/config.toml")
    ) -> None:
        local_key = self._get_local_key(local_key_name, local_key_value)
        em = EncryptionManager()
        salt = em.generate_salt()
        fernet_key = em.derive_key(local_key, salt)
        local_key_hash = em.hash(local_key, salt)

        try:
            with open(config_path, "r") as f:
                data = pytomlpp.load(f)
        except FileNotFoundError:
            self.logger.warning(f"{config_path} not found. Creating new config file.")
            data = {self.config_index: {}}

        if self.config_index not in data:
            data[self.config_index] = {}

        data[self.config_index]["KEY_NAME"] = local_key_name
        data[self.config_index]["SALT"] = salt
        data[self.config_index]["HASH"] = local_key_hash
        data[self.config_index]["USERNAME"] = em.encrypt(username, fernet_key)
        data[self.config_index]["PASSWORD"] = em.encrypt(password, fernet_key)

        with open(config_path, "w") as f:
            pytomlpp.dump(data, f)

        self.logger.info("The encrypted values and checks have been written to the config file.")

    def verify_credentials(
        self,
        *,
        local_key_name: str | None = None,
        local_key_value: str | None = None,
        config_path: Path = Path(r"configs/config.toml")
    ) -> bool:
        local_key = self._get_local_key(local_key_name, local_key_value)
        try:
            config: Dict[Any, Any] = pytomlpp.load(config_path)
        except FileNotFoundError:
            self.logger.error(f"{config_path} not found.")
            return False

        section = config.get(self.config_index, {})
        config_hash = section.get("HASH", UNINITIALIZED)
        config_salt = section.get("SALT", UNINITIALIZED)
        config_encrypted_username = section.get("USERNAME", UNINITIALIZED)
        config_encrypted_password = section.get("PASSWORD", UNINITIALIZED)

        if any(val == UNINITIALIZED for val in [config_hash, config_salt, config_encrypted_username, config_encrypted_password]):
            self.logger.error("The config file contains `UNINITIALIZED`.")
            return False

        em = EncryptionManager()
        if em.hash(local_key, config_salt) == config_hash:
            self.logger.info("The provided key is valid.")
            return True
        else:
            self.logger.error("The provided key is INVALID.")
            return False

    

    def run(
        self,
        base_path: Path | None = None,
        defaults_path: Path | None = None,
        master_filename: str | None = None,
        logger: logging.Logger | None = None
    ):
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


