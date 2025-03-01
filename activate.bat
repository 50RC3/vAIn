@echo off
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat 
    echo Virtual environment activated.
) else (
    echo Virtual environment not found.
    echo Creating new virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo Virtual environment created and activated.
    echo Installing requirements...
    pip install -r requirements.txt
)
