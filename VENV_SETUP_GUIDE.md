# Agentic AI Project - Virtual Environment Setup

## ✅ What I've Set Up For You

### 1. **Quick Activation Scripts**
- `activate_venv.ps1` - PowerShell script with project info
- `activate_venv.bat` - Batch file alternative

### 2. **VS Code Integration**
- `.vscode/settings.json` - Auto-activates venv in VS Code terminals
- `.vscode/profile.ps1` - PowerShell profile for automatic activation
- Python interpreter path set to `./venv/Scripts/python.exe`

### 3. **Streamlit Config**
- `.streamlit/config.toml` - Fixed theme configuration for proper text visibility

## 🚀 How to Use

### Method 1: Quick Activation (Recommended)
```powershell
# In project root directory
.\activate_venv.ps1
```

### Method 2: Manual Activation
```powershell
.\venv\Scripts\Activate.ps1
```

### Method 3: VS Code Integration
- Open VS Code in the project folder
- Open a new terminal - venv should auto-activate
- If not, reload VS Code window (Ctrl+Shift+P → "Developer: Reload Window")

## 🔧 Running the Applications

Once venv is activated, use these commands:

### Main Streamlit App (with fixed text colors)
```powershell
python -m streamlit run src/main.py --server.port 8502
```

### Agent Protocol Server
```powershell
python src/agents/agent_protocol.py --host 127.0.0.1 --port 8080
```

### Agent Collaboration Dashboard
```powershell
streamlit run agent_collaboration_dashboard.py --server.port 8501
```

### Task Management
```powershell
task-master list
```

## 🎨 Fixed Issues

### Text Color Problem
- Updated `src/components/layout.py` with enhanced CSS
- Added `!important` declarations to override Streamlit defaults
- Created proper Streamlit theme configuration

### Auto-Environment Activation
- VS Code will automatically activate venv when opening terminals
- Project-specific Python interpreter configured
- Environment variables set for proper module detection

## 🔍 Verification

To verify everything is working:

1. **Check venv activation:**
   ```powershell
   .\activate_venv.ps1
   # Should show "(venv)" in prompt and project info
   ```

2. **Check Python packages:**
   ```powershell
   pip list | findstr -i "streamlit pandas crewai"
   # Should show installed versions
   ```

3. **Test Streamlit:**
   ```powershell
   python -m streamlit run src/main.py --server.port 8502
   # Should open with proper text colors (black text on white background)
   ```

## 🆘 Troubleshooting

### If venv doesn't activate in VS Code:
1. Press `Ctrl+Shift+P`
2. Type "Python: Select Interpreter"
3. Choose `./venv/Scripts/python.exe`
4. Reload VS Code window

### If text is still invisible in Streamlit:
1. Clear browser cache
2. Try incognito/private browsing mode
3. Check if `.streamlit/config.toml` exists

### If commands don't work:
1. Ensure you're in the project root directory
2. Check that venv exists: `ls venv/Scripts/`
3. Reinstall if needed: `python -m venv venv --clear`

---

**Now your venv will be the default environment for this project! 🎉**
