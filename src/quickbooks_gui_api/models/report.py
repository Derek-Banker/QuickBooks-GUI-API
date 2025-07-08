# src\quickbooks_gui_api\models\report.py

class Report:
    def __init__(self,
                 name: str,
                 file_name: str | None,
                ) -> None:
        self._name: str = name
        
        if file_name is None:
            self._file_name: str = name
        else:
            self._file_name: str = file_name

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def file_name(self) -> str:
        return self._file_name

    