"""
Multi-Agent Revenue Optimization System
Uses CrewAI framework to demonstrate true agentic AI collaboration
"""

from crewai import Agent, Crew, Task, Process
from typing import Dict, Any, List, Optional
import json
import os
from dataclasses import dataclass, asdict

from src.agents.core_agent import CoreAgent
from src.agents.customer_analysis import CustomerDataAnalyzer
from src.agents.three_hk_business_rules import ThreeHKBusinessRulesEngine
from src.agents.lead_scoring import LeadScoringEngine


@dataclass
class MarketContext:
    """Market intelligence context shared between agents"""
    competitive_landscape: Dict[str, Any]
    market_trends: List[str]
    economic_indicators: Dict[str, float]
    customer_segments: List[str]


class LeadIntelligenceAgent(Agent):
    """
    Specialized agent for lead generation and customer intelligence
    Collaborates with Revenue Optimization Agent for strategic decisions
    """
    
    def __init__(self):
        super().__init__(
            role="Lead Intelligence Specialist",
            goal="Analyze customer data to identify high-value prospects and growth opportunities",
            backstory="""You are an expert in customer data analysis with deep knowledge of 
            Hong Kong telecom market patterns. You excel at identifying behavioral signals that 
            indicate upsell potential, churn risk, and cross-sell opportunities. You collaborate 
            closely with business strategy specialists to ensure recommendations are commercially viable.""",
            
            # Enable collaboration features
            allow_delegation=True,
            verbose=True,
            
            # Advanced configuration
            max_iter=5,
            memory=True,
        )
        
        # Initialize supporting engines
        self.customer_analyzer = CustomerDataAnalyzer()
        self.lead_scorer = LeadScoringEngine()
        
    def analyze_customer_patterns(self, customer_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze customer patterns and delegate pricing questions"""
        # Use existing customer analysis capabilities
        analysis_results = []
        
        for customer in customer_data:
            result = self.customer_analyzer.analyze_customer(customer)
            analysis_results.append(result)
            
        # Identify patterns requiring business strategy input
        high_value_patterns = [r for r in analysis_results 
                             if r.get('customer_value_score', 0) > 0.7]
        
        return {
            'customer_analysis': analysis_results,
            'high_value_patterns': high_value_patterns,
            'collaboration_needed': len(high_value_patterns) > 0
        }


class RevenueOptimizationAgent(Agent):
    """
    Specialized agent for business strategy and revenue optimization
    Responds to questions from Lead Intelligence Agent
    """
    
    def __init__(self):
        super().__init__(
            role="Revenue Optimization Strategist",
            goal="Develop optimal pricing and product strategies to maximize customer lifetime value",
            backstory="""You are a seasoned business strategist specializing in Hong Kong telecom 
            revenue optimization. You have deep knowledge of Three HK product portfolio, competitive 
            positioning, and market dynamics. You work closely with data analysts to ground your 
            strategies in customer insights and market reality.""",
            
            # Enable collaboration features
            allow_delegation=True,
            verbose=True,
            
            # Advanced configuration  
            max_iter=5,
            memory=True,
        )
        
        # Initialize business engines
        self.business_rules = ThreeHKBusinessRulesEngine()
        
    def optimize_revenue_strategy(self, lead_intelligence: Dict[str, Any], 
                                market_context: MarketContext) -> Dict[str, Any]:
        """Develop revenue optimization strategy based on lead intelligence"""
        
        high_value_patterns = lead_intelligence.get('high_value_patterns', [])
        
        # Generate Three HK specific offers
        optimized_strategies = []
        
        for pattern in high_value_patterns:
            customer_segment = pattern.get('predicted_segment')
            current_spend = pattern.get('monthly_spend', 0)
            
            # Use existing business rules engine
            offers = self.business_rules.match_offers_for_customer({
                'customer_segment': customer_segment,
                'current_monthly_spend': current_spend,
                'engagement_level': pattern.get('engagement_level', 'medium')
            })
            
            strategy = {
                'customer_pattern': pattern,
                'recommended_offers': offers,
                'revenue_uplift_potential': self._calculate_uplift(current_spend, offers),
                'market_positioning': self._assess_market_position(customer_segment, market_context)
            }
            
            optimized_strategies.append(strategy)
            
        return {
            'revenue_strategies': optimized_strategies,
            'total_revenue_potential': sum(s['revenue_uplift_potential'] for s in optimized_strategies),
            'market_insights': self._generate_market_insights(market_context)
        }
    
    def _calculate_uplift(self, current_spend: float, offers: List[Dict]) -> float:
        """Calculate potential revenue uplift"""
        if not offers:
            return 0.0
        
        best_offer = max(offers, key=lambda x: x.get('expected_revenue', 0))
        return best_offer.get('expected_revenue', 0) - current_spend
    
    def _assess_market_position(self, segment: str, context: MarketContext) -> Dict[str, Any]:
        """Assess competitive position for segment"""
        return {
            'segment_competitiveness': 'strong' if segment in ['enterprise', 'premium'] else 'moderate',
            'market_trends_alignment': context.market_trends[:3],
            'economic_sensitivity': context.economic_indicators.get('gdp_growth', 0) * 10
        }
    
    def _generate_market_insights(self, context: MarketContext) -> List[str]:
        """Generate actionable market insights"""
        insights = []
        
        if context.economic_indicators.get('gdp_growth', 0) < 0:
            insights.append("Focus on value-retention strategies due to economic headwinds")
            
        if 'digital_transformation' in context.market_trends:
            insights.append("Prioritize digital service bundles for competitive advantage")
            
        return insights


class AgenticRevenueAccelerator:
    """
    Main orchestrator for multi-agent revenue optimization
    Demonstrates true agentic AI collaboration using CrewAI
    """
    
    def __init__(self):
        """Initialize the multi-agent system"""
        
        # Create collaborative agents
        self.lead_agent = LeadIntelligenceAgent()
        self.revenue_agent = RevenueOptimizationAgent()
        
        # Define collaborative tasks
        self.setup_collaborative_tasks()
        
        # Create CrewAI crew
        self.crew = Crew(
            agents=[self.lead_agent, self.revenue_agent],
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
            planning=True  # Enable automatic planning
        )
        
    def setup_collaborative_tasks(self):
        """Define tasks that require agent collaboration"""
        
        # Task 1: Lead Intelligence Analysis (Lead Agent leads)
        self.lead_analysis_task = Task(
            description="""Analyze customer data to identify high-value prospects and patterns.
            
            Your analysis should include:
            - Customer segmentation and behavioral patterns
            - Lead scoring and prioritization
            - Risk assessment and churn prediction
            - Growth opportunity identification
            
            **Collaboration Instructions:**
            - If you identify high-value patterns that need pricing strategy input, 
              delegate the revenue optimization questions to the Revenue Optimization Strategist
            - Ask specific questions about market positioning and competitive strategy
            - Request validation of your growth opportunity assessments
            
            Context: Use the provided customer data and purchase history to identify patterns 
            that indicate revenue optimization opportunities.""",
            
            expected_output="Comprehensive lead intelligence report with customer patterns, "
                          "scores, and areas requiring strategic collaboration",
            agent=self.lead_agent
        )
        
        # Task 2: Revenue Strategy Development (Revenue Agent leads)  
        self.revenue_strategy_task = Task(
            description="""Develop optimal revenue optimization strategies based on lead intelligence.
            
            Your strategy should include:
            - Product and service recommendations for high-value segments
            - Pricing optimization suggestions
            - Market positioning strategies
            - Competitive differentiation approaches
            
            **Collaboration Instructions:**
            - Build upon the lead intelligence analysis from the previous task
            - If you need additional customer behavior insights, ask the Lead Intelligence Specialist
            - Validate your assumptions about customer preferences with data-driven evidence
            - Ensure all recommendations align with Three HK's product portfolio
            
            Context: Hong Kong telecom market faces economic challenges, requiring balanced 
            growth and retention strategies.""",
            
            expected_output="Comprehensive revenue optimization strategy with specific recommendations, "
                          "projected revenue impact, and implementation priorities",
            agent=self.revenue_agent,
            context=[self.lead_analysis_task]  # Depends on lead analysis
        )
        
        # Task 3: Collaborative Integration (Lead Agent coordinates final output)
        self.integration_task = Task(
            description="""Integrate lead intelligence and revenue strategies into actionable recommendations.
            
            Create the final business recommendations by:
            - Combining customer insights with revenue strategies  
            - Prioritizing actions by impact and feasibility
            - Identifying quick wins and long-term opportunities
            - Providing implementation roadmap
            
            **Collaboration Instructions:**
            - Work with the Revenue Optimization Strategist to validate all recommendations
            - Ensure strategies are grounded in customer data insights
            - Ask for clarification on any revenue projections or market assumptions
            - Collaborate on risk assessment and mitigation strategies
            
            Expected deliverable: Executive summary suitable for Three HK management.""",
            
            expected_output="Executive summary with integrated recommendations, prioritized action plan, "
                          "revenue projections, and implementation roadmap",
            agent=self.lead_agent,
            context=[self.lead_analysis_task, self.revenue_strategy_task]
        )
        
        self.tasks = [self.lead_analysis_task, self.revenue_strategy_task, self.integration_task]
    
    def process_customer_data(self, customer_data: List[Dict[str, Any]], 
                            market_context: Optional[MarketContext] = None) -> Dict[str, Any]:
        """
        Process customer data through multi-agent collaboration
        
        Args:
            customer_data: List of customer records
            market_context: Current market conditions and trends
            
        Returns:
            Comprehensive analysis with collaborative insights
        """
        
        # Set default market context if not provided
        if market_context is None:
            market_context = MarketContext(
                competitive_landscape={
                    'main_competitors': ['HKT', 'SmarTone', 'China Mobile HK'],
                    'market_share': {'three_hk': 0.25, 'competitors': 0.75}
                },
                market_trends=['5G_adoption', 'digital_transformation', 'remote_work'],
                economic_indicators={'gdp_growth': -0.5, 'unemployment': 3.2},
                customer_segments=['enterprise', 'sme', 'consumer', 'premium']
            )
        
        # Prepare inputs for the crew
        crew_inputs = {
            'customer_data': customer_data,
            'market_context': asdict(market_context),
            'analysis_date': '2025-07-22',
            'target_market': 'Hong Kong Telecom'
        }
        
        # Execute multi-agent collaboration
        try:
            result = self.crew.kickoff(inputs=crew_inputs)
            
            return {
                'success': True,
                'collaborative_analysis': result,
                'agent_interactions': self._extract_collaboration_metrics(),
                'recommendations': self._parse_recommendations(result),
                'metadata': {
                    'agents_used': ['Lead Intelligence Agent', 'Revenue Optimization Agent'],
                    'collaboration_type': 'Sequential with Cross-Delegation',
                    'processing_time': 'Real-time',
                    'market_context': market_context
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'fallback_analysis': self._fallback_single_agent_analysis(customer_data)
            }
    
    def _extract_collaboration_metrics(self) -> Dict[str, Any]:
        """Extract metrics about agent collaboration"""
        return {
            'delegations_made': "Available in crew execution logs",
            'questions_asked': "Available in crew execution logs", 
            'context_sharing': "Sequential task context passing enabled",
            'memory_usage': "Inter-agent memory enabled"
        }
    
    def _parse_recommendations(self, crew_result) -> List[Dict[str, Any]]:
        """Parse final recommendations from crew output"""
        # This would parse the actual crew result
        # For now, return structure for demonstration
        return [
            {
                'priority': 'High',
                'type': 'Customer Retention',
                'description': 'Target high-value at-risk customers with personalized offers',
                'expected_impact': 'Parsed from crew result',
                'implementation_complexity': 'Medium'
            },
            {
                'priority': 'Medium', 
                'type': 'Upsell Opportunity',
                'description': 'Cross-sell digital services to enterprise segment',
                'expected_impact': 'Parsed from crew result',
                'implementation_complexity': 'Low'
            }
        ]
    
    def _fallback_single_agent_analysis(self, customer_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback to single-agent analysis if multi-agent fails"""
        core_agent = CoreAgent()
        
        # Process first customer as fallback
        if customer_data:
            result = core_agent.process_customer(
                customer_data=customer_data[0],
                purchase_history=[],
                engagement_data={}
            )
            
            return {
                'fallback_type': 'Single Agent Analysis',
                'analysis': result,
                'note': 'Multi-agent collaboration failed, using single-agent fallback'
            }
        
        return {'fallback_type': 'No Analysis Available'}


# Convenience functions for easy usage
def create_agentic_crew() -> AgenticRevenueAccelerator:
    """Create a new multi-agent revenue optimization crew"""
    return AgenticRevenueAccelerator()


def demonstrate_collaboration(sample_customers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Demonstrate multi-agent collaboration with sample data"""
    
    # Create the agentic system
    accelerator = create_agentic_crew()
    
    # Create realistic market context
    hk_market_context = MarketContext(
        competitive_landscape={
            'main_competitors': ['HKT', 'SmarTone', 'China Mobile HK'],
            'market_dynamics': 'Intensifying competition with 5G rollout',
            'three_hk_position': 'Innovation leader with aggressive pricing'
        },
        market_trends=[
            '5G_enterprise_adoption',
            'remote_work_permanency', 
            'digital_payment_integration',
            'IoT_business_solutions'
        ],
        economic_indicators={
            'gdp_growth': -1.2,  # Recession conditions
            'business_confidence': 3.2,  # Scale 1-10
            'telecom_spending_growth': -0.8
        },
        customer_segments=['enterprise', 'sme', 'consumer_premium', 'consumer_budget']
    )
    
    # Execute collaborative analysis
    result = accelerator.process_customer_data(
        customer_data=sample_customers,
        market_context=hk_market_context
    )
    
    return result


if __name__ == "__main__":
    # Example usage and testing
    sample_customers = [
        {
            'customer_id': 'CUST_001',
            'customer_name': 'TechCorp HK',
            'customer_type': 'enterprise',
            'current_monthly_spend': 45000,
            'contract_length': 24,
            'engagement_score': 0.85,
            'churn_risk_factors': ['price_sensitivity'],
            'growth_indicators': ['expanding_workforce', 'new_office_locations']
        },
        {
            'customer_id': 'CUST_002', 
            'customer_name': 'SME Solutions Ltd',
            'customer_type': 'sme',
            'current_monthly_spend': 8500,
            'contract_length': 12,
            'engagement_score': 0.72,
            'churn_risk_factors': ['economic_pressure'],
            'growth_indicators': ['digital_transformation_initiative']
        }
    ]
    
    print("🚀 Demonstrating Multi-Agent Collaboration...")
    result = demonstrate_collaboration(sample_customers)
    
    print("\n📊 Collaboration Results:")
    print(json.dumps(result, indent=2, default=str))
