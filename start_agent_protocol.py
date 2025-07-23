"""
Agent Protocol Server Launcher
==============================

Proper launcher for the Agent Protocol server that handles import paths correctly.
This script resolves the relative import issues when running the server directly.

Usage:
python start_agent_protocol.py [--host HOST] [--port PORT]
"""

import os
import sys
import argparse

def main():
    """Main launcher for Agent Protocol server"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Start Agent Protocol server")
    parser.add_argument("--host", default="127.0.0.1", help="Server host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8080, help="Server port (default: 8080)")
    
    args = parser.parse_args()
    
    # Add the project root to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = current_dir
    sys.path.insert(0, project_root)
    
    print("🚀 Starting Agent Protocol Server")
    print("=" * 50)
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Project Root: {project_root}")
    print()
    
    # Import and create the server
    try:
        from src.agents.agent_protocol import create_agent_protocol_server
        
        print("📦 Creating Agent Protocol server...")
        server = create_agent_protocol_server()
        
        print("🌐 Server configuration:")
        print(f"   • REST API: http://{args.host}:{args.port}")
        print(f"   • API Docs: http://{args.host}:{args.port}/ap/v1/docs")
        print(f"   • Health Check: http://{args.host}:{args.port}/ap/v1/agent/health")
        print()
        
        print("🎯 Available Endpoints:")
        endpoints = [
            ("GET", "/ap/v1/agent/tasks", "List all tasks"),
            ("POST", "/ap/v1/agent/tasks", "Create new task"),
            ("GET", "/ap/v1/agent/tasks/{task_id}", "Get specific task"),
            ("POST", "/ap/v1/agent/tasks/{task_id}/steps", "Create task step"),
            ("GET", "/ap/v1/agent/tasks/{task_id}/steps", "List task steps"),
            ("GET", "/ap/v1/agent/tasks/{task_id}/steps/{step_id}", "Get specific step"),
            ("GET", "/ap/v1/agent/health", "Health check")
        ]
        
        for method, endpoint, description in endpoints:
            print(f"   {method:4} {endpoint:35} - {description}")
        print()
        
        print("🤖 Multi-Agent Capabilities:")
        print("   • Lead Intelligence Agent (DeepSeek LLM)")
        print("   • Revenue Optimization Agent (Llama3 LLM)")
        print("   • Collaborative multi-agent workflows")
        print("   • Hong Kong telecom market specialization")
        print()
        
        print("💡 Sample API Calls:")
        print(f"   curl http://{args.host}:{args.port}/ap/v1/agent/health")
        print(f"   curl -X POST http://{args.host}:{args.port}/ap/v1/agent/tasks \\\\")
        print('        -H "Content-Type: application/json" \\\\')
        print('        -d \'{"input": "Analyze customer patterns", "additional_input": {"focus": "lead_intelligence"}}\'')
        print()
        
        print("🎬 Starting server... (Press Ctrl+C to stop)")
        print("=" * 50)
        
        # Start the server
        server.start_server(host=args.host, port=args.port)
        
    except KeyboardInterrupt:
        print("\\n🛑 Server stopped by user")
    except ImportError as e:
        print(f"❌ Import Error: {str(e)}")
        print("   Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Server Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
