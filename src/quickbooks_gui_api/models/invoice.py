# src\quickbooks_gui_api\models\invoice.py

from pathlib import Path
from quickbooks_gui_api.utilities import sanitize_file_name, ensure_file_extension

class Invoice:
    def __init__(self,
                 number: str,
                 file_name: str | None,
                 save_directory: Path
                ) -> None:
        self._number:           str  = number
        self._file_name:        str  = sanitize_file_name( file_name if file_name is not None else number)
        self._save_directory:   Path = save_directory
        

    @property
    def number(self) -> str:
        return self._number
    
    @property
    def file_name(self) -> str:
        return self._file_name
    
    def export_path(self) -> Path:
        return ensure_file_extension(self._save_directory.joinpath(self._file_name),["pdf"])
