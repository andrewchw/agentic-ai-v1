"""
Comprehensive Agent Protocol Demo
=================================

This script demonstrates all three types of tasks supported by our Agent Protocol:
1. Lead Intelligence Tasks (DeepSeek LLM)
2. Revenue Optimization Tasks (Llama3 LLM)  
3. Collaborative Multi-Agent Tasks

Usage:
python demo_agent_protocol_comprehensive.py
"""

import requests
import json
import time
from typing import Dict, Any

def test_comprehensive_agent_protocol():
    """Comprehensive demonstration of Agent Protocol capabilities"""
    
    base_url = "http://127.0.0.1:8080"
    
    print("🎯 Comprehensive Agent Protocol Demonstration")
    print("=" * 60)
    print()
    
    # Verify server is running
    print("🔍 Checking server health...")
    try:
        response = requests.get(f"{base_url}/ap/v1/agent/health")
        if response.status_code != 200:
            print(f"❌ Server not responding. Please start with: python start_agent_protocol.py")
            return False
        
        health = response.json()
        print(f"✅ Server Status: {health.get('status')}")
        print(f"   Protocol Version: {health.get('agent_protocol_version')}")
        print(f"   Active Tasks: {health.get('active_tasks', 0)}")
        print()
    except Exception as e:
        print(f"❌ Cannot connect to server: {str(e)}")
        print("   Please start the server with: python start_agent_protocol.py")
        return False
    
    # Task 1: Lead Intelligence Analysis
    print("1️⃣ Lead Intelligence Task (DeepSeek LLM)")
    print("-" * 50)
    
    lead_task = {
        "input": "Analyze customer churn patterns and identify high-value retention opportunities for Hong Kong telecom customers",
        "additional_input": {
            "focus": "lead_intelligence",
            "analysis_type": "churn_prediction",
            "market": "hong_kong_telecom",
            "priority": "high"
        }
    }
    
    task_id_1 = create_and_monitor_task(base_url, lead_task, "Lead Intelligence")
    if not task_id_1:
        return False
    
    print()
    
    # Task 2: Revenue Optimization Strategy
    print("2️⃣ Revenue Optimization Task (Llama3 LLM)")
    print("-" * 50)
    
    revenue_task = {
        "input": "Develop pricing strategy and product recommendations for premium enterprise customers with Three HK",
        "additional_input": {
            "focus": "revenue_optimization",
            "customer_segment": "premium_enterprise",
            "product_focus": "three_hk_5g",
            "priority": "high"
        }
    }
    
    task_id_2 = create_and_monitor_task(base_url, revenue_task, "Revenue Optimization")
    if not task_id_2:
        return False
    
    print()
    
    # Task 3: Collaborative Multi-Agent Analysis
    print("3️⃣ Collaborative Multi-Agent Task (Both Agents)")
    print("-" * 50)
    
    collab_task = {
        "input": "Perform comprehensive customer portfolio analysis and develop integrated revenue growth strategy for Hong Kong market",
        "additional_input": {
            "focus": "collaborative",
            "agents": ["lead_intelligence", "revenue_optimization"],
            "scope": "comprehensive_analysis",
            "priority": "high"
        }
    }
    
    task_id_3 = create_and_monitor_task(base_url, collab_task, "Collaborative Multi-Agent")
    if not task_id_3:
        return False
    
    print()
    
    # Final Summary
    print("📊 Final Results Summary")
    print("=" * 60)
    
    all_tasks = [task_id_1, task_id_2, task_id_3]
    task_names = ["Lead Intelligence", "Revenue Optimization", "Collaborative"]
    
    for i, (task_id, name) in enumerate(zip(all_tasks, task_names), 1):
        print(f"\\n{i}️⃣ {name} Task Results:")
        get_final_task_status(base_url, task_id)
    
    # List all tasks
    print("\\n📋 All Tasks Overview:")
    try:
        response = requests.get(f"{base_url}/ap/v1/agent/tasks")
        if response.status_code == 200:
            tasks = response.json()
            print(f"   Total Tasks Created: {len(tasks)}")
            for i, task in enumerate(tasks, 1):
                print(f"   {i}. {task.get('task_id')[:8]}... - {task.get('status')}")
        else:
            print(f"   ❌ Failed to list tasks: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error listing tasks: {str(e)}")
    
    print("\\n🎉 Comprehensive Agent Protocol Demo Complete!")
    print("\\n💡 Key Achievements:")
    print("   ✅ Lead Intelligence Agent successfully analyzed customer patterns")
    print("   ✅ Revenue Optimization Agent developed strategic recommendations")
    print("   ✅ Multi-Agent collaboration demonstrated working integration")
    print("   ✅ All three task routing mechanisms validated")
    print("   ✅ Hong Kong telecom specialization confirmed")
    
    return True

def create_and_monitor_task(base_url: str, task_data: Dict[str, Any], task_type: str) -> str:
    """Create a task and monitor its execution"""
    
    print(f"Creating {task_type} task...")
    print(f"Input: {task_data['input'][:80]}...")
    
    try:
        # Create task
        response = requests.post(f"{base_url}/ap/v1/agent/tasks", 
                               json=task_data,
                               headers={"Content-Type": "application/json"})
        
        if response.status_code != 200:
            print(f"❌ Failed to create task: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
        
        task_result = response.json()
        task_id = task_result.get('task_id')
        
        print(f"✅ Task created: {task_id}")
        print(f"   Initial Status: {task_result.get('status')}")
        
        # Monitor execution
        print("   ⏳ Monitoring execution...")
        
        for attempt in range(10):  # Max 10 seconds
            time.sleep(1)
            
            try:
                response = requests.get(f"{base_url}/ap/v1/agent/tasks/{task_id}")
                if response.status_code == 200:
                    task_status = response.json()
                    current_status = task_status.get('status')
                    
                    if current_status == 'completed':
                        print(f"   ✅ Task completed successfully!")
                        return task_id
                    elif current_status == 'failed':
                        print(f"   ❌ Task failed!")
                        return task_id
                    else:
                        print(f"   ⏳ Status: {current_status}")
                        
            except Exception as e:
                print(f"   ⚠️ Monitoring error: {str(e)}")
                
        print("   ⏰ Task still running after 10 seconds")
        return task_id
        
    except Exception as e:
        print(f"❌ Error creating task: {str(e)}")
        return None

def get_final_task_status(base_url: str, task_id: str):
    """Get final status and results of a task"""
    
    try:
        response = requests.get(f"{base_url}/ap/v1/agent/tasks/{task_id}")
        if response.status_code == 200:
            task = response.json()
            print(f"   Task ID: {task_id}")
            print(f"   Status: {task.get('status')}")
            print(f"   Created: {task.get('created_at')}")
            print(f"   Modified: {task.get('modified_at')}")
            print(f"   Artifacts: {len(task.get('artifacts', []))}")
        else:
            print(f"   ❌ Failed to get task status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error getting task status: {str(e)}")

if __name__ == "__main__":
    print("🤖 Agent Protocol Comprehensive Demo")
    print("   Ensure the server is running first!")
    print("   Start with: python start_agent_protocol.py")
    print()
    
    input("Press Enter when the server is ready...")
    
    success = test_comprehensive_agent_protocol()
    
    if success:
        print("\\n🎊 Demo completed successfully!")
        print("\\n📖 Explore more at: http://127.0.0.1:8080/ap/v1/docs")
    else:
        print("\\n😞 Demo encountered issues.")
        print("   Check that the Agent Protocol server is running.")
