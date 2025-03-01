"""Mobile vAIn package for handling mobile device interactions."""

import warnings

warnings.warn(
    "The 'mobile_vAIn' package has been renamed to 'mobile_vain'. "
    "Please update your imports to use 'mobile_vain' instead. "
    "This import path will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2
)

from mobile_vain import *  # Forward imports from the new package
