@echo off
SETLOCAL

REM 1) Switch into this folder
cd /d "%~dp0"

REM 2) Ensure the Python script exists
if not exist data_combiner_vendor_tagger.py (
  echo ERROR: Cannot find data_combiner_vendor_tagger.py in %cd%
  pause
  exit /B 1
)

REM 3) Verify Python is installed
python --version >nul 2>&1
IF ERRORLEVEL 1 (
  echo ERROR: Python not found. Install Python 3 and ensure it’s on your PATH.
  pause
  exit /B 1
)

REM 4) Install/upgrade dependencies
echo Installing/upgrading dependencies from requirements.txt…
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

REM 5) Launch Streamlit in its own window
echo Starting Data Combiner & Vendor Tagger…
start "Data Combiner & Vendor Tagger" cmd /k ^
  "python -m streamlit run data_combiner_vendor_tagger.py --server.headless false"

REM 6) Wait a moment, then open the browser
timeout /t 5 >nul
echo Opening http://localhost:8501 …
start "" "http://localhost:8501"

ENDLOCAL
