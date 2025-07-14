# src\quickbooks_gui_api\models\element.py

from typing import Literal

from pywinauto import WindowSpecification

class Element:
    def __init__(
            self,
            control_type:   Literal["Window", "Edit", "Pane", "Button"] | None = None,
            title:          str | None = None,
            auto_id:        str | int | None = None,
            parent:         WindowSpecification | None = None
        ) -> None:
    
        self._control_type  = control_type
        self._title         = title
        self._auto_id       = str(auto_id)
        self._parent        = parent
        
        self._as_element: WindowSpecification | None = None

    def __str__(self) -> str:
        return f"{{control_type: `{self._control_type}`, title: `{self._title}`, auto_id: `{self._auto_id}`}}"

    @property
    def control_type(self) -> str | None:
        return self._control_type
    
    @property
    def title(self) -> str | None:
        return self._title
    
    @property
    def auto_id(self) -> str | None:
        return self._auto_id

    @property
    def kwargs(self) -> dict[str, str]:
        mapping = {
            "control_type": self._control_type,
            "title":        self._title,
            "auto_id":      self._auto_id,
        }
        # remove any entries whose value is None, "", or the literal "None"
        return {
            key: value
            for key, value in mapping.items()
            if value not in (None, "", "None")
        }
    
    def as_element(self, parent: WindowSpecification | None = None) -> WindowSpecification:

        if self._as_element is None:    
            if parent is None:
                if self._parent is not None:
                    parent = self._parent
                else:
                    raise    
                
            self._as_element = parent.child_window(**self.kwargs)

        return self._as_element
        

