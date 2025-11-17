@echo off

set AREYOUSURE=N

:PROMPT
REM Configure console output coloring
for /F %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"

REM Check if parameter was passed (for automated usage)
if not "%1"=="" (
    set "AREYOUSURE=%1"
    echo Automated mode: %1
    goto PROCESS_CHOICE
)

echo Create an empty .venv...
echo How would you like to proceed?
REM red - recreate .venv
echo %ESC%[91m  R - delete and create a new .venv.%ESC%[0m
REM yelllow - run on existing env (create if missing)
echo %ESC%[33m  K - keep an existing .venv (create if missing)%ESC%[0m
REM gray - cancel
echo %ESC%[100m  N (or whatever) - cancel%ESC%[0m
set /p AREYOUSURE=?

:PROCESS_CHOICE

REM Process selected option
IF /I "%AREYOUSURE%" EQU "R" GOTO REWRITE
IF /I "%AREYOUSURE%" EQU "K" GOTO KEEP
GOTO CANCEL

:CANCEL
echo Canceled
GOTO END

:REWRITE
echo.
echo Create an empty .venv
IF EXIST ".venv" rd /s /q .venv
python -m venv .venv
GOTO INSTALL

:KEEP
echo Check existing .venv
IF EXIST ".venv" GOTO INSTALL
python -m venv .venv
GOTO INSTALL


:INSTALL
echo.
echo Activate .venv
call .venv\Scripts\activate.bat

echo.
echo Upgrade pip
python -m pip install --upgrade pip

echo.
echo Install requirements (excludes linter and build requirements)
pip install -r requirements.lock

echo.
echo Deactivate .venv
call .venv\Scripts\deactivate.bat

:END
