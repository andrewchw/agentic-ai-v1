"""
Core AI Agent for Agentic AI Revenue Assistant

This module implements the central orchestration and reasoning system for the AI agent,
providing modular perception, reasoning, and action components specifically designed
for Hong Kong telecom revenue optimization workflows.

Key Features:
- Modular agent architecture (Perception, Reasoning, Action)
- Context-aware state management
- Telecom-specific business logic integration
- Privacy-compliant data processing
- Real-time and batch processing support
- Integration with OpenRouter business analysis
"""

import os
import json
import time
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

# Import business analysis workflow
try:
    from ..utils.business_analysis_workflow import BusinessAnalysisWorkflow, AnalysisRequest, AnalysisResult
    from ..utils.enhanced_field_identification import EnhancedFieldIdentifier
    from ..utils.integrated_display_masking import IntegratedDisplayMasking
except ImportError:
    from utils.business_analysis_workflow import BusinessAnalysisWorkflow, AnalysisRequest, AnalysisResult
    from utils.enhanced_field_identification import EnhancedFieldIdentifier
    from utils.integrated_display_masking import IntegratedDisplayMasking

from .recommendation_generator import (
    RecommendationGenerator,
    ActionableRecommendation,
    RecommendationPriority,
    ActionType,
    create_sample_recommendations
)

# Configure logging
logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Agent processing states."""

    IDLE = "idle"
    PERCEIVING = "perceiving"
    REASONING = "reasoning"
    ACTING = "acting"
    ERROR = "error"
    COMPLETED = "completed"


class ProcessingMode(Enum):
    """Agent processing modes."""

    REAL_TIME = "real_time"
    BATCH = "batch"
    STREAMING = "streaming"


@dataclass
class AgentContext:
    """Context information maintained across agent operations."""

    session_id: str
    customer_id: Optional[str] = None
    processing_mode: ProcessingMode = ProcessingMode.REAL_TIME
    timestamp: str = ""

    # Data context
    customer_data: Optional[Dict[str, Any]] = None
    purchase_history: Optional[List[Dict[str, Any]]] = None
    engagement_data: Optional[Dict[str, Any]] = None
    market_context: Optional[Dict[str, Any]] = None

    # Processing context
    current_state: AgentState = AgentState.IDLE
    processing_steps: List[str] = None
    error_history: List[str] = None

    # Results context
    analysis_results: Optional[Dict[str, Any]] = None
    lead_scores: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if self.processing_steps is None:
            self.processing_steps = []
        if self.error_history is None:
            self.error_history = []


@dataclass
class AgentDecision:
    """Represents an agent reasoning decision."""

    decision_type: str  # "analyze", "score", "recommend", "skip", "retry"
    confidence: float  # 0.0 to 1.0
    reasoning: str
    parameters: Dict[str, Any]
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class AgentAction:
    """Represents an agent action to be executed."""

    action_type: str  # "customer_analysis", "lead_scoring", "generate_recommendations"
    parameters: Dict[str, Any]
    priority: int = 1  # 1 (highest) to 5 (lowest)
    estimated_duration: float = 0.0
    retry_count: int = 0
    max_retries: int = 3

    def __post_init__(self):
        if not hasattr(self, "created_at"):
            self.created_at = datetime.now().isoformat()


class PerceptionModule:
    """
    Handles data intake and preprocessing for the AI agent.

    Responsible for:
    - Data validation and preprocessing
    - Privacy compliance checks
    - Feature extraction and normalization
    - Context enrichment
    """

    def __init__(self, enable_privacy_masking: bool = True):
        self.enable_privacy = enable_privacy_masking

        # Initialize privacy components if available
        try:
            if enable_privacy_masking:
                self.field_identifier = EnhancedFieldIdentifier()
                self.display_masking = IntegratedDisplayMasking(self.field_identifier)
                logger.info("Privacy components initialized in PerceptionModule")
        except Exception as e:
            logger.warning(f"Privacy components not available: {e}")
            self.enable_privacy = False

    def perceive_customer_data(self, raw_customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and validate raw customer data.

        Args:
            raw_customer_data: Raw customer profile data

        Returns:
            Processed and validated customer data
        """
        try:
            # Basic validation
            if not raw_customer_data:
                raise ValueError("Empty customer data provided")

            # Data cleaning and normalization
            processed_data = self._clean_customer_data(raw_customer_data)

            # Privacy compliance check
            if self.enable_privacy:
                processed_data = self._apply_privacy_protection(processed_data)

            # Feature extraction
            extracted_features = self._extract_customer_features(processed_data)

            # Combine original data with extracted features
            result = {
                "original_data": processed_data,
                "extracted_features": extracted_features,
                "privacy_protected": self.enable_privacy,
                "processing_timestamp": datetime.now().isoformat(),
            }

            logger.debug(f"Customer data perception completed: {len(processed_data)} fields processed")
            return result

        except Exception as e:
            logger.error(f"Customer data perception failed: {e}")
            raise

    def perceive_purchase_history(self, raw_purchase_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process and analyze purchase history data.

        Args:
            raw_purchase_history: Raw purchase history records

        Returns:
            Processed purchase history with extracted patterns
        """
        try:
            if not raw_purchase_history:
                logger.warning("Empty purchase history provided")
                return {"records": [], "patterns": {}, "summary": {}}

            # Clean and validate purchase records
            cleaned_records = [self._clean_purchase_record(record) for record in raw_purchase_history]

            # Extract purchase patterns
            patterns = self._extract_purchase_patterns(cleaned_records)

            # Generate summary statistics
            summary = self._generate_purchase_summary(cleaned_records)

            result = {
                "records": cleaned_records,
                "patterns": patterns,
                "summary": summary,
                "processing_timestamp": datetime.now().isoformat(),
            }

            logger.debug(f"Purchase history perception completed: {len(cleaned_records)} records processed")
            return result

        except Exception as e:
            logger.error(f"Purchase history perception failed: {e}")
            raise

    def perceive_market_context(self, context_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Gather and process market context information.

        Args:
            context_data: Optional external market context

        Returns:
            Processed market context
        """
        try:
            # Default Hong Kong telecom market context
            default_context = {
                "market": "Hong Kong",
                "industry": "Telecommunications",
                "primary_competitors": ["SmarTone", "CSL Mobile", "PCCW Mobile"],
                "market_trends": {
                    "5g_adoption_rate": 0.75,
                    "data_usage_growth": 0.15,
                    "price_sensitivity": "medium",
                    "premium_segment_growth": 0.08,
                },
                "seasonal_factors": self._get_seasonal_factors(),
                "regulatory_environment": {
                    "data_protection": "PDPO_compliant",
                    "number_portability": True,
                    "roaming_regulations": "standard",
                },
            }

            # Merge with provided context
            if context_data:
                default_context.update(context_data)

            logger.debug("Market context perception completed")
            return default_context

        except Exception as e:
            logger.error(f"Market context perception failed: {e}")
            return {}

    def _clean_customer_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize customer data."""
        cleaned = {}

        for key, value in data.items():
            # Handle None values
            if value is None:
                continue

            # Convert to string and strip whitespace
            if isinstance(value, str):
                value = value.strip()
                if not value:  # Skip empty strings
                    continue

            # Normalize field names
            normalized_key = key.lower().replace(" ", "_").replace("-", "_")
            cleaned[normalized_key] = value

        return cleaned

    def _clean_purchase_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate a single purchase record."""
        cleaned = {}

        for key, value in record.items():
            if value is None:
                continue

            # Normalize key
            normalized_key = key.lower().replace(" ", "_").replace("-", "_")

            # Type-specific cleaning
            if normalized_key in ["amount", "price", "cost"]:
                try:
                    cleaned[normalized_key] = float(value)
                except (ValueError, TypeError):
                    logger.warning(f"Invalid amount value: {value}")
                    continue
            elif normalized_key in ["date", "purchase_date", "transaction_date"]:
                # Keep as string for now, could add date parsing later
                cleaned[normalized_key] = str(value)
            else:
                cleaned[normalized_key] = value

        return cleaned

    def _apply_privacy_protection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply privacy protection to sensitive data."""
        if not self.enable_privacy:
            return data

        try:
            # This would integrate with the privacy pipeline
            # For now, return as-is since we handle privacy in the workflow layer
            return data
        except Exception as e:
            logger.warning(f"Privacy protection failed: {e}")
            return data

    def _extract_customer_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant features from customer data."""
        features = {}

        # Demographic features
        if "age" in data or "age_group" in data:
            features["demographic_segment"] = self._categorize_age_group(data.get("age", data.get("age_group")))

        # Financial features
        if "monthly_spend" in data:
            features["spend_category"] = self._categorize_spend_level(data["monthly_spend"])

        # Tenure features
        if "tenure_months" in data:
            features["tenure_category"] = self._categorize_tenure(data["tenure_months"])

        # Geographic features
        if "location" in data:
            features["location_category"] = self._categorize_location(data["location"])

        # Account type features
        if "account_type" in data:
            features["account_tier"] = self._categorize_account_type(data["account_type"])

        return features

    def _extract_purchase_patterns(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract patterns from purchase history."""
        if not records:
            return {}

        patterns = {}

        # Calculate purchase frequency
        if len(records) >= 2:
            patterns["purchase_frequency"] = self._calculate_purchase_frequency(records)

        # Calculate average spend
        amounts = [record.get("amount", 0) for record in records if "amount" in record]
        if amounts:
            patterns["average_spend"] = sum(amounts) / len(amounts)
            patterns["total_spend"] = sum(amounts)
            patterns["spend_variance"] = self._calculate_variance(amounts)

        # Product category preferences
        categories = [record.get("category", "unknown") for record in records]
        patterns["category_preferences"] = self._calculate_category_distribution(categories)

        # Seasonality patterns
        patterns["seasonal_patterns"] = self._analyze_seasonal_patterns(records)

        return patterns

    def _generate_purchase_summary(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for purchase history."""
        if not records:
            return {}

        summary = {
            "total_purchases": len(records),
            "date_range": self._get_date_range(records),
            "unique_categories": len(set(record.get("category", "unknown") for record in records)),
            "recent_activity": self._analyze_recent_activity(records),
        }

        return summary

    def _get_seasonal_factors(self) -> Dict[str, float]:
        """Get seasonal factors for Hong Kong market."""
        month = datetime.now().month

        # Hong Kong seasonal patterns for telecom
        seasonal_factors = {
            "chinese_new_year": 1.2 if month in [1, 2] else 1.0,
            "summer_holidays": 1.1 if month in [7, 8] else 1.0,
            "christmas_promotions": 1.15 if month == 12 else 1.0,
            "back_to_school": 1.1 if month == 9 else 1.0,
        }

        return seasonal_factors

    # Helper methods for categorization
    def _categorize_age_group(self, age_value) -> str:
        """Categorize age into segments."""
        if isinstance(age_value, str):
            return age_value  # Already categorized

        try:
            age = int(age_value)
            if age < 25:
                return "young_adult"
            elif age < 35:
                return "early_career"
            elif age < 45:
                return "mid_career"
            elif age < 55:
                return "senior_professional"
            else:
                return "mature"
        except (ValueError, TypeError):
            return "unknown"

    def _categorize_spend_level(self, spend) -> str:
        """Categorize spending level."""
        try:
            amount = float(spend)
            if amount < 300:
                return "budget"
            elif amount < 600:
                return "standard"
            elif amount < 1000:
                return "premium"
            else:
                return "enterprise"
        except (ValueError, TypeError):
            return "unknown"

    def _categorize_tenure(self, tenure) -> str:
        """Categorize customer tenure."""
        try:
            months = int(tenure)
            if months < 6:
                return "new"
            elif months < 12:
                return "recent"
            elif months < 24:
                return "established"
            else:
                return "loyal"
        except (ValueError, TypeError):
            return "unknown"

    def _categorize_location(self, location) -> str:
        """Categorize location into business segments."""
        location_str = str(location).lower()

        if "hong kong island" in location_str or "central" in location_str:
            return "premium_business"
        elif "kowloon" in location_str:
            return "urban_residential"
        elif "new territories" in location_str:
            return "suburban_family"
        else:
            return "general"

    def _categorize_account_type(self, account_type) -> str:
        """Categorize account type."""
        type_str = str(account_type).lower()

        if "premium" in type_str or "vip" in type_str:
            return "premium"
        elif "business" in type_str or "corporate" in type_str:
            return "business"
        elif "family" in type_str:
            return "family"
        else:
            return "standard"

    # Helper methods for pattern analysis
    def _calculate_purchase_frequency(self, records: List[Dict[str, Any]]) -> str:
        """Calculate purchase frequency category."""
        # Simplified frequency calculation
        if len(records) >= 10:
            return "high"
        elif len(records) >= 5:
            return "medium"
        else:
            return "low"

    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of values."""
        if len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance

    def _calculate_category_distribution(self, categories: List[str]) -> Dict[str, float]:
        """Calculate distribution of purchase categories."""
        if not categories:
            return {}

        counts = {}
        for category in categories:
            counts[category] = counts.get(category, 0) + 1

        total = len(categories)
        return {cat: count / total for cat, count in counts.items()}

    def _analyze_seasonal_patterns(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze seasonal purchasing patterns."""
        # Simplified seasonal analysis
        return {"pattern": "analysis_placeholder"}

    def _get_date_range(self, records: List[Dict[str, Any]]) -> Dict[str, str]:
        """Get date range of purchase records."""
        dates = []
        for record in records:
            for key in ["date", "purchase_date", "transaction_date"]:
                if key in record:
                    dates.append(record[key])
                    break

        if dates:
            return {"earliest": min(dates), "latest": max(dates)}
        else:
            return {}

    def _analyze_recent_activity(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze recent purchase activity."""
        # Simplified recent activity analysis
        recent_count = len([r for r in records[-3:]])  # Last 3 purchases
        return {"recent_purchases": recent_count}


class ReasoningModule:
    """
    Handles decision-making and strategic reasoning for the AI agent.

    Responsible for:
    - Analyzing perceived data
    - Making strategic decisions
    - Determining optimal actions
    - Context-aware reasoning
    """

    def __init__(self):
        # Business rules and thresholds
        self.scoring_weights = {
            "engagement_score": 0.25,
            "financial_value": 0.30,
            "purchase_frequency": 0.20,
            "tenure_value": 0.15,
            "market_fit": 0.10,
        }

        self.decision_thresholds = {
            "high_value_threshold": 0.8,
            "medium_value_threshold": 0.6,
            "action_required_threshold": 0.7,
            "skip_threshold": 0.3,
        }

    def reason_about_customer(self, context: AgentContext) -> AgentDecision:
        """
        Analyze customer context and decide on the best approach.

        Args:
            context: Current agent context with customer data

        Returns:
            Decision on how to proceed with this customer
        """
        try:
            # Analyze customer value potential
            value_score = self._assess_customer_value(context)

            # Analyze engagement opportunity
            engagement_score = self._assess_engagement_opportunity(context)

            # Analyze market fit
            market_fit_score = self._assess_market_fit(context)

            # Combined reasoning score
            overall_score = (
                value_score * self.scoring_weights["financial_value"]
                + engagement_score * self.scoring_weights["engagement_score"]
                + market_fit_score * self.scoring_weights["market_fit"]
            )

            # Make decision based on scores
            if overall_score >= self.decision_thresholds["high_value_threshold"]:
                decision_type = "comprehensive_analysis"
                reasoning = f"High-value customer (score: {overall_score:.2f}) - proceed with full analysis"
            elif overall_score >= self.decision_thresholds["medium_value_threshold"]:
                decision_type = "standard_analysis"
                reasoning = f"Medium-value customer (score: {overall_score:.2f}) - proceed with standard analysis"
            elif overall_score >= self.decision_thresholds["action_required_threshold"]:
                decision_type = "targeted_analysis"
                reasoning = f"Targeted opportunity (score: {overall_score:.2f}) - focused analysis recommended"
            else:
                decision_type = "skip"
                reasoning = f"Low priority customer (score: {overall_score:.2f}) - minimal action required"

            return AgentDecision(
                decision_type=decision_type,
                confidence=overall_score,
                reasoning=reasoning,
                parameters={
                    "value_score": value_score,
                    "engagement_score": engagement_score,
                    "market_fit_score": market_fit_score,
                    "overall_score": overall_score,
                },
            )

        except Exception as e:
            logger.error(f"Customer reasoning failed: {e}")
            return AgentDecision(
                decision_type="error", confidence=0.0, reasoning=f"Reasoning failed: {str(e)}", parameters={}
            )

    def reason_about_recommendations(self, analysis_results: Dict[str, Any], context: AgentContext) -> AgentDecision:
        """
        Reason about what recommendations to generate based on analysis results.

        Args:
            analysis_results: Results from customer analysis
            context: Current agent context

        Returns:
            Decision on recommendation strategy
        """
        try:
            # Extract key insights from analysis
            if not analysis_results or "customer_patterns" not in analysis_results:
                return AgentDecision(
                    decision_type="skip_recommendations",
                    confidence=0.1,
                    reasoning="Insufficient analysis data for recommendations",
                    parameters={},
                )

            patterns = analysis_results.get("customer_patterns", {})
            lead_score = analysis_results.get("lead_score", {})

            # Assess recommendation opportunity
            recommendation_score = self._assess_recommendation_opportunity(patterns, lead_score)

            # Determine recommendation strategy
            if recommendation_score >= 0.8:
                strategy = "premium_recommendations"
                reasoning = "High-value customer warrants premium offer recommendations"
            elif recommendation_score >= 0.6:
                strategy = "standard_recommendations"
                reasoning = "Standard customer suitable for targeted offers"
            elif recommendation_score >= 0.4:
                strategy = "retention_recommendations"
                reasoning = "Focus on retention and engagement offers"
            else:
                strategy = "minimal_recommendations"
                reasoning = "Basic offers only to maintain engagement"

            return AgentDecision(
                decision_type=strategy,
                confidence=recommendation_score,
                reasoning=reasoning,
                parameters={
                    "recommendation_score": recommendation_score,
                    "focus_areas": self._identify_focus_areas(patterns, lead_score),
                },
            )

        except Exception as e:
            logger.error(f"Recommendation reasoning failed: {e}")
            return AgentDecision(
                decision_type="error",
                confidence=0.0,
                reasoning=f"Recommendation reasoning failed: {str(e)}",
                parameters={},
            )

    def _assess_customer_value(self, context: AgentContext) -> float:
        """Assess the financial value potential of a customer."""
        score = 0.5  # Default score

        try:
            if context.customer_data and "extracted_features" in context.customer_data:
                features = context.customer_data["extracted_features"]

                # Spend category assessment
                spend_category = features.get("spend_category", "unknown")
                if spend_category == "enterprise":
                    score += 0.4
                elif spend_category == "premium":
                    score += 0.3
                elif spend_category == "standard":
                    score += 0.1

                # Account tier assessment
                account_tier = features.get("account_tier", "unknown")
                if account_tier == "premium":
                    score += 0.2
                elif account_tier == "business":
                    score += 0.15

                # Tenure assessment
                tenure_category = features.get("tenure_category", "unknown")
                if tenure_category == "loyal":
                    score += 0.1
                elif tenure_category == "established":
                    score += 0.05

        except Exception as e:
            logger.warning(f"Customer value assessment error: {e}")

        return min(1.0, max(0.0, score))

    def _assess_engagement_opportunity(self, context: AgentContext) -> float:
        """Assess engagement opportunity based on customer behavior."""
        score = 0.5  # Default score

        try:
            # Check for engagement data
            if context.engagement_data:
                # Simplified engagement scoring
                satisfaction = context.engagement_data.get("satisfaction_score", 5.0)
                if satisfaction >= 8.0:
                    score += 0.3
                elif satisfaction >= 6.0:
                    score += 0.1

                # App usage assessment
                usage_hours = context.engagement_data.get("app_usage_hours", 0)
                if usage_hours >= 10:
                    score += 0.2
                elif usage_hours >= 5:
                    score += 0.1

        except Exception as e:
            logger.warning(f"Engagement assessment error: {e}")

        return min(1.0, max(0.0, score))

    def _assess_market_fit(self, context: AgentContext) -> float:
        """Assess how well the customer fits target market segments."""
        score = 0.5  # Default score

        try:
            if context.customer_data and "extracted_features" in context.customer_data:
                features = context.customer_data["extracted_features"]

                # Location category assessment
                location_category = features.get("location_category", "general")
                if location_category == "premium_business":
                    score += 0.3
                elif location_category == "urban_residential":
                    score += 0.2

                # Demographics assessment
                demographic_segment = features.get("demographic_segment", "unknown")
                if demographic_segment in ["early_career", "mid_career", "senior_professional"]:
                    score += 0.2

        except Exception as e:
            logger.warning(f"Market fit assessment error: {e}")

        return min(1.0, max(0.0, score))

    def _assess_recommendation_opportunity(self, patterns: Dict[str, Any], lead_score: Dict[str, Any]) -> float:
        """Assess the opportunity for generating valuable recommendations."""
        score = 0.5  # Default score

        try:
            # Check lead score if available
            if lead_score and "overall_score" in lead_score:
                overall_lead_score = lead_score["overall_score"]
                score += (overall_lead_score / 100) * 0.4  # Assuming score is 0-100

            # Check patterns for upsell/cross-sell opportunities
            if patterns and "opportunities" in patterns:
                opportunities = patterns["opportunities"]
                upsell_potential = opportunities.get("upsell_potential", "low")

                if upsell_potential == "high":
                    score += 0.3
                elif upsell_potential == "medium":
                    score += 0.2
                elif upsell_potential == "low":
                    score += 0.1

        except Exception as e:
            logger.warning(f"Recommendation opportunity assessment error: {e}")

        return min(1.0, max(0.0, score))

    def _identify_focus_areas(self, patterns: Dict[str, Any], lead_score: Dict[str, Any]) -> List[str]:
        """Identify key focus areas for recommendations."""
        focus_areas = []

        try:
            # Analyze patterns for focus areas
            if patterns and "opportunities" in patterns:
                opportunities = patterns["opportunities"]

                if opportunities.get("upsell_potential") == "high":
                    focus_areas.append("upsell")

                cross_sell_categories = opportunities.get("cross_sell_categories", [])
                if cross_sell_categories:
                    focus_areas.extend(cross_sell_categories)

            # Analyze lead score for focus areas
            if lead_score and "key_factors" in lead_score:
                key_factors = lead_score["key_factors"]
                if "high_engagement" in str(key_factors).lower():
                    focus_areas.append("engagement")
                if "premium_potential" in str(key_factors).lower():
                    focus_areas.append("premium_upgrade")

        except Exception as e:
            logger.warning(f"Focus area identification error: {e}")

        return list(set(focus_areas))  # Remove duplicates


class ActionModule:
    """
    Handles action execution for the AI agent.

    Responsible for:
    - Executing analysis workflows
    - Generating recommendations using RecommendationGenerator
    - Managing action queues
    - Coordinating with external systems
    """

    def __init__(self, business_workflow: BusinessAnalysisWorkflow):
        self.business_workflow = business_workflow
        self.action_queue = []
        self.active_actions = {}
        
        # Initialize recommendation generator with integrated components
        try:
            from .customer_analysis import CustomerDataAnalyzer
            from .lead_scoring import LeadScoringEngine
            from .three_hk_business_rules import ThreeHKBusinessRulesEngine
            
            self.recommendation_generator = RecommendationGenerator(
                customer_analyzer=CustomerDataAnalyzer(),
                lead_scorer=LeadScoringEngine(),
                business_rules=ThreeHKBusinessRulesEngine()
            )
            logger.info("RecommendationGenerator initialized successfully")
        except Exception as e:
            logger.warning(f"RecommendationGenerator initialization failed: {e}")
            self.recommendation_generator = None

    def execute_action(self, action: AgentAction, context: AgentContext) -> Dict[str, Any]:
        """
        Execute a specific agent action.

        Args:
            action: Action to execute
            context: Current agent context

        Returns:
            Action execution results
        """
        try:
            logger.info(f"Executing action: {action.action_type}")

            if action.action_type == "customer_analysis":
                return self._execute_customer_analysis(action, context)
            elif action.action_type == "lead_scoring":
                return self._execute_lead_scoring(action, context)
            elif action.action_type == "generate_recommendations":
                return self._execute_generate_recommendations(action, context)
            else:
                raise ValueError(f"Unknown action type: {action.action_type}")

        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return {"success": False, "error": str(e), "action_type": action.action_type}

    def _execute_customer_analysis(self, action: AgentAction, context: AgentContext) -> Dict[str, Any]:
        """Execute customer analysis action."""
        try:
            # Prepare analysis request
            # Handle both list and dict formats for purchase_history
            if isinstance(context.purchase_history, dict):
                purchase_records = context.purchase_history.get("records", [])
            else:
                purchase_records = context.purchase_history or []

            request = AnalysisRequest(
                customer_data=context.customer_data.get("original_data", {}),
                purchase_history=purchase_records,
                engagement_data=context.engagement_data or {},
                analysis_type="patterns_only",
                context="Three HK telecom analysis",
                customer_id=context.customer_id,
            )

            # Execute analysis
            result = self.business_workflow._analyze_customer_patterns(request)

            return {
                "success": result.success,
                "result": result.customer_patterns if result.success else None,
                "error": result.error_message,
                "processing_time": result.processing_time,
                "tokens_used": result.tokens_used,
            }

        except Exception as e:
            logger.error(f"Customer analysis execution failed: {e}")
            return {"success": False, "error": str(e)}

    def _execute_lead_scoring(self, action: AgentAction, context: AgentContext) -> Dict[str, Any]:
        """Execute lead scoring action."""
        try:
            # Prepare scoring request
            # Handle both list and dict formats for purchase_history
            if isinstance(context.purchase_history, dict):
                purchase_records = context.purchase_history.get("records", [])
            else:
                purchase_records = context.purchase_history or []

            request = AnalysisRequest(
                customer_data=context.customer_data.get("original_data", {}),
                purchase_history=purchase_records,
                engagement_data=context.engagement_data or {},
                analysis_type="scoring_only",
                context="Three HK lead scoring",
                customer_id=context.customer_id,
            )

            # Execute scoring
            result = self.business_workflow._score_lead_priority(request)

            return {
                "success": result.success,
                "result": result.lead_score if result.success else None,
                "error": result.error_message,
                "processing_time": result.processing_time,
                "tokens_used": result.tokens_used,
            }

        except Exception as e:
            logger.error(f"Lead scoring execution failed: {e}")
            return {"success": False, "error": str(e)}

    def _execute_generate_recommendations(self, action: AgentAction, context: AgentContext) -> Dict[str, Any]:
        """Execute recommendations generation action using the enhanced RecommendationGenerator."""
        try:
            if not self.recommendation_generator:
                # Fallback to old LLM-based recommendations
                return self._execute_legacy_recommendations(action, context)
            
            start_time = time.time()
            
            # Prepare customer data for recommendation generation
            customer_data = context.customer_data.get("original_data", {})
            
            # Handle purchase history format
            if isinstance(context.purchase_history, dict):
                purchase_records = context.purchase_history.get("records", [])
            else:
                purchase_records = context.purchase_history or []
            
            # Create lead DataFrame for the recommendation generator
            lead_row = {
                "customer_id": context.customer_id,
                "customer_name": customer_data.get("customer_name", customer_data.get("name", "Unknown")),
                "customer_type": customer_data.get("customer_type", customer_data.get("account_type", "unknown")),
                "annual_revenue": customer_data.get("annual_revenue", 0),
                "employee_count": customer_data.get("employee_count", 0),
                "current_monthly_spend": customer_data.get("monthly_spend", customer_data.get("current_monthly_spend", 0)),
                "contract_end_date": customer_data.get("contract_end_date", ""),
                "last_interaction": customer_data.get("last_interaction", datetime.now().strftime("%Y-%m-%d")),
                "preferred_contact_time": customer_data.get("preferred_contact_time", "morning"),
                "industry": customer_data.get("industry", customer_data.get("segment", "unknown")),
                "location": customer_data.get("location", "Hong Kong"),
                "decision_maker_identified": customer_data.get("decision_maker_identified", True),
                "budget_confirmed": customer_data.get("budget_confirmed", False),
                "competitor_mentions": customer_data.get("competitor_mentions", ""),
                "urgency_indicators": customer_data.get("urgency_indicators", []),
                "pain_points": customer_data.get("pain_points", []),
            }
            
            # Add purchase history context
            if purchase_records:
                total_spend = sum(record.get("amount", 0) for record in purchase_records)
                recent_purchases = len([r for r in purchase_records if r.get("purchase_date", "") > "2023-01-01"])
                lead_row.update({
                    "total_historical_spend": total_spend,
                    "recent_purchase_count": recent_purchases,
                    "purchase_categories": list(set(record.get("category", "") for record in purchase_records))
                })
            
            # Create single-row DataFrame
            leads_df = pd.DataFrame([lead_row])
            
            # Generate recommendations
            recommendations = self.recommendation_generator.generate_recommendations(
                leads_df, max_recommendations=5
            )
            
            processing_time = time.time() - start_time
            
            # Format recommendations for agent context
            formatted_recommendations = []
            for rec in recommendations:
                formatted_rec = {
                    "recommendation_id": rec.recommendation_id,
                    "customer_id": rec.lead_id,
                    "customer_name": rec.customer_name,
                    "priority": rec.priority.value,
                    "action_type": rec.action_type.value,
                    "title": rec.title,
                    "description": rec.description,
                    "expected_revenue": rec.expected_revenue,
                    "conversion_probability": rec.conversion_probability,
                    "urgency_score": rec.urgency_score,
                    "business_impact_score": rec.business_impact_score,
                    "next_steps": rec.next_steps,
                    "talking_points": rec.talking_points,
                    "objection_handling": rec.objection_handling,
                    "recommended_offers": rec.recommended_offers,
                    "explanation": {
                        "primary_reason": rec.explanation.primary_reason,
                        "supporting_factors": rec.explanation.supporting_factors,
                        "risk_factors": rec.explanation.risk_factors,
                        "confidence_score": rec.explanation.confidence_score,
                        "data_sources": rec.explanation.data_sources,
                    },
                    "expires_at": rec.expires_at.isoformat() if rec.expires_at else None,
                    "tags": rec.tags,
                    "created_at": rec.created_at.isoformat(),
                }
                formatted_recommendations.append(formatted_rec)
            
            # Create summary statistics
            summary = {
                "total_recommendations": len(recommendations),
                "priority_distribution": {},
                "action_type_distribution": {},
                "total_expected_revenue": sum(rec.expected_revenue for rec in recommendations),
                "average_conversion_probability": sum(rec.conversion_probability for rec in recommendations) / len(recommendations) if recommendations else 0,
                "average_business_impact": sum(rec.business_impact_score for rec in recommendations) / len(recommendations) if recommendations else 0,
            }
            
            # Calculate distributions
            for rec in recommendations:
                priority = rec.priority.value
                action_type = rec.action_type.value
                
                summary["priority_distribution"][priority] = summary["priority_distribution"].get(priority, 0) + 1
                summary["action_type_distribution"][action_type] = summary["action_type_distribution"].get(action_type, 0) + 1
            
            logger.info(f"Generated {len(recommendations)} recommendations in {processing_time:.2f}s")
            
            return {
                "success": True,
                "result": {
                    "recommendations": formatted_recommendations,
                    "summary": summary,
                    "generation_metadata": {
                        "generator_type": "RecommendationGenerator",
                        "processing_time": processing_time,
                        "customer_id": context.customer_id,
                        "timestamp": datetime.now().isoformat(),
                    }
                },
                "error": None,
                "processing_time": processing_time,
                "tokens_used": 0,  # Our generator doesn't use external API tokens
            }

        except Exception as e:
            logger.error(f"Enhanced recommendations generation failed: {e}")
            # Fallback to legacy system
            return self._execute_legacy_recommendations(action, context)

    def _execute_legacy_recommendations(self, action: AgentAction, context: AgentContext) -> Dict[str, Any]:
        """Execute legacy LLM-based recommendations as fallback."""
        try:
            logger.info("Using legacy LLM-based recommendation generation")
            
            # Get customer analysis from context
            analysis_data = context.analysis_results or {}

            # Handle both list and dict formats for purchase_history
            if isinstance(context.purchase_history, dict):
                purchase_records = context.purchase_history.get("records", [])
            else:
                purchase_records = context.purchase_history or []

            # Prepare recommendation request
            request = AnalysisRequest(
                customer_data=context.customer_data.get("original_data", {}),
                purchase_history=purchase_records,
                engagement_data=context.engagement_data or {},
                available_offers=action.parameters.get("offers", self._get_default_offers()),
                analysis_type="recommendations_only",
                context="Three HK sales recommendations",
                customer_id=context.customer_id,
            )

            # Execute recommendations
            result = self.business_workflow._generate_sales_recommendations(request, analysis_data)

            return {
                "success": result.success,
                "result": result.sales_recommendations if result.success else None,
                "error": result.error_message,
                "processing_time": result.processing_time,
                "tokens_used": result.tokens_used,
            }

        except Exception as e:
            logger.error(f"Legacy recommendations generation execution failed: {e}")
            return {"success": False, "error": str(e)}

    def _get_default_offers(self) -> List[Dict[str, Any]]:
        """Get default Three HK offers."""
        return [
            {
                "offer_id": "THREE_5G_PREMIUM_2024",
                "name": "5G Premium Unlimited",
                "price": 699.00,
                "currency": "HKD",
                "features": ["Unlimited 5G Data", "International Roaming", "Priority Support"],
                "target_segment": "Premium",
            },
            {
                "offer_id": "THREE_BUSINESS_PRO",
                "name": "Business Pro Package",
                "price": 1299.00,
                "currency": "HKD",
                "features": ["Business Support 24/7", "Dedicated Account Manager", "Priority Network"],
                "target_segment": "Business",
            },
            {
                "offer_id": "THREE_FAMILY_PLUS",
                "name": "Family Plus Plan",
                "price": 399.00,
                "currency": "HKD",
                "features": ["Multi-device sharing", "Parental controls", "Family discounts"],
                "target_segment": "Consumer",
            },
        ]

    def get_action_status(self, action_id: str) -> Dict[str, Any]:
        """Get status of a specific action."""
        return self.active_actions.get(action_id, {"status": "not_found"})

    def list_active_actions(self) -> List[Dict[str, Any]]:
        """List all currently active actions."""
        return list(self.active_actions.values())

    def queue_action(self, action: AgentAction) -> str:
        """Add an action to the execution queue."""
        action_id = f"action_{int(time.time())}"
        self.action_queue.append({"id": action_id, "action": action, "queued_at": time.time()})
        return action_id


class CoreAgent:
    """
    Main AI agent orchestrator that coordinates perception, reasoning, and action.

    This is the central agent that manages the complete workflow for customer
    analysis, lead scoring, and recommendation generation.
    """

    def __init__(self, enable_privacy_masking: bool = True, enable_logging: bool = True):
        """
        Initialize the core AI agent.

        Args:
            enable_privacy_masking: Whether to enable privacy protection
            enable_logging: Whether to enable detailed logging
        """
        # Initialize modules
        self.perception = PerceptionModule(enable_privacy_masking)
        self.reasoning = ReasoningModule()

        # Initialize business workflow
        self.business_workflow = BusinessAnalysisWorkflow(
            enable_privacy_masking=enable_privacy_masking, enable_logging=enable_logging
        )

        self.action = ActionModule(self.business_workflow)

        # Agent state
        self.current_context = None
        self.processing_history = []

        logger.info("Core AI Agent initialized")

    def process_customer(
        self,
        customer_data: Dict[str, Any],
        purchase_history: List[Dict[str, Any]],
        engagement_data: Optional[Dict[str, Any]] = None,
        processing_mode: ProcessingMode = ProcessingMode.REAL_TIME,
    ) -> Dict[str, Any]:
        """
        Process a customer through the complete AI agent workflow.

        Args:
            customer_data: Customer profile data
            purchase_history: Purchase history records
            engagement_data: Optional engagement metrics
            processing_mode: How to process (real-time, batch, streaming)

        Returns:
            Complete processing results
        """
        start_time = time.time()

        # Initialize context
        context = AgentContext(
            session_id=f"session_{int(time.time())}",
            customer_id=customer_data.get("customer_id", "unknown"),
            processing_mode=processing_mode,
            current_state=AgentState.IDLE,
        )

        self.current_context = context

        try:
            # PERCEPTION PHASE
            context.current_state = AgentState.PERCEIVING
            context.processing_steps.append("perception_started")

            # Perceive customer data
            context.customer_data = self.perception.perceive_customer_data(customer_data)

            # Perceive purchase history
            context.purchase_history = self.perception.perceive_purchase_history(purchase_history)

            # Perceive engagement data
            context.engagement_data = engagement_data

            # Perceive market context
            context.market_context = self.perception.perceive_market_context()

            context.processing_steps.append("perception_completed")

            # REASONING PHASE
            context.current_state = AgentState.REASONING
            context.processing_steps.append("reasoning_started")

            # Reason about customer approach
            customer_decision = self.reasoning.reason_about_customer(context)

            context.processing_steps.append(f"customer_decision: {customer_decision.decision_type}")

            # ACTION PHASE
            context.current_state = AgentState.ACTING
            context.processing_steps.append("action_started")

            action_results = {}

            # Execute actions based on decision
            if customer_decision.decision_type != "skip" and customer_decision.decision_type != "error":

                # Customer analysis action
                analysis_action = AgentAction(action_type="customer_analysis", parameters=customer_decision.parameters)

                analysis_result = self.action.execute_action(analysis_action, context)
                action_results["customer_analysis"] = analysis_result

                if analysis_result["success"]:
                    context.analysis_results = analysis_result["result"]

                # Lead scoring action
                scoring_action = AgentAction(action_type="lead_scoring", parameters=customer_decision.parameters)

                scoring_result = self.action.execute_action(scoring_action, context)
                action_results["lead_scoring"] = scoring_result

                if scoring_result["success"]:
                    context.lead_scores = scoring_result["result"]

                # Reasoning about recommendations
                recommendation_decision = self.reasoning.reason_about_recommendations(
                    {"customer_patterns": context.analysis_results, "lead_score": context.lead_scores}, context
                )

                # Generate recommendations if warranted
                if recommendation_decision.decision_type != "skip_recommendations":
                    recommendation_action = AgentAction(
                        action_type="generate_recommendations", parameters=recommendation_decision.parameters
                    )

                    recommendation_result = self.action.execute_action(recommendation_action, context)
                    action_results["recommendations"] = recommendation_result

                    if recommendation_result["success"]:
                        context.recommendations = recommendation_result["result"]

            context.processing_steps.append("action_completed")
            context.current_state = AgentState.COMPLETED

            # Compile final results
            processing_time = time.time() - start_time

            final_results = {
                "success": True,
                "customer_id": context.customer_id,
                "processing_time": processing_time,
                "processing_mode": processing_mode.value,
                "agent_decision": {
                    "decision_type": customer_decision.decision_type,
                    "confidence": customer_decision.confidence,
                    "reasoning": customer_decision.reasoning,
                },
                "results": {
                    "customer_analysis": context.analysis_results,
                    "lead_scores": context.lead_scores,
                    "recommendations": context.recommendations,
                },
                "action_results": action_results,
                "processing_steps": context.processing_steps,
                "metadata": {
                    "session_id": context.session_id,
                    "timestamp": datetime.now().isoformat(),
                    "privacy_protected": self.perception.enable_privacy,
                },
            }

            # Store in processing history
            self.processing_history.append(final_results)

            logger.info(f"Customer processing completed in {processing_time:.2f}s for {context.customer_id}")

            return final_results

        except Exception as e:
            context.current_state = AgentState.ERROR
            context.error_history.append(str(e))

            logger.error(f"Customer processing failed: {e}")

            return {
                "success": False,
                "customer_id": context.customer_id,
                "error": str(e),
                "processing_time": time.time() - start_time,
                "processing_steps": context.processing_steps,
                "error_history": context.error_history,
            }

    def get_agent_statistics(self) -> Dict[str, Any]:
        """Get comprehensive agent performance statistics."""
        successful_processings = [r for r in self.processing_history if r.get("success", False)]
        failed_processings = [r for r in self.processing_history if not r.get("success", False)]

        stats = {
            "total_processings": len(self.processing_history),
            "successful_processings": len(successful_processings),
            "failed_processings": len(failed_processings),
            "success_rate": len(successful_processings) / max(1, len(self.processing_history)) * 100,
            "average_processing_time": sum(r.get("processing_time", 0) for r in successful_processings)
            / max(1, len(successful_processings)),
            "workflow_statistics": self.business_workflow.get_workflow_statistics(),
            "current_state": self.current_context.current_state.value if self.current_context else "idle",
        }

        return stats

    def validate_system_health(self) -> Dict[str, Any]:
        """Validate overall system health and readiness."""
        health = {
            "perception_module": True,
            "reasoning_module": True,
            "action_module": True,
            "business_workflow": False,
            "overall_health": False,
        }

        try:
            # Test business workflow connectivity
            health["business_workflow"] = self.business_workflow.validate_api_connectivity()

            # Overall health check
            health["overall_health"] = all(
                [health["perception_module"], health["reasoning_module"], health["action_module"]]
            )

        except Exception as e:
            logger.error(f"Health validation failed: {e}")
            health["error"] = str(e)

        return health


# Convenience functions for quick agent usage
def create_agent(enable_privacy: bool = True, enable_logging: bool = True) -> CoreAgent:
    """Create a core agent with default configuration."""
    return CoreAgent(enable_privacy_masking=enable_privacy, enable_logging=enable_logging)


def quick_customer_processing(
    customer_data: Dict[str, Any],
    purchase_history: List[Dict[str, Any]],
    engagement_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Process a customer quickly with minimal setup."""
    agent = create_agent()
    return agent.process_customer(customer_data, purchase_history, engagement_data)
