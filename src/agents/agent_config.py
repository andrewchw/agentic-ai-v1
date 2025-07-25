"""
Agent Configuration for Multi-Agent Revenue System
=================================================

This module defines the configuration and behavior patterns for the 
two specialized agents in the revenue optimization system.
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
import json


@dataclass 
class LLMConfig:
    """Configuration for LLM providers and models"""
    provider: str
    model_id: str
    base_url: str
    max_tokens: int = 4000
    temperature: float = 0.7
    api_key_env: str = "OPENROUTER_API_KEY"


@dataclass
class AgentPersonality:
    """Agent personality and behavior configuration"""
    communication_style: str
    decision_making_approach: str
    collaboration_preferences: List[str]
    expertise_areas: List[str]


class AgentConfigManager:
    """Manages configuration for all agents in the system"""
    
    def __init__(self):
        self.configs = self._load_agent_configs()
    
    def _load_agent_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load agent configurations"""
        return {
            "lead_intelligence": self._get_lead_intelligence_config(),
            "revenue_optimization": self._get_revenue_optimization_config()
        }
    
    def _get_lead_intelligence_config(self) -> Dict[str, Any]:
        """Configuration for Lead Intelligence Agent using DeepSeek"""
        return {
            "agent_info": {
                "name": "Lead Intelligence Agent",
                "code_name": "intelligence_agent",
                "role": "Senior Data Intelligence Specialist",
                "department": "Customer Analytics"
            },
            "llm_config": asdict(LLMConfig(
                provider="openrouter",
                model_id="qwen/qwen3-coder:free",  # Changed to FREE model
                base_url="https://openrouter.ai/api/v1",
                max_tokens=4000,
                temperature=0.2,  # Lower temperature for analytical precision
                api_key_env="OPENROUTER_API_KEY"
            )),
            "personality": asdict(AgentPersonality(
                communication_style="analytical_and_precise",
                decision_making_approach="data_driven_systematic",
                collaboration_preferences=[
                    "shares_detailed_analysis",
                    "asks_clarifying_questions", 
                    "provides_statistical_context",
                    "delegates_strategy_questions"
                ],
                expertise_areas=[
                    "customer_segmentation",
                    "behavioral_pattern_analysis", 
                    "churn_prediction",
                    "lead_quality_scoring",
                    "lifetime_value_calculation",
                    "competitive_intelligence",
                    "hong_kong_telecom_market"
                ]
            )),
            "goals": [
                "Identify high-value customer prospects with 90%+ accuracy",
                "Predict churn risk within 7-day accuracy window", 
                "Segment customers into actionable business categories",
                "Calculate realistic lifetime value projections",
                "Provide statistically significant insights for strategy development"
            ],
            "task_specializations": [
                "customer_data_analysis",
                "pattern_recognition", 
                "lead_scoring",
                "risk_assessment",
                "market_trend_analysis"
            ],
            "collaboration_protocols": {
                "with_revenue_agent": {
                    "delegates_to": ["pricing_strategy", "offer_optimization", "retention_tactics"],
                    "requests_from": ["market_positioning", "competitive_pricing", "product_fit_analysis"],
                    "shares": ["customer_insights", "behavioral_patterns", "risk_scores"]
                }
            }
        }
    
    def _get_revenue_optimization_config(self) -> Dict[str, Any]:
        """Configuration for Revenue Optimization Agent using Llama3"""
        return {
            "agent_info": {
                "name": "Revenue Optimization Agent",
                "code_name": "revenue_agent", 
                "role": "Senior Business Strategy Advisor",
                "department": "Revenue Management"
            },
            "llm_config": asdict(LLMConfig(
                provider="openrouter",
                model_id="mistralai/mistral-7b-instruct:free",  # Use working model
                base_url="https://openrouter.ai/api/v1", 
                max_tokens=4000,
                temperature=0.4,  # Moderate temperature for creative strategy
                api_key_env="OPENROUTER_API_KEY"
            )),
            "personality": asdict(AgentPersonality(
                communication_style="strategic_and_consultative",
                decision_making_approach="business_outcome_focused",
                collaboration_preferences=[
                    "provides_strategic_context",
                    "asks_for_data_validation",
                    "offers_multiple_scenarios", 
                    "delegates_analytical_deep_dives"
                ],
                expertise_areas=[
                    "revenue_optimization",
                    "pricing_strategy", 
                    "offer_personalization",
                    "customer_retention",
                    "three_hk_product_portfolio",
                    "hong_kong_regulatory_compliance",
                    "competitive_positioning"
                ]
            )),
            "goals": [
                "Maximize customer lifetime value through optimal offers",
                "Reduce churn by 15%+ through targeted retention strategies",
                "Increase average revenue per user (ARPU) by 20%+",
                "Match customers to optimal Three HK products with 85%+ satisfaction", 
                "Develop competitive pricing strategies for Hong Kong market"
            ],
            "task_specializations": [
                "pricing_optimization",
                "offer_personalization",
                "retention_strategy_development", 
                "product_portfolio_matching",
                "competitive_analysis"
            ],
            "collaboration_protocols": {
                "with_intelligence_agent": {
                    "delegates_to": ["deep_data_analysis", "pattern_validation", "risk_quantification"],
                    "requests_from": ["customer_behavior_insights", "segment_characteristics", "predictive_analytics"], 
                    "shares": ["strategy_recommendations", "pricing_models", "offer_frameworks"]
                }
            },
            "three_hk_knowledge_base": {
                "product_categories": [
                    "5G_individual_plans",
                    "5G_family_plans", 
                    "roaming_packages",
                    "business_solutions",
                    "iot_services"
                ],
                "pricing_tiers": ["basic", "standard", "premium", "enterprise"],
                "target_segments": ["individual", "family", "sme", "enterprise", "tourist"],
                "competitive_advantages": [
                    "extensive_5g_coverage",
                    "competitive_roaming_rates", 
                    "innovative_digital_services",
                    "strong_customer_support"
                ]
            }
        }
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get configuration for specific agent"""
        if agent_name not in self.configs:
            raise ValueError(f"Unknown agent: {agent_name}")
        return self.configs[agent_name]
    
    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get all agent configurations"""
        return self.configs
    
    def get_collaboration_matrix(self) -> Dict[str, Any]:
        """Get inter-agent collaboration rules"""
        return {
            "collaboration_flow": {
                "sequential_tasks": [
                    "intelligence_agent_analyzes_data",
                    "revenue_agent_develops_strategy", 
                    "joint_recommendation_synthesis"
                ],
                "delegation_patterns": {
                    "intelligence_to_revenue": [
                        "pricing_strategy_questions",
                        "offer_optimization_requests",
                        "competitive_positioning_queries"
                    ],
                    "revenue_to_intelligence": [
                        "data_validation_requests", 
                        "deeper_analysis_needs",
                        "pattern_confirmation_queries"
                    ]
                }
            },
            "communication_protocols": {
                "formal_handoffs": ["completed_analysis", "strategy_recommendations"],
                "informal_queries": ["clarification_questions", "validation_requests"],
                "collaborative_tasks": ["final_synthesis", "recommendation_review"]
            }
        }


# Global configuration instance
agent_config_manager = AgentConfigManager()


def get_agent_config(agent_name: str) -> Dict[str, Any]:
    """Convenience function to get agent configuration"""
    return agent_config_manager.get_agent_config(agent_name)


def get_collaboration_rules() -> Dict[str, Any]:
    """Convenience function to get collaboration matrix"""
    return agent_config_manager.get_collaboration_matrix()


if __name__ == "__main__":
    # Demo configuration display
    configs = agent_config_manager.get_all_configs()
    print("Agent Configurations:")
    print(json.dumps(configs, indent=2))
    
    print("\nCollaboration Matrix:")
    collaboration = agent_config_manager.get_collaboration_matrix()
    print(json.dumps(collaboration, indent=2))
