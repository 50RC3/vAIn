"""
Custom exceptions for vAIn core functionality.

This module contains essential custom exceptions used throughout the vAIn platform
for proper error handling and reporting.
"""

class ModuleInitializationError(Exception):
    """Raised when a module fails to initialize properly or its dependencies cannot be satisfied."""

class ConfigurationError(Exception):
    """Raised when configuration loading or validation fails."""

class MemoryManagementError(Exception):
    """Raised when memory operations fail."""

# Note: Removed NetworkError (use built-in ConnectionError instead)
# Note: Merged ModuleDependencyError into ModuleInitializationError
# Note: Removed DependencyValidationError as it overlapped with ModuleInitializationError
