import re
from typing import Any, Dict

def safe_xmlattr(d: Dict[str, Any]) -> str:
    """
    Safe version of xmlattr filter that sanitizes attribute keys.
    Only allows alphanumeric characters and dashes/underscores in keys.
    """
    valid_key_pattern = re.compile(r'^[a-zA-Z0-9_-]+$')
    result = []
    
    for key, value in d.items():
        # Only process keys that match our safe pattern
        if valid_key_pattern.match(key):
            if value is True:
                result.append(key)
            elif value is False or value is None:
                continue
            else:
                result.append(f'{key}="{str(value)}"')
                
    return ' '.join(result)
