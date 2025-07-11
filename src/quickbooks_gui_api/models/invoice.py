# src\quickbooks_gui_api\models\invoice.py

from pathlib import Path
from quickbooks_gui_api.utilities import sanitize_file_name

class Invoice:
    def __init__(self,
                 number: str,
                 file_name: str | None,
                 save_path: Path
                ) -> None:
        self._number:       str  = number
        self._file_name:    str  = sanitize_file_name( file_name if file_name is not None else number) + ".pdf"
        self._save_path:    Path = save_path
        

    @property
    def number(self) -> str:
        return self._number
    
    @property
    def file_name(self) -> str:
        return self._file_name
    
    def export_path(self) -> Path:
        return self._save_path.joinpath(self._file_name)
