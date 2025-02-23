@echo off
SET VENV_DIR=venv

IF NOT EXIST %VENV_DIR% (
    echo Creating virtual environment...
    python -m venv %VENV_DIR%
    echo Virtual environment created.
)

echo Activating virtual environment...
call %VENV_DIR%\Scripts\activate.bat
echo Virtual environment activated.
