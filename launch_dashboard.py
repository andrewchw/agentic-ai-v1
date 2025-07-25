#!/usr/bin/env python3
"""
Agent Collaboration Dashboard Launcher
=====================================

Launch script for the Agent Collaboration Dashboard with automatic
Agent Protocol server startup and health checks.

Usage:
    python launch_dashboard.py

Author: Agentic AI Revenue Assistant
Date: 2025-07-23
"""

import subprocess
import time
import requests
import os
import sys
import threading
from pathlib import Path

# Configuration
AGENT_PROTOCOL_URL = "http://127.0.0.1:8080"
DASHBOARD_PORT = 8501

def check_agent_protocol_health():
    """Check if Agent Protocol server is running."""
    try:
        response = requests.get(f"{AGENT_PROTOCOL_URL}/ap/v1/agent/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_agent_protocol():
    """Start the Agent Protocol server in background."""
    print("🚀 Starting Agent Protocol server...")
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Start the server
    process = subprocess.Popen([
        sys.executable, "start_agent_protocol.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=project_dir)
    
    # Wait for server to start
    print("⏳ Waiting for Agent Protocol server to be ready...")
    max_retries = 30
    for i in range(max_retries):
        if check_agent_protocol_health():
            print("✅ Agent Protocol server is healthy!")
            return process
        time.sleep(2)
        print(f"   Attempt {i+1}/{max_retries}...")
    
    print("❌ Failed to start Agent Protocol server")
    return None

def launch_dashboard():
    """Launch the Streamlit dashboard."""
    print("🚀 Starting Agent Collaboration Dashboard...")
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Launch Streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "agent_collaboration_dashboard.py",
        "--server.port", str(DASHBOARD_PORT),
        "--server.headless", "false",
        "--server.fileWatcherType", "none"
    ])

def main():
    """Main launcher function."""
    print("=" * 60)
    print("🤖 Agent Collaboration Dashboard Launcher")
    print("=" * 60)
    
    # Check if Agent Protocol is already running
    if check_agent_protocol_health():
        print("✅ Agent Protocol server is already running")
    else:
        # Start Agent Protocol server
        agent_process = start_agent_protocol()
        if not agent_process:
            print("❌ Cannot start dashboard without Agent Protocol server")
            return
    
    print()
    print("🎯 Dashboard Configuration:")
    print(f"   • Agent Protocol URL: {AGENT_PROTOCOL_URL}")
    print(f"   • Dashboard URL: http://localhost:{DASHBOARD_PORT}")
    print()
    
    # Launch dashboard
    try:
        launch_dashboard()
    except KeyboardInterrupt:
        print("\n👋 Dashboard shutdown initiated by user")
    except Exception as e:
        print(f"❌ Dashboard error: {e}")

if __name__ == "__main__":
    main()
