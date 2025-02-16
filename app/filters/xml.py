import re
from typing import Any, Dict, List

from .config import VALID_ATTR_PATTERN

def safe_xmlattr(attributes: Dict[str, Any]) -> str:
    """
    Safely convert a dictionary to XML attributes string.
    
    Args:
        attributes: Dictionary of attribute names and values
        
    Returns:
        String of formatted XML attributes
        
    Example:
        >>> safe_xmlattr({'class': 'btn', 'disabled': True})
        'class="btn" disabled'
    """
    if not attributes:
        return ''
        
    result: List[str] = []
    
    for key, value in attributes.items():
        if not VALID_ATTR_PATTERN.match(key):
            continue
            
        if value is True:
            result.append(key)
        elif value is False or value is None:
            continue
        else:
            # Escape quotes in attribute values
            escaped_value = str(value).replace('"', '&quot;')
            result.append(f'{key}="{escaped_value}"')
                
    return ' '.join(result)
