import re 
import unicodedata

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