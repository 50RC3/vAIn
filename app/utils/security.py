from requests import Session
from typing import Optional, Union, Any

class SecureSession(Session):
    """Session class that enforces SSL verification."""
    
    def request(
        self,
        method: str,
        url: str,
        verify: Union[bool, str] = True,
        **kwargs: Any
    ) -> Any:
        """Override request method to enforce SSL verification."""
        # Force verify to True regardless of what's passed
        return super().request(method, url, verify=True, **kwargs)
