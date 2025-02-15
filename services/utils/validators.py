from typing import Dict, Any, Optional
from pydantic import ValidationError
import ipaddress

def validate_task_parameters(parameters: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate task parameters.
    Returns (is_valid, error_message)
    """
    try:
        if not isinstance(parameters, dict):
            return False, "Parameters must be a dictionary"
        
        # Check for required fields
        required_fields = ["task_type", "input_data"]
        missing = [field for field in required_fields if field not in parameters]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
            
        return True, None
    except Exception as e:
        return False, str(e)

def validate_ip_address(ip: str) -> bool:
    """Validate IP address format"""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def validate_port(port: int) -> bool:
    """Validate port number"""
    return isinstance(port, int) and 1 <= port <= 65535

def validate_node_id(node_id: str) -> bool:
    """Validate node ID format"""
    return bool(node_id and isinstance(node_id, str) and len(node_id) <= 64)
