import pytesseract
import logging

from typing import List, Dict

from quickbooks_gui_api.models import Image

class OCRManager:
    """
    Uses `pytesseract` to for OCR functionality. Used to Verify on scree information.
    Attributes:
        logger (logging.Logger): Logger instance for logging operations.
    """

    def __init__(self,
                 logger: logging.Logger | None = None
                 ) -> None:
        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            if isinstance(logger, logging.Logger):
                self.logger = logger 
            else:
                raise TypeError("Provided parameter `logger` is not an instance of `logging.Logger`.")
            
    def get_text(
            self, 
            image: Image,
            config: str = ""
        ) ->  str:
        """ 
        Attempts to pull pull text from the provided image.

        :param image: The image to process.
        :type image: Image
        :param config: Extension of pytesseract's config parameter.
        :type config: str = ""
        """
        try:
            text = pytesseract.image_to_string(image.img, config=config)
            self.logger.debug("Extracted text: %s", text)
            return text
        except Exception as e:
            self.logger.error("OCR failed: %s", e)
            raise
    
    def get_multi_text(
            self, 
            images: List[Image],
            config: str = ""
        ) ->  Dict[Image,str]:
        """
        Attempts to pull text from the provided images.

        :param image: The images to process.
        :type image: List[Image]
        :param config: Extension of pytesseract's config parameter.
        :type config: str = ""
        """
        results: Dict[Image, str] = {}
        for img in images:
            try:
                results[img] = self.get_text(img, config=config)
            except Exception:
                results[img] = ""
        return results
