# src\quickbooks_gui_api\models\report.py

from pathlib import Path
from quickbooks_gui_api.utilities import sanitize_file_name

class Report:
    def __init__(self,
                 name: str,
                 file_name: str | None,
                 save_path: Path
                ) -> None:
        self._name:         str  = name
        self._file_name:    str  = sanitize_file_name( file_name if file_name is not None else name) + ".csv"
        self._save_path:    Path = save_path
        

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def file_name(self) -> str:
        return self._file_name
    
    def export_path(self) -> Path:
        return self._save_path.joinpath(self._file_name)

    