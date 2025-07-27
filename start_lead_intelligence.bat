@echo off
echo.
echo 🤖 Starting Lead Intelligence Agent...
echo 📊 Port: 8502
echo 🔗 URL: http://localhost:8502
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo 🔧 Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo.
echo 🚀 Starting Lead Intelligence Agent on port 8502...
echo    Access at: http://localhost:8502
echo.

REM Start the Streamlit application on port 8502
streamlit run src/main.py --server.port 8502 --server.address localhost
