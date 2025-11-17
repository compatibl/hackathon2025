@echo off

echo.
echo Activate .venv
call .venv\Scripts\activate.bat

:: List of package subdirectories
set "dirs=runtime convince hackathon"

:: Add package roots to PYTHONPATH
setlocal enabledelayedexpansion
set PYTHONPATH=
for %%d in (%dirs%) do (
    set PYTHONPATH=%%d;!PYTHONPATH!
)

echo.
echo Run tests in each package
for %%d in (%dirs%) do (
    echo Running scripts in %%d
    pytest %%d\tests
)
pause

echo.
echo Deactivate .venv
call .venv\Scripts\deactivate.bat
