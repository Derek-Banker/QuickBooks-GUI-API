# src\quickbooks_gui_api\__init__.py

from importlib.metadata import version as _version

from .gui_api import QuickBookGUIAPI
from .config_init import ConfigInit

__version__ = _version("qb-gui-api")

__all__ = [
           "QuickBookGUIAPI",
           "ConfigInit",
           "__version__",
          ]