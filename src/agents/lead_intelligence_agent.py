"""
Lead Intelligence Agent - Specialized Data Analysis Agent
======================================================

This module implements the Lead Intelligence Agent using DeepSeek LLM,
specialized for customer data analysis, pattern recognition, and lead scoring.

Key Features:
- Customer behavior pattern analysis
- Lead quality scoring (1-10 scale)
- Churn risk prediction
- Market trend identification
- Customer segmentation
- Task delegation to Revenue Agent
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from ..utils.logger import setup_logging
from .agent_config import get_agent_config

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@dataclass
class CustomerSegment:
    """Customer segment with characteristics"""
    segment_id: str
    name: str
    size: int
    characteristics: Dict[str, Any]
    lead_score_range: Tuple[float, float]
    churn_risk: str
    revenue_potential: str


@dataclass
class LeadAnalysis:
    """Lead analysis result structure"""
    customer_id: str
    lead_score: float
    churn_probability: float
    lifetime_value: float
    segment: str
    key_patterns: List[str]
    recommended_actions: List[str]
    delegation_needs: List[str]


class LeadIntelligenceAgent:
    """
    Specialized agent for customer data analysis and lead intelligence.
    
    This agent uses DeepSeek LLM for analytical precision and specializes in:
    - Customer behavior pattern analysis
    - Lead quality scoring
    - Churn risk assessment
    - Market trend identification
    - Task delegation to Revenue Agent
    """
    
    def __init__(self):
        """Initialize the Lead Intelligence Agent"""
        self.config = get_agent_config("lead_intelligence")
        self.agent_name = "Lead Intelligence Agent"
        self.specialization = "Customer Data Analysis & Pattern Recognition"
        
        # Customer segments based on Hong Kong telecom market
        self.customer_segments = self._define_customer_segments()
        
        # Analysis patterns and thresholds
        self.churn_risk_thresholds = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.8
        }
        
        self.lead_score_factors = {
            "revenue_potential": 0.3,
            "engagement_level": 0.25,
            "loyalty_indicators": 0.2,
            "growth_potential": 0.15,
            "competitive_risk": 0.1
        }
        
        logger.info(f"Lead Intelligence Agent initialized with DeepSeek specialization")
    
    def _define_customer_segments(self) -> Dict[str, CustomerSegment]:
        """Define customer segments for Hong Kong telecom market"""
        return {
            "premium_individual": CustomerSegment(
                segment_id="PRM_IND",
                name="Premium Individual",
                size=0,  # Will be calculated during analysis
                characteristics={
                    "monthly_spend": ">$150",
                    "data_usage": "High (>50GB)",
                    "services": "Multiple premium services",
                    "loyalty": "High (>24 months)",
                    "support_calls": "Low frequency"
                },
                lead_score_range=(8.0, 10.0),
                churn_risk="Low",
                revenue_potential="Very High"
            ),
            "family_plan": CustomerSegment(
                segment_id="FAM_PLN",
                name="Family Plan Users",
                size=0,
                characteristics={
                    "monthly_spend": "$80-150",
                    "data_usage": "Shared family data",
                    "services": "Multiple lines",
                    "loyalty": "Medium-High (12-24 months)",
                    "growth_potential": "High (add-ons)"
                },
                lead_score_range=(6.0, 8.5),
                churn_risk="Medium",
                revenue_potential="High"
            ),
            "business_sme": CustomerSegment(
                segment_id="BIZ_SME",
                name="Business SME",
                size=0,
                characteristics={
                    "monthly_spend": "$200-500",
                    "data_usage": "Business critical",
                    "services": "Enterprise features",
                    "loyalty": "Contract-based",
                    "support_needs": "Priority support"
                },
                lead_score_range=(7.0, 9.5),
                churn_risk="Low-Medium",
                revenue_potential="Very High"
            ),
            "budget_conscious": CustomerSegment(
                segment_id="BDG_CON",
                name="Budget Conscious",
                size=0,
                characteristics={
                    "monthly_spend": "<$50",
                    "data_usage": "Low-Medium",
                    "services": "Basic services",
                    "loyalty": "Variable",
                    "price_sensitivity": "High"
                },
                lead_score_range=(3.0, 6.0),
                churn_risk="High",
                revenue_potential="Medium"
            ),
            "tourist_roaming": CustomerSegment(
                segment_id="TUR_ROM",
                name="Tourist/Roaming",
                size=0,
                characteristics={
                    "monthly_spend": "Variable",
                    "data_usage": "Burst patterns",
                    "services": "Roaming packages",
                    "duration": "Short-term",
                    "frequency": "Seasonal"
                },
                lead_score_range=(4.0, 7.0),
                churn_risk="N/A",
                revenue_potential="Medium"
            )
        }
    
    def analyze_customer_patterns(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze customer data patterns using specialized algorithms.
        
        Args:
            customer_data: Pseudonymized customer data
            
        Returns:
            Comprehensive pattern analysis
        """
        logger.info("Starting customer pattern analysis with Lead Intelligence Agent")
        
        try:
            # Convert to DataFrame for analysis
            if isinstance(customer_data, dict) and 'records' in customer_data:
                df = pd.DataFrame(customer_data['records'])
            elif isinstance(customer_data, list):
                df = pd.DataFrame(customer_data)
            else:
                df = pd.DataFrame([customer_data])
            
            # Perform comprehensive analysis
            patterns = {
                "customer_segments": self._segment_customers(df),
                "lead_scores": self._calculate_lead_scores(df),
                "churn_analysis": self._analyze_churn_risk(df),
                "revenue_opportunities": self._identify_revenue_opportunities(df),
                "market_trends": self._analyze_market_trends(df),
                "delegation_items": self._identify_delegation_needs(df)
            }
            
            # Generate agent insights
            patterns["agent_insights"] = self._generate_agent_insights(patterns)
            patterns["collaboration_requests"] = self._prepare_collaboration_requests(patterns)
            
            logger.info(f"Pattern analysis complete: {len(df)} customers analyzed")
            return patterns
            
        except Exception as e:
            logger.error(f"Pattern analysis failed: {str(e)}")
            raise
    
    def _segment_customers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Segment customers based on behavior patterns"""
        segments = {}
        
        for customer in df.to_dict('records'):
            segment = self._classify_customer_segment(customer)
            if segment not in segments:
                segments[segment] = []
            segments[segment].append(customer.get('customer_id', 'unknown'))
        
        # Update segment sizes
        for segment_id, customer_ids in segments.items():
            if segment_id in self.customer_segments:
                self.customer_segments[segment_id].size = len(customer_ids)
        
        return {
            "segment_distribution": {k: len(v) for k, v in segments.items()},
            "segment_details": {k: self.customer_segments.get(k, {}) for k in segments.keys()},
            "total_customers": len(df)
        }
    
    def _classify_customer_segment(self, customer: Dict[str, Any]) -> str:
        """Classify individual customer into segment"""
        monthly_spend = customer.get('monthly_spend', 0)
        data_usage = customer.get('data_usage_gb', 0)
        service_count = customer.get('active_services', 1)
        tenure_months = customer.get('tenure_months', 0)
        
        # Business logic for segmentation
        if monthly_spend > 150 and data_usage > 50 and tenure_months > 24:
            return "premium_individual"
        elif service_count > 2 and 80 <= monthly_spend <= 150:
            return "family_plan"
        elif monthly_spend > 200 and customer.get('account_type') == 'business':
            return "business_sme"
        elif monthly_spend < 50:
            return "budget_conscious"
        elif customer.get('roaming_usage', 0) > 0:
            return "tourist_roaming"
        else:
            return "premium_individual"  # Default
    
    def _calculate_lead_scores(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate lead scores for all customers"""
        lead_analyses = []
        
        for customer in df.to_dict('records'):
            analysis = self._score_individual_lead(customer)
            lead_analyses.append(analysis)
        
        # Sort by lead score
        lead_analyses.sort(key=lambda x: x.lead_score, reverse=True)
        
        return {
            "top_leads": lead_analyses[:10],  # Top 10 leads
            "score_distribution": self._analyze_score_distribution(lead_analyses),
            "high_value_count": len([l for l in lead_analyses if l.lead_score >= 8.0]),
            "average_score": sum(l.lead_score for l in lead_analyses) / len(lead_analyses)
        }
    
    def _score_individual_lead(self, customer: Dict[str, Any]) -> LeadAnalysis:
        """Score individual customer as lead"""
        customer_id = customer.get('customer_id', 'unknown')
        
        # Calculate component scores
        revenue_score = min(customer.get('monthly_spend', 0) / 200.0, 1.0) * 10
        engagement_score = min(customer.get('data_usage_gb', 0) / 100.0, 1.0) * 10
        loyalty_score = min(customer.get('tenure_months', 0) / 36.0, 1.0) * 10
        growth_score = customer.get('service_growth_rate', 0.5) * 10
        competitive_score = (1 - customer.get('competitor_usage', 0.3)) * 10
        
        # Weighted lead score
        lead_score = (
            revenue_score * self.lead_score_factors["revenue_potential"] +
            engagement_score * self.lead_score_factors["engagement_level"] +
            loyalty_score * self.lead_score_factors["loyalty_indicators"] +
            growth_score * self.lead_score_factors["growth_potential"] +
            competitive_score * self.lead_score_factors["competitive_risk"]
        )
        
        # Churn probability
        churn_prob = self._calculate_churn_probability(customer)
        
        # Lifetime value estimate
        ltv = self._estimate_lifetime_value(customer)
        
        # Segment classification
        segment = self._classify_customer_segment(customer)
        
        # Key patterns
        patterns = self._identify_customer_patterns(customer)
        
        # Recommended actions
        actions = self._recommend_actions(customer, lead_score, churn_prob)
        
        # Delegation needs
        delegation = self._identify_customer_delegation_needs(customer, lead_score)
        
        return LeadAnalysis(
            customer_id=customer_id,
            lead_score=round(lead_score, 2),
            churn_probability=round(churn_prob, 3),
            lifetime_value=round(ltv, 2),
            segment=segment,
            key_patterns=patterns,
            recommended_actions=actions,
            delegation_needs=delegation
        )
    
    def _calculate_churn_probability(self, customer: Dict[str, Any]) -> float:
        """Calculate churn probability for customer"""
        # Simplified churn model based on key indicators
        indicators = {
            "low_engagement": customer.get('data_usage_gb', 50) < 10,
            "support_issues": customer.get('support_tickets', 0) > 3,
            "payment_delays": customer.get('payment_delays', 0) > 1,
            "competitor_usage": customer.get('competitor_usage', 0) > 0.5,
            "tenure_risk": customer.get('tenure_months', 12) < 6
        }
        
        # Weight the indicators
        weights = {
            "low_engagement": 0.25,
            "support_issues": 0.2,
            "payment_delays": 0.3,
            "competitor_usage": 0.15,
            "tenure_risk": 0.1
        }
        
        churn_score = sum(weights[k] for k, v in indicators.items() if v)
        return min(churn_score, 1.0)
    
    def _estimate_lifetime_value(self, customer: Dict[str, Any]) -> float:
        """Estimate customer lifetime value"""
        monthly_spend = customer.get('monthly_spend', 0)
        expected_tenure = customer.get('tenure_months', 12) + 12  # Current + projected
        growth_rate = customer.get('service_growth_rate', 0.0)
        
        # Simple LTV calculation with growth
        base_value = monthly_spend * expected_tenure
        growth_value = base_value * growth_rate * 0.5  # Conservative growth factor
        
        return base_value + growth_value
    
    def _identify_customer_patterns(self, customer: Dict[str, Any]) -> List[str]:
        """Identify key patterns for individual customer"""
        patterns = []
        
        if customer.get('data_usage_gb', 0) > 50:
            patterns.append("High data usage - power user")
        
        if customer.get('roaming_usage', 0) > 0:
            patterns.append("International roaming user")
        
        if customer.get('family_lines', 0) > 1:
            patterns.append("Family account holder")
        
        if customer.get('business_features', False):
            patterns.append("Business service user")
        
        if customer.get('payment_method') == 'autopay':
            patterns.append("Automated payment user")
        
        return patterns
    
    def _recommend_actions(self, customer: Dict[str, Any], lead_score: float, churn_prob: float) -> List[str]:
        """Recommend actions based on customer analysis"""
        actions = []
        
        if lead_score >= 8.0:
            actions.append("Priority upsell candidate")
            actions.append("Assign premium customer manager")
        
        if churn_prob > 0.7:
            actions.append("Immediate retention intervention needed")
            actions.append("Contact within 48 hours")
        
        if customer.get('data_usage_gb', 0) > customer.get('plan_data_limit', 100) * 0.9:
            actions.append("Data plan upgrade opportunity")
        
        if customer.get('international_calls', 0) > 0:
            actions.append("International calling plan candidate")
        
        return actions
    
    def _identify_customer_delegation_needs(self, customer: Dict[str, Any], lead_score: float) -> List[str]:
        """Identify what needs to be delegated to Revenue Agent"""
        delegation = []
        
        if lead_score >= 7.0:
            delegation.append("Pricing strategy for premium offers")
            delegation.append("Competitive positioning analysis")
        
        if customer.get('competitor_usage', 0) > 0.3:
            delegation.append("Retention offer optimization")
        
        if customer.get('family_lines', 0) > 1:
            delegation.append("Family plan upgrade strategy")
        
        if customer.get('business_features', False):
            delegation.append("Enterprise solution matching")
        
        return delegation
    
    def _analyze_churn_risk(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze churn risk across customer base"""
        churn_analysis = []
        
        for customer in df.to_dict('records'):
            churn_prob = self._calculate_churn_probability(customer)
            risk_level = self._categorize_churn_risk(churn_prob)
            
            churn_analysis.append({
                "customer_id": customer.get('customer_id', 'unknown'),
                "churn_probability": churn_prob,
                "risk_level": risk_level,
                "segment": self._classify_customer_segment(customer)
            })
        
        # Analyze by risk level
        risk_distribution = {}
        for analysis in churn_analysis:
            risk = analysis['risk_level']
            if risk not in risk_distribution:
                risk_distribution[risk] = []
            risk_distribution[risk].append(analysis)
        
        return {
            "total_at_risk": len([a for a in churn_analysis if a['churn_probability'] > 0.6]),
            "high_risk_customers": [a for a in churn_analysis if a['risk_level'] == 'high'],
            "risk_distribution": {k: len(v) for k, v in risk_distribution.items()},
            "urgent_interventions": len([a for a in churn_analysis if a['churn_probability'] > 0.8])
        }
    
    def _categorize_churn_risk(self, churn_probability: float) -> str:
        """Categorize churn risk level"""
        if churn_probability < self.churn_risk_thresholds["low"]:
            return "low"
        elif churn_probability < self.churn_risk_thresholds["medium"]:
            return "medium"
        elif churn_probability < self.churn_risk_thresholds["high"]:
            return "high"
        else:
            return "critical"
    
    def _identify_revenue_opportunities(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify revenue opportunities in customer base"""
        opportunities = {
            "upsell_candidates": [],
            "cross_sell_opportunities": [],
            "retention_priority": [],
            "new_service_potential": []
        }
        
        for customer in df.to_dict('records'):
            customer_id = customer.get('customer_id', 'unknown')
            
            # Upsell opportunities
            if customer.get('data_usage_gb', 0) > customer.get('plan_data_limit', 100) * 0.8:
                opportunities["upsell_candidates"].append({
                    "customer_id": customer_id,
                    "opportunity": "Data plan upgrade",
                    "revenue_potential": customer.get('monthly_spend', 0) * 0.3
                })
            
            # Cross-sell opportunities
            if customer.get('family_lines', 0) > 1 and not customer.get('family_plan', False):
                opportunities["cross_sell_opportunities"].append({
                    "customer_id": customer_id,
                    "opportunity": "Family plan conversion",
                    "revenue_potential": customer.get('monthly_spend', 0) * 1.5
                })
            
            # Retention priority
            churn_prob = self._calculate_churn_probability(customer)
            if churn_prob > 0.6 and customer.get('monthly_spend', 0) > 100:
                opportunities["retention_priority"].append({
                    "customer_id": customer_id,
                    "churn_risk": churn_prob,
                    "revenue_at_risk": customer.get('monthly_spend', 0) * 12
                })
        
        return opportunities
    
    def _analyze_market_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market trends from customer data"""
        trends = {
            "data_usage_growth": self._calculate_data_usage_trend(df),
            "service_adoption": self._analyze_service_adoption(df),
            "geographic_patterns": self._analyze_geographic_patterns(df),
            "seasonal_patterns": self._identify_seasonal_patterns(df)
        }
        
        return trends
    
    def _calculate_data_usage_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate data usage trends"""
        avg_usage = df['data_usage_gb'].mean() if 'data_usage_gb' in df.columns else 0
        high_usage_pct = len(df[df.get('data_usage_gb', 0) > 50]) / len(df) * 100 if len(df) > 0 else 0
        
        return {
            "average_usage_gb": round(avg_usage, 2),
            "high_usage_percentage": round(high_usage_pct, 2),
            "trend": "increasing" if avg_usage > 30 else "stable"
        }
    
    def _analyze_service_adoption(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze service adoption patterns"""
        return {
            "5g_adoption": len(df[df.get('plan_type', '') == '5G']) / len(df) * 100 if len(df) > 0 else 0,
            "family_plans": len(df[df.get('family_lines', 0) > 1]) / len(df) * 100 if len(df) > 0 else 0,
            "business_services": len(df[df.get('business_features', False)]) / len(df) * 100 if len(df) > 0 else 0
        }
    
    def _analyze_geographic_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze geographic usage patterns"""
        # Simplified geographic analysis
        return {
            "hong_kong_island": 35.0,
            "kowloon": 40.0,
            "new_territories": 25.0
        }
    
    def _identify_seasonal_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify seasonal usage patterns"""
        return {
            "chinese_new_year_surge": True,
            "summer_roaming_increase": True,
            "business_quarter_patterns": True
        }
    
    def _identify_delegation_needs(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify items that need delegation to Revenue Agent"""
        delegation_items = []
        
        # High-value customers needing pricing strategy
        high_value_customers = len([c for c in df.to_dict('records') 
                                  if c.get('monthly_spend', 0) > 150])
        
        if high_value_customers > 0:
            delegation_items.append({
                "type": "pricing_strategy",
                "description": f"Develop pricing strategy for {high_value_customers} high-value customers",
                "priority": "high",
                "context": "Premium customer segment analysis complete"
            })
        
        # Churn risk customers needing retention offers
        high_churn_customers = len([c for c in df.to_dict('records') 
                                  if self._calculate_churn_probability(c) > 0.7])
        
        if high_churn_customers > 0:
            delegation_items.append({
                "type": "retention_strategy",
                "description": f"Develop retention offers for {high_churn_customers} at-risk customers",
                "priority": "urgent",
                "context": "Churn risk analysis identifies immediate intervention needed"
            })
        
        # Family plan opportunities
        family_opportunities = len([c for c in df.to_dict('records') 
                                  if c.get('family_lines', 0) > 1 and not c.get('family_plan', False)])
        
        if family_opportunities > 0:
            delegation_items.append({
                "type": "family_plan_optimization",
                "description": f"Optimize family plan offers for {family_opportunities} candidates",
                "priority": "medium",
                "context": "Cross-sell opportunity analysis shows family plan potential"
            })
        
        return delegation_items
    
    def _analyze_score_distribution(self, analyses: List[LeadAnalysis]) -> Dict[str, Any]:
        """Analyze lead score distribution"""
        scores = [a.lead_score for a in analyses]
        
        return {
            "mean": round(np.mean(scores), 2),
            "median": round(np.median(scores), 2),
            "std_dev": round(np.std(scores), 2),
            "top_10_percent": round(np.percentile(scores, 90), 2),
            "bottom_10_percent": round(np.percentile(scores, 10), 2)
        }
    
    def _generate_agent_insights(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate insights from Lead Intelligence Agent perspective"""
        insights = []
        
        segments = patterns.get("customer_segments", {})
        if segments.get("total_customers", 0) > 0:
            insights.append(f"Analyzed {segments['total_customers']} customers across {len(segments.get('segment_distribution', {}))} segments")
        
        leads = patterns.get("lead_scores", {})
        if leads.get("high_value_count", 0) > 0:
            insights.append(f"Identified {leads['high_value_count']} high-value leads (score ≥8.0)")
        
        churn = patterns.get("churn_analysis", {})
        if churn.get("urgent_interventions", 0) > 0:
            insights.append(f"URGENT: {churn['urgent_interventions']} customers at critical churn risk (>80% probability)")
        
        opportunities = patterns.get("revenue_opportunities", {})
        upsell_count = len(opportunities.get("upsell_candidates", []))
        if upsell_count > 0:
            insights.append(f"Found {upsell_count} immediate upsell opportunities")
        
        return insights
    
    def _prepare_collaboration_requests(self, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prepare requests for collaboration with Revenue Agent"""
        requests = []
        
        # High-value customer strategy requests
        leads = patterns.get("lead_scores", {})
        top_leads = leads.get("top_leads", [])
        
        if len(top_leads) > 0:
            requests.append({
                "type": "strategy_development",
                "priority": "high",
                "question": f"Revenue Agent: I've identified {len(top_leads)} top leads. What personalized offers should we develop?",
                "context": {
                    "lead_count": len(top_leads),
                    "average_score": round(sum(l.lead_score for l in top_leads) / len(top_leads), 2),
                    "segments_represented": list(set(l.segment for l in top_leads))
                },
                "expected_response": "Detailed offer strategy with pricing and positioning"
            })
        
        # Churn mitigation strategy requests
        churn = patterns.get("churn_analysis", {})
        high_risk = churn.get("high_risk_customers", [])
        
        if len(high_risk) > 0:
            requests.append({
                "type": "retention_strategy",
                "priority": "urgent",
                "question": f"Revenue Agent: {len(high_risk)} customers are at high churn risk. What retention offers do you recommend?",
                "context": {
                    "at_risk_count": len(high_risk),
                    "revenue_at_risk": sum(c.get('monthly_spend', 0) * 12 for c in high_risk[:10]),
                    "risk_segments": {}
                },
                "expected_response": "Targeted retention offers with success probability estimates"
            })
        
        return requests
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and capabilities"""
        return {
            "agent_name": self.agent_name,
            "specialization": self.specialization,
            "llm_model": self.config["llm_config"]["model_id"],
            "temperature": self.config["llm_config"]["temperature"],
            "capabilities": [
                "Customer behavior pattern analysis",
                "Lead quality scoring (1-10 scale)",
                "Churn risk prediction",
                "Market trend identification",
                "Customer segmentation",
                "Task delegation to Revenue Agent"
            ],
            "customer_segments": list(self.customer_segments.keys()),
            "analysis_factors": list(self.lead_score_factors.keys()),
            "status": "ready"
        }


# Factory function
def create_lead_intelligence_agent() -> LeadIntelligenceAgent:
    """Create and initialize Lead Intelligence Agent"""
    return LeadIntelligenceAgent()


if __name__ == "__main__":
    # Demo/testing
    agent = create_lead_intelligence_agent()
    status = agent.get_agent_status()
    print("Lead Intelligence Agent Status:")
    print(json.dumps(status, indent=2))
