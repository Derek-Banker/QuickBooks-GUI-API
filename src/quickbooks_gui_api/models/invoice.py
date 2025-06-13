# src\quickbooks_gui_api\models\invoice.py

class Invoice:
    def __init__(self,
                 number: str,
                 file_name: str | None,
                ) -> None:
        self._number: str = number
        
        if file_name is None:
            self._file_name: str = number
        else:
            self._file_name: str = file_name

    @property
    def number(self) -> str:
        return self._number
    
    @property
    def file_name(self) -> str:
        return self._file_name
