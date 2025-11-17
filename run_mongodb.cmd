@echo off
setlocal

TITLE MongoDB Server (DEV)

REM Check if MongoDB is already running
echo Checking if MongoDB is already running...
echo.

REM Try to connect to MongoDB on default port 27017
powershell -NoLogo -NoProfile -Command "try { $null = [System.Net.Sockets.TcpClient]::new('localhost', 27017); Write-Host 'SUCCESS: MongoDB is already running on localhost:27017' -ForegroundColor Green; Write-Host 'No need to start a separate local MongoDB server.' -ForegroundColor Yellow; exit 0 } catch { Write-Host 'INFO: No MongoDB server detected on localhost:27017' -ForegroundColor Cyan; exit 1 }" >nul 2>&1

if %errorlevel%==0 (
  echo.
  echo MongoDB is already running and accessible.
  echo You can proceed with your application setup.
  echo.
  echo Press any key to close this window...
  pause >nul
  exit /b 0
)

echo Starting local MongoDB server...
echo.

REM Configuration
set "MONGO_VERSION=7.0.22"
set "MONGO_BASE_URL=https://fastdl.mongodb.org/windows/mongodb-windows-x86_64"
set "INSTALL_DIR=%~dp0mongodb"
set "DATA_DIR=%INSTALL_DIR%\data\db"
set "ZIP_FILE=%INSTALL_DIR%\mongodb.zip"
set "EXTRACTED_DIR=%INSTALL_DIR%\mongodb-windows-x86_64-%MONGO_VERSION%"
set "URL=%MONGO_BASE_URL%-%MONGO_VERSION%.zip"
set "MONGOD_EXE="

REM Prepare directories
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Try to find existing mongod.exe anywhere under install_dir (skip download if found)
for /f "delims=" %%F in ('dir /b /s "%INSTALL_DIR%\mongod.exe" 2^>nul ^| findstr /i "\\bin\\mongod.exe$"') do (
  set "MONGOD_EXE=%%F"
  goto RUN
)

REM Download (curl -> BITS -> Invoke-WebRequest) only if not already installed
echo Downloading MongoDB v%MONGO_VERSION% from:
echo   %URL%
echo.

where curl >nul 2>&1
if %errorlevel%==0 (
  call :DOWNLOAD_WITH_CURL
  if errorlevel 1 goto DL_FAIL
) else (
  call :DOWNLOAD_WITH_BITS
  if errorlevel 1 call :DOWNLOAD_WITH_IWR
  if errorlevel 1 goto DL_FAIL
)

echo.
echo Extracting MongoDB...
where tar >nul 2>&1
if %errorlevel%==0 (
  tar -xf "%ZIP_FILE%" -C "%INSTALL_DIR%"
) else (
  powershell -NoLogo -NoProfile -Command "Expand-Archive -Path '%ZIP_FILE%' -DestinationPath '%INSTALL_DIR%' -Force"
)
if errorlevel 1 (
  echo Extraction failed.
  exit /b 1
)

REM Move extracted files if they landed in a versioned folder
if exist "%EXTRACTED_DIR%\bin\mongod.exe" (
  xcopy "%EXTRACTED_DIR%\*" "%INSTALL_DIR%\" /E /I /Y >nul
  rmdir /S /Q "%EXTRACTED_DIR%"
)

del "%ZIP_FILE%" 2>nul

REM Locate mongod.exe after extraction
for /f "delims=" %%F in ('dir /b /s "%INSTALL_DIR%\mongod.exe" 2^>nul ^| findstr /i "\\bin\\mongod.exe$"') do (
  set "MONGOD_EXE=%%F"
  goto RUN
)

echo ERROR: mongod.exe not found after extraction.
echo Listing contents of "%INSTALL_DIR%" to help debug:
dir /s /b "%INSTALL_DIR%"
exit /b 1

:RUN
REM Ensure data directory exists
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"

REM Start MongoDB
echo Starting MongoDB from:
echo   %MONGOD_EXE%
"%MONGOD_EXE%" --dbpath "%DATA_DIR%" --bind_ip 127.0.0.1
exit /b %ERRORLEVEL%

:DL_FAIL
echo.
echo ERROR: Could not download MongoDB. Quick tips:
echo  - Check your proxy/firewall.
echo  - You can pre-download the ZIP to:
echo      %ZIP_FILE%
echo    then re-run this script.
exit /b 1

REM Helper functions
:DOWNLOAD_WITH_CURL
echo Using curl...
curl -L --fail --retry 8 --retry-delay 2 --retry-connrefused --continue-at - -# -o "%ZIP_FILE%" "%URL%"
exit /b %ERRORLEVEL%

:DOWNLOAD_WITH_BITS
echo curl not found. Trying PowerShell BITS (Start-BitsTransfer)...
powershell -NoLogo -NoProfile -Command ^
  "$ErrorActionPreference='Stop';" ^
  "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12;" ^
  "Import-Module BitsTransfer;" ^
  "Start-BitsTransfer -Source '%U
