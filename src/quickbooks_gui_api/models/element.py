# src\quickbooks_gui_api\models\element.py

from dataclasses import dataclass
from typing import Literal

@dataclass
class Element:
    def __init__(
            self,
            control_type:   Literal["Window", "Edit", "Pane", "Button"] | None = None,
            title:          str | None = None,
            auto_id:        str | None = None
        ) -> None:
    
        self._control_type  = control_type
        self._title         = title
        self._auto_id       = auto_id

    @property
    def control_type(self) -> str | None:
        return self._control_type
    
    @property
    def title(self) -> str | None:
        return self._title
    
    @property
    def auto_id(self) -> str | None:
        return self._auto_id

    