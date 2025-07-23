"""
div99 Agent Protocol Implementation
===================================

This module implements the div99 Agent Protocol standard for enhanced agent communication.
It provides REST API endpoints that comply with the Agent Protocol specification.

API Endpoints:
- GET /ap/v1/agent/tasks - List all tasks
- POST /ap/v1/agent/tasks - Create a new task
- GET /ap/v1/agent/tasks/{task_id} - Get specific task
- POST /ap/v1/agent/tasks/{task_id}/steps - Create a step for a task
- GET /ap/v1/agent/tasks/{task_id}/steps - List steps for a task
- GET /ap/v1/agent/tasks/{task_id}/steps/{step_id} - Get specific step

References:
- div99 Agent Protocol: https://github.com/div99/agent-protocol
- OpenAPI Specification: Compliant with Agent Protocol v1.0
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4
import asyncio

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Handle relative imports when running as script
if __name__ == "__main__":
    # Add the project root to the path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    sys.path.insert(0, project_root)
    
    from src.utils.logger import setup_logging
    from src.agents.multi_agent_system import MultiAgentRevenueSystem
    from src.agents.lead_intelligence_agent import create_lead_intelligence_agent
    from src.agents.revenue_optimization_agent import create_revenue_optimization_agent
else:
    from ..utils.logger import setup_logging
    from .multi_agent_system import MultiAgentRevenueSystem
    from .lead_intelligence_agent import create_lead_intelligence_agent
    from .revenue_optimization_agent import create_revenue_optimization_agent

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Task status enumeration per Agent Protocol spec"""
    CREATED = "created"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"


class StepStatus(str, Enum):
    """Step status enumeration per Agent Protocol spec"""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Artifact:
    """Artifact data structure per Agent Protocol spec"""
    artifact_id: str = field(default_factory=lambda: str(uuid4()))
    agent_created: bool = True
    file_name: str = ""
    relative_path: Optional[str] = None


@dataclass
class Step:
    """Step data structure per Agent Protocol spec"""
    step_id: str = field(default_factory=lambda: str(uuid4()))
    task_id: str = ""
    name: Optional[str] = None
    status: StepStatus = StepStatus.CREATED
    output: Optional[str] = None
    additional_output: Optional[Dict[str, Any]] = None
    artifacts: List[Artifact] = field(default_factory=list)
    is_last: bool = False
    additional_input: Optional[Dict[str, Any]] = None


@dataclass 
class Task:
    """Task data structure per Agent Protocol spec"""
    task_id: str = field(default_factory=lambda: str(uuid4()))
    input: str = ""
    additional_input: Optional[Dict[str, Any]] = None
    status: TaskStatus = TaskStatus.CREATED
    artifacts: List[Artifact] = field(default_factory=list)
    steps: List[Step] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    modified_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# Pydantic models for API validation
class TaskInput(BaseModel):
    """Task input model for API"""
    input: str = Field(..., description="Input prompt for the task")
    additional_input: Optional[Dict[str, Any]] = Field(None, description="Additional input parameters")


class StepInput(BaseModel):
    """Step input model for API"""
    name: Optional[str] = Field(None, description="Step name")
    additional_input: Optional[Dict[str, Any]] = Field(None, description="Additional input for the step")


class TaskResponse(BaseModel):
    """Task response model"""
    task_id: str
    input: str
    additional_input: Optional[Dict[str, Any]] = None
    status: TaskStatus
    artifacts: List[Dict[str, Any]] = []
    created_at: str
    modified_at: str


class StepResponse(BaseModel):
    """Step response model"""
    step_id: str
    task_id: str
    name: Optional[str] = None
    status: StepStatus
    output: Optional[str] = None
    additional_output: Optional[Dict[str, Any]] = None
    artifacts: List[Dict[str, Any]] = []
    is_last: bool = False


class AgentProtocolServer:
    """
    Agent Protocol server implementation for multi-agent system.
    
    This server exposes our multi-agent system through the standard Agent Protocol
    REST API, enabling integration with other Agent Protocol compliant tools.
    """
    
    def __init__(self, multi_agent_system: Optional[MultiAgentRevenueSystem] = None):
        """Initialize the Agent Protocol server"""
        self.multi_agent_system = multi_agent_system or MultiAgentRevenueSystem()
        self.tasks: Dict[str, Task] = {}
        self.app = FastAPI(
            title="Multi-Agent Revenue System - Agent Protocol API",
            description="Agent Protocol implementation for Hong Kong telecom revenue optimization",
            version="1.0.0",
            docs_url="/ap/v1/docs",
            redoc_url="/ap/v1/redoc"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self._setup_routes()
        logger.info("Agent Protocol server initialized")
    
    def _setup_routes(self):
        """Setup API routes according to Agent Protocol specification"""
        
        @self.app.get("/ap/v1/agent/tasks", response_model=List[TaskResponse])
        async def list_tasks():
            """List all tasks"""
            try:
                tasks = []
                for task in self.tasks.values():
                    tasks.append(TaskResponse(
                        task_id=task.task_id,
                        input=task.input,
                        additional_input=task.additional_input,
                        status=task.status,
                        artifacts=[asdict(artifact) for artifact in task.artifacts],
                        created_at=task.created_at,
                        modified_at=task.modified_at
                    ))
                
                logger.info(f"Listed {len(tasks)} tasks")
                return tasks
                
            except Exception as e:
                logger.error(f"Error listing tasks: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to list tasks: {str(e)}"
                )
        
        @self.app.post("/ap/v1/agent/tasks", response_model=TaskResponse)
        async def create_task(task_input: TaskInput):
            """Create a new task"""
            try:
                task = Task(
                    input=task_input.input,
                    additional_input=task_input.additional_input
                )
                
                self.tasks[task.task_id] = task
                
                # Start task execution asynchronously
                asyncio.create_task(self._execute_task(task.task_id))
                
                logger.info(f"Created task {task.task_id}: {task_input.input[:100]}...")
                
                return TaskResponse(
                    task_id=task.task_id,
                    input=task.input,
                    additional_input=task.additional_input,
                    status=task.status,
                    artifacts=[asdict(artifact) for artifact in task.artifacts],
                    created_at=task.created_at,
                    modified_at=task.modified_at
                )
                
            except Exception as e:
                logger.error(f"Error creating task: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create task: {str(e)}"
                )
        
        @self.app.get("/ap/v1/agent/tasks/{task_id}", response_model=TaskResponse)
        async def get_task(task_id: str):
            """Get specific task by ID"""
            try:
                if task_id not in self.tasks:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Task {task_id} not found"
                    )
                
                task = self.tasks[task_id]
                
                return TaskResponse(
                    task_id=task.task_id,
                    input=task.input,
                    additional_input=task.additional_input,
                    status=task.status,
                    artifacts=[asdict(artifact) for artifact in task.artifacts],
                    created_at=task.created_at,
                    modified_at=task.modified_at
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting task {task_id}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to get task: {str(e)}"
                )
        
        @self.app.post("/ap/v1/agent/tasks/{task_id}/steps", response_model=StepResponse)
        async def create_step(task_id: str, step_input: StepInput):
            """Create a new step for a task"""
            try:
                if task_id not in self.tasks:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Task {task_id} not found"
                    )
                
                task = self.tasks[task_id]
                
                step = Step(
                    task_id=task_id,
                    name=step_input.name,
                    additional_input=step_input.additional_input
                )
                
                task.steps.append(step)
                task.modified_at = datetime.now(timezone.utc).isoformat()
                
                # Execute step asynchronously
                asyncio.create_task(self._execute_step(task_id, step.step_id))
                
                logger.info(f"Created step {step.step_id} for task {task_id}")
                
                return StepResponse(
                    step_id=step.step_id,
                    task_id=step.task_id,
                    name=step.name,
                    status=step.status,
                    output=step.output,
                    additional_output=step.additional_output,
                    artifacts=[asdict(artifact) for artifact in step.artifacts],
                    is_last=step.is_last
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error creating step for task {task_id}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create step: {str(e)}"
                )
        
        @self.app.get("/ap/v1/agent/tasks/{task_id}/steps", response_model=List[StepResponse])
        async def list_steps(task_id: str):
            """List all steps for a task"""
            try:
                if task_id not in self.tasks:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Task {task_id} not found"
                    )
                
                task = self.tasks[task_id]
                steps = []
                
                for step in task.steps:
                    steps.append(StepResponse(
                        step_id=step.step_id,
                        task_id=step.task_id,
                        name=step.name,
                        status=step.status,
                        output=step.output,
                        additional_output=step.additional_output,
                        artifacts=[asdict(artifact) for artifact in step.artifacts],
                        is_last=step.is_last
                    ))
                
                logger.info(f"Listed {len(steps)} steps for task {task_id}")
                return steps
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error listing steps for task {task_id}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to list steps: {str(e)}"
                )
        
        @self.app.get("/ap/v1/agent/tasks/{task_id}/steps/{step_id}", response_model=StepResponse)
        async def get_step(task_id: str, step_id: str):
            """Get specific step by ID"""
            try:
                if task_id not in self.tasks:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Task {task_id} not found"
                    )
                
                task = self.tasks[task_id]
                step = None
                
                for s in task.steps:
                    if s.step_id == step_id:
                        step = s
                        break
                
                if not step:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Step {step_id} not found in task {task_id}"
                    )
                
                return StepResponse(
                    step_id=step.step_id,
                    task_id=step.task_id,
                    name=step.name,
                    status=step.status,
                    output=step.output,
                    additional_output=step.additional_output,
                    artifacts=[asdict(artifact) for artifact in step.artifacts],
                    is_last=step.is_last
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting step {step_id} for task {task_id}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to get step: {str(e)}"
                )

        @self.app.get("/ap/v1/agent/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "agent_protocol_version": "1.0.0",
                "multi_agent_system": "ready",
                "active_tasks": len(self.tasks),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    async def _execute_task(self, task_id: str):
        """Execute a task using the multi-agent system"""
        try:
            task = self.tasks[task_id]
            task.status = TaskStatus.RUNNING
            task.modified_at = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"Starting execution of task {task_id}")
            
            # Create analysis step
            analysis_step = Step(
                task_id=task_id,
                name="Multi-Agent Analysis",
                status=StepStatus.RUNNING
            )
            task.steps.append(analysis_step)
            
            # Determine task type and route to appropriate agent workflow
            task_input = task.input.lower()
            
            if any(keyword in task_input for keyword in ["customer", "data", "pattern", "churn", "lead"]):
                # Lead Intelligence focused task
                result = await self._execute_lead_intelligence_task(task, analysis_step)
            elif any(keyword in task_input for keyword in ["pricing", "offer", "strategy", "retention", "revenue"]):
                # Revenue Optimization focused task  
                result = await self._execute_revenue_optimization_task(task, analysis_step)
            else:
                # Collaborative task
                result = await self._execute_collaborative_task(task, analysis_step)
            
            # Complete the task
            analysis_step.status = StepStatus.COMPLETED
            analysis_step.output = result.get("summary", "Task completed")
            analysis_step.additional_output = result
            analysis_step.is_last = True
            
            # Create artifacts if results include data
            if "data" in result:
                artifact = Artifact(
                    file_name=f"task_{task_id}_results.json",
                    relative_path=f"results/task_{task_id}_results.json"
                )
                analysis_step.artifacts.append(artifact)
                task.artifacts.append(artifact)
            
            task.status = TaskStatus.COMPLETED
            task.modified_at = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task_id} execution failed: {str(e)}")
            task.status = TaskStatus.FAILED
            task.modified_at = datetime.now(timezone.utc).isoformat()
            
            if task.steps:
                task.steps[-1].status = StepStatus.FAILED
                task.steps[-1].output = f"Task failed: {str(e)}"
                task.steps[-1].is_last = True

    async def _execute_step(self, task_id: str, step_id: str):
        """Execute a specific step"""
        try:
            task = self.tasks[task_id]
            step = None
            
            for s in task.steps:
                if s.step_id == step_id:
                    step = s
                    break
            
            if not step:
                logger.error(f"Step {step_id} not found in task {task_id}")
                return
            
            step.status = StepStatus.RUNNING
            task.modified_at = datetime.now(timezone.utc).isoformat()
            
            # Execute step based on additional input or name
            step_name = step.name or "Custom Step"
            
            # Simple step execution - in real implementation this would be more sophisticated
            step.output = f"Executed {step_name} for task {task_id}"
            step.additional_output = {
                "execution_time": datetime.now(timezone.utc).isoformat(),
                "step_type": "manual",
                "success": True
            }
            
            step.status = StepStatus.COMPLETED
            task.modified_at = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"Step {step_id} completed for task {task_id}")
            
        except Exception as e:
            logger.error(f"Step {step_id} execution failed: {str(e)}")
            if step:
                step.status = StepStatus.FAILED
                step.output = f"Step failed: {str(e)}"

    async def _execute_lead_intelligence_task(self, task: Task, step: Step) -> Dict[str, Any]:
        """Execute task focused on lead intelligence analysis"""
        try:
            # Create sample customer data for demonstration
            sample_data = self._generate_sample_customer_data()
            
            # Use the lead intelligence agent for analysis
            if __name__ == "__main__":
                from src.agents.lead_intelligence_agent import create_lead_intelligence_agent
            else:
                from .lead_intelligence_agent import create_lead_intelligence_agent
            
            lead_agent = create_lead_intelligence_agent() 
            analysis_result = lead_agent.analyze_customer_patterns(sample_data)
            
            return {
                "summary": "Lead Intelligence analysis completed",
                "agent": "Lead Intelligence Agent (DeepSeek)",
                "analysis_type": "customer_pattern_analysis",
                "key_findings": analysis_result.get("agent_insights", []),
                "lead_scores": analysis_result.get("lead_scores", {}),
                "customer_segments": analysis_result.get("customer_segments", {}),
                "data": analysis_result
            }
            
        except Exception as e:
            logger.error(f"Lead intelligence task failed: {str(e)}")
            return {
                "summary": f"Lead Intelligence analysis failed: {str(e)}",
                "agent": "Lead Intelligence Agent (DeepSeek)",
                "error": str(e)
            }

    async def _execute_revenue_optimization_task(self, task: Task, step: Step) -> Dict[str, Any]:
        """Execute task focused on revenue optimization"""
        try:
            # Use the revenue optimization agent
            if __name__ == "__main__":
                from src.agents.revenue_optimization_agent import create_revenue_optimization_agent
            else:
                from .revenue_optimization_agent import create_revenue_optimization_agent
            
            revenue_agent = create_revenue_optimization_agent()
            
            # Example revenue optimization task
            optimization_result = revenue_agent.optimize_customer_offers({
                "customer_segment": "premium_individual",
                "current_plan": "5G Supreme",
                "usage_pattern": "high_data_user",
                "churn_risk": "low"
            })
            
            return {
                "summary": "Revenue optimization analysis completed", 
                "agent": "Revenue Optimization Agent (Llama3)",
                "analysis_type": "offer_optimization",
                "recommendations": optimization_result.get("recommendations", []),
                "pricing_strategy": optimization_result.get("pricing_analysis", {}),
                "data": optimization_result
            }
            
        except Exception as e:
            logger.error(f"Revenue optimization task failed: {str(e)}")
            return {
                "summary": f"Revenue optimization failed: {str(e)}",
                "agent": "Revenue Optimization Agent (Llama3)",
                "error": str(e)
            }

    async def _execute_collaborative_task(self, task: Task, step: Step) -> Dict[str, Any]:
        """Execute collaborative task using both agents"""
        try:
            # Use the full multi-agent system for collaboration
            sample_data = self._generate_sample_customer_data()
            
            result = self.multi_agent_system.run_collaborative_analysis(
                customer_data=sample_data,
                analysis_focus=task.input
            )
            
            return {
                "summary": "Multi-agent collaborative analysis completed",
                "agents": ["Lead Intelligence Agent (DeepSeek)", "Revenue Optimization Agent (Llama3)"],
                "analysis_type": "collaborative_analysis",
                "collaboration_summary": result.get("collaboration_summary", {}),
                "lead_analysis": result.get("lead_analysis", {}),
                "revenue_analysis": result.get("revenue_analysis", {}),
                "data": result
            }
            
        except Exception as e:
            logger.error(f"Collaborative task failed: {str(e)}")
            return {
                "summary": f"Collaborative analysis failed: {str(e)}",
                "agents": ["Lead Intelligence Agent (DeepSeek)", "Revenue Optimization Agent (Llama3)"],
                "error": str(e)
            }

    def _generate_sample_customer_data(self) -> Dict[str, Any]:
        """Generate sample customer data for demonstrations"""
        return {
            "records": [
                {
                    "customer_id": "HK_CUST_001",
                    "monthly_spend": 180.50,
                    "data_usage_gb": 65.2,
                    "active_services": 3,
                    "tenure_months": 28,
                    "plan_type": "5G",
                    "family_lines": 2,
                    "business_features": False,
                    "roaming_usage": 5.2,
                    "support_tickets": 1,
                    "payment_delays": 0,
                    "competitor_usage": 0.1
                },
                {
                    "customer_id": "HK_CUST_002", 
                    "monthly_spend": 45.00,
                    "data_usage_gb": 8.5,
                    "active_services": 1,
                    "tenure_months": 6,
                    "plan_type": "4G",
                    "family_lines": 0,
                    "business_features": False,
                    "roaming_usage": 0,
                    "support_tickets": 3,
                    "payment_delays": 2,
                    "competitor_usage": 0.6
                },
                {
                    "customer_id": "HK_CUST_003",
                    "monthly_spend": 320.00,
                    "data_usage_gb": 120.0,
                    "active_services": 5,
                    "tenure_months": 48,
                    "plan_type": "5G",
                    "family_lines": 4,
                    "business_features": True,
                    "roaming_usage": 15.8,
                    "support_tickets": 0,
                    "payment_delays": 0,
                    "competitor_usage": 0.05
                }
            ]
        }

    def start_server(self, host: str = "127.0.0.1", port: int = 8080):
        """Start the Agent Protocol server"""
        logger.info(f"Starting Agent Protocol server on {host}:{port}")
        logger.info(f"API Documentation available at: http://{host}:{port}/ap/v1/docs")
        
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info"
        )


# Factory function
def create_agent_protocol_server(multi_agent_system: Optional[MultiAgentRevenueSystem] = None) -> AgentProtocolServer:
    """Create and initialize Agent Protocol server"""
    return AgentProtocolServer(multi_agent_system)


# CLI entry point
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Start Agent Protocol server")
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--port", type=int, default=8080, help="Server port")
    
    args = parser.parse_args()
    
    # Create and start server
    server = create_agent_protocol_server()
    server.start_server(host=args.host, port=args.port)
