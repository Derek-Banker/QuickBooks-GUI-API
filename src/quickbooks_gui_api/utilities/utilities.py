import re 
import unicodedata

from pathlib import Path
from typing import Sequence

def sanitize_file_name(file_name: str) -> str:
    # 1. Normalize to Unicode NFKC
    name = unicodedata.normalize('NFKC', file_name)

    # 2. Replace illegal chars (incl. control chars) with underscore
    #    <>:"/\|?* and U+0000–U+001F
    name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', name)

    # 3. Strip trailing spaces or dots
    name = name.rstrip(' .')

    # 4. Avoid Windows reserved names
    if re.match(r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?$', name, re.IGNORECASE):
        name = "_" + name

    # 5. Truncate to 255 characters
    return name[:255] if len(name) > 255 else name

def ensure_file_extension(path: Path, valid_extensions: Sequence[str]) -> Path:
    """
    Ensure that the given `path` ends with one of `valid_extensions`.
    
    :param path:             A pathlib.Path pointing to a file (may or may not have an extension).
    :param valid_extensions: A sequence of extensions (with or without leading dots), e.g. ["txt", ".md", "csv"].
    :returns:                The original Path if its suffix is in the list, otherwise a new Path
                             with the first valid extension appended.
    :raises TypeError:       If `path` is not a Path or `valid_extensions` isn’t a sequence of strings.
    :raises ValueError:      If `valid_extensions` is empty.
    """
    # 1. Validate inputs
    if not isinstance(path, Path):
        raise TypeError(f"path must be a pathlib.Path, not {type(path).__name__}")
    if not isinstance(valid_extensions, Sequence):
        raise TypeError("valid_extensions must be a sequence of strings")
    if not valid_extensions:
        raise ValueError("valid_extensions must contain at least one extension")

    # 2. Normalize extensions to lowercase with leading dots
    normalized = []
    for ext in valid_extensions:
        if not isinstance(ext, str):
            raise TypeError("each extension must be a string")
        ext = ext if ext.startswith('.') else f'.{ext}'
        normalized.append(ext.lower())

    # 3. If the path already has a valid suffix, return it unchanged
    if path.suffix.lower() in normalized:
        return path

    # 4. Otherwise, append (or replace) with the first valid extension
    return path.with_suffix(normalized[0])