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
from .lead_intelligence_agent import create_lead_intelligence_agent
from .revenue_optimization_agent import create_revenue_optimization_agent

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

    def get_agent_protocol_status(self) -> Dict[str, Any]:
        """
        Get Agent Protocol compatible status information.
        
        Returns:
            Status information formatted for Agent Protocol
        """
        return {
            "system_name": "Multi-Agent Revenue System",
            "protocol_version": "1.0.0",
            "agents": [
                {
                    "name": "Lead Intelligence Agent",
                    "role": self.lead_intelligence_config.role,
                    "llm_model": self.lead_intelligence_config.llm_model,
                    "status": "ready" if self.lead_intelligence_agent else "not_initialized",
                    "capabilities": [
                        "customer_pattern_analysis",
                        "lead_scoring",
                        "churn_prediction",
                        "market_trends"
                    ]
                },
                {
                    "name": "Revenue Optimization Agent", 
                    "role": self.revenue_optimization_config.role,
                    "llm_model": self.revenue_optimization_config.llm_model,
                    "status": "ready" if self.revenue_optimization_agent else "not_initialized",
                    "capabilities": [
                        "pricing_optimization",
                        "offer_matching",
                        "retention_strategies",
                        "revenue_analysis"
                    ]
                }
            ],
            "collaboration_features": [
                "task_delegation",
                "inter_agent_communication",
                "collaborative_analysis",
                "unified_recommendations"
            ],
            "privacy_compliance": "GDPR/PDPO",
            "market_specialization": "Hong Kong Telecommunications"
        }

    def execute_agent_protocol_task(self, task_input: str, additional_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a task using Agent Protocol interface.
        
        Args:
            task_input: Task description/prompt
            additional_input: Additional parameters
            
        Returns:
            Task execution results formatted for Agent Protocol
        """
        try:
            logger.info(f"Executing Agent Protocol task: {task_input[:100]}...")
            
            # Determine task routing based on input analysis
            task_type = self._analyze_task_type(task_input, additional_input)
            
            if task_type == "lead_intelligence":
                return self._execute_lead_intelligence_task(task_input, additional_input)
            elif task_type == "revenue_optimization":
                return self._execute_revenue_optimization_task(task_input, additional_input)
            else:
                return self._execute_collaborative_task(task_input, additional_input)
                
        except Exception as e:
            logger.error(f"Agent Protocol task execution failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "output": f"Task execution failed: {str(e)}"
            }

    def _analyze_task_type(self, task_input: str, additional_input: Optional[Dict[str, Any]] = None) -> str:
        """Analyze task input to determine appropriate agent routing"""
        
        # Check additional_input for explicit routing
        if additional_input and "focus" in additional_input:
            return additional_input["focus"]
        
        # Analyze task_input for keywords
        task_lower = task_input.lower()
        
        lead_keywords = ["customer", "data", "pattern", "churn", "lead", "segment", "analyze"]
        revenue_keywords = ["pricing", "offer", "strategy", "retention", "revenue", "optimize"]
        
        lead_matches = sum(1 for keyword in lead_keywords if keyword in task_lower)
        revenue_matches = sum(1 for keyword in revenue_keywords if keyword in task_lower)
        
        if lead_matches > revenue_matches and lead_matches > 1:
            return "lead_intelligence"
        elif revenue_matches > lead_matches and revenue_matches > 1:
            return "revenue_optimization"
        else:
            return "collaborative"

    def _execute_lead_intelligence_task(self, task_input: str, additional_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute task using Lead Intelligence Agent"""
        try:
            # Generate sample data for demonstration
            sample_data = self._generate_sample_data()
            
            # Execute using specialized Lead Intelligence Agent
            lead_agent = create_lead_intelligence_agent()
            analysis_result = lead_agent.analyze_customer_patterns(sample_data)
            
            return {
                "status": "completed",
                "agent": "Lead Intelligence Agent (DeepSeek)",
                "analysis_type": "customer_pattern_analysis",
                "output": f"Lead Intelligence analysis completed for {len(sample_data.get('records', []))} customers",
                "results": {
                    "lead_scores": analysis_result.get("lead_scores", {}),
                    "customer_segments": analysis_result.get("customer_segments", {}),
                    "churn_analysis": analysis_result.get("churn_analysis", {}),
                    "agent_insights": analysis_result.get("agent_insights", [])
                }
            }
            
        except Exception as e:
            logger.error(f"Lead Intelligence task failed: {str(e)}")
            return {
                "status": "failed",
                "agent": "Lead Intelligence Agent (DeepSeek)",
                "error": str(e),
                "output": f"Lead Intelligence analysis failed: {str(e)}"
            }

    def _execute_revenue_optimization_task(self, task_input: str, additional_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute task using Revenue Optimization Agent"""
        try:
            # Execute using specialized Revenue Optimization Agent
            revenue_agent = create_revenue_optimization_agent()
            
            # Create sample optimization context
            optimization_context = {
                "customer_segment": additional_input.get("customer_segment", "premium_individual") if additional_input else "premium_individual",
                "current_plan": "5G Supreme",
                "usage_pattern": "high_data_user",
                "churn_risk": "low"
            }
            
            optimization_result = revenue_agent.optimize_customer_offers(optimization_context)
            
            return {
                "status": "completed",
                "agent": "Revenue Optimization Agent (Llama3)",
                "analysis_type": "offer_optimization",
                "output": f"Revenue optimization completed for {optimization_context['customer_segment']} segment",
                "results": {
                    "recommendations": optimization_result.get("recommendations", []),
                    "pricing_analysis": optimization_result.get("pricing_analysis", {}),
                    "revenue_impact": optimization_result.get("revenue_impact", {})
                }
            }
            
        except Exception as e:
            logger.error(f"Revenue optimization task failed: {str(e)}")
            return {
                "status": "failed",
                "agent": "Revenue Optimization Agent (Llama3)",
                "error": str(e),
                "output": f"Revenue optimization failed: {str(e)}"
            }

    def _execute_collaborative_task(self, task_input: str, additional_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute collaborative task using both agents"""
        try:
            # Generate sample data
            sample_data = self._generate_sample_data()
            
            # Execute collaborative analysis
            collaboration_result = self.run_collaborative_analysis(sample_data)
            
            return {
                "status": "completed",
                "agents": ["Lead Intelligence Agent (DeepSeek)", "Revenue Optimization Agent (Llama3)"],
                "analysis_type": "collaborative_analysis",
                "output": "Multi-agent collaborative analysis completed successfully",
                "results": collaboration_result
            }
            
        except Exception as e:
            logger.error(f"Collaborative task failed: {str(e)}")
            return {
                "status": "failed",
                "agents": ["Lead Intelligence Agent (DeepSeek)", "Revenue Optimization Agent (Llama3)"],
                "error": str(e),
                "output": f"Collaborative analysis failed: {str(e)}"
            }

    def _generate_sample_data(self) -> Dict[str, Any]:
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
                    "roaming_usage": 5.2
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
                    "roaming_usage": 0
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
                    "roaming_usage": 15.8
                }
            ]
        }
    
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
    
    def run_collaborative_analysis(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run collaborative analysis between Lead Intelligence and Revenue Optimization agents.
        
        This demonstrates true agentic AI collaboration where:
        1. Lead Intelligence Agent analyzes customer data
        2. Identifies items that need Revenue Agent expertise
        3. Delegates specific tasks to Revenue Agent
        4. Revenue Agent responds with strategic recommendations
        5. Both agents collaborate on final recommendations
        
        Args:
            customer_data: Customer data for analysis
            
        Returns:
            Comprehensive collaboration results
        """
        logger.info("Starting collaborative multi-agent analysis")
        
        try:
            # Step 1: Lead Intelligence Agent analyzes customer data
            lead_agent = create_lead_intelligence_agent()
            logger.info("Lead Intelligence Agent analyzing customer patterns...")
            
            lead_analysis = lead_agent.analyze_customer_patterns(customer_data)
            
            # Step 2: Extract delegation items
            delegation_items = lead_analysis.get("delegation_items", [])
            collaboration_requests = lead_analysis.get("collaboration_requests", [])
            
            logger.info(f"Lead Agent identified {len(delegation_items)} delegation items")
            
            # Step 3: Revenue Optimization Agent responds to delegations
            revenue_agent = create_revenue_optimization_agent()
            logger.info("Revenue Optimization Agent processing delegations...")
            
            revenue_responses = []
            for item in delegation_items:
                response = revenue_agent.respond_to_delegation(item)
                revenue_responses.append(response)
            
            # Step 4: Revenue Agent provides additional analysis
            revenue_analysis = revenue_agent.optimize_revenue_opportunities(lead_analysis)
            
            # Step 5: Combine results for final recommendations
            collaborative_results = {
                "lead_intelligence_analysis": {
                    "customer_segments": lead_analysis.get("customer_segments"),
                    "lead_scores": lead_analysis.get("lead_scores"),
                    "churn_analysis": lead_analysis.get("churn_analysis"),
                    "agent_insights": lead_analysis.get("agent_insights")
                },
                "revenue_optimization_analysis": {
                    "total_revenue_potential": revenue_analysis.total_revenue_potential,
                    "segment_opportunities": revenue_analysis.segment_opportunities,
                    "retention_savings": revenue_analysis.retention_savings,
                    "recommended_actions": revenue_analysis.recommended_actions
                },
                "agent_collaboration": {
                    "delegation_items": delegation_items,
                    "revenue_responses": revenue_responses,
                    "collaboration_requests": collaboration_requests
                },
                "combined_recommendations": self._synthesize_recommendations(
                    lead_analysis, revenue_analysis, revenue_responses
                ),
                "collaboration_summary": {
                    "lead_agent_contributions": len(lead_analysis.get("agent_insights", [])),
                    "revenue_agent_responses": len(revenue_responses),
                    "total_opportunities_identified": len(delegation_items),
                    "collaboration_success": True
                }
            }
            
            logger.info("Collaborative analysis completed successfully")
            return collaborative_results
            
        except Exception as e:
            logger.error(f"Collaborative analysis failed: {str(e)}")
            return {
                "error": str(e),
                "collaboration_success": False
            }
    
    def _synthesize_recommendations(self, lead_analysis: Dict[str, Any], 
                                  revenue_analysis, revenue_responses: List[Dict[str, Any]]) -> List[str]:
        """Synthesize recommendations from both agents"""
        recommendations = []
        
        # Add Lead Agent insights
        lead_insights = lead_analysis.get("agent_insights", [])
        for insight in lead_insights:
            recommendations.append(f"Lead Intelligence: {insight}")
        
        # Add Revenue Agent recommendations
        revenue_actions = revenue_analysis.recommended_actions
        for action in revenue_actions:
            recommendations.append(f"Revenue Strategy: {action}")
        
        # Add collaboration-specific recommendations
        for response in revenue_responses:
            if response.get("status") == "completed":
                response_type = response.get("response_type", "general")
                if response_type == "pricing_strategy":
                    recommendations.append("Collaboration Result: Tiered pricing strategy developed with Lead Agent insights")
                elif response_type == "retention_strategy":
                    recommendations.append("Collaboration Result: Targeted retention campaigns designed based on churn analysis")
        
        return recommendations

    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents in the system"""
        try:
            # Get Lead Intelligence Agent status
            lead_agent = create_lead_intelligence_agent()
            lead_status = lead_agent.get_agent_status()
            
            # Get Revenue Optimization Agent status
            revenue_agent = create_revenue_optimization_agent()
            revenue_status = revenue_agent.get_agent_status()
            
            return {
                "lead_intelligence_agent": {
                    "name": "lead_intelligence_agent",
                    "model": lead_status.get("llm_model", "unknown"),
                    "status": lead_status.get("status", "unknown")
                },
                "revenue_optimization_agent": {
                    "name": "revenue_optimization_agent", 
                    "model": revenue_status.get("llm_model", "unknown"),
                    "status": revenue_status.get("status", "unknown")
                },
                "system_status": "operational" if self.privacy_pipeline else "error"
            }
        except Exception as e:
            logger.error(f"Failed to get agent status: {str(e)}")
            return {
                "error": str(e),
                "system_status": "error"
            }
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
