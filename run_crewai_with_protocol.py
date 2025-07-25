"""
Run CrewAI with Agent Protocol Integration
=========================================

This script runs your CrewAI analysis and automatically creates Agent Protocol tasks
so you can see real-time progress in the dashboard.
"""

import requests
import json
import time
from src.agents.crew_config import CrewAIConfig
import sys
import os

def create_agent_protocol_task(task_input: str, task_type: str = "crewai_analysis"):
    """Create a task in the Agent Protocol server"""
    try:
        response = requests.post(
            "http://127.0.0.1:8080/ap/v1/agent/tasks",
            json={
                "input": task_input,
                "additional_input": {
                    "task_type": task_type,
                    "timestamp": time.time(),
                    "agent_system": "CrewAI"
                }
            },
            timeout=15
        )
        
        if response.status_code == 200:
            task_data = response.json()
            print(f"✅ Created Agent Protocol task: {task_data.get('task_id', 'Unknown')}")
            return task_data.get('task_id')
        else:
            print(f"❌ Failed to create task: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating task: {e}")
        return None

def update_task_status(task_id: str, status: str, output: str = None):
    """Update task status in Agent Protocol"""
    try:
        # Note: This would require implementing a PATCH endpoint in the Agent Protocol server
        # For now, we'll just print the status
        print(f"📝 Task {task_id[:8]}: {status}")
        if output:
            print(f"   Output preview: {output[:100]}...")
            
    except Exception as e:
        print(f"❌ Error updating task: {e}")

def run_crewai_with_protocol():
    """Run CrewAI analysis with Agent Protocol integration"""
    
    print("🚀 Starting CrewAI Analysis with Agent Protocol Integration")
    print("=" * 60)
    
    try:
        # Initialize CrewAI
        config = CrewAIConfig()
        
        # Sample customer data (you can modify this)
        customer_data = {
            "total_customers": 25000,
            "fields": ["customer_id", "usage_gb", "plan_type", "tenure", "arpu"],
            "source": "Hong Kong Telecom Market Analysis"
        }
        
        # Create Agent Protocol task for tracking
        task_input = f"CrewAI Multi-Agent Analysis: Lead Intelligence + Revenue Optimization for {customer_data['total_customers']} customers"
        protocol_task_id = create_agent_protocol_task(task_input, "crewai_multi_agent")
        
        if protocol_task_id:
            print(f"🔗 Monitor progress in dashboard: http://localhost:8501")
            print(f"📋 Task ID: {protocol_task_id}")
            print()
        
        # Update status: Starting analysis
        if protocol_task_id:
            update_task_status(protocol_task_id, "running", "Initializing CrewAI multi-agent crew...")
        
        # Create and run the crew
        print("🤖 Creating multi-agent crew...")
        crew = config.create_multi_agent_crew(customer_data)
        
        # Update status: Running analysis
        if protocol_task_id:
            update_task_status(protocol_task_id, "running", "Executing Lead Intelligence and Revenue Optimization analysis...")
        
        print("⚡ Starting multi-agent analysis...")
        print("   - Lead Intelligence Agent: Analyzing customer data patterns")
        print("   - Revenue Optimization Agent: Developing business strategies")
        print()
        
        # Run the crew
        result = crew.kickoff()
        
        # Update status: Completed
        if protocol_task_id:
            update_task_status(protocol_task_id, "completed", str(result))
        
        print("✅ CrewAI Analysis Completed!")
        print("=" * 60)
        print("RESULTS:")
        print(result)
        print("=" * 60)
        print(f"🎯 Check the Agent Collaboration Dashboard for full details!")
        
        return result
        
    except Exception as e:
        print(f"❌ CrewAI Error: {e}")
        if protocol_task_id:
            update_task_status(protocol_task_id, "failed", f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    result = run_crewai_with_protocol()
    
    if result:
        print("\n🎉 Analysis complete! Check the dashboard for detailed agent assignments.")
    else:
        print("\n❌ Analysis failed. Check the error messages above.")
