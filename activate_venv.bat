@echo off
echo 🚀 Activating Agentic AI venv environment...
call .\venv\Scripts\activate.bat
echo ✅ Virtual environment activated!
echo 📍 Project: Agentic AI Revenue Assistant
python --version
echo.
echo 🔧 Ready for development! Available commands:
echo   streamlit run src/main.py --server.port 8502
echo   python src/agents/agent_protocol.py --host 127.0.0.1 --port 8080
echo   task-master list
echo.
