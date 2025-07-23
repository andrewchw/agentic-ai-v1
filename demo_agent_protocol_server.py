"""
Agent Protocol Server Demonstration
====================================

This script demonstrates the div99 Agent Protocol implementation for our multi-agent system.
It shows how to start the server and interact with it using the standard Agent Protocol REST API.

Features Demonstrated:
- Agent Protocol REST API compliance
- Multi-agent task routing
- Lead Intelligence and Revenue Optimization collaboration
- Real-time task execution and monitoring
- Industry-standard communication protocols

Usage:
python demo_agent_protocol_server.py
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.agent_protocol import create_agent_protocol_server
from src.utils.logger import setup_logging

# Setup logging
setup_logging()

def main():
    """Main demonstration of Agent Protocol server"""
    
    print("🚀 Agent Protocol Server Demonstration")
    print("=" * 60)
    print()
    
    print("📋 Features Demonstrated:")
    print("   ✓ div99 Agent Protocol REST API compliance")
    print("   ✓ Multi-agent task routing and execution")
    print("   ✓ Lead Intelligence Agent (DeepSeek LLM)")
    print("   ✓ Revenue Optimization Agent (Llama3 LLM)")
    print("   ✓ Collaborative multi-agent workflows")
    print("   ✓ Hong Kong telecom market specialization")
    print("   ✓ Industry-standard communication protocols")
    print()
    
    print("🔧 Agent Protocol API Endpoints:")
    endpoints = [
        ("GET", "/ap/v1/agent/tasks", "List all tasks"),
        ("POST", "/ap/v1/agent/tasks", "Create a new task"),
        ("GET", "/ap/v1/agent/tasks/{task_id}", "Get specific task"),
        ("POST", "/ap/v1/agent/tasks/{task_id}/steps", "Create task step"),
        ("GET", "/ap/v1/agent/tasks/{task_id}/steps", "List task steps"),
        ("GET", "/ap/v1/agent/tasks/{task_id}/steps/{step_id}", "Get specific step"),
        ("GET", "/ap/v1/agent/health", "Health check")
    ]
    
    for method, endpoint, description in endpoints:
        print(f"   {method:4} {endpoint:35} - {description}")
    print()
    
    print("🎯 Sample Task Types:")
    print("   • Lead Intelligence: Customer pattern analysis, lead scoring, churn prediction")
    print("   • Revenue Optimization: Pricing strategy, offer matching, retention plans")
    print("   • Collaborative: Multi-agent comprehensive revenue analysis")
    print()
    
    print("📊 Sample API Requests:")
    print()
    
    # Lead Intelligence Task Example
    lead_task = {
        "input": "Analyze customer patterns and identify high-value leads for Hong Kong telecom market",
        "additional_input": {
            "focus": "lead_intelligence",
            "market": "hong_kong_telecom",
            "priority": "high"
        }
    }
    
    print("1️⃣ Lead Intelligence Task:")
    print(f"   POST /ap/v1/agent/tasks")
    print(f"   Body: {json.dumps(lead_task, indent=8)}")
    print()
    
    # Revenue Optimization Task Example
    revenue_task = {
        "input": "Develop pricing strategy and retention offers for premium customers",
        "additional_input": {
            "focus": "revenue_optimization",
            "customer_segment": "premium_individual",
            "priority": "high"
        }
    }
    
    print("2️⃣ Revenue Optimization Task:")
    print(f"   POST /ap/v1/agent/tasks")
    print(f"   Body: {json.dumps(revenue_task, indent=8)}")
    print()
    
    # Collaborative Task Example
    collab_task = {
        "input": "Perform comprehensive customer analysis and develop integrated revenue strategy",
        "additional_input": {
            "focus": "collaborative",
            "agents": ["lead_intelligence", "revenue_optimization"],
            "priority": "high"
        }
    }
    
    print("3️⃣ Collaborative Multi-Agent Task:")
    print(f"   POST /ap/v1/agent/tasks")
    print(f"   Body: {json.dumps(collab_task, indent=8)}")
    print()
    
    print("🌐 Starting Agent Protocol Server:")
    print("   Host: 127.0.0.1")
    print("   Port: 8080")
    print("   Protocol: div99 Agent Protocol v1.0.0")
    print()
    print("📖 API Documentation will be available at:")
    print("   http://127.0.0.1:8080/ap/v1/docs")
    print("   http://127.0.0.1:8080/ap/v1/redoc")
    print()
    
    print("💡 Try these sample requests once the server is running:")
    print()
    print("   # Health Check")
    print("   curl http://127.0.0.1:8080/ap/v1/agent/health")
    print()
    print("   # Create Lead Intelligence Task")
    print("   curl -X POST http://127.0.0.1:8080/ap/v1/agent/tasks \\")
    print("        -H 'Content-Type: application/json' \\")
    print(f"        -d '{json.dumps(lead_task)}'")
    print()
    print("   # List All Tasks")
    print("   curl http://127.0.0.1:8080/ap/v1/agent/tasks")
    print()
    
    print("=" * 60)
    print("🎬 Starting Server... (Press Ctrl+C to stop)")
    print("=" * 60)
    
    try:
        # Create and start the Agent Protocol server
        server = create_agent_protocol_server()
        server.start_server(host="127.0.0.1", port=8080)
        
    except KeyboardInterrupt:
        print("\\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\\n❌ Server error: {str(e)}")


if __name__ == "__main__":
    main()
