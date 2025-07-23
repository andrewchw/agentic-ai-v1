"""
Quick Agent Protocol Test
========================

Simple test to verify the Agent Protocol server is working correctly.
"""

import requests
import json
import time

def test_agent_protocol_server():
    """Test the Agent Protocol server endpoints"""
    
    base_url = "http://127.0.0.1:8080"
    
    print("🧪 Testing Agent Protocol Server")
    print("=" * 40)
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/ap/v1/agent/health")
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health Check Passed")
            print(f"   Status: {health_data.get('status')}")
            print(f"   Protocol Version: {health_data.get('agent_protocol_version')}")
            print(f"   Multi-Agent System: {health_data.get('multi_agent_system')}")
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health Check Error: {str(e)}")
        return False
    
    # Test 2: Create a Task
    print("\n2️⃣ Testing Task Creation...")
    try:
        task_data = {
            "input": "Analyze customer patterns for Hong Kong telecom market",
            "additional_input": {
                "focus": "lead_intelligence",
                "priority": "high"
            }
        }
        
        response = requests.post(f"{base_url}/ap/v1/agent/tasks", 
                               json=task_data,
                               headers={"Content-Type": "application/json"})
        
        if response.status_code == 200:
            task_result = response.json()
            task_id = task_result.get('task_id')
            print("✅ Task Creation Passed")
            print(f"   Task ID: {task_id}")
            print(f"   Status: {task_result.get('status')}")
            
            # Test 3: Get Task Status
            print("\n3️⃣ Testing Task Retrieval...")
            time.sleep(2)  # Wait for processing
            
            response = requests.get(f"{base_url}/ap/v1/agent/tasks/{task_id}")
            if response.status_code == 200:
                task_status = response.json()
                print("✅ Task Retrieval Passed")
                print(f"   Status: {task_status.get('status')}")
                print(f"   Modified: {task_status.get('modified_at')}")
            else:
                print(f"❌ Task Retrieval Failed: {response.status_code}")
            
        else:
            print(f"❌ Task Creation Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Task Creation Error: {str(e)}")
        return False
    
    # Test 4: List All Tasks
    print("\n4️⃣ Testing Task Listing...")
    try:
        response = requests.get(f"{base_url}/ap/v1/agent/tasks")
        if response.status_code == 200:
            tasks = response.json()
            print("✅ Task Listing Passed")
            print(f"   Total Tasks: {len(tasks)}")
        else:
            print(f"❌ Task Listing Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Task Listing Error: {str(e)}")
    
    print("\n🎉 Agent Protocol Test Complete!")
    return True

if __name__ == "__main__":
    # Wait a moment for server to fully start
    print("⏳ Waiting for server to start...")
    time.sleep(5)
    
    success = test_agent_protocol_server()
    
    if success:
        print("\n✅ Agent Protocol server is working correctly!")
        print("\n📖 Try the API documentation at: http://127.0.0.1:8080/ap/v1/docs")
    else:
        print("\n❌ Agent Protocol server test failed!")
        print("   Check that the server is running on http://127.0.0.1:8080")
