"""
Setup script for the mobile_vain package.
"""

from setuptools import setup, find_packages

setup(
    name="mobile_vain",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "grpcio>=1.54.2",
        "cryptography>=41.0.1",
        "fastapi>=0.68.1",
        "pydantic>=1.8.2",
    ],
    python_requires=">=3.8",
    package_data={
        "mobile_vain": ["py.typed"],
    },
    # Use extras_require to define optional dependencies.
    # For example, if later you want to offer extra features (e.g. a "dev" extra):
    # extras_require={
    #     "dev": ["pytest", "flake8"],
    # },
    description="vAIn mobile node implementation (formerly mobile_vAIn)",
)
