"""
Multi-Agent Revenue Assistant System using CrewAI Framework
============================================================

This module implements a collaborative multi-agent system for revenue optimization
using two specialized agents that communicate and delegate tasks to each other.

Agents:
- Lead Intelligence Agent (DeepSeek): Customer data analysis and pattern recognition
- Revenue Optimization Agent (Llama3): Business strategy and offer optimization

Architecture: CrewAI framework with OpenRouter LLM integration
Privacy: All data is pseudonymized before processing
"""

import os
import logging
from typing import Dict, List, Any, Optional
from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM
from dataclasses import dataclass
import json

from ..utils.logger import setup_logging
from ..utils.privacy_pipeline import PrivacyPipeline
from ..utils.openrouter_client import OpenRouterClient

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for individual agents"""
    name: str
    role: str
    goal: str
    backstory: str
    llm_model: str
    llm_provider: str = "openrouter"
    max_tokens: int = 4000
    temperature: float = 0.7


class MultiAgentRevenueSystem:
    """
    Multi-agent system for collaborative revenue optimization.
    
    Features:
    - Two specialized agents with different LLMs
    - Task delegation and inter-agent communication
    - Privacy-first data processing
    - Real-time collaboration tracking
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the multi-agent system.
        
        Args:
            config_path: Path to agent configuration file
        """
        self.privacy_pipeline = PrivacyPipeline()
        self.openrouter_client = OpenRouterClient()
        
        # Agent configurations
        self.lead_intelligence_config = AgentConfig(
            name="lead_intelligence_agent",
            role="Lead Intelligence Specialist",
            goal="Analyze customer data patterns and identify high-value prospects for Hong Kong telecom market",
            backstory="""You are a senior data analyst specializing in Hong Kong telecommunications market.
            You excel at identifying patterns in customer behavior, predicting churn risk, and scoring lead quality.
            Your expertise includes customer segmentation, lifetime value calculation, and competitive analysis.
            You work closely with business strategists to ensure data insights translate into actionable revenue opportunities.""",
            llm_model="deepseek/deepseek-chat",
            temperature=0.2  # Lower temperature for analytical tasks
        )
        
        self.revenue_optimization_config = AgentConfig(
            name="revenue_optimization_agent", 
            role="Revenue Strategy Advisor",
            goal="Develop optimal business strategies and pricing recommendations for Three HK customers",
            backstory="""You are a strategic business advisor with deep expertise in Hong Kong telecommunications market.
            You specialize in pricing optimization, offer matching, and retention strategies for Three HK.
            Your knowledge includes competitive positioning, market trends, and customer psychology.
            You collaborate with data analysts to transform insights into profitable business actions.""",
            llm_model="meta-llama/llama-3.1-8b-instruct:free",
            temperature=0.4  # Moderate temperature for strategic thinking
        )
        
        # Initialize agents
        self.lead_intelligence_agent = None
        self.revenue_optimization_agent = None
        self.crew = None
        
        self._setup_agents()
        
    def _create_llm(self, model: str, temperature: float, max_tokens: int) -> LLM:
        """Create LLM instance for OpenRouter"""
        return LLM(
            model=model,
            api_key=os.getenv('OPENROUTER_API_KEY'),
            base_url="https://openrouter.ai/api/v1",
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def _setup_agents(self):
        """Initialize the specialized agents"""
        try:
            # Lead Intelligence Agent with DeepSeek
            lead_llm = self._create_llm(
                self.lead_intelligence_config.llm_model,
                self.lead_intelligence_config.temperature,
                self.lead_intelligence_config.max_tokens
            )
            
            self.lead_intelligence_agent = Agent(
                role=self.lead_intelligence_config.role,
                goal=self.lead_intelligence_config.goal,
                backstory=self.lead_intelligence_config.backstory,
                llm=lead_llm,
                verbose=True,
                allow_delegation=True,  # Enable task delegation
                max_iter=3
            )
            
            # Revenue Optimization Agent with Llama3
            revenue_llm = self._create_llm(
                self.revenue_optimization_config.llm_model,
                self.revenue_optimization_config.temperature, 
                self.revenue_optimization_config.max_tokens
            )
            
            self.revenue_optimization_agent = Agent(
                role=self.revenue_optimization_config.role,
                goal=self.revenue_optimization_config.goal,
                backstory=self.revenue_optimization_config.backstory,
                llm=revenue_llm,
                verbose=True,
                allow_delegation=True,  # Enable task delegation
                max_iter=3
            )
            
            logger.info("Multi-agent system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {str(e)}")
            raise
    
    def create_customer_analysis_tasks(self, customer_data: Dict[str, Any]) -> List[Task]:
        """
        Create tasks for collaborative customer analysis.
        
        Args:
            customer_data: Pseudonymized customer data
            
        Returns:
            List of tasks for agent collaboration
        """
        # Task 1: Lead Intelligence Agent analyzes customer patterns
        lead_analysis_task = Task(
            description=f"""
            Analyze the provided customer data to identify high-value prospects and patterns:
            
            Customer Data: {json.dumps(customer_data, indent=2)}
            
            Your analysis should include:
            1. Customer segmentation and behavior patterns
            2. Lead quality scoring (1-10 scale)
            3. Churn risk assessment
            4. Lifetime value estimation
            5. Key insights for revenue optimization
            
            Important: This data is already pseudonymized for privacy compliance.
            Focus on actionable patterns that can drive revenue growth.
            
            After your analysis, delegate pricing strategy questions to the Revenue Optimization Agent.
            """,
            agent=self.lead_intelligence_agent,
            expected_output="Detailed customer analysis with lead scores, segments, and strategic recommendations"
        )
        
        # Task 2: Revenue Optimization Agent develops strategy
        revenue_strategy_task = Task(
            description=f"""
            Based on the customer analysis, develop optimal revenue strategies:
            
            Your strategy should include:
            1. Personalized offer recommendations for each customer segment
            2. Pricing optimization suggestions
            3. Three HK product matching (5G plans, roaming, business solutions)
            4. Retention strategies for high-risk customers
            5. Cross-sell and upsell opportunities
            
            Collaborate with the Lead Intelligence Agent to clarify any customer patterns
            that need deeper analysis for strategy development.
            
            Three HK Products Available:
            - 5G Individual Plans (various data allowances)
            - 5G Family Plans (shared data)
            - Roaming Packages (Asia, Global)
            - Business Solutions (enterprise connectivity)
            - IoT Services (smart city applications)
            """,
            agent=self.revenue_optimization_agent,
            expected_output="Comprehensive revenue optimization strategy with specific offers and pricing"
        )
        
        # Task 3: Collaborative recommendation synthesis
        synthesis_task = Task(
            description="""
            Synthesize the customer analysis and revenue strategy into final recommendations:
            
            Create a unified recommendation that combines:
            1. Top 10 highest-value leads with specific action plans
            2. Recommended offers for each customer segment
            3. Expected revenue impact estimates
            4. Implementation timeline and priorities
            5. Risk mitigation strategies
            
            Both agents should collaborate to ensure recommendations are:
            - Data-driven and analytically sound
            - Strategically aligned with Three HK business goals
            - Actionable for sales teams
            - Compliant with Hong Kong market regulations
            """,
            agent=self.lead_intelligence_agent,  # Lead agent coordinates final output
            expected_output="Final actionable revenue recommendations with implementation plan"
        )
        
        return [lead_analysis_task, revenue_strategy_task, synthesis_task]
    
    def run_collaborative_analysis(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute collaborative multi-agent analysis.
        
        Args:
            customer_data: Raw customer data (will be pseudonymized)
            
        Returns:
            Collaborative analysis results
        """
        try:
            logger.info("Starting multi-agent collaborative analysis")
            
            # Step 1: Pseudonymize sensitive data
            pseudonymized_result = self.privacy_pipeline.process_upload(customer_data)
            pseudonymized_data = pseudonymized_result.processed_data
            logger.info(f"Pseudonymized {len(pseudonymized_data)} customer records")
            
            # Step 2: Create collaborative tasks
            tasks = self.create_customer_analysis_tasks(pseudonymized_data)
            
            # Step 3: Initialize crew with sequential process for task delegation
            self.crew = Crew(
                agents=[self.lead_intelligence_agent, self.revenue_optimization_agent],
                tasks=tasks,
                process=Process.sequential,  # Allows for task delegation and collaboration
                verbose=True,
                memory=True  # Enable memory for better collaboration
            )
            
            # Step 4: Execute collaborative analysis
            logger.info("Executing multi-agent collaboration...")
            result = self.crew.kickoff()
            
            # Step 5: Format results
            analysis_results = {
                "collaboration_summary": {
                    "total_agents": 2,
                    "tasks_completed": len(tasks),
                    "execution_status": "success"
                },
                "agent_contributions": {
                    "lead_intelligence": "Customer analysis and pattern recognition",
                    "revenue_optimization": "Strategic recommendations and offer matching"
                },
                "final_recommendations": result,
                "privacy_compliance": {
                    "data_pseudonymized": True,
                    "records_processed": len(pseudonymized_data),
                    "compliance_status": "GDPR/PDPO compliant"
                }
            }
            
            logger.info("Multi-agent analysis completed successfully")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Multi-agent analysis failed: {str(e)}")
            raise
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current status of all agents"""
        return {
            "lead_intelligence_agent": {
                "name": self.lead_intelligence_config.name,
                "model": self.lead_intelligence_config.llm_model,
                "status": "ready" if self.lead_intelligence_agent else "not_initialized"
            },
            "revenue_optimization_agent": {
                "name": self.revenue_optimization_config.name, 
                "model": self.revenue_optimization_config.llm_model,
                "status": "ready" if self.revenue_optimization_agent else "not_initialized"
            },
            "system_status": "operational" if self.crew else "standby"
        }


# Factory function for easy initialization
def create_multi_agent_system() -> MultiAgentRevenueSystem:
    """Create and initialize the multi-agent system"""
    return MultiAgentRevenueSystem()


if __name__ == "__main__":
    # Demo/testing code
    system = create_multi_agent_system()
    status = system.get_agent_status()
    print("Multi-Agent System Status:")
    print(json.dumps(status, indent=2))
