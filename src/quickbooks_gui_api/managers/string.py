# src\quickbooks_gui_api\managers\string.py

import logging

from rapidfuzz import fuzz
from typing import Tuple, overload


class StringManager:

    def __init__(
        self, 
        logger: logging.Logger | None = None
    ) -> None:
        if logger is None:
            self.logger = logging.getLogger(__name__)
        elif isinstance(logger, logging.Logger):
            self.logger = logger
        else:
            raise TypeError("Provided parameter `logger` is not an instance of `logging.Logger`.")

    def rank_matches(
            self, 
            options: list[str] , 
            target: str, 
            first_past_post: bool = False,
            match_threshold: float = 100,
            ) -> list[Tuple[str,float]]:
        
        results: list[Tuple[str,float]] = [] 
        
        for string in options:
            confidence = fuzz.ratio(string,target)
            self.logger.debug("Comparing '%s' to '%s': Score = %f", string, target, confidence)
            
            results.append((string,confidence))
            if (first_past_post and (confidence >= match_threshold)):
                return results

        return results
    
    def match(
            self, 
            input: str, 
            target: str
            ) -> float:
        return fuzz.ratio(input,target)
        
    @overload        
    def is_match(self,threshold: float = 100,*,input: str, target: str,) -> bool: ...

    @overload
    def is_match(self, threshold: float = 100.00, *, ranked: Tuple[str,float]) -> bool:...
    
    def is_match(
        self,
        threshold: float = 100,
        *,
        input: str | None = None,
        target: str | None = None,
        ranked: Tuple[str, float] | None = None,
    ) -> bool:
        """
        Determines if the similarity between two strings or a ranked match meets a specified threshold.
    
        :param threshold: The minimum similarity score required to consider a match. Defaults to 100.
        :type threshold: float = 100
        :param input: The input string to compare.
        :type input: str | None = None
        :param target: The target string to compare against.
        :type target: str | None = None
        :param ranked: A tuple containing a string and its associated similarity score.
        :type ranked: Tuple[str, float] | None = None
        :returns:  True if the similarity score meets or exceeds the threshold, False otherwise. If 'ranked' is provided, returns the comparison result based on its score.
        :rtype: bool
        Raises:
            ValueError: If neither ('input' and 'target') nor 'ranked' are provided.
        """

        if ranked is not None:
            return ranked[1] >= threshold
        
        elif input is not None and target is not None:
            confidence = fuzz.ratio(input, target)
            return confidence >= threshold
        
        else:
            raise ValueError("Either 'input' and 'target', or 'ranked' must be provided.")
        
        
    def is_match_in_list(
            self,
            target: str,
            input: list[str],  
            threshold: float = 100,
        ) -> bool:
        """
        Determines if the similarity between two strings or a ranked match meets a specified threshold.
    
        :param target: The target string to compare against.
        :type target: str | None = None
        :param threshold: The minimum similarity score required to consider a match. Defaults to 100.
        :type threshold: float = 100
        :param input: List of strings to compare against.
        :type input: str | None = None
        :returns:  True if the similarity score meets or exceeds the threshold, False otherwise. If 'ranked' is provided, returns the comparison result based on its score.
        :rtype: bool
        Raises:
            ValueError: If neither ('input' and 'target') nor 'ranked' are provided.
        """

        for string in input:
            if fuzz.ratio(string, target) >= threshold:
                return True
        
        return False
    

        
