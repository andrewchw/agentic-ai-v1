#!/usr/bin/env python3
"""
Quick test for Agent Protocol connection
=======================================

Test script to verify Agent Protocol server connectivity and task creation.
"""

import requests
import time
import json

AGENT_PROTOCOL_URL = "http://127.0.0.1:8080"
API_BASE = f"{AGENT_PROTOCOL_URL}/ap/v1"

def test_agent_protocol_connection():
    """Test Agent Protocol server connection and functionality"""
    
    print("🔧 Testing Agent Protocol Connection...")
    print(f"Server URL: {AGENT_PROTOCOL_URL}")
    print("=" * 50)
    
    # Test 1: Server Health Check
    try:
        print("\n1. Health Check...")
        response = requests.get(f"{API_BASE}/agent/health", timeout=5)
        if response.status_code == 200:
            print("✅ Agent Protocol server is healthy")
        else:
            print(f"⚠️ Health check returned status: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: List existing tasks
    try:
        print("\n2. Listing existing tasks...")
        response = requests.get(f"{API_BASE}/agent/tasks", timeout=10)
        if response.status_code == 200:
            tasks = response.json()
            print(f"✅ Found {len(tasks)} existing tasks")
            if tasks:
                latest_task = max(tasks, key=lambda x: x.get('created_at', ''))
                print(f"   Latest task: {latest_task.get('task_id', 'Unknown')[:8]}")
        else:
            print(f"⚠️ Task listing returned status: {response.status_code}")
    except Exception as e:
        print(f"❌ Task listing failed: {e}")
    
    # Test 3: Create a test task
    try:
        print("\n3. Creating test task...")
        test_task_data = {
            "input": "Lead Intelligence Analysis Test - Connection Verification",
            "additional_input": {
                "task_type": "connection_test",
                "timestamp": time.time(),
                "agent_system": "Test System",
                "test_purpose": "Verify dashboard connectivity"
            }
        }
        
        response = requests.post(
            f"{API_BASE}/agent/tasks",
            json=test_task_data,
            timeout=15
        )
        
        if response.status_code == 200:
            task_data = response.json()
            task_id = task_data.get('task_id', 'Unknown')
            print(f"✅ Test task created successfully!")
            print(f"   Task ID: {task_id}")
            return task_id
        else:
            print(f"❌ Task creation failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Task creation failed: {e}")
        return False

def test_dashboard_visibility(task_id):
    """Test if created task is visible to dashboard"""
    
    print(f"\n4. Testing dashboard visibility for task {task_id[:8]}...")
    
    try:
        # Fetch task details
        response = requests.get(f"{API_BASE}/agent/tasks/{task_id}", timeout=10)
        if response.status_code == 200:
            task_details = response.json()
            print("✅ Task details retrieved successfully")
            print(f"   Status: {task_details.get('status', 'Unknown')}")
            print(f"   Created: {task_details.get('created_at', 'Unknown')}")
            return True
        else:
            print(f"❌ Task details retrieval failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Task details retrieval failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Agent Protocol Connection Test")
    print("=" * 50)
    
    # Run connection test
    task_id = test_agent_protocol_connection()
    
    if task_id:
        # Test dashboard visibility
        test_dashboard_visibility(task_id)
        
        print("\n" + "=" * 50)
        print("🎯 Test Results Summary:")
        print("✅ Agent Protocol server is running and accessible")
        print("✅ Tasks can be created successfully")
        print("✅ Dashboard should be able to see the tasks")
        print("\n💡 Next Steps:")
        print("1. Open Agent Collaboration Dashboard: http://localhost:8501")
        print("2. Check if the test task appears in the task list")
        print("3. Run 'Launch Collaboration' in your analysis to create real tasks")
        
    else:
        print("\n" + "=" * 50)
        print("❌ Connection test failed!")
        print("💡 Troubleshooting:")
        print("1. Make sure Agent Protocol server is running on port 8080")
        print("2. Try: python start_agent_protocol.py")
        print("3. Check if any firewall is blocking the connection")
