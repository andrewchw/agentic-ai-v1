"""
Lead Scoring and Prioritization Engine for Agentic AI Revenue Assistant

This module implements sophisticated lead scoring and prioritization algorithms
specifically designed for Hong Kong telecom revenue optimization. It builds upon
the customer analysis algorithms to provide actionable lead rankings for sales teams.

Key Features:
- Multi-factor lead scoring with telecom-specific KPIs
- Revenue potential assessment and conversion probability modeling
- Urgency and strategic value analysis
- Hong Kong market-specific business rules
- Priority queue management and dynamic ranking
- Explainable scoring with detailed breakdowns
- Integration with Three HK business logic
- Compliance with telecom industry best practices
"""

import os
import json
import time
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import math
from collections import defaultdict, Counter
import warnings

# Import customer analysis components
try:
    from .customer_analysis import CustomerDataAnalyzer, FeatureSet, PatternAnalysis, CustomerSegment
except ImportError:
    from customer_analysis import CustomerDataAnalyzer, FeatureSet, PatternAnalysis, CustomerSegment

# Import Three HK business rules (optional integration)
try:
    from .three_hk_business_rules import ThreeHKBusinessRulesEngine, OfferMatch

    THREE_HK_INTEGRATION_AVAILABLE = True
except ImportError:
    try:
        from three_hk_business_rules import ThreeHKBusinessRulesEngine, OfferMatch

        THREE_HK_INTEGRATION_AVAILABLE = True
    except ImportError:
        THREE_HK_INTEGRATION_AVAILABLE = False
        # Suppress warning during package initialization to avoid circular import noise
        # The integration works fine when modules are imported individually

# Configure logging
logger = logging.getLogger(__name__)


class LeadPriority(Enum):
    """Lead priority levels for sales team routing."""

    CRITICAL = "critical"  # Immediate attention required
    HIGH = "high"  # Priority follow-up within 24 hours
    MEDIUM = "medium"  # Standard follow-up within 48 hours
    LOW = "low"  # Routine follow-up within 7 days
    NURTURE = "nurture"  # Long-term nurturing required


class ScoringCategory(Enum):
    """Main categories for lead scoring."""

    REVENUE_POTENTIAL = "revenue_potential"
    CONVERSION_PROBABILITY = "conversion_probability"
    URGENCY_FACTOR = "urgency_factor"
    STRATEGIC_VALUE = "strategic_value"


class LeadQualification(Enum):
    """Lead qualification levels."""

    HOT = "hot"  # Ready to buy, high intent
    WARM = "warm"  # Interested, needs nurturing
    COLD = "cold"  # Minimal interest, long-term prospect
    UNQUALIFIED = "unqualified"  # Does not meet criteria


@dataclass
class LeadScore:
    """Container for comprehensive lead scoring results."""

    # Core scoring components
    revenue_potential: float = 0.0  # Expected revenue value (0-100)
    conversion_probability: float = 0.0  # Likelihood to convert (0-100)
    urgency_factor: float = 0.0  # Time sensitivity (0-100)
    strategic_value: float = 0.0  # Long-term value (0-100)

    # Composite scores
    overall_score: float = 0.0  # Weighted composite (0-100)
    priority_score: float = 0.0  # Priority ranking (0-100)

    # Classifications
    lead_priority: LeadPriority = LeadPriority.MEDIUM
    qualification_level: LeadQualification = LeadQualification.COLD

    # Metadata
    score_timestamp: str = ""
    processing_time: float = 0.0
    confidence_level: float = 0.0  # Model confidence (0-1)

    # Explainability
    key_factors: Optional[List[str]] = None
    risk_factors: Optional[List[str]] = None
    opportunities: Optional[List[str]] = None
    recommended_actions: Optional[List[str]] = None

    def __post_init__(self):
        if not self.score_timestamp:
            self.score_timestamp = datetime.now().isoformat()
        if self.key_factors is None:
            self.key_factors = []
        if self.risk_factors is None:
            self.risk_factors = []
        if self.opportunities is None:
            self.opportunities = []
        if self.recommended_actions is None:
            self.recommended_actions = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return asdict(self)


@dataclass
class PrioritizedLead:
    """Container for prioritized lead with full context."""

    # Lead identification
    customer_id: str
    lead_id: str = ""

    # Customer context
    customer_features: Optional[FeatureSet] = None
    customer_segment: Optional[CustomerSegment] = None

    # Scoring results
    lead_score: Optional[LeadScore] = None

    # Prioritization context
    queue_position: int = 0
    assigned_rep: Optional[str] = None
    follow_up_date: Optional[str] = None

    # Business context
    relevant_offers: Optional[List[str]] = None
    campaign_context: Optional[Dict[str, Any]] = None
    competitive_intel: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if not self.lead_id:
            self.lead_id = f"lead_{self.customer_id}_{int(time.time())}"
        if self.relevant_offers is None:
            self.relevant_offers = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class LeadScoringEngine:
    """
    Comprehensive lead scoring and prioritization engine for Hong Kong telecom market.

    This engine integrates with the CustomerDataAnalyzer to provide sophisticated
    lead qualification, scoring, and prioritization capabilities specifically
    designed for telecom revenue optimization.
    """

    def __init__(self, customer_analyzer: Optional[CustomerDataAnalyzer] = None):
        """
        Initialize the lead scoring engine.

        Args:
            customer_analyzer: CustomerDataAnalyzer instance for feature extraction
        """
        self.customer_analyzer = customer_analyzer or CustomerDataAnalyzer()

        # Initialize Three HK business rules integration if available
        if THREE_HK_INTEGRATION_AVAILABLE:
            self.three_hk_engine = ThreeHKBusinessRulesEngine()
            logger.info("Three HK Business Rules integration enabled")
        else:
            self.three_hk_engine = None
            logger.info("Three HK Business Rules integration not available")

        # Scoring model weights (should be trained/validated with historical data)
        self.scoring_weights = {
            "revenue_potential": 0.35,  # 35% - Expected revenue impact
            "conversion_probability": 0.30,  # 30% - Likelihood to convert
            "urgency_factor": 0.20,  # 20% - Time sensitivity
            "strategic_value": 0.15,  # 15% - Long-term strategic importance
        }

        # Hong Kong telecom market parameters
        self.hk_market_params = {
            "average_deal_size": 1200.0,  # HKD monthly
            "premium_deal_size": 2500.0,  # HKD monthly
            "enterprise_deal_size": 5000.0,  # HKD monthly
            "conversion_rates": {
                "premium_business": 0.25,
                "urban_professional": 0.18,
                "family_subscriber": 0.15,
                "young_digital": 0.20,
                "budget_conscious": 0.08,
                "enterprise_client": 0.35,
                "high_value_loyalist": 0.40,
            },
            "urgency_multipliers": {
                "contract_expiring": 2.0,
                "competitor_offer": 1.8,
                "service_complaint": 1.5,
                "usage_spike": 1.3,
                "plan_inadequate": 1.4,
            },
        }

        # Three HK specific business rules
        self.three_hk_rules = {
            "minimum_spend_qualification": 200.0,  # HKD monthly
            "tenure_preference": {"new_customer_bonus": 1.2, "loyalty_bonus": 1.1, "churner_penalty": 0.8},
            "location_multipliers": {
                "premium_business": 1.3,
                "urban_residential": 1.1,
                "suburban_family": 1.0,
                "remote_areas": 0.9,
            },
            "compliance_requirements": {
                "data_privacy_consent": True,
                "marketing_opt_in": True,
                "age_verification": True,
            },
        }

        # Priority thresholds
        self.priority_thresholds = {
            "critical": 85.0,  # 85+ overall score
            "high": 70.0,  # 70+ overall score
            "medium": 50.0,  # 50+ overall score
            "low": 30.0,  # 30+ overall score
            # Below 30 = nurture
        }

        # Qualification thresholds
        self.qualification_thresholds = {
            "hot": 75.0,  # 75+ conversion probability
            "warm": 50.0,  # 50+ conversion probability
            "cold": 25.0,  # 25+ conversion probability
            # Below 25 = unqualified
        }

        logger.info("LeadScoringEngine initialized with Hong Kong telecom parameters")

    def score_lead(
        self,
        customer_data: Dict[str, Any],
        purchase_history: List[Dict[str, Any]],
        engagement_data: Optional[Dict[str, Any]] = None,
        market_context: Optional[Dict[str, Any]] = None,
    ) -> LeadScore:
        """
        Generate comprehensive lead score for a customer.

        Args:
            customer_data: Customer profile information
            purchase_history: Historical purchase records
            engagement_data: Customer engagement metrics
            market_context: Market and competitive context

        Returns:
            Comprehensive lead scoring results
        """
        start_time = time.time()

        try:
            # Extract customer features using the analyzer
            features = self.customer_analyzer.extract_customer_features(
                customer_data, purchase_history, engagement_data
            )

            # Analyze behavioral patterns
            patterns = self.customer_analyzer.analyze_customer_patterns(
                customer_data, purchase_history, engagement_data
            )

            # Score each category
            revenue_score = self._score_revenue_potential(features, patterns, market_context)
            conversion_score = self._score_conversion_probability(features, patterns, market_context)
            urgency_score = self._score_urgency_factor(features, patterns, market_context)
            strategic_score = self._score_strategic_value(features, patterns, market_context)

            # Calculate composite scores
            overall_score = (
                revenue_score * self.scoring_weights["revenue_potential"]
                + conversion_score * self.scoring_weights["conversion_probability"]
                + urgency_score * self.scoring_weights["urgency_factor"]
                + strategic_score * self.scoring_weights["strategic_value"]
            )

            # Calculate priority score (considers urgency more heavily)
            priority_score = overall_score * 0.7 + urgency_score * 0.3

            # Determine classifications
            lead_priority = self._classify_priority(priority_score)
            qualification = self._classify_qualification(conversion_score)

            # Calculate confidence level
            confidence = self._calculate_confidence(features, patterns)

            # Generate explainability
            key_factors = self._identify_key_factors(
                features,
                patterns,
                {
                    "revenue": revenue_score,
                    "conversion": conversion_score,
                    "urgency": urgency_score,
                    "strategic": strategic_score,
                },
            )

            risk_factors = self._identify_risk_factors(features, patterns)
            opportunities = self._identify_opportunities(features, patterns)
            actions = self._recommend_actions(features, patterns, lead_priority, qualification)

            processing_time = time.time() - start_time

            lead_score = LeadScore(
                revenue_potential=revenue_score,
                conversion_probability=conversion_score,
                urgency_factor=urgency_score,
                strategic_value=strategic_score,
                overall_score=overall_score,
                priority_score=priority_score,
                lead_priority=lead_priority,
                qualification_level=qualification,
                processing_time=processing_time,
                confidence_level=confidence,
                key_factors=key_factors,
                risk_factors=risk_factors,
                opportunities=opportunities,
                recommended_actions=actions,
            )

            logger.debug(
                f"Lead scored: {overall_score:.1f} overall, {conversion_score:.1f} conversion, {lead_priority.value} priority"
            )

            return lead_score

        except Exception as e:
            logger.error(f"Lead scoring failed: {e}")
            return LeadScore(
                overall_score=0.0,
                priority_score=0.0,
                lead_priority=LeadPriority.NURTURE,
                qualification_level=LeadQualification.UNQUALIFIED,
                processing_time=time.time() - start_time,
                confidence_level=0.0,
            )

    def prioritize_leads(
        self, lead_scores: List[Tuple[str, LeadScore]], constraints: Optional[Dict[str, Any]] = None
    ) -> List[PrioritizedLead]:
        """
        Prioritize and rank leads for sales team assignment.

        Args:
            lead_scores: List of (customer_id, LeadScore) tuples
            constraints: Optional constraints for prioritization

        Returns:
            Ranked list of prioritized leads
        """
        try:
            constraints = constraints or {}
            max_leads = constraints.get("max_leads", 100)
            min_score_threshold = constraints.get("min_score_threshold", 20.0)

            # Filter leads by minimum score
            qualified_leads = [
                (customer_id, score) for customer_id, score in lead_scores if score.overall_score >= min_score_threshold
            ]

            # Sort by priority score (descending)
            sorted_leads = sorted(
                qualified_leads,
                key=lambda x: (x[1].priority_score, x[1].urgency_factor, x[1].revenue_potential),
                reverse=True,
            )

            # Limit to max leads
            top_leads = sorted_leads[:max_leads]

            # Create prioritized lead objects
            prioritized_leads = []
            for position, (customer_id, lead_score) in enumerate(top_leads, 1):
                prioritized_lead = PrioritizedLead(
                    customer_id=customer_id,
                    lead_score=lead_score,
                    queue_position=position,
                    follow_up_date=self._calculate_follow_up_date(lead_score.lead_priority),
                )

                # Add relevant offers based on score (enhanced matching if customer data available)
                prioritized_lead.relevant_offers = self._match_relevant_offers(lead_score)

                prioritized_leads.append(prioritized_lead)

            logger.info(f"Prioritized {len(prioritized_leads)} leads from {len(lead_scores)} candidates")

            return prioritized_leads

        except Exception as e:
            logger.error(f"Lead prioritization failed: {e}")
            return []

    def batch_score_leads(
        self, customer_datasets: List[Dict[str, Any]], market_context: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, LeadScore]]:
        """
        Score multiple leads in batch for efficiency.

        Args:
            customer_datasets: List of customer data for scoring
            market_context: Market context for all leads

        Returns:
            List of (customer_id, LeadScore) tuples
        """
        try:
            scored_leads = []

            for i, data in enumerate(customer_datasets):
                customer_data = data.get("customer_data", {})
                purchase_history = data.get("purchase_history", [])
                engagement_data = data.get("engagement_data", {})

                customer_id = customer_data.get("customer_id", f"unknown_{i}")

                lead_score = self.score_lead(customer_data, purchase_history, engagement_data, market_context)

                scored_leads.append((customer_id, lead_score))

                # Log progress for large batches
                if (i + 1) % 50 == 0:
                    logger.info(f"Scored {i + 1}/{len(customer_datasets)} leads")

            logger.info(f"Batch scoring completed: {len(scored_leads)} leads processed")

            return scored_leads

        except Exception as e:
            logger.error(f"Batch lead scoring failed: {e}")
            return []

    def _score_revenue_potential(
        self, features: FeatureSet, patterns: List[PatternAnalysis], market_context: Optional[Dict[str, Any]]
    ) -> float:
        """Score revenue potential (0-100)."""
        try:
            revenue_score = 0.0

            # Base revenue from current spend (40%)
            current_spend_normalized = min(
                100.0, (features.monthly_spend / self.hk_market_params["premium_deal_size"]) * 100
            )
            revenue_score += current_spend_normalized * 0.4

            # Upsell potential (30%)
            upsell_score = features.upsell_propensity * 100
            revenue_score += upsell_score * 0.3

            # Customer value tier (20%)
            value_tier_score = features.customer_value_score * 100
            revenue_score += value_tier_score * 0.2

            # Account type multiplier (10%)
            account_multipliers = {
                "enterprise": 100.0,
                "business": 80.0,
                "premium": 70.0,
                "family": 50.0,
                "standard": 40.0,
            }
            account_score = account_multipliers.get(features.account_type, 40.0)
            revenue_score += account_score * 0.1

            # Apply Hong Kong market adjustments
            location_multiplier = self.three_hk_rules["location_multipliers"].get(features.location_category, 1.0)
            revenue_score *= location_multiplier

            return min(100.0, max(0.0, revenue_score))

        except Exception as e:
            logger.warning(f"Revenue potential scoring error: {e}")
            return 50.0  # Default neutral score

    def _score_conversion_probability(
        self, features: FeatureSet, patterns: List[PatternAnalysis], market_context: Optional[Dict[str, Any]]
    ) -> float:
        """Score conversion probability (0-100)."""
        try:
            conversion_score = 0.0

            # Base conversion rate by segment (40%)
            segment_rates = self.hk_market_params["conversion_rates"]
            base_rate = segment_rates.get(features.hk_market_segment, 0.12)  # Default 12%
            conversion_score += (base_rate * 100) * 0.4

            # Engagement factor (25%)
            engagement_score = features.digital_engagement * 100
            conversion_score += engagement_score * 0.25

            # Satisfaction factor (20%)
            satisfaction_normalized = min(100.0, (features.satisfaction_score / 10.0) * 100)
            conversion_score += satisfaction_normalized * 0.2

            # Purchase behavior (15%)
            purchase_scores = {"high": 90.0, "medium": 60.0, "low": 30.0}
            purchase_score = purchase_scores.get(features.purchase_frequency, 30.0)
            conversion_score += purchase_score * 0.15

            # Adjust for churn risk (penalty)
            churn_penalty = features.churn_risk_score * 30  # Up to 30 point penalty
            conversion_score -= churn_penalty

            # Tenure adjustment
            tenure_bonus = self.three_hk_rules["tenure_preference"]
            if features.tenure_category == "new":
                conversion_score *= tenure_bonus["new_customer_bonus"]
            elif features.tenure_category == "loyal":
                conversion_score *= tenure_bonus["loyalty_bonus"]
            elif features.churn_risk_score > 0.7:
                conversion_score *= tenure_bonus["churner_penalty"]

            return min(100.0, max(0.0, conversion_score))

        except Exception as e:
            logger.warning(f"Conversion probability scoring error: {e}")
            return 50.0

    def _score_urgency_factor(
        self, features: FeatureSet, patterns: List[PatternAnalysis], market_context: Optional[Dict[str, Any]]
    ) -> float:
        """Score urgency factor (0-100)."""
        try:
            urgency_score = 30.0  # Base urgency

            # Churn risk urgency (40%)
            if features.churn_risk_score >= 0.8:
                urgency_score += 40.0
            elif features.churn_risk_score >= 0.6:
                urgency_score += 25.0
            elif features.churn_risk_score >= 0.4:
                urgency_score += 15.0

            # Complaint urgency (20%)
            if features.complaint_count >= 3:
                urgency_score += 20.0
            elif features.complaint_count >= 1:
                urgency_score += 10.0

            # Competitive pressure (15%)
            if features.competitor_switch_risk >= 0.7:
                urgency_score += 15.0
            elif features.competitor_switch_risk >= 0.5:
                urgency_score += 10.0

            # Satisfaction drop urgency (15%)
            if features.satisfaction_score <= 4.0:
                urgency_score += 15.0
            elif features.satisfaction_score <= 6.0:
                urgency_score += 8.0

            # Engagement drop urgency (10%)
            if features.digital_engagement <= 0.3:
                urgency_score += 10.0
            elif features.digital_engagement <= 0.5:
                urgency_score += 5.0

            # Market context urgency
            if market_context:
                if market_context.get("contract_renewal_season", False):
                    urgency_score *= 1.3
                if market_context.get("competitive_campaign_active", False):
                    urgency_score *= 1.2

            return min(100.0, max(0.0, urgency_score))

        except Exception as e:
            logger.warning(f"Urgency factor scoring error: {e}")
            return 30.0

    def _score_strategic_value(
        self, features: FeatureSet, patterns: List[PatternAnalysis], market_context: Optional[Dict[str, Any]]
    ) -> float:
        """Score strategic value (0-100)."""
        try:
            strategic_score = 0.0

            # Long-term value potential (40%)
            if features.age_group in ["early_career", "mid_career"]:
                strategic_score += 40.0  # Long customer lifetime
            elif features.age_group == "young_adult":
                strategic_score += 35.0
            elif features.age_group == "senior_professional":
                strategic_score += 30.0
            else:
                strategic_score += 20.0

            # Account growth potential (30%)
            if features.account_type == "family" and features.monthly_spend < 800:
                strategic_score += 30.0  # Family expansion potential
            elif features.account_type == "business":
                strategic_score += 25.0  # Business growth potential
            elif features.spend_category in ["budget", "minimal"]:
                strategic_score += 20.0  # Upsell potential
            else:
                strategic_score += 15.0

            # Market influence (20%)
            if features.location_category == "premium_business":
                strategic_score += 20.0  # Influential location
            elif features.hk_market_segment == "urban_professional":
                strategic_score += 15.0  # Trendsetter segment
            elif features.digital_engagement > 0.8:
                strategic_score += 15.0  # Digital influencer
            else:
                strategic_score += 10.0

            # Loyalty potential (10%)
            if features.satisfaction_score >= 8.0:
                strategic_score += 10.0
            elif features.satisfaction_score >= 6.0:
                strategic_score += 7.0
            else:
                strategic_score += 3.0

            return min(100.0, max(0.0, strategic_score))

        except Exception as e:
            logger.warning(f"Strategic value scoring error: {e}")
            return 50.0

    def _classify_priority(self, priority_score: float) -> LeadPriority:
        """Classify lead priority based on score."""
        if priority_score >= self.priority_thresholds["critical"]:
            return LeadPriority.CRITICAL
        elif priority_score >= self.priority_thresholds["high"]:
            return LeadPriority.HIGH
        elif priority_score >= self.priority_thresholds["medium"]:
            return LeadPriority.MEDIUM
        elif priority_score >= self.priority_thresholds["low"]:
            return LeadPriority.LOW
        else:
            return LeadPriority.NURTURE

    def _classify_qualification(self, conversion_score: float) -> LeadQualification:
        """Classify lead qualification based on conversion probability."""
        if conversion_score >= self.qualification_thresholds["hot"]:
            return LeadQualification.HOT
        elif conversion_score >= self.qualification_thresholds["warm"]:
            return LeadQualification.WARM
        elif conversion_score >= self.qualification_thresholds["cold"]:
            return LeadQualification.COLD
        else:
            return LeadQualification.UNQUALIFIED

    def _calculate_confidence(self, features: FeatureSet, patterns: List[PatternAnalysis]) -> float:
        """Calculate model confidence based on data quality."""
        try:
            confidence_factors = []

            # Data completeness
            feature_dict = features.to_dict()
            non_default_features = sum(
                1 for v in feature_dict.values() if v not in [0, 0.0, "", "unknown", "general", "new"]
            )
            total_features = len(feature_dict)
            completeness = non_default_features / total_features
            confidence_factors.append(completeness * 0.4)

            # Pattern confidence
            if patterns:
                avg_pattern_confidence = sum(p.confidence for p in patterns) / len(patterns)
                confidence_factors.append(avg_pattern_confidence * 0.3)
            else:
                confidence_factors.append(0.1)  # Low confidence without patterns

            # Engagement data quality
            if features.digital_engagement > 0:
                confidence_factors.append(0.2)
            else:
                confidence_factors.append(0.05)

            # Tenure reliability
            if features.tenure_category in ["established", "loyal"]:
                confidence_factors.append(0.1)
            else:
                confidence_factors.append(0.05)

            return min(1.0, sum(confidence_factors))

        except Exception as e:
            logger.warning(f"Confidence calculation error: {e}")
            return 0.5

    def _identify_key_factors(
        self, features: FeatureSet, patterns: List[PatternAnalysis], scores: Dict[str, float]
    ) -> List[str]:
        """Identify key factors driving the lead score."""
        factors = []

        # Revenue factors
        if scores["revenue"] >= 70:
            if features.monthly_spend >= 1000:
                factors.append("High current spend")
            if features.upsell_propensity >= 0.7:
                factors.append("Strong upsell potential")
            if features.account_type in ["business", "enterprise"]:
                factors.append("Business account type")

        # Conversion factors
        if scores["conversion"] >= 70:
            if features.digital_engagement >= 0.7:
                factors.append("High digital engagement")
            if features.satisfaction_score >= 8.0:
                factors.append("High satisfaction score")
            if features.purchase_frequency == "high":
                factors.append("Frequent purchaser")

        # Urgency factors
        if scores["urgency"] >= 70:
            if features.churn_risk_score >= 0.7:
                factors.append("High churn risk")
            if features.complaint_count >= 2:
                factors.append("Recent complaints")
            if features.competitor_switch_risk >= 0.6:
                factors.append("Competitive pressure")

        # Strategic factors
        if scores["strategic"] >= 70:
            if features.age_group in ["early_career", "mid_career"]:
                factors.append("Long-term value potential")
            if features.location_category == "premium_business":
                factors.append("Premium market segment")
            if features.account_type == "family":
                factors.append("Family expansion opportunity")

        return factors[:5]  # Top 5 factors

    def _identify_risk_factors(self, features: FeatureSet, patterns: List[PatternAnalysis]) -> List[str]:
        """Identify risk factors that could impact conversion."""
        risks = []

        if features.churn_risk_score >= 0.6:
            risks.append("Elevated churn risk")

        if features.satisfaction_score <= 5.0:
            risks.append("Low satisfaction score")

        if features.complaint_count >= 2:
            risks.append("Multiple recent complaints")

        if features.competitor_switch_risk >= 0.6:
            risks.append("Competitor switching risk")

        if features.digital_engagement <= 0.3:
            risks.append("Low digital engagement")

        if features.monthly_spend < self.three_hk_rules["minimum_spend_qualification"]:
            risks.append("Below minimum spend threshold")

        return risks

    def _identify_opportunities(self, features: FeatureSet, patterns: List[PatternAnalysis]) -> List[str]:
        """Identify revenue opportunities."""
        opportunities = []

        if features.upsell_propensity >= 0.6:
            opportunities.append("Plan upgrade opportunity")

        if features.data_usage_gb > 40 and features.spend_category == "budget":
            opportunities.append("Unlimited data plan upsell")

        if features.account_type != "family" and features.age_group in ["mid_career", "senior_professional"]:
            opportunities.append("Family plan addition")

        if features.roaming_usage == 0 and features.location_category == "premium_business":
            opportunities.append("International roaming package")

        if features.digital_engagement > 0.7:
            opportunities.append("Digital services bundle")

        if features.voice_minutes > 400 and features.spend_category in ["budget", "minimal"]:
            opportunities.append("Voice plan upgrade")

        return opportunities

    def _recommend_actions(
        self,
        features: FeatureSet,
        patterns: List[PatternAnalysis],
        priority: LeadPriority,
        qualification: LeadQualification,
    ) -> List[str]:
        """Recommend specific actions for sales teams."""
        actions = []

        # Priority-based actions
        if priority == LeadPriority.CRITICAL:
            actions.append("Immediate senior rep contact within 4 hours")
            actions.append("Escalate to account management")
        elif priority == LeadPriority.HIGH:
            actions.append("Priority follow-up within 24 hours")
            actions.append("Prepare customized offer presentation")
        elif priority == LeadPriority.MEDIUM:
            actions.append("Standard follow-up within 48 hours")
            actions.append("Send targeted promotional materials")

        # Qualification-based actions
        if qualification == LeadQualification.HOT:
            actions.append("Schedule product demonstration")
            actions.append("Prepare contract documentation")
        elif qualification == LeadQualification.WARM:
            actions.append("Nurture with educational content")
            actions.append("Invite to product webinar")

        # Risk-based actions
        if features.churn_risk_score >= 0.7:
            actions.append("Retention specialist consultation")
            actions.append("Offer loyalty incentives")

        # Opportunity-based actions
        if features.upsell_propensity >= 0.7:
            actions.append("Present premium plan options")
            actions.append("Highlight value-added services")

        return actions[:4]  # Top 4 actions

    def _calculate_follow_up_date(self, priority: LeadPriority) -> str:
        """Calculate recommended follow-up date based on priority."""
        now = datetime.now()

        if priority == LeadPriority.CRITICAL:
            follow_up = now + timedelta(hours=4)
        elif priority == LeadPriority.HIGH:
            follow_up = now + timedelta(days=1)
        elif priority == LeadPriority.MEDIUM:
            follow_up = now + timedelta(days=2)
        elif priority == LeadPriority.LOW:
            follow_up = now + timedelta(days=7)
        else:  # NURTURE
            follow_up = now + timedelta(days=30)

        return follow_up.isoformat()

    def _match_relevant_offers(
        self,
        lead_score: LeadScore,
        customer_features: Optional[FeatureSet] = None,
        customer_segment: Optional[CustomerSegment] = None,
    ) -> List[str]:
        """Match relevant Three HK offers based on lead score and customer data."""
        offers = []

        # Use advanced Three HK Business Rules Engine if available
        if self.three_hk_engine is not None and customer_features is not None and customer_segment is not None:

            try:
                # Get sophisticated offer matches
                offer_matches = self.three_hk_engine.match_offers_for_customer(
                    customer_features, lead_score, customer_segment
                )

                # Extract offer names from matches
                for offer_match in offer_matches:
                    offers.append(offer_match.product.product_name)

                logger.debug(f"Matched {len(offers)} Three HK offers using business rules engine")
                return offers

            except Exception as e:
                logger.warning(f"Three HK offer matching failed, falling back to basic matching: {e}")

        # Fallback to basic offer matching
        # Priority-based offers
        if lead_score.lead_priority == LeadPriority.CRITICAL:
            offers.extend(["VIP retention package", "Premium loyalty bonus"])
        elif lead_score.lead_priority == LeadPriority.HIGH:
            offers.extend(["Priority customer upgrade", "Limited time promotion"])

        # Score-based offers
        if lead_score.revenue_potential >= 80:
            offers.append("Enterprise solution bundle")
        elif lead_score.revenue_potential >= 60:
            offers.append("Premium plan upgrade")

        if lead_score.conversion_probability >= 75:
            offers.append("New customer incentive")

        if lead_score.urgency_factor >= 70:
            offers.extend(["Retention specialist consultation", "Immediate upgrade discount"])

        return list(set(offers))  # Remove duplicates


# Convenience functions for easy integration


def score_single_lead(
    customer_data: Dict[str, Any],
    purchase_history: List[Dict[str, Any]],
    engagement_data: Optional[Dict[str, Any]] = None,
    market_context: Optional[Dict[str, Any]] = None,
) -> LeadScore:
    """
    Convenience function to score a single lead.

    Args:
        customer_data: Customer profile information
        purchase_history: Historical purchase records
        engagement_data: Customer engagement metrics
        market_context: Market context

    Returns:
        Lead scoring results
    """
    engine = LeadScoringEngine()
    return engine.score_lead(customer_data, purchase_history, engagement_data, market_context)


def batch_score_and_prioritize(
    customer_datasets: List[Dict[str, Any]], market_context: Optional[Dict[str, Any]] = None, max_leads: int = 100
) -> List[PrioritizedLead]:
    """
    Convenience function to score and prioritize multiple leads.

    Args:
        customer_datasets: List of customer data for scoring
        market_context: Market context
        max_leads: Maximum number of leads to return

    Returns:
        Prioritized list of leads
    """
    engine = LeadScoringEngine()

    # Score all leads
    scored_leads = engine.batch_score_leads(customer_datasets, market_context)

    # Prioritize leads
    constraints = {"max_leads": max_leads, "min_score_threshold": 20.0}
    prioritized_leads = engine.prioritize_leads(scored_leads, constraints)

    return prioritized_leads


if __name__ == "__main__":
    # Example usage
    logger.info("Lead Scoring Engine ready for use")
