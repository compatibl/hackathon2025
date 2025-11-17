@echo off
setlocal

REM Set Python path for runtime modules
set "PYTHONPATH=.\runtime;.\convince;.\hackathon;%PYTHONPATH%"
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
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)

echo.
echo Initializing database...
python -m tools.cl.runtime.init_db
if errorlevel 1 (
    echo ERROR: Database initialization failed.
    pause
    exit /b 1
)

echo.
echo Database initialized successfully.
echo Deactivating virtual environment...
call .venv\Scripts\deactivate.bat

echo.
echo Database initialization completed.
