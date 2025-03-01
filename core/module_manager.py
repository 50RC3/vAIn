"""
Module manager for handling service initialization and dependencies.

This module provides the core dependency injection and service management functionality
for the vAIn platform. It handles module registration, dependency validation, and
runtime status tracking of all system components.

Classes:
    ModuleManager: Core class for managing service modules and their dependencies.
"""

from typing import Dict, Any, Optional
from logging_config import get_logger
from .exceptions import ModuleInitializationError, ModuleDependencyError

logger = get_logger("core.module_manager")

class ModuleManager:
    """Manages service modules and their dependencies."""
    
    def __init__(self):
        self._modules: Dict[str, Any] = {}
        self._dependencies: Dict[str, list] = {}
        self._status: Dict[str, bool] = {}
        
    def register_module(self, name: str, module: Any, dependencies: Optional[list] = None) -> None:
        """Register a module with optional dependencies"""
        try:
            self._modules[name] = module
            self._dependencies[name] = dependencies or []
            self._status[name] = True
            logger.info(f"Module {name} registered successfully")
        except Exception as e:
            self._status[name] = False
            logger.error(f"Failed to register module {name}: {str(e)}")
            raise ModuleInitializationError(f"Module registration failed: {str(e)}")
        
    def get_module(self, name: str) -> Any:
        """Get a registered module by name."""
        return self._modules.get(name)
        
    def validate_dependencies(self) -> bool:
        """Validate that all module dependencies are satisfied."""
        try:
            for module, deps in self._dependencies.items():
                for dep in deps:
                    if dep not in self._modules or not self._status[dep]:
                        raise DependencyValidationError(
                            f"Module {module} dependency {dep} not satisfied"
                        )
            return True
        except Exception as e:
            logger.error(f"Dependency validation failed: {str(e)}")
            return False
        
    def get_module_status(self) -> Dict[str, str]:
        """Get status of all registered modules."""
        return {name: "active" if module else "inactive" 
                for name, module in self._modules.items()}
