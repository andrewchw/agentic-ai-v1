"""
Recommendation Generator Module

This module generates personalized, actionable lead recommendations by combining:
- Lead scores from LeadScoringEngine
- Offer matches from ThreeHKBusinessRulesEngine  
- Customer analysis from CustomerDataAnalyzer
- Contextual business factors

It ranks recommendations for maximum business impact and provides explainability.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from enum import Enum

from .customer_analysis import CustomerDataAnalyzer
from .lead_scoring import LeadScoringEngine
from .three_hk_business_rules import ThreeHKBusinessRulesEngine


class RecommendationPriority(Enum):
    """Recommendation priority levels"""
    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"  # Action within 1-2 days
    MEDIUM = "medium"  # Action within 1 week
    LOW = "low"  # Action within 2 weeks
    WATCH = "watch"  # Monitor for changes


class ActionType(Enum):
    """Types of recommended actions"""
    IMMEDIATE_CALL = "immediate_call"
    SCHEDULE_MEETING = "schedule_meeting"
    SEND_PROPOSAL = "send_proposal"
    OFFER_UPGRADE = "offer_upgrade"
    RETENTION_OUTREACH = "retention_outreach"
    CROSS_SELL = "cross_sell"
    UPSELL = "upsell"
    FOLLOW_UP = "follow_up"
    NURTURE = "nurture"
    ESCALATE = "escalate"


@dataclass
class RecommendationExplanation:
    """Explanation for why a recommendation was made"""
    primary_reason: str
    supporting_factors: List[str]
    risk_factors: List[str]
    confidence_score: float
    data_sources: List[str]


@dataclass
class ActionableRecommendation:
    """A complete actionable recommendation for a lead"""
    lead_id: str
    customer_name: str
    recommendation_id: str
    priority: RecommendationPriority
    action_type: ActionType
    title: str
    description: str
    recommended_offers: List[Dict[str, Any]]
    expected_revenue: float
    conversion_probability: float
    urgency_score: float
    business_impact_score: float
    next_steps: List[str]
    talking_points: List[str]
    objection_handling: Dict[str, str]
    explanation: RecommendationExplanation
    created_at: datetime
    expires_at: Optional[datetime]
    tags: List[str]


class RecommendationGenerator:
    """
    Generates and ranks actionable recommendations for lead management
    """

    def __init__(
        self,
        customer_analyzer: CustomerDataAnalyzer,
        lead_scorer: LeadScoringEngine,
        business_rules: ThreeHKBusinessRulesEngine,
    ):
        self.customer_analyzer = customer_analyzer
        self.lead_scorer = lead_scorer
        self.business_rules = business_rules
        self.logger = logging.getLogger(__name__)

        # Business intelligence for Hong Kong telecom market
        self.market_intelligence = {
            "peak_contact_hours": [9, 10, 11, 14, 15, 16],  # 9-11 AM, 2-4 PM
            "optimal_call_days": [1, 2, 3, 4],  # Monday-Thursday
            "average_decision_time": {"enterprise": 45, "sme": 21, "consumer": 7},  # days
            "competitor_strengths": {
                "PCCW": ["fiber_coverage", "enterprise_solutions"],
                "CSL": ["mobile_coverage", "roaming"],
                "China_Mobile": ["mainland_connectivity", "pricing"],
            },
            "seasonal_factors": {
                "q1": 0.85,  # Post-holiday budget constraints
                "q2": 1.0,  # Normal period
                "q3": 0.9,  # Summer slower period
                "q4": 1.15,  # Year-end budget spend
            },
        }

        # Recommendation templates
        self.recommendation_templates = {
            ActionType.IMMEDIATE_CALL: {
                "title": "Urgent: High-Value Lead Ready to Convert",
                "description": "Customer shows strong buying signals and competitive threat. Immediate contact recommended.",
                "next_steps": [
                    "Call within 2 hours during business hours",
                    "Prepare competitive differentiation materials",
                    "Have pricing authority ready for negotiation",
                ],
            },
            ActionType.SCHEDULE_MEETING: {
                "title": "Schedule Discovery Meeting",
                "description": "Customer profile indicates complex needs requiring detailed consultation.",
                "next_steps": [
                    "Send meeting request with agenda",
                    "Prepare customized solution overview",
                    "Research customer's industry challenges",
                ],
            },
            ActionType.SEND_PROPOSAL: {
                "title": "Send Targeted Proposal",
                "description": "Customer requirements are well-defined and match our offerings.",
                "next_steps": [
                    "Generate customized proposal document",
                    "Include ROI calculations and case studies",
                    "Schedule follow-up call for questions",
                ],
            },
            ActionType.OFFER_UPGRADE: {
                "title": "Present Upgrade Opportunity",
                "description": "Current usage patterns indicate readiness for service upgrade.",
                "next_steps": [
                    "Analyze current usage vs. plan limits",
                    "Calculate upgrade benefits and savings",
                    "Present upgrade options with incentives",
                ],
            },
            ActionType.RETENTION_OUTREACH: {
                "title": "Proactive Retention Engagement",
                "description": "Customer showing signs of potential churn or competitive interest.",
                "next_steps": [
                    "Schedule loyalty review call",
                    "Prepare retention incentives",
                    "Address any service issues proactively",
                ],
            },
        }

    def generate_recommendations(
        self, leads_data: pd.DataFrame, max_recommendations: int = 50
    ) -> List[ActionableRecommendation]:
        """
        Generate ranked actionable recommendations for a set of leads
        
        Args:
            leads_data: DataFrame with lead information
            max_recommendations: Maximum number of recommendations to return
            
        Returns:
            List of ranked actionable recommendations
        """
        self.logger.info(f"Generating recommendations for {len(leads_data)} leads")

        recommendations = []

        for _, lead_row in leads_data.iterrows():
            try:
                # Get comprehensive analysis for this lead
                customer_analysis = self._get_customer_analysis(lead_row)
                lead_scores = self._get_lead_scores(lead_row)
                offer_matches = self._get_offer_matches(lead_row, customer_analysis)

                # Generate recommendation based on analysis
                recommendation = self._create_recommendation(
                    lead_row, customer_analysis, lead_scores, offer_matches
                )

                if recommendation:
                    recommendations.append(recommendation)

            except Exception as e:
                self.logger.error(
                    f"Error generating recommendation for lead {lead_row.get('customer_id', 'unknown')}: {e}"
                )
                continue

        # Rank recommendations by business impact
        ranked_recommendations = self._rank_recommendations(recommendations)

        # Apply business constraints and limits
        final_recommendations = self._apply_business_constraints(
            ranked_recommendations, max_recommendations
        )

        self.logger.info(
            f"Generated {len(final_recommendations)} actionable recommendations"
        )
        return final_recommendations

    def _get_customer_analysis(self, lead_row: pd.Series) -> Dict[str, Any]:
        """Get customer analysis from CustomerDataAnalyzer"""
        try:
            # Use single customer analysis method
            analysis = self.customer_analyzer.analyze_single_customer(lead_row.to_dict())
            return analysis if analysis else {}
        except Exception as e:
            self.logger.warning(f"Customer analysis failed: {e}")
            return {}

    def _get_lead_scores(self, lead_row: pd.Series) -> Dict[str, float]:
        """Get lead scores from LeadScoringEngine"""
        try:
            scores = self.lead_scorer.score_single_lead(lead_row.to_dict())
            return scores if scores else {}
        except Exception as e:
            self.logger.warning(f"Lead scoring failed: {e}")
            return {}

    def _get_offer_matches(
        self, lead_row: pd.Series, customer_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get offer matches from ThreeHKBusinessRulesEngine"""
        try:
            offers = self.business_rules.match_offers_for_customer(
                lead_row.to_dict(), customer_analysis
            )
            return offers[:3]  # Top 3 offers
        except Exception as e:
            self.logger.warning(f"Offer matching failed: {e}")
            return []

    def _create_recommendation(
        self,
        lead_row: pd.Series,
        customer_analysis: Dict[str, Any],
        lead_scores: Dict[str, float],
        offer_matches: List[Dict[str, Any]],
    ) -> Optional[ActionableRecommendation]:
        """Create a single actionable recommendation"""
        try:
            # Determine action type based on analysis
            action_type = self._determine_action_type(
                lead_scores, customer_analysis, offer_matches
            )

            # Calculate priority
            priority = self._calculate_priority(lead_scores, customer_analysis)

            # Get template for this action type
            template = self.recommendation_templates.get(
                action_type, self.recommendation_templates[ActionType.FOLLOW_UP]
            )

            # Generate explanation
            explanation = self._generate_explanation(
                lead_scores, customer_analysis, offer_matches, action_type
            )

            # Calculate business metrics
            expected_revenue = self._calculate_expected_revenue(
                offer_matches, lead_scores.get("overall_score", 0)
            )
            conversion_probability = lead_scores.get("conversion_probability", 0.5)

            # Generate talking points and objection handling
            talking_points = self._generate_talking_points(
                customer_analysis, offer_matches
            )
            objection_handling = self._generate_objection_handling(
                customer_analysis, offer_matches
            )

            # Create recommendation
            recommendation = ActionableRecommendation(
                lead_id=str(lead_row.get("customer_id", "")),
                customer_name=lead_row.get("customer_name", "Unknown"),
                recommendation_id=f"REC_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{lead_row.get('customer_id', '')}",
                priority=priority,
                action_type=action_type,
                title=template["title"],
                description=self._customize_description(
                    template["description"], customer_analysis, offer_matches
                ),
                recommended_offers=offer_matches,
                expected_revenue=expected_revenue,
                conversion_probability=conversion_probability,
                urgency_score=self._calculate_urgency_score(
                    customer_analysis, lead_scores
                ),
                business_impact_score=self._calculate_business_impact_score(
                    expected_revenue, conversion_probability, priority
                ),
                next_steps=self._customize_next_steps(
                    template["next_steps"], customer_analysis, offer_matches
                ),
                talking_points=talking_points,
                objection_handling=objection_handling,
                explanation=explanation,
                created_at=datetime.now(),
                expires_at=self._calculate_expiry_date(priority, action_type),
                tags=self._generate_tags(customer_analysis, offer_matches, action_type),
            )

            return recommendation

        except Exception as e:
            self.logger.error(f"Error creating recommendation: {e}")
            return None

    def _determine_action_type(
        self,
        lead_scores: Dict[str, float],
        customer_analysis: Dict[str, Any],
        offer_matches: List[Dict[str, Any]],
    ) -> ActionType:
        """Determine the most appropriate action type"""
        overall_score = lead_scores.get("overall_score", 0)
        conversion_prob = lead_scores.get("conversion_probability", 0)
        urgency = lead_scores.get("urgency_factor", 0)

        # High urgency and high score = immediate call
        if urgency > 0.8 and overall_score > 0.7:
            return ActionType.IMMEDIATE_CALL

        # High conversion probability = schedule meeting
        if conversion_prob > 0.6 and overall_score > 0.6:
            return ActionType.SCHEDULE_MEETING

        # Good offers available = send proposal
        if offer_matches and overall_score > 0.5:
            return ActionType.SEND_PROPOSAL

        # Existing customer with upgrade potential
        if (
            customer_analysis.get("customer_segment") in ["existing_premium", "existing_basic"]
            and overall_score > 0.4
        ):
            return ActionType.OFFER_UPGRADE

        # Low engagement or competitor threat = retention
        if customer_analysis.get("churn_risk", 0) > 0.3:
            return ActionType.RETENTION_OUTREACH

        # Default to follow-up
        return ActionType.FOLLOW_UP

    def _calculate_priority(
        self, lead_scores: Dict[str, float], customer_analysis: Dict[str, Any]
    ) -> RecommendationPriority:
        """Calculate recommendation priority"""
        overall_score = lead_scores.get("overall_score", 0)
        urgency = lead_scores.get("urgency_factor", 0)
        revenue_potential = lead_scores.get("revenue_potential", 0)

        # Critical: High urgency + high score + high revenue
        if urgency > 0.8 and overall_score > 0.7 and revenue_potential > 0.7:
            return RecommendationPriority.CRITICAL

        # High: High score + decent urgency
        if overall_score > 0.6 and urgency > 0.5:
            return RecommendationPriority.HIGH

        # Medium: Moderate scores
        if overall_score > 0.4:
            return RecommendationPriority.MEDIUM

        # Low: Lower scores but still viable
        if overall_score > 0.2:
            return RecommendationPriority.LOW

        return RecommendationPriority.WATCH

    def _generate_explanation(
        self,
        lead_scores: Dict[str, float],
        customer_analysis: Dict[str, Any],
        offer_matches: List[Dict[str, Any]],
        action_type: ActionType,
    ) -> RecommendationExplanation:
        """Generate explanation for the recommendation"""
        
        # Primary reason based on highest scoring factor
        score_factors = {
            "Revenue Potential": lead_scores.get("revenue_potential", 0),
            "Conversion Probability": lead_scores.get("conversion_probability", 0),
            "Urgency Factor": lead_scores.get("urgency_factor", 0),
            "Strategic Value": lead_scores.get("strategic_value", 0),
        }
        
        primary_factor = max(score_factors.items(), key=lambda x: x[1])
        primary_reason = f"High {primary_factor[0]} ({primary_factor[1]:.1%})"

        # Supporting factors
        supporting_factors = []
        if customer_analysis.get("customer_segment"):
            supporting_factors.append(
                f"Customer segment: {customer_analysis['customer_segment']}"
            )
        if offer_matches:
            supporting_factors.append(f"{len(offer_matches)} relevant offers available")
        if lead_scores.get("overall_score", 0) > 0.5:
            supporting_factors.append(
                f"Strong overall lead score ({lead_scores['overall_score']:.1%})"
            )

        # Risk factors
        risk_factors = []
        if customer_analysis.get("churn_risk", 0) > 0.3:
            risk_factors.append("Moderate churn risk detected")
        if lead_scores.get("conversion_probability", 0) < 0.3:
            risk_factors.append("Lower conversion probability")

        # Confidence score based on data quality
        confidence_score = min(
            1.0,
            (
                len([v for v in lead_scores.values() if v > 0]) / 4 * 0.4
                + len([v for v in customer_analysis.values() if v is not None]) / 10 * 0.3
                + len(offer_matches) / 3 * 0.3
            ),
        )

        return RecommendationExplanation(
            primary_reason=primary_reason,
            supporting_factors=supporting_factors,
            risk_factors=risk_factors,
            confidence_score=confidence_score,
            data_sources=["Lead Scoring", "Customer Analysis", "Offer Matching"],
        )

    def _calculate_expected_revenue(
        self, offer_matches: List[Dict[str, Any]], overall_score: float
    ) -> float:
        """Calculate expected revenue from recommendation"""
        if not offer_matches:
            return 0.0

        total_value = sum(
            offer.get("monthly_value", 0) * 12 for offer in offer_matches
        )  # Annual value
        return total_value * overall_score * 0.7  # Apply conversion discount

    def _calculate_urgency_score(
        self, customer_analysis: Dict[str, Any], lead_scores: Dict[str, float]
    ) -> float:
        """Calculate urgency score for the recommendation"""
        base_urgency = lead_scores.get("urgency_factor", 0.3)
        
        # Increase urgency for churn risk
        if customer_analysis.get("churn_risk", 0) > 0.5:
            base_urgency += 0.3
            
        # Increase urgency for competitive threats
        if customer_analysis.get("competitor_interest", False):
            base_urgency += 0.2
            
        return min(1.0, base_urgency)

    def _calculate_business_impact_score(
        self, expected_revenue: float, conversion_probability: float, priority: RecommendationPriority
    ) -> float:
        """Calculate overall business impact score"""
        revenue_score = min(1.0, expected_revenue / 100000)  # Normalize to 100K HKD
        conversion_score = conversion_probability
        
        priority_multiplier = {
            RecommendationPriority.CRITICAL: 1.0,
            RecommendationPriority.HIGH: 0.8,
            RecommendationPriority.MEDIUM: 0.6,
            RecommendationPriority.LOW: 0.4,
            RecommendationPriority.WATCH: 0.2,
        }
        
        return (revenue_score * 0.5 + conversion_score * 0.5) * priority_multiplier[priority]

    def _generate_talking_points(
        self, customer_analysis: Dict[str, Any], offer_matches: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate talking points for the recommendation"""
        talking_points = []
        
        # Customer-specific points
        segment = customer_analysis.get("customer_segment")
        if segment == "enterprise":
            talking_points.extend([
                "Scalable enterprise solutions with dedicated support",
                "Hong Kong's most reliable network infrastructure",
                "Mainland China connectivity advantages"
            ])
        elif segment == "sme":
            talking_points.extend([
                "Cost-effective business solutions",
                "Local Hong Kong support team",
                "Flexible contract terms"
            ])
        else:
            talking_points.extend([
                "Competitive consumer pricing",
                "Wide coverage across Hong Kong",
                "Latest technology offerings"
            ])
            
        # Offer-specific points
        for offer in offer_matches[:2]:  # Top 2 offers
            if offer.get("name"):
                talking_points.append(f"{offer['name']}: {offer.get('key_benefit', 'Enhanced service')}")
                
        return talking_points

    def _generate_objection_handling(
        self, customer_analysis: Dict[str, Any], offer_matches: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Generate objection handling responses"""
        return {
            "price_concern": "Our ROI analysis shows cost savings within 6 months through improved efficiency and reliability.",
            "competitor_comparison": "Three HK offers superior mainland connectivity and local support that competitors can't match.",
            "contract_length": "We offer flexible terms and can structure the agreement to meet your specific timeline needs.",
            "technical_concerns": "Our technical team provides comprehensive migration support and 24/7 monitoring.",
            "timing_issues": "We can phase the implementation to minimize disruption and align with your business calendar."
        }

    def _customize_description(
        self, template_description: str, customer_analysis: Dict[str, Any], offer_matches: List[Dict[str, Any]]
    ) -> str:
        """Customize the description based on customer specifics"""
        custom_desc = template_description
        
        if customer_analysis.get("customer_segment"):
            custom_desc += f" Customer profile indicates {customer_analysis['customer_segment']} segment with specific needs."
            
        if offer_matches:
            custom_desc += f" {len(offer_matches)} targeted offers identified for maximum relevance."
            
        return custom_desc

    def _customize_next_steps(
        self, template_steps: List[str], customer_analysis: Dict[str, Any], offer_matches: List[Dict[str, Any]]
    ) -> List[str]:
        """Customize next steps based on customer specifics"""
        custom_steps = template_steps.copy()
        
        # Add customer-specific steps
        if customer_analysis.get("preferred_contact_time"):
            custom_steps.insert(0, f"Contact during preferred time: {customer_analysis['preferred_contact_time']}")
            
        if offer_matches:
            custom_steps.append(f"Prepare materials for {offer_matches[0].get('name', 'primary offer')}")
            
        return custom_steps

    def _calculate_expiry_date(self, priority: RecommendationPriority, action_type: ActionType) -> Optional[datetime]:
        """Calculate when the recommendation expires"""
        expiry_days = {
            RecommendationPriority.CRITICAL: 1,
            RecommendationPriority.HIGH: 3,
            RecommendationPriority.MEDIUM: 7,
            RecommendationPriority.LOW: 14,
            RecommendationPriority.WATCH: 30,
        }
        
        days = expiry_days.get(priority, 7)
        return datetime.now() + timedelta(days=days)

    def _generate_tags(
        self, customer_analysis: Dict[str, Any], offer_matches: List[Dict[str, Any]], action_type: ActionType
    ) -> List[str]:
        """Generate tags for the recommendation"""
        tags = [action_type.value]
        
        if customer_analysis.get("customer_segment"):
            tags.append(customer_analysis["customer_segment"])
            
        if customer_analysis.get("churn_risk", 0) > 0.5:
            tags.append("churn_risk")
            
        for offer in offer_matches[:2]:
            if offer.get("category"):
                tags.append(offer["category"])
                
        return list(set(tags))  # Remove duplicates

    def _rank_recommendations(self, recommendations: List[ActionableRecommendation]) -> List[ActionableRecommendation]:
        """Rank recommendations by business impact"""
        
        def ranking_score(rec: ActionableRecommendation) -> float:
            # Multi-factor ranking
            priority_weight = {
                RecommendationPriority.CRITICAL: 1.0,
                RecommendationPriority.HIGH: 0.8,
                RecommendationPriority.MEDIUM: 0.6,
                RecommendationPriority.LOW: 0.4,
                RecommendationPriority.WATCH: 0.2,
            }
            
            return (
                rec.business_impact_score * 0.4 +
                priority_weight[rec.priority] * 0.3 +
                rec.conversion_probability * 0.2 +
                rec.urgency_score * 0.1
            )
        
        return sorted(recommendations, key=ranking_score, reverse=True)

    def _apply_business_constraints(
        self, recommendations: List[ActionableRecommendation], max_recommendations: int
    ) -> List[ActionableRecommendation]:
        """Apply business constraints and limits"""
        
        # Limit by maximum number
        limited_recommendations = recommendations[:max_recommendations]
        
        # Ensure priority distribution (don't have too many low priority)
        priority_counts = {}
        final_recommendations = []
        
        priority_limits = {
            RecommendationPriority.CRITICAL: max_recommendations,  # No limit on critical
            RecommendationPriority.HIGH: max_recommendations // 2,
            RecommendationPriority.MEDIUM: max_recommendations // 3,
            RecommendationPriority.LOW: max_recommendations // 4,
            RecommendationPriority.WATCH: max_recommendations // 10,
        }
        
        for rec in limited_recommendations:
            count = priority_counts.get(rec.priority, 0)
            limit = priority_limits.get(rec.priority, max_recommendations)
            
            if count < limit:
                final_recommendations.append(rec)
                priority_counts[rec.priority] = count + 1
        
        return final_recommendations

    def export_recommendations(
        self, recommendations: List[ActionableRecommendation], format: str = "json"
    ) -> Dict[str, Any]:
        """Export recommendations in specified format"""
        
        export_data = {
            "generated_at": datetime.now().isoformat(),
            "total_recommendations": len(recommendations),
            "recommendations": [asdict(rec) for rec in recommendations],
            "summary": {
                "by_priority": {},
                "by_action_type": {},
                "total_expected_revenue": sum(rec.expected_revenue for rec in recommendations),
                "average_conversion_probability": np.mean([rec.conversion_probability for rec in recommendations]) if recommendations else 0,
            }
        }
        
        # Calculate summaries
        for rec in recommendations:
            # Priority summary
            priority_key = rec.priority.value
            if priority_key not in export_data["summary"]["by_priority"]:
                export_data["summary"]["by_priority"][priority_key] = 0
            export_data["summary"]["by_priority"][priority_key] += 1
            
            # Action type summary
            action_key = rec.action_type.value
            if action_key not in export_data["summary"]["by_action_type"]:
                export_data["summary"]["by_action_type"][action_key] = 0
            export_data["summary"]["by_action_type"][action_key] += 1
        
        return export_data


# Example usage and testing functions
def create_sample_recommendations() -> List[ActionableRecommendation]:
    """Create sample recommendations for testing"""
    
    sample_recommendations = [
        ActionableRecommendation(
            lead_id="LEAD_001",
            customer_name="ABC Corporation",
            recommendation_id="REC_20240115_001",
            priority=RecommendationPriority.CRITICAL,
            action_type=ActionType.IMMEDIATE_CALL,
            title="Urgent: High-Value Enterprise Lead Ready to Convert",
            description="Large enterprise customer showing strong buying signals and competitive threat from PCCW. Immediate contact recommended to secure deal.",
            recommended_offers=[
                {"name": "Enterprise Fiber Plus", "monthly_value": 15000, "category": "fiber"},
                {"name": "Cloud Connect Pro", "monthly_value": 8000, "category": "cloud"}
            ],
            expected_revenue=276000.0,  # 24 months * 23K * 0.5 conversion
            conversion_probability=0.75,
            urgency_score=0.9,
            business_impact_score=0.85,
            next_steps=[
                "Call within 2 hours during business hours (9-11 AM, 2-4 PM)",
                "Prepare competitive differentiation vs PCCW fiber",
                "Have enterprise pricing authority ready",
                "Schedule on-site technical assessment"
            ],
            talking_points=[
                "Superior mainland China connectivity vs competitors",
                "Dedicated enterprise support team in Hong Kong",
                "Proven reliability for financial services sector",
                "Scalable cloud integration capabilities"
            ],
            objection_handling={
                "price_concern": "ROI analysis shows 40% cost savings vs current setup within 12 months",
                "competitor_comparison": "Three HK's mainland connectivity is unmatched - 50% faster than PCCW",
                "contract_length": "Flexible 24-month terms with performance guarantees"
            },
            explanation=RecommendationExplanation(
                primary_reason="High Revenue Potential (85%)",
                supporting_factors=[
                    "Enterprise segment with large connectivity needs",
                    "2 high-value offers perfectly matched",
                    "Strong overall lead score (75%)"
                ],
                risk_factors=["Competitive pressure from PCCW"],
                confidence_score=0.9,
                data_sources=["Lead Scoring", "Customer Analysis", "Offer Matching"]
            ),
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=1),
            tags=["immediate_call", "enterprise", "fiber", "cloud", "high_value"]
        )
    ]
    
    return sample_recommendations


if __name__ == "__main__":
    # Basic functionality test
    logging.basicConfig(level=logging.INFO)
    
    print("Recommendation Generator Module Test")
    print("=" * 50)
    
    # Create sample recommendations
    samples = create_sample_recommendations()
    
    print(f"Created {len(samples)} sample recommendations")
    for rec in samples:
        print(f"\nRecommendation: {rec.title}")
        print(f"Priority: {rec.priority.value}")
        print(f"Action: {rec.action_type.value}")
        print(f"Expected Revenue: HK${rec.expected_revenue:,.0f}")
        print(f"Conversion Probability: {rec.conversion_probability:.1%}")
        print(f"Business Impact Score: {rec.business_impact_score:.2f}")
    
    print("\n✅ Recommendation Generator module ready for integration") 