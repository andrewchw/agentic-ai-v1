"""
CrewAI Configuration for Multi-Agent Revenue Assistant
Configures the Lead Intelligence Agent and Revenue Optimization Agent
"""

from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM
import os
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrewAIConfig:
    """Configuration class for CrewAI multi-agent system"""
    
    def __init__(self):
        """Initialize CrewAI configuration with OpenRouter LLMs"""
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
        
        # Configure Llama 3.3 70B LLM for Lead Intelligence Agent (more reliable than DeepSeek R1)
        self.llama_llm = LLM(
            model="openrouter/meta-llama/llama-3.3-70b-instruct:free",
            api_key=self.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.2,
            max_tokens=4000
        )
        
        # Configure Llama3 LLM for Revenue Optimization Agent (using working model)
        self.llama3_llm = LLM(
            model="openrouter/mistralai/mistral-7b-instruct:free",  # Use working model
            api_key=self.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.3,
            max_tokens=4000
        )
        
        logger.info("CrewAI configuration initialized with Llama 3.3 70B and Mistral LLMs")
    
    def create_lead_intelligence_agent(self) -> Agent:
        """Create the Lead Intelligence Agent specialized in data analysis"""
        return Agent(
            role="Lead Intelligence Specialist",
            goal="Analyze customer data, identify patterns, and score leads for maximum revenue potential",
            backstory="""You are an expert data analyst specializing in customer behavior analysis 
            and lead generation for Hong Kong telecom companies. You excel at identifying high-value 
            prospects through pattern recognition and statistical analysis. You work collaboratively 
            with the Revenue Optimization Agent to develop comprehensive business strategies.""",
            
            llm=self.llama_llm,
            verbose=True,
            allow_delegation=True,  # Can delegate tasks to Revenue Optimization Agent
            
            # Agent capabilities and tools
            tools=[],  # Will be populated with data analysis tools
            
            # Agent behavior configuration
            max_iter=3,
            max_execution_time=30,
            system_template="""You are a Lead Intelligence Specialist focused on:
            - Customer data analysis and pattern recognition
            - Lead scoring and prioritization
            - Customer segmentation and profiling
            - Identifying high-value prospects
            
            When you need business strategy advice, delegate to the Revenue Optimization Agent.
            Always maintain privacy by working only with pseudonymized data."""
        )
    
    def create_revenue_optimization_agent(self) -> Agent:
        """Create the Revenue Optimization Agent specialized in business strategy"""
        return Agent(
            role="Revenue Optimization Strategist",
            goal="Develop optimal business strategies, pricing, and offers to maximize revenue growth",
            backstory="""You are a business strategy expert specializing in revenue optimization 
            for Hong Kong telecom companies. You understand Three HK's product portfolio, competitive 
            landscape, and market dynamics. You collaborate with the Lead Intelligence Agent to 
            create data-driven business recommendations.""",
            
            llm=self.llama3_llm,
            verbose=True,
            allow_delegation=True,  # Can delegate data analysis to Lead Intelligence Agent
            
            # Agent capabilities and tools
            tools=[],  # Will be populated with business strategy tools
            
            # Agent behavior configuration
            max_iter=3,
            max_execution_time=30,
            system_template="""You are a Revenue Optimization Strategist focused on:
            - Business strategy and revenue optimization
            - Three HK product and offer matching
            - Pricing strategy and competitive analysis
            - Customer retention and upselling strategies
            
            When you need detailed data analysis, delegate to the Lead Intelligence Agent.
            Always consider Hong Kong market dynamics and Three HK's business objectives."""
        )
    
    def create_customer_analysis_task(self, customer_data: Dict[str, Any]) -> Task:
        """Create a customer analysis task for the Lead Intelligence Agent"""
        return Task(
            description=f"""Analyze the provided customer data and generate insights:
            
            Customer Data Summary:
            - Total customers: {customer_data.get('total_customers', 'Unknown')}
            - Data fields: {', '.join(customer_data.get('fields', []))}
            
            Your analysis should include:
            1. Customer segmentation and profiling
            2. Lead scoring and prioritization
            3. Key patterns and insights
            4. High-value prospect identification
            
            Delegate pricing and offer strategy questions to the Revenue Optimization Agent.
            
            Provide your analysis in a structured format that can be used for business decisions.""",
            
            expected_output="""A comprehensive customer analysis report including:
            - Customer segments with characteristics
            - Lead scores and priorities
            - Key behavioral patterns
            - Recommendations for further analysis""",
            
            agent=None,  # Will be assigned when creating the crew
        )
    
    def create_revenue_strategy_task(self, analysis_results: str) -> Task:
        """Create a revenue optimization task for the Revenue Optimization Agent"""
        return Task(
            description=f"""Based on the lead analysis results, develop optimal revenue strategies:
            
            Analysis Results:
            {analysis_results}
            
            Your strategy should include:
            1. Three HK product and offer matching
            2. Pricing recommendations
            3. Customer retention strategies
            4. Revenue optimization opportunities
            
            Ask the Lead Intelligence Agent for additional data insights if needed.
            
            Provide actionable business recommendations that can be implemented immediately.""",
            
            expected_output="""A comprehensive revenue optimization strategy including:
            - Product/offer recommendations per customer segment
            - Pricing strategies and competitive positioning
            - Retention and upselling opportunities
            - Implementation roadmap with expected ROI""",
            
            agent=None,  # Will be assigned when creating the crew
        )
    
    def create_multi_agent_crew(self, customer_data: Dict[str, Any]) -> Crew:
        """Create and configure the multi-agent crew"""
        # Create agents
        lead_agent = self.create_lead_intelligence_agent()
        revenue_agent = self.create_revenue_optimization_agent()
        
        # Create tasks
        analysis_task = self.create_customer_analysis_task(customer_data)
        strategy_task = self.create_revenue_strategy_task("")
        
        # Assign agents to tasks
        analysis_task.agent = lead_agent
        strategy_task.agent = revenue_agent
        
        # Create crew with sequential processing (analysis first, then strategy)
        crew = Crew(
            agents=[lead_agent, revenue_agent],
            tasks=[analysis_task, strategy_task],
            process=Process.sequential,  # Tasks run in sequence
            verbose=True,
            memory=True,  # Enable crew memory for context sharing
            planning=True,  # Enable planning phase
            embedder={
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small",
                    "api_key": os.getenv("OPENAI_API_KEY", "dummy-key")
                }
            }
        )
        
        logger.info("Multi-agent crew created with Lead Intelligence and Revenue Optimization agents")
        return crew

# Example usage and testing
if __name__ == "__main__":
    try:
        # Initialize configuration
        config = CrewAIConfig()
        
        # Test agent creation
        lead_agent = config.create_lead_intelligence_agent()
        revenue_agent = config.create_revenue_optimization_agent()
        
        print("✅ CrewAI configuration successful!")
        print(f"Lead Intelligence Agent: {lead_agent.role}")
        print(f"Revenue Optimization Agent: {revenue_agent.role}")
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
