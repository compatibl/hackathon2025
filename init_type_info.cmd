@echo off

echo.
echo Checking virtual environment...
if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating one...
    echo.
    call init_venv.cmd R
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
    echo.
) else (
    echo Virtual environment found.
)


echo.
echo Activate .venv
call .venv\Scripts\activate.bat

set PYTHONPATH=.\runtime;.\convince;.\hackathon;%PYTHONPATH%

echo.
echo Regenerate Type Info
python -m tools.cl.runtime.init_type_info

echo.
echo Deactivate .venv
call .venv\Scripts\deactivate.bat
