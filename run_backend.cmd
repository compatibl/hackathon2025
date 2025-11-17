@echo off
setlocal

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

REM Check if MongoDB is running
echo Checking MongoDB status...

powershell -NoLogo -NoProfile -Command "try { $null = [System.Net.Sockets.TcpClient]::new('localhost', 27017); Write-Host 'MongoDB port 27017 is accessible' -ForegroundColor Green; exit 0 } catch { Write-Host 'MongoDB port 27017 not accessible' -ForegroundColor Yellow; exit 1 }"

if %errorlevel%==0 (
    echo MongoDB is running.
    goto MONGODB_READY
)

echo MongoDB not detected. Starting MongoDB server in separate window...
start "MongoDB Server" run_mongodb.cmd
echo MongoDB startup initiated in separate window. Waiting for it to be ready...

REM Wait a bit for MongoDB to start
timeout /t 3 /nobreak >nul

REM Check again if MongoDB is now running with timeout
echo Waiting for MongoDB to start...
set /a attempts=0
:WAIT_FOR_MONGODB
set /a attempts+=1
if %attempts% gtr 30 (
    echo ERROR: MongoDB failed to start after 60 seconds. Please check the MongoDB window.
    echo.
    echo You can also:
    echo 1. Check if MongoDB is already running in another window
    echo 2. Manually start MongoDB with: run_mongodb.cmd
    echo 3. Press any key to continue anyway...
    pause
    goto MONGODB_READY
)

REM Check if MongoDB is now running
powershell -NoLogo -NoProfile -Command "try { $null = [System.Net.Sockets.TcpClient]::new('localhost', 27017); Write-Host 'MongoDB port 27017 is accessible' -ForegroundColor Green; exit 0 } catch { Write-Host 'MongoDB port 27017 not accessible' -ForegroundColor Yellow; exit 1 }"

if "%ERRORLEVEL%"=="0" (
    echo MongoDB is now running.
    goto MONGODB_READY
)

echo Waiting for MongoDB to start... (attempt %attempts%/30, retrying in 2 seconds)
timeout /t 2 /nobreak >nul
goto WAIT_FOR_MONGODB

:MONGODB_READY
echo MongoDB is ready.
echo.

echo Activating virtual environment...
call .venv\Scripts\activate.bat

set PYTHONPATH=.\runtime;.\convince;.\hackathon;%PYTHONPATH%

REM Check if TypeInfo.csv exists
echo.
echo Checking TypeInfo.csv...
if not exist "resources\bootstrap\TypeInfo.csv" (
    echo TypeInfo.csv not found. Initializing type information...
    echo.
    python -m tools.cl.runtime.init_type_info
    if errorlevel 1 (
        echo WARNING: Failed to initialize type information.
        echo Continuing with backend startup...
    ) else (
        echo Type information initialized successfully.
    )
    echo.
) else (
    echo TypeInfo.csv found.
)

if /I "%1"=="auth" (
    set CL_AUTH_ENABLED=true
)
TITLE Hackathon Build Server (DEV)
echo Starting backend...
python -m cl.runtime

echo.
echo Backend stopped. Deactivating .venv...
call .venv\Scripts\deactivate.bat
echo.
echo Note: MongoDB is still running in a separate window.
echo To stop MongoDB, close the MongoDB Server window or run: taskkill /f /im mongod.exe
