# src\quickbooks_gui_api\managers\helper.py

import logging
import pywinauto

from typing                         import Dict, Any, Literal
from pywinauto                      import WindowSpecification
from pywinauto.controls.uiawrapper  import UIAWrapper

from quickbooks_gui_api.managers    import image, ocr, string, window
from quickbooks_gui_api.models      import Image


class Helper:
    """
    Acts as a wrapper for the other managers.
    Attributes:
        logger (logging.Logger): Logger instance for logging operations.
    """

    def __init__(self, logger: logging.Logger | None = None) -> None:
        if logger is None:
            self.logger = logging.getLogger(__name__)
        elif isinstance(logger, logging.Logger):
            self.logger = logger
        else:
            raise TypeError("Provided parameter `logger` is not an instance of `logging.Logger`.")
        
        self.img_man = image.ImageManager() 
        self.str_man = string.StringManager()
        self.win_man = window.WindowManager()
        self.ocr_man = ocr.OCRManager() 

    def capture_element(
            self,
            element: UIAWrapper | WindowSpecification | None = None,
            *,
            root: WindowSpecification | None = None,
            **child_kwargs: Dict[str, Any],
        ) -> Image:
        """
        Captures the specified elements as a screenshot.

        :param element:         pywinauto WindowSpecification instance.
        :type  element:         pywinauto.WindowSpecification | pywinauto.controls.uiawrapper.UIAWrapper
        :param root:            Parent element for creating an element from parameters.
        :type  root:            pywinauto.WindowSpecification
        :param child_kwargs:    Parameters for creating an element. 
        :type  child_kwargs:    Dict[str, Any]
        """
        if element is None:
                if root is None or not child_kwargs:
                    raise ValueError(
                        "Must provide either `element` or (`root` + child_window criteria)"
                    )
                element = root.child_window(**child_kwargs)

        try:
            element.set_focus()
        except Exception:
            pass

        size, pos = self.win_man.rect_to_size_pos(element.rectangle())

        return self.img_man.capture(size, pos)
        




    def capture_isolate_ocr_match(
            self,
            element: UIAWrapper | WindowSpecification | None = None,
            *,
            single_or_multi: Literal["single", "multi"],
            color: image.Color, 
            tolerance: float = 0.0,
            min_size: tuple[int | None, int | None] = (None, None) ,
            min_area: int | None = None,
            target_text: str,
            match_threshold: float = 100.0,
            root: pywinauto.WindowSpecification | None = None,
            **child_kwargs: dict[str, Any],
        ) -> tuple [ bool , str , float]:
        """
        Wrapper function to encapsulate the managers into a single cohesive function.
        Locates element, captures it, isolates it, OCR's it, then match's it.

        :param element:         pywinauto WindowSpecification instance.
        :type  element:         pywinauto.WindowSpecification | pywinauto.controls.uiawrapper.UIAWrapper
        :param root:            Parent element for creating an element from parameters.
        :type  root:            pywinauto.WindowSpecification
        :param child_kwargs:    Parameters for creating an element. 
        :type  child_kwargs:    Dict[str, Any]
        :param single_or_multi: If isolation should be preformed on a single or multiple regions. 
        :type  single_or_multi: bool
        :param tolerance:       Allowable color variance for color region isolation.
        :type  tolerance:       float = 0.0
        :param color:           The color to isolate.
        :type  color:           image.Color
        :param min_size:        Minimum allowable size for isolated regions. Used with multi-region isolation.
        :type  min_size:        tuple[int | None, int | None] = (None, None) 
        :param min_area:        Minimum allowable area for isolated regions. Used with multi-region isolation.
        :type  min_area:        int | None = None
        :param target_text:     The target text to compare the OCR'd text against.
        :type  target_text:     str
        :param match_threshold: The match confidence needed to pass.
        :type  match_threshold: float = 100.0
        :returns: Result of match, OCR'd text, match confidence. 
        :rtype: tuple [ bool , str , float]
        """
            
        if element is None:
            if root is None or not child_kwargs:
                raise ValueError(
                    "Must provide either `element` or (`root` + child_window criteria)"
                )
            element = root.child_window(**child_kwargs)

        try:
            element.set_focus()
        except Exception:
            pass

        capture = self.capture_element(element)

        if single_or_multi == "single":
            isolated = self.img_man.isolate_region(capture, color, tolerance)
            pulled_text = self.ocr_man.get_text(isolated)

        elif single_or_multi == "multi":
            isolated = self.img_man.isolate_multiple_regions(capture, color, tolerance, min_area=min_area, min_size=min_size)

            if len(isolated) > 1:
                    raise ValueError("Multiple images are returned as a results of the multi-isolation. Cannot OCR and match all. Refine parameters.")
            else: 
                pulled_text = self.ocr_man.get_text(isolated[0])

        else:
            raise ValueError(f"Invalid parameter state. single_or_multi: Literal['single', 'multi'] = `{single_or_multi}`.")

        match_confidence = self.str_man.match(pulled_text, target_text)

        return match_confidence >= match_threshold, pulled_text, match_confidence
    
    def safely_set_text(
            self,
            text: str,
            element: WindowSpecification | None = None,
            *,
            root: WindowSpecification | None = None,
            wait_time: float = 2.0,
            # wait_parameters: str = "exists enabled visible ready",
            **child_kwargs: Dict[str, Any],
        ) -> None:

        if element is None:
            if root is None or not child_kwargs:
                raise ValueError(
                    "Must provide either `element` or (`root` + child_window criteria)"
                )
            element = root.child_window(**child_kwargs)

        try:
            element.set_focus()
        except Exception:
            pass
        
        if self.win_man.is_element_active(element,timeout= wait_time):
            element.set_text(text)  
        else:
            raise

    def await_element(
            self,
            element: WindowSpecification | None = None,
            *,
            root: WindowSpecification | None = None,
            wait_time: float = 2.0,
            wait_parameters: str = "exists enabled visible ready",
            **child_kwargs: Dict[str, Any],
        ) -> None:
    
        if element is None:
            if root is None or not child_kwargs:
                raise ValueError(
                    "Must provide either `element` or (`root` + child_window criteria)"
                )
            element = root.child_window(**child_kwargs)

        try:
            element.set_focus()
        except Exception:
            pass

        element.wait(wait_parameters, wait_time)
