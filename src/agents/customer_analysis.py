"""
Customer Data Analysis Algorithms for Agentic AI Revenue Assistant

This module implements sophisticated algorithms to process and analyze pseudonymized
customer and purchase data, extracting relevant features and identifying behavioral
patterns specifically for Hong Kong telecom revenue optimization.

Key Features:
- Privacy-preserving data preprocessing pipelines
- Telecom-specific feature extraction algorithms
- Behavioral pattern recognition and clustering
- Customer lifecycle analysis
- Revenue opportunity identification
- Hong Kong market-specific insights
- Statistical and machine learning techniques
- Regulatory compliance (GDPR/Hong Kong PDPO)
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

# Statistical and ML imports
try:
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    from sklearn.metrics import silhouette_score

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    warnings.warn("scikit-learn not available. Some advanced analysis features will be limited.")

# Configure logging
logger = logging.getLogger(__name__)


class CustomerSegment(Enum):
    """Customer segmentation categories for Hong Kong telecom market."""

    PREMIUM_BUSINESS = "premium_business"
    URBAN_PROFESSIONAL = "urban_professional"
    FAMILY_SUBSCRIBER = "family_subscriber"
    YOUNG_DIGITAL = "young_digital"
    BUDGET_CONSCIOUS = "budget_conscious"
    ENTERPRISE_CLIENT = "enterprise_client"
    INACTIVE_CHURNER = "inactive_churner"
    HIGH_VALUE_LOYALIST = "high_value_loyalist"


class AnalysisType(Enum):
    """Types of customer analysis."""

    DEMOGRAPHIC_PROFILE = "demographic_profile"
    SPENDING_BEHAVIOR = "spending_behavior"
    USAGE_PATTERNS = "usage_patterns"
    LIFECYCLE_STAGE = "lifecycle_stage"
    CHURN_RISK = "churn_risk"
    UPSELL_POTENTIAL = "upsell_potential"
    CROSS_SELL_OPPORTUNITY = "cross_sell_opportunity"
    ENGAGEMENT_LEVEL = "engagement_level"


@dataclass
class FeatureSet:
    """Container for extracted customer features."""

    # Demographic features
    age_group: str = "unknown"
    location_category: str = "general"
    account_type: str = "standard"
    tenure_category: str = "new"

    # Financial features
    monthly_spend: float = 0.0
    spend_category: str = "budget"
    spend_variance: float = 0.0
    payment_reliability: float = 0.0

    # Usage features
    data_usage_gb: float = 0.0
    voice_minutes: float = 0.0
    sms_count: int = 0
    roaming_usage: float = 0.0

    # Behavioral features
    purchase_frequency: str = "low"
    service_interactions: int = 0
    complaint_count: int = 0
    satisfaction_score: float = 5.0

    # Engagement features
    app_usage_hours: float = 0.0
    digital_engagement: float = 0.0
    promotion_response_rate: float = 0.0

    # Market-specific features
    hk_market_segment: str = "general"
    competitor_switch_risk: float = 0.0
    regulatory_compliance_score: float = 1.0

    # Computed features
    customer_value_score: float = 0.0
    churn_risk_score: float = 0.0
    upsell_propensity: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for analysis."""
        return asdict(self)

    def get_numerical_features(self) -> Dict[str, float]:
        """Get only numerical features for ML algorithms."""
        numerical = {}
        for key, value in self.to_dict().items():
            if isinstance(value, (int, float)) and not math.isnan(value):
                numerical[key] = float(value)
        return numerical


@dataclass
class PatternAnalysis:
    """Container for identified behavioral patterns."""

    pattern_type: str
    pattern_name: str
    confidence: float
    description: str
    key_indicators: List[str]
    business_impact: str
    recommended_actions: List[str]

    # Pattern-specific metrics
    frequency: Optional[float] = None
    seasonality: Optional[str] = None
    trend_direction: Optional[str] = None
    correlation_factors: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class CustomerDataAnalyzer:
    """
    Core customer data analysis engine implementing sophisticated algorithms
    for Hong Kong telecom market analysis.
    """

    def __init__(self, enable_ml_clustering: bool = True, enable_advanced_stats: bool = True):
        """
        Initialize the customer data analyzer.

        Args:
            enable_ml_clustering: Enable machine learning clustering features
            enable_advanced_stats: Enable advanced statistical analysis
        """
        self.enable_ml = enable_ml_clustering and SKLEARN_AVAILABLE
        self.enable_advanced_stats = enable_advanced_stats

        # Hong Kong telecom market parameters
        self.hk_market_params = {
            "average_monthly_spend": 650.0,  # HKD
            "premium_threshold": 1000.0,  # HKD
            "budget_threshold": 300.0,  # HKD
            "high_usage_data_gb": 50.0,  # GB
            "standard_data_gb": 20.0,  # GB
            "high_voice_minutes": 500.0,  # minutes
            "churn_risk_threshold": 0.7,
            "upsell_threshold": 0.6,
        }

        # Initialize ML components if available
        if self.enable_ml:
            self.scaler = StandardScaler()
            self.clustering_model = None
            self.pca_model = None

        logger.info(f"CustomerDataAnalyzer initialized (ML: {self.enable_ml}, Stats: {self.enable_advanced_stats})")

    def extract_customer_features(
        self,
        customer_data: Dict[str, Any],
        purchase_history: List[Dict[str, Any]],
        engagement_data: Optional[Dict[str, Any]] = None,
    ) -> FeatureSet:
        """
        Extract comprehensive feature set from customer data.

        Args:
            customer_data: Customer profile information
            purchase_history: Historical purchase records
            engagement_data: Optional engagement metrics

        Returns:
            Extracted feature set
        """
        try:
            features = FeatureSet()

            # Extract demographic features
            features = self._extract_demographic_features(features, customer_data)

            # Extract financial features
            features = self._extract_financial_features(features, customer_data, purchase_history)

            # Extract usage features
            features = self._extract_usage_features(features, customer_data, engagement_data)

            # Extract behavioral features
            features = self._extract_behavioral_features(features, purchase_history, engagement_data)

            # Extract engagement features
            features = self._extract_engagement_features(features, engagement_data)

            # Extract Hong Kong market-specific features
            features = self._extract_hk_market_features(features, customer_data)

            # Compute derived features
            features = self._compute_derived_features(features)

            logger.debug(f"Feature extraction completed for customer {customer_data.get('customer_id', 'unknown')}")
            return features

        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return FeatureSet()  # Return default features on error

    def analyze_customer_patterns(
        self,
        customer_data: Dict[str, Any],
        purchase_history: List[Dict[str, Any]],
        engagement_data: Optional[Dict[str, Any]] = None,
    ) -> List[PatternAnalysis]:
        """
        Identify behavioral patterns in customer data.

        Args:
            customer_data: Customer profile information
            purchase_history: Historical purchase records
            engagement_data: Optional engagement metrics

        Returns:
            List of identified patterns
        """
        try:
            patterns = []

            # Extract features first
            features = self.extract_customer_features(customer_data, purchase_history, engagement_data)

            # Analyze spending patterns
            spending_patterns = self._analyze_spending_patterns(purchase_history, features)
            patterns.extend(spending_patterns)

            # Analyze usage patterns
            usage_patterns = self._analyze_usage_patterns(customer_data, engagement_data, features)
            patterns.extend(usage_patterns)

            # Analyze lifecycle patterns
            lifecycle_patterns = self._analyze_lifecycle_patterns(customer_data, purchase_history, features)
            patterns.extend(lifecycle_patterns)

            # Analyze engagement patterns
            engagement_patterns = self._analyze_engagement_patterns(engagement_data, features)
            patterns.extend(engagement_patterns)

            # Analyze seasonality patterns
            seasonality_patterns = self._analyze_seasonality_patterns(purchase_history, features)
            patterns.extend(seasonality_patterns)

            # Analyze churn risk patterns
            churn_patterns = self._analyze_churn_risk_patterns(features, purchase_history)
            patterns.extend(churn_patterns)

            logger.debug(f"Pattern analysis completed: {len(patterns)} patterns identified")
            return patterns

        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")
            return []

    def segment_customer(
        self,
        customer_data: Dict[str, Any],
        purchase_history: List[Dict[str, Any]],
        engagement_data: Optional[Dict[str, Any]] = None,
    ) -> Tuple[CustomerSegment, float]:
        """
        Segment customer into Hong Kong telecom market categories.

        Args:
            customer_data: Customer profile information
            purchase_history: Historical purchase records
            engagement_data: Optional engagement metrics

        Returns:
            Tuple of (segment, confidence_score)
        """
        try:
            features = self.extract_customer_features(customer_data, purchase_history, engagement_data)

            # Apply segmentation rules
            segment, confidence = self._apply_segmentation_rules(features)

            logger.debug(f"Customer segmented as {segment.value} with confidence {confidence:.2f}")
            return segment, confidence

        except Exception as e:
            logger.error(f"Customer segmentation failed: {e}")
            return CustomerSegment.BUDGET_CONSCIOUS, 0.5

    def cluster_customers(self, customer_datasets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform ML-based customer clustering analysis.

        Args:
            customer_datasets: List of customer data for clustering

        Returns:
            Clustering results and insights
        """
        if not self.enable_ml:
            logger.warning("ML clustering not available - scikit-learn not installed")
            return {"error": "ML clustering not available"}

        try:
            # Extract features for all customers
            all_features = []
            customer_ids = []

            for data in customer_datasets:
                customer_data = data.get("customer_data", {})
                purchase_history = data.get("purchase_history", [])
                engagement_data = data.get("engagement_data", {})

                features = self.extract_customer_features(customer_data, purchase_history, engagement_data)
                numerical_features = features.get_numerical_features()

                if numerical_features:
                    all_features.append(list(numerical_features.values()))
                    customer_ids.append(customer_data.get("customer_id", f"unknown_{len(customer_ids)}"))

            if len(all_features) < 3:
                return {"error": "Insufficient data for clustering (minimum 3 customers required)"}

            # Convert to numpy array and scale
            feature_matrix = np.array(all_features)
            scaled_features = self.scaler.fit_transform(feature_matrix)

            # Determine optimal number of clusters
            optimal_clusters = self._find_optimal_clusters(scaled_features)

            # Perform clustering
            self.clustering_model = KMeans(n_clusters=optimal_clusters, random_state=42, n_init=10)
            cluster_labels = self.clustering_model.fit_predict(scaled_features)

            # Analyze clusters
            cluster_analysis = self._analyze_clusters(scaled_features, cluster_labels, customer_ids, all_features)

            logger.info(f"Clustering completed: {optimal_clusters} clusters identified")
            return cluster_analysis

        except Exception as e:
            logger.error(f"Customer clustering failed: {e}")
            return {"error": str(e)}

    def generate_customer_insights(
        self,
        customer_data: Dict[str, Any],
        purchase_history: List[Dict[str, Any]],
        engagement_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive customer insights combining all analysis techniques.

        Args:
            customer_data: Customer profile information
            purchase_history: Historical purchase records
            engagement_data: Optional engagement metrics

        Returns:
            Comprehensive customer insights
        """
        try:
            start_time = time.time()

            # Handle None inputs gracefully
            if customer_data is None:
                customer_data = {}
            if purchase_history is None:
                purchase_history = []
            if engagement_data is None:
                engagement_data = {}

            # Extract features
            features = self.extract_customer_features(customer_data, purchase_history, engagement_data)

            # Identify patterns
            patterns = self.analyze_customer_patterns(customer_data, purchase_history, engagement_data)

            # Segment customer
            segment, segment_confidence = self.segment_customer(customer_data, purchase_history, engagement_data)

            # Generate risk assessments
            churn_risk = self._assess_churn_risk(features, patterns)
            upsell_potential = self._assess_upsell_potential(features, patterns)

            # Generate opportunities
            opportunities = self._identify_opportunities(features, patterns, segment)

            # Generate recommendations
            recommendations = self._generate_recommendations(features, patterns, opportunities)

            processing_time = time.time() - start_time

            insights = {
                "customer_id": customer_data.get("customer_id", "unknown"),
                "analysis_timestamp": datetime.now().isoformat(),
                "processing_time": processing_time,
                # Core analysis results
                "features": features.to_dict(),
                "patterns": [pattern.to_dict() for pattern in patterns],
                "segment": {
                    "category": segment.value,
                    "confidence": segment_confidence,
                    "description": self._get_segment_description(segment),
                },
                # Risk assessments
                "risk_assessments": {
                    "churn_risk": churn_risk,
                    "upsell_potential": upsell_potential,
                    "overall_health_score": self._calculate_health_score(features),
                },
                # Business opportunities
                "opportunities": opportunities,
                "recommendations": recommendations,
                # Market context
                "market_context": {
                    "hk_market_position": self._assess_market_position(features),
                    "competitive_comparison": self._assess_competitive_position(features),
                    "regulatory_compliance": features.regulatory_compliance_score,
                },
                # Summary metrics
                "summary": {
                    "customer_value_tier": self._get_value_tier(features.customer_value_score),
                    "engagement_level": self._get_engagement_level(features.digital_engagement),
                    "priority_score": self._calculate_priority_score(features, churn_risk, upsell_potential),
                    "key_insights": self._extract_key_insights(features, patterns, opportunities),
                },
            }

            logger.info(f"Customer insights generated in {processing_time:.2f}s")
            return insights

        except Exception as e:
            logger.error(f"Customer insights generation failed: {e}")
            return {
                "error": str(e),
                "customer_id": customer_data.get("customer_id", "unknown"),
                "analysis_timestamp": datetime.now().isoformat(),
            }

    # Private helper methods for feature extraction

    def _extract_demographic_features(self, features: FeatureSet, customer_data: Dict[str, Any]) -> FeatureSet:
        """Extract demographic features."""
        try:
            # Age group
            age = customer_data.get("age", 0)
            if isinstance(age, str):
                features.age_group = age.lower()
            elif isinstance(age, (int, float)):
                if age < 25:
                    features.age_group = "young_adult"
                elif age < 35:
                    features.age_group = "early_career"
                elif age < 45:
                    features.age_group = "mid_career"
                elif age < 55:
                    features.age_group = "senior_professional"
                else:
                    features.age_group = "mature"

            # Location category
            location = str(customer_data.get("location", "")).lower()
            if "hong kong island" in location or "central" in location:
                features.location_category = "premium_business"
            elif "kowloon" in location:
                features.location_category = "urban_residential"
            elif "new territories" in location:
                features.location_category = "suburban_family"
            else:
                features.location_category = "general"

            # Account type
            account_type = str(customer_data.get("account_type", "")).lower()
            if "premium" in account_type or "vip" in account_type:
                features.account_type = "premium"
            elif "business" in account_type:
                features.account_type = "business"
            elif "family" in account_type:
                features.account_type = "family"
            else:
                features.account_type = "standard"

            # Tenure category
            tenure_months = customer_data.get("tenure_months", 0)
            if isinstance(tenure_months, (int, float)):
                if tenure_months < 6:
                    features.tenure_category = "new"
                elif tenure_months < 12:
                    features.tenure_category = "recent"
                elif tenure_months < 24:
                    features.tenure_category = "established"
                else:
                    features.tenure_category = "loyal"

        except Exception as e:
            logger.warning(f"Demographic feature extraction error: {e}")

        return features

    def _extract_financial_features(
        self, features: FeatureSet, customer_data: Dict[str, Any], purchase_history: List[Dict[str, Any]]
    ) -> FeatureSet:
        """Extract financial features."""
        try:
            # Monthly spend
            monthly_spend = customer_data.get("monthly_spend", 0)
            if isinstance(monthly_spend, (int, float)):
                features.monthly_spend = float(monthly_spend)

                # Spend category
                if monthly_spend >= self.hk_market_params["premium_threshold"]:
                    features.spend_category = "premium"
                elif monthly_spend >= self.hk_market_params["average_monthly_spend"]:
                    features.spend_category = "standard"
                elif monthly_spend >= self.hk_market_params["budget_threshold"]:
                    features.spend_category = "budget"
                else:
                    features.spend_category = "minimal"

            # Analyze purchase history for spend patterns
            if purchase_history:
                amounts = []
                for purchase in purchase_history:
                    amount = purchase.get("amount", 0)
                    if isinstance(amount, (int, float)) and amount > 0:
                        amounts.append(float(amount))

                if amounts:
                    # Spend variance
                    if len(amounts) > 1:
                        mean_amount = sum(amounts) / len(amounts)
                        variance = sum((x - mean_amount) ** 2 for x in amounts) / len(amounts)
                        features.spend_variance = variance

                    # Payment reliability (simplified)
                    features.payment_reliability = min(1.0, len(amounts) / 12.0)  # Based on purchase frequency

        except Exception as e:
            logger.warning(f"Financial feature extraction error: {e}")

        return features

    def _extract_usage_features(
        self, features: FeatureSet, customer_data: Dict[str, Any], engagement_data: Optional[Dict[str, Any]]
    ) -> FeatureSet:
        """Extract usage features."""
        try:
            # Data usage
            data_usage = customer_data.get("data_usage_gb", 0)
            if isinstance(data_usage, (int, float)):
                features.data_usage_gb = float(data_usage)

            # Voice minutes
            voice_minutes = customer_data.get("voice_minutes", 0)
            if isinstance(voice_minutes, (int, float)):
                features.voice_minutes = float(voice_minutes)

            # SMS count
            sms_count = customer_data.get("sms_count", 0)
            if isinstance(sms_count, (int, float)):
                features.sms_count = int(sms_count)

            # Roaming usage
            roaming_usage = customer_data.get("roaming_usage", 0)
            if isinstance(roaming_usage, (int, float)):
                features.roaming_usage = float(roaming_usage)

            # Extract from engagement data if available
            if engagement_data:
                app_usage = engagement_data.get("app_usage_hours", 0)
                if isinstance(app_usage, (int, float)):
                    features.app_usage_hours = float(app_usage)

        except Exception as e:
            logger.warning(f"Usage feature extraction error: {e}")

        return features

    def _extract_behavioral_features(
        self, features: FeatureSet, purchase_history: List[Dict[str, Any]], engagement_data: Optional[Dict[str, Any]]
    ) -> FeatureSet:
        """Extract behavioral features."""
        try:
            # Purchase frequency
            if purchase_history:
                purchase_count = len(purchase_history)
                if purchase_count >= 10:
                    features.purchase_frequency = "high"
                elif purchase_count >= 5:
                    features.purchase_frequency = "medium"
                else:
                    features.purchase_frequency = "low"

            # Service interactions and satisfaction from engagement data
            if engagement_data:
                features.service_interactions = int(engagement_data.get("service_interactions", 0))
                features.complaint_count = int(engagement_data.get("complaint_count", 0))
                features.satisfaction_score = float(engagement_data.get("satisfaction_score", 5.0))

        except Exception as e:
            logger.warning(f"Behavioral feature extraction error: {e}")

        return features

    def _extract_engagement_features(
        self, features: FeatureSet, engagement_data: Optional[Dict[str, Any]]
    ) -> FeatureSet:
        """Extract engagement features."""
        try:
            if engagement_data:
                # App usage hours already extracted in usage features

                # Digital engagement score
                app_hours = features.app_usage_hours
                interactions = features.service_interactions
                satisfaction = features.satisfaction_score

                # Compute digital engagement score (0-1)
                engagement_score = 0.0
                if app_hours > 0:
                    engagement_score += min(0.4, app_hours / 20.0)  # Max 0.4 for 20+ hours
                if interactions > 0:
                    engagement_score += min(0.3, interactions / 10.0)  # Max 0.3 for 10+ interactions
                if satisfaction > 5.0:
                    engagement_score += min(0.3, (satisfaction - 5.0) / 5.0)  # Max 0.3 for 10/10 satisfaction

                features.digital_engagement = min(1.0, engagement_score)

                # Promotion response rate
                promotion_responses = engagement_data.get("promotion_responses", 0)
                promotion_offers = engagement_data.get("promotion_offers", 1)
                features.promotion_response_rate = min(1.0, promotion_responses / promotion_offers)

        except Exception as e:
            logger.warning(f"Engagement feature extraction error: {e}")

        return features

    def _extract_hk_market_features(self, features: FeatureSet, customer_data: Dict[str, Any]) -> FeatureSet:
        """Extract Hong Kong market-specific features."""
        try:
            # HK market segment based on location and spend
            location_cat = features.location_category
            spend_cat = features.spend_category
            account_type = features.account_type

            if location_cat == "premium_business" and spend_cat in ["premium", "standard"]:
                features.hk_market_segment = "premium_business"
            elif account_type == "business":
                features.hk_market_segment = "corporate"
            elif location_cat == "urban_residential" and features.age_group in ["young_adult", "early_career"]:
                features.hk_market_segment = "urban_professional"
            elif account_type == "family":
                features.hk_market_segment = "family_subscriber"
            else:
                features.hk_market_segment = "general_consumer"

            # Competitor switch risk (simplified assessment)
            risk_factors = 0
            if features.satisfaction_score < 6.0:
                risk_factors += 0.3
            if features.complaint_count > 2:
                risk_factors += 0.2
            if features.spend_category == "minimal":
                risk_factors += 0.2
            if features.tenure_category == "new":
                risk_factors += 0.15

            features.competitor_switch_risk = min(1.0, risk_factors)

            # Regulatory compliance score (always high for processed data)
            features.regulatory_compliance_score = 1.0

        except Exception as e:
            logger.warning(f"HK market feature extraction error: {e}")

        return features

    def _compute_derived_features(self, features: FeatureSet) -> FeatureSet:
        """Compute derived features from base features."""
        try:
            # Customer value score (0-1)
            value_components = []

            # Spend component (40%)
            spend_normalized = min(1.0, features.monthly_spend / self.hk_market_params["premium_threshold"])
            value_components.append(spend_normalized * 0.4)

            # Tenure component (20%)
            tenure_scores = {"new": 0.2, "recent": 0.5, "established": 0.8, "loyal": 1.0}
            tenure_score = tenure_scores.get(features.tenure_category, 0.2)
            value_components.append(tenure_score * 0.2)

            # Engagement component (25%)
            value_components.append(features.digital_engagement * 0.25)

            # Satisfaction component (15%)
            satisfaction_normalized = min(1.0, features.satisfaction_score / 10.0)
            value_components.append(satisfaction_normalized * 0.15)

            features.customer_value_score = sum(value_components)

            # Churn risk score (0-1)
            churn_components = []

            # Satisfaction risk (40%)
            if features.satisfaction_score < 5.0:
                churn_components.append(0.4)
            elif features.satisfaction_score < 7.0:
                churn_components.append(0.2)
            else:
                churn_components.append(0.0)

            # Engagement risk (30%)
            if features.digital_engagement < 0.3:
                churn_components.append(0.3)
            elif features.digital_engagement < 0.6:
                churn_components.append(0.15)
            else:
                churn_components.append(0.0)

            # Complaint risk (20%)
            if features.complaint_count > 3:
                churn_components.append(0.2)
            elif features.complaint_count > 1:
                churn_components.append(0.1)
            else:
                churn_components.append(0.0)

            # Competitor switch risk (10%)
            churn_components.append(features.competitor_switch_risk * 0.1)

            features.churn_risk_score = min(1.0, sum(churn_components))

            # Upsell propensity (0-1)
            upsell_components = []

            # Spending capacity (40%)
            if features.spend_category in ["budget", "minimal"]:
                current_spend_ratio = features.monthly_spend / self.hk_market_params["average_monthly_spend"]
                if current_spend_ratio < 0.8:  # Room to grow
                    upsell_components.append(0.4)
                else:
                    upsell_components.append(0.2)
            elif features.spend_category == "standard":
                upsell_components.append(0.3)
            else:
                upsell_components.append(0.1)  # Premium already

            # Engagement propensity (35%)
            upsell_components.append(features.digital_engagement * 0.35)

            # Satisfaction propensity (25%)
            if features.satisfaction_score >= 8.0:
                upsell_components.append(0.25)
            elif features.satisfaction_score >= 6.0:
                upsell_components.append(0.15)
            else:
                upsell_components.append(0.05)

            features.upsell_propensity = min(1.0, sum(upsell_components))

        except Exception as e:
            logger.warning(f"Derived feature computation error: {e}")

        return features

    # Pattern analysis methods

    def _analyze_spending_patterns(
        self, purchase_history: List[Dict[str, Any]], features: FeatureSet
    ) -> List[PatternAnalysis]:
        """Analyze spending behavior patterns."""
        patterns = []

        try:
            if not purchase_history:
                return patterns

            # Extract spending data
            amounts = []
            dates = []
            for purchase in purchase_history:
                amount = purchase.get("amount", 0)
                date = purchase.get("date", "")
                if isinstance(amount, (int, float)) and amount > 0:
                    amounts.append(float(amount))
                    dates.append(date)

            if not amounts:
                return patterns

            # Analyze spending consistency
            if len(amounts) > 2:
                mean_spend = sum(amounts) / len(amounts)
                variance = sum((x - mean_spend) ** 2 for x in amounts) / len(amounts)
                coefficient_of_variation = math.sqrt(variance) / mean_spend if mean_spend > 0 else 0

                if coefficient_of_variation < 0.2:
                    patterns.append(
                        PatternAnalysis(
                            pattern_type="spending_behavior",
                            pattern_name="consistent_spender",
                            confidence=0.9,
                            description="Customer shows consistent spending patterns with low variance",
                            key_indicators=["Low spending variance", "Regular purchase amounts"],
                            business_impact="High predictability for revenue forecasting",
                            recommended_actions=["Offer subscription plans", "Predictable billing options"],
                        )
                    )
                elif coefficient_of_variation > 0.8:
                    patterns.append(
                        PatternAnalysis(
                            pattern_type="spending_behavior",
                            pattern_name="variable_spender",
                            confidence=0.8,
                            description="Customer shows highly variable spending patterns",
                            key_indicators=["High spending variance", "Irregular purchase amounts"],
                            business_impact="Unpredictable revenue contribution",
                            recommended_actions=["Flexible plans", "Usage-based pricing"],
                        )
                    )

            # Analyze spending trend
            if len(amounts) >= 3:
                recent_avg = sum(amounts[-3:]) / 3
                early_avg = sum(amounts[:3]) / 3

                if recent_avg > early_avg * 1.2:
                    patterns.append(
                        PatternAnalysis(
                            pattern_type="spending_behavior",
                            pattern_name="increasing_spend",
                            confidence=0.8,
                            description="Customer spending is trending upward",
                            key_indicators=["Recent purchases > historical average"],
                            business_impact="Positive revenue growth potential",
                            recommended_actions=["Premium upsell offers", "Value-added services"],
                            trend_direction="increasing",
                        )
                    )
                elif recent_avg < early_avg * 0.8:
                    patterns.append(
                        PatternAnalysis(
                            pattern_type="spending_behavior",
                            pattern_name="decreasing_spend",
                            confidence=0.8,
                            description="Customer spending is trending downward",
                            key_indicators=["Recent purchases < historical average"],
                            business_impact="Risk of revenue decline",
                            recommended_actions=["Retention offers", "Engagement campaigns"],
                            trend_direction="decreasing",
                        )
                    )

        except Exception as e:
            logger.warning(f"Spending pattern analysis error: {e}")

        return patterns

    def _analyze_usage_patterns(
        self, customer_data: Dict[str, Any], engagement_data: Optional[Dict[str, Any]], features: FeatureSet
    ) -> List[PatternAnalysis]:
        """Analyze usage behavior patterns."""
        patterns = []

        try:
            # High data usage pattern
            if features.data_usage_gb > self.hk_market_params["high_usage_data_gb"]:
                patterns.append(
                    PatternAnalysis(
                        pattern_type="usage_patterns",
                        pattern_name="heavy_data_user",
                        confidence=0.9,
                        description="Customer is a heavy data user exceeding average consumption",
                        key_indicators=[f"Data usage: {features.data_usage_gb}GB/month"],
                        business_impact="High value customer for unlimited plans",
                        recommended_actions=["Unlimited data plans", "5G premium services"],
                    )
                )

            # Voice-heavy usage pattern
            if features.voice_minutes > self.hk_market_params["high_voice_minutes"]:
                patterns.append(
                    PatternAnalysis(
                        pattern_type="usage_patterns",
                        pattern_name="voice_heavy_user",
                        confidence=0.85,
                        description="Customer makes extensive use of voice services",
                        key_indicators=[f"Voice usage: {features.voice_minutes} minutes/month"],
                        business_impact="Good candidate for voice-inclusive plans",
                        recommended_actions=["Unlimited calling plans", "International calling packages"],
                    )
                )

            # Digital engagement pattern
            if features.digital_engagement > 0.7:
                patterns.append(
                    PatternAnalysis(
                        pattern_type="usage_patterns",
                        pattern_name="digitally_engaged",
                        confidence=0.8,
                        description="Customer shows high digital engagement across services",
                        key_indicators=["High app usage", "Active service interactions"],
                        business_impact="Receptive to digital services and offers",
                        recommended_actions=["Digital service bundles", "App-based promotions"],
                    )
                )

            # Low usage pattern
            if (
                features.data_usage_gb < self.hk_market_params["standard_data_gb"]
                and features.voice_minutes < 100
                and features.digital_engagement < 0.3
            ):
                patterns.append(
                    PatternAnalysis(
                        pattern_type="usage_patterns",
                        pattern_name="minimal_user",
                        confidence=0.75,
                        description="Customer shows minimal usage across all services",
                        key_indicators=["Low data usage", "Low voice usage", "Low engagement"],
                        business_impact="At risk customer, potential for churn",
                        recommended_actions=["Basic plans", "Education campaigns", "Retention efforts"],
                    )
                )

        except Exception as e:
            logger.warning(f"Usage pattern analysis error: {e}")

        return patterns

    def _analyze_lifecycle_patterns(
        self, customer_data: Dict[str, Any], purchase_history: List[Dict[str, Any]], features: FeatureSet
    ) -> List[PatternAnalysis]:
        """Analyze customer lifecycle patterns."""
        patterns = []

        try:
            # New customer pattern
            if features.tenure_category == "new":
                patterns.append(
                    PatternAnalysis(
                        pattern_type="lifecycle_stage",
                        pattern_name="new_customer_onboarding",
                        confidence=0.9,
                        description="Customer is in the early onboarding phase",
                        key_indicators=["Tenure < 6 months"],
                        business_impact="Critical period for satisfaction and retention",
                        recommended_actions=["Welcome programs", "Onboarding support", "Early engagement"],
                    )
                )

            # Loyal customer pattern
            if features.tenure_category == "loyal" and features.satisfaction_score >= 7.0:
                patterns.append(
                    PatternAnalysis(
                        pattern_type="lifecycle_stage",
                        pattern_name="loyal_advocate",
                        confidence=0.9,
                        description="Long-term satisfied customer with advocacy potential",
                        key_indicators=["Tenure > 24 months", "High satisfaction"],
                        business_impact="High lifetime value and referral potential",
                        recommended_actions=["Loyalty rewards", "Referral programs", "VIP services"],
                    )
                )

            # At-risk established customer
            if (
                features.tenure_category in ["established", "loyal"]
                and features.churn_risk_score > self.hk_market_params["churn_risk_threshold"]
            ):
                patterns.append(
                    PatternAnalysis(
                        pattern_type="lifecycle_stage",
                        pattern_name="at_risk_established",
                        confidence=0.8,
                        description="Established customer showing signs of dissatisfaction",
                        key_indicators=["Long tenure but high churn risk"],
                        business_impact="High-value customer at risk of leaving",
                        recommended_actions=["Retention campaigns", "Personal account management", "Service recovery"],
                    )
                )

        except Exception as e:
            logger.warning(f"Lifecycle pattern analysis error: {e}")

        return patterns

    def _analyze_engagement_patterns(
        self, engagement_data: Optional[Dict[str, Any]], features: FeatureSet
    ) -> List[PatternAnalysis]:
        """Analyze customer engagement patterns."""
        patterns = []

        try:
            if not engagement_data:
                return patterns

            # High engagement pattern
            if features.digital_engagement > 0.7 and features.satisfaction_score >= 8.0:
                patterns.append(
                    PatternAnalysis(
                        pattern_type="engagement_level",
                        pattern_name="highly_engaged_advocate",
                        confidence=0.9,
                        description="Customer is highly engaged and satisfied",
                        key_indicators=["High digital engagement", "High satisfaction score"],
                        business_impact="Strong candidate for premium services and advocacy",
                        recommended_actions=["Premium offers", "Beta testing programs", "Referral incentives"],
                    )
                )

            # Declining engagement pattern
            if (
                features.digital_engagement < 0.4
                and features.service_interactions == 0
                and features.satisfaction_score < 6.0
            ):
                patterns.append(
                    PatternAnalysis(
                        pattern_type="engagement_level",
                        pattern_name="disengaged_at_risk",
                        confidence=0.8,
                        description="Customer shows declining engagement and satisfaction",
                        key_indicators=["Low digital engagement", "No recent interactions", "Low satisfaction"],
                        business_impact="High churn risk requiring immediate intervention",
                        recommended_actions=["Re-engagement campaigns", "Proactive support", "Win-back offers"],
                    )
                )

            # Service-heavy engagement
            if features.service_interactions > 5 and features.complaint_count > 2:
                patterns.append(
                    PatternAnalysis(
                        pattern_type="engagement_level",
                        pattern_name="high_maintenance_customer",
                        confidence=0.75,
                        description="Customer requires frequent service support",
                        key_indicators=["High service interactions", "Multiple complaints"],
                        business_impact="High service cost but potential for improvement",
                        recommended_actions=["Proactive support", "Service improvement", "Alternative solutions"],
                    )
                )

        except Exception as e:
            logger.warning(f"Engagement pattern analysis error: {e}")

        return patterns

    def _analyze_seasonality_patterns(
        self, purchase_history: List[Dict[str, Any]], features: FeatureSet
    ) -> List[PatternAnalysis]:
        """Analyze seasonal patterns in customer behavior."""
        patterns = []

        try:
            if len(purchase_history) < 6:  # Need sufficient data for seasonality
                return patterns

            # Simple seasonality detection (would be more sophisticated in production)
            monthly_spending = defaultdict(list)

            for purchase in purchase_history:
                date_str = purchase.get("date", "")
                amount = purchase.get("amount", 0)

                if date_str and isinstance(amount, (int, float)) and amount > 0:
                    try:
                        # Extract month (simplified - assumes YYYY-MM-DD format)
                        if "-" in date_str:
                            month = date_str.split("-")[1]
                            monthly_spending[month].append(amount)
                    except (ValueError, IndexError, TypeError):
                        continue

            # Analyze monthly patterns
            if len(monthly_spending) >= 3:
                monthly_avg = {}
                for month, amounts in monthly_spending.items():
                    monthly_avg[month] = sum(amounts) / len(amounts)

                overall_avg = sum(monthly_avg.values()) / len(monthly_avg)

                # Identify high-spending months
                high_months = [month for month, avg in monthly_avg.items() if avg > overall_avg * 1.3]
                if high_months:
                    patterns.append(
                        PatternAnalysis(
                            pattern_type="seasonality",
                            pattern_name="seasonal_high_spending",
                            confidence=0.7,
                            description=f"Customer shows increased spending in months: {', '.join(high_months)}",
                            key_indicators=[f"High spending months: {', '.join(high_months)}"],
                            business_impact="Predictable high-value periods for targeted offers",
                            recommended_actions=["Seasonal promotions", "Targeted campaigns"],
                            seasonality=f"High: {', '.join(high_months)}",
                        )
                    )

        except Exception as e:
            logger.warning(f"Seasonality pattern analysis error: {e}")

        return patterns

    def _analyze_churn_risk_patterns(
        self, features: FeatureSet, purchase_history: List[Dict[str, Any]]
    ) -> List[PatternAnalysis]:
        """Analyze patterns that indicate churn risk."""
        patterns = []

        try:
            if features.churn_risk_score > self.hk_market_params["churn_risk_threshold"]:
                risk_factors = []

                if features.satisfaction_score < 5.0:
                    risk_factors.append("Low satisfaction score")
                if features.digital_engagement < 0.3:
                    risk_factors.append("Low digital engagement")
                if features.complaint_count > 2:
                    risk_factors.append("Multiple complaints")
                if features.competitor_switch_risk > 0.6:
                    risk_factors.append("High competitor switch risk")

                confidence = min(0.9, features.churn_risk_score)

                patterns.append(
                    PatternAnalysis(
                        pattern_type="churn_risk",
                        pattern_name="high_churn_risk",
                        confidence=confidence,
                        description="Customer shows multiple indicators of potential churn",
                        key_indicators=risk_factors,
                        business_impact="Immediate risk of customer loss",
                        recommended_actions=[
                            "Immediate retention intervention",
                            "Personal account management",
                            "Service recovery program",
                            "Competitive retention offers",
                        ],
                    )
                )

        except Exception as e:
            logger.warning(f"Churn risk pattern analysis error: {e}")

        return patterns

    # Additional helper methods for clustering and insights

    def _find_optimal_clusters(self, feature_matrix: np.ndarray) -> int:
        """Find optimal number of clusters using elbow method."""
        if len(feature_matrix) < 3:
            return 2

        max_clusters = min(8, len(feature_matrix) // 2)
        inertias = []

        for k in range(2, max_clusters + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(feature_matrix)
            inertias.append(kmeans.inertia_)

        # Simple elbow detection (could be more sophisticated)
        if len(inertias) >= 3:
            return min(5, len(inertias) + 1)  # Conservative approach
        else:
            return 3

    def _analyze_clusters(
        self,
        feature_matrix: np.ndarray,
        cluster_labels: np.ndarray,
        customer_ids: List[str],
        original_features: List[List[float]],
    ) -> Dict[str, Any]:
        """Analyze clustering results and generate insights."""
        try:
            cluster_analysis = {
                "n_clusters": len(set(cluster_labels)),
                "silhouette_score": silhouette_score(feature_matrix, cluster_labels),
                "clusters": {},
                "insights": [],
            }

            # Analyze each cluster
            for cluster_id in set(cluster_labels):
                cluster_mask = cluster_labels == cluster_id
                cluster_customers = [customer_ids[i] for i in range(len(customer_ids)) if cluster_mask[i]]
                cluster_features = feature_matrix[cluster_mask]

                cluster_info = {
                    "cluster_id": int(cluster_id),
                    "size": len(cluster_customers),
                    "customers": cluster_customers,
                    "centroid": cluster_features.mean(axis=0).tolist(),
                    "characteristics": self._describe_cluster_characteristics(cluster_features),
                }

                cluster_analysis["clusters"][f"cluster_{cluster_id}"] = cluster_info

            # Generate overall insights
            cluster_analysis["insights"] = self._generate_cluster_insights(cluster_analysis["clusters"])

            return cluster_analysis

        except Exception as e:
            logger.error(f"Cluster analysis failed: {e}")
            return {"error": str(e)}

    def _describe_cluster_characteristics(self, cluster_features: np.ndarray) -> Dict[str, str]:
        """Describe the characteristics of a cluster."""
        characteristics = {}

        try:
            # Simple statistical description
            mean_features = cluster_features.mean(axis=0)

            # This would map back to feature names in a real implementation
            characteristics["description"] = f"Cluster with {len(cluster_features)} customers"
            characteristics["size_category"] = "large" if len(cluster_features) > 10 else "small"

        except Exception as e:
            logger.warning(f"Cluster characteristics description error: {e}")

        return characteristics

    def _generate_cluster_insights(self, clusters: Dict[str, Any]) -> List[str]:
        """Generate business insights from clustering results."""
        insights = []

        try:
            total_customers = sum(cluster["size"] for cluster in clusters.values())

            for cluster_name, cluster_info in clusters.items():
                percentage = (cluster_info["size"] / total_customers) * 100
                insights.append(f"{cluster_name}: {cluster_info['size']} customers ({percentage:.1f}%)")

            # Add strategic insights
            largest_cluster = max(clusters.values(), key=lambda x: x["size"])
            insights.append(
                f"Largest segment represents {(largest_cluster['size']/total_customers)*100:.1f}% of customers"
            )

        except Exception as e:
            logger.warning(f"Cluster insights generation error: {e}")

        return insights

    # Segmentation and assessment methods

    def _apply_segmentation_rules(self, features: FeatureSet) -> Tuple[CustomerSegment, float]:
        """Apply business rules to segment customer."""
        try:
            # Premium Business segment
            if (
                features.location_category == "premium_business"
                and features.spend_category in ["premium", "standard"]
                and features.account_type in ["premium", "business"]
            ):
                return CustomerSegment.PREMIUM_BUSINESS, 0.9

            # Enterprise Client segment
            if (
                features.account_type == "business"
                and features.monthly_spend >= self.hk_market_params["premium_threshold"]
            ):
                return CustomerSegment.ENTERPRISE_CLIENT, 0.85

            # High Value Loyalist segment
            if (
                features.tenure_category == "loyal"
                and features.customer_value_score >= 0.8
                and features.satisfaction_score >= 8.0
            ):
                return CustomerSegment.HIGH_VALUE_LOYALIST, 0.9

            # Urban Professional segment
            if (
                features.location_category == "urban_residential"
                and features.age_group in ["early_career", "mid_career"]
                and features.digital_engagement >= 0.6
            ):
                return CustomerSegment.URBAN_PROFESSIONAL, 0.8

            # Family Subscriber segment
            if features.account_type == "family":
                return CustomerSegment.FAMILY_SUBSCRIBER, 0.85

            # Young Digital segment
            if features.age_group == "young_adult" and features.digital_engagement >= 0.7:
                return CustomerSegment.YOUNG_DIGITAL, 0.8

            # Inactive Churner segment
            if features.churn_risk_score >= self.hk_market_params["churn_risk_threshold"]:
                return CustomerSegment.INACTIVE_CHURNER, 0.75

            # Default to Budget Conscious
            return CustomerSegment.BUDGET_CONSCIOUS, 0.6

        except Exception as e:
            logger.warning(f"Customer segmentation error: {e}")
            return CustomerSegment.BUDGET_CONSCIOUS, 0.5

    def _assess_churn_risk(self, features: FeatureSet, patterns: List[PatternAnalysis]) -> Dict[str, Any]:
        """Assess comprehensive churn risk."""
        try:
            churn_risk = {
                "risk_score": features.churn_risk_score,
                "risk_level": self._get_risk_level(features.churn_risk_score),
                "risk_factors": [],
                "protective_factors": [],
                "recommended_interventions": [],
            }

            # Identify risk factors
            if features.satisfaction_score < 6.0:
                churn_risk["risk_factors"].append("Low satisfaction score")
            if features.complaint_count > 2:
                churn_risk["risk_factors"].append("Multiple recent complaints")
            if features.digital_engagement < 0.4:
                churn_risk["risk_factors"].append("Low digital engagement")
            if features.competitor_switch_risk > 0.6:
                churn_risk["risk_factors"].append("High competitor appeal")

            # Identify protective factors
            if features.tenure_category in ["established", "loyal"]:
                churn_risk["protective_factors"].append("Long tenure relationship")
            if features.customer_value_score > 0.7:
                churn_risk["protective_factors"].append("High customer value")
            if features.satisfaction_score >= 8.0:
                churn_risk["protective_factors"].append("High satisfaction")

            # Recommend interventions based on risk level
            if churn_risk["risk_score"] >= 0.8:
                churn_risk["recommended_interventions"].extend(
                    ["Immediate personal contact", "Service recovery program", "Retention specialist assignment"]
                )
            elif churn_risk["risk_score"] >= 0.6:
                churn_risk["recommended_interventions"].extend(
                    ["Proactive retention campaign", "Satisfaction survey", "Competitive offer matching"]
                )

            return churn_risk

        except Exception as e:
            logger.warning(f"Churn risk assessment error: {e}")
            return {"risk_score": 0.5, "risk_level": "medium"}

    def _assess_upsell_potential(self, features: FeatureSet, patterns: List[PatternAnalysis]) -> Dict[str, Any]:
        """Assess upsell and cross-sell potential."""
        try:
            upsell_assessment = {
                "upsell_score": features.upsell_propensity,
                "potential_level": self._get_potential_level(features.upsell_propensity),
                "upsell_opportunities": [],
                "cross_sell_opportunities": [],
                "recommended_offers": [],
            }

            # Identify upsell opportunities
            if features.spend_category in ["budget", "minimal"]:
                upsell_assessment["upsell_opportunities"].append("Plan upgrade potential")
            if features.data_usage_gb > self.hk_market_params["high_usage_data_gb"]:
                upsell_assessment["upsell_opportunities"].append("Unlimited data plan")
            if features.satisfaction_score >= 8.0:
                upsell_assessment["upsell_opportunities"].append("Premium service features")

            # Identify cross-sell opportunities
            if features.roaming_usage == 0 and features.location_category == "premium_business":
                upsell_assessment["cross_sell_opportunities"].append("International roaming package")
            if features.account_type != "family" and features.age_group in ["mid_career", "senior_professional"]:
                upsell_assessment["cross_sell_opportunities"].append("Family plan addition")
            if features.digital_engagement > 0.7:
                upsell_assessment["cross_sell_opportunities"].append("Digital service bundle")

            # Generate specific recommendations
            if upsell_assessment["upsell_score"] >= 0.7:
                upsell_assessment["recommended_offers"].extend(
                    [
                        "Premium plan upgrade with incentives",
                        "Value-added services bundle",
                        "Loyalty program enrollment",
                    ]
                )

            return upsell_assessment

        except Exception as e:
            logger.warning(f"Upsell assessment error: {e}")
            return {"upsell_score": 0.5, "potential_level": "medium"}

    # Helper methods for insights generation

    def _identify_opportunities(
        self, features: FeatureSet, patterns: List[PatternAnalysis], segment: CustomerSegment
    ) -> Dict[str, Any]:
        """Identify business opportunities for the customer."""
        opportunities = {
            "revenue_opportunities": [],
            "retention_opportunities": [],
            "engagement_opportunities": [],
            "cost_optimization_opportunities": [],
        }

        try:
            # Revenue opportunities
            if features.upsell_propensity >= 0.6:
                opportunities["revenue_opportunities"].append(
                    {
                        "type": "upsell",
                        "description": "Customer shows strong upsell potential",
                        "estimated_impact": "high",
                    }
                )

            if features.customer_value_score >= 0.7 and features.satisfaction_score >= 8.0:
                opportunities["revenue_opportunities"].append(
                    {
                        "type": "advocacy",
                        "description": "Customer could become brand advocate",
                        "estimated_impact": "medium",
                    }
                )

            # Retention opportunities
            if features.churn_risk_score >= 0.6:
                opportunities["retention_opportunities"].append(
                    {"type": "retention", "description": "Proactive retention required", "urgency": "high"}
                )

            # Engagement opportunities
            if features.digital_engagement < 0.5:
                opportunities["engagement_opportunities"].append(
                    {"type": "digital_adoption", "description": "Increase digital service usage", "potential": "medium"}
                )

            # Cost optimization
            if features.service_interactions > 5:
                opportunities["cost_optimization_opportunities"].append(
                    {
                        "type": "self_service",
                        "description": "Migrate to self-service channels",
                        "cost_savings": "medium",
                    }
                )

        except Exception as e:
            logger.warning(f"Opportunity identification error: {e}")

        return opportunities

    def _generate_recommendations(
        self, features: FeatureSet, patterns: List[PatternAnalysis], opportunities: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate actionable business recommendations."""
        recommendations = []

        try:
            # High-priority recommendations based on risk and opportunity
            if features.churn_risk_score >= 0.8:
                recommendations.append(
                    {
                        "priority": "critical",
                        "category": "retention",
                        "action": "Immediate retention intervention",
                        "description": "Customer at critical risk of churn - requires immediate personal attention",
                        "timeline": "immediate",
                        "expected_outcome": "Prevent churn",
                    }
                )

            if features.upsell_propensity >= 0.8 and features.satisfaction_score >= 8.0:
                recommendations.append(
                    {
                        "priority": "high",
                        "category": "revenue_growth",
                        "action": "Premium upsell offer",
                        "description": "Present premium service upgrade with personalized benefits",
                        "timeline": "this_month",
                        "expected_outcome": "20-30% revenue increase",
                    }
                )

            # Medium-priority recommendations
            if features.digital_engagement < 0.5:
                recommendations.append(
                    {
                        "priority": "medium",
                        "category": "engagement",
                        "action": "Digital adoption campaign",
                        "description": "Encourage adoption of digital services and self-service options",
                        "timeline": "next_quarter",
                        "expected_outcome": "Improved engagement and reduced service costs",
                    }
                )

            # Segment-specific recommendations
            if features.hk_market_segment == "premium_business":
                recommendations.append(
                    {
                        "priority": "medium",
                        "category": "service_enhancement",
                        "action": "Business service review",
                        "description": "Schedule dedicated business account review",
                        "timeline": "next_month",
                        "expected_outcome": "Enhanced business relationship",
                    }
                )

        except Exception as e:
            logger.warning(f"Recommendation generation error: {e}")

        return recommendations

    # Utility methods

    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to risk level."""
        if risk_score >= 0.8:
            return "critical"
        elif risk_score >= 0.6:
            return "high"
        elif risk_score >= 0.4:
            return "medium"
        else:
            return "low"

    def _get_potential_level(self, potential_score: float) -> str:
        """Convert potential score to potential level."""
        if potential_score >= 0.8:
            return "very_high"
        elif potential_score >= 0.6:
            return "high"
        elif potential_score >= 0.4:
            return "medium"
        else:
            return "low"

    def _get_segment_description(self, segment: CustomerSegment) -> str:
        """Get description for customer segment."""
        descriptions = {
            CustomerSegment.PREMIUM_BUSINESS: "High-value business customer in premium Hong Kong locations",
            CustomerSegment.URBAN_PROFESSIONAL: "Career-focused urban professional with digital preferences",
            CustomerSegment.FAMILY_SUBSCRIBER: "Family-oriented customer with multiple line needs",
            CustomerSegment.YOUNG_DIGITAL: "Digital-native young customer with high engagement",
            CustomerSegment.BUDGET_CONSCIOUS: "Price-sensitive customer focused on value",
            CustomerSegment.ENTERPRISE_CLIENT: "Large business customer with complex needs",
            CustomerSegment.INACTIVE_CHURNER: "At-risk customer showing signs of disengagement",
            CustomerSegment.HIGH_VALUE_LOYALIST: "Long-term high-value customer with strong loyalty",
        }
        return descriptions.get(segment, "General customer segment")

    def _calculate_health_score(self, features: FeatureSet) -> float:
        """Calculate overall customer health score."""
        try:
            health_components = [
                features.satisfaction_score / 10.0 * 0.3,  # Satisfaction (30%)
                features.digital_engagement * 0.25,  # Engagement (25%)
                (1.0 - features.churn_risk_score) * 0.25,  # Retention (25%)
                features.customer_value_score * 0.2,  # Value (20%)
            ]
            return min(1.0, sum(health_components))
        except:
            return 0.5

    def _assess_market_position(self, features: FeatureSet) -> str:
        """Assess customer's position in Hong Kong market."""
        try:
            if features.monthly_spend >= self.hk_market_params["premium_threshold"]:
                return "premium_segment"
            elif features.monthly_spend >= self.hk_market_params["average_monthly_spend"]:
                return "mainstream_segment"
            else:
                return "value_segment"
        except:
            return "mainstream_segment"

    def _assess_competitive_position(self, features: FeatureSet) -> str:
        """Assess competitive positioning."""
        try:
            if features.competitor_switch_risk < 0.3 and features.satisfaction_score >= 8.0:
                return "strong_position"
            elif features.competitor_switch_risk >= 0.7:
                return "vulnerable_position"
            else:
                return "neutral_position"
        except:
            return "neutral_position"

    def _get_value_tier(self, value_score: float) -> str:
        """Get customer value tier."""
        if value_score >= 0.8:
            return "platinum"
        elif value_score >= 0.6:
            return "gold"
        elif value_score >= 0.4:
            return "silver"
        else:
            return "bronze"

    def _get_engagement_level(self, engagement_score: float) -> str:
        """Get engagement level description."""
        if engagement_score >= 0.8:
            return "highly_engaged"
        elif engagement_score >= 0.6:
            return "moderately_engaged"
        elif engagement_score >= 0.4:
            return "lightly_engaged"
        else:
            return "minimally_engaged"

    def _calculate_priority_score(
        self, features: FeatureSet, churn_risk: Dict[str, Any], upsell: Dict[str, Any]
    ) -> float:
        """Calculate overall priority score for customer attention."""
        try:
            priority_components = [
                features.customer_value_score * 0.4,  # Value weight
                churn_risk.get("risk_score", 0.5) * 0.35,  # Risk weight
                upsell.get("upsell_score", 0.5) * 0.25,  # Opportunity weight
            ]
            return min(1.0, sum(priority_components))
        except:
            return 0.5

    def _extract_key_insights(
        self, features: FeatureSet, patterns: List[PatternAnalysis], opportunities: Dict[str, Any]
    ) -> List[str]:
        """Extract top 3-5 key insights for executive summary."""
        insights = []

        try:
            # Value insight
            value_tier = self._get_value_tier(features.customer_value_score)
            insights.append(f"Customer is in {value_tier} value tier with score {features.customer_value_score:.2f}")

            # Risk insight
            if features.churn_risk_score >= 0.7:
                insights.append(f"High churn risk ({features.churn_risk_score:.2f}) - immediate attention required")
            elif features.churn_risk_score <= 0.3:
                insights.append(f"Low churn risk ({features.churn_risk_score:.2f}) - stable customer")

            # Opportunity insight
            if features.upsell_propensity >= 0.7:
                insights.append(
                    f"Strong upsell potential ({features.upsell_propensity:.2f}) - revenue growth opportunity"
                )

            # Engagement insight
            engagement_level = self._get_engagement_level(features.digital_engagement)
            insights.append(f"Customer is {engagement_level} with digital services")

            # Pattern insight
            high_confidence_patterns = [p for p in patterns if p.confidence >= 0.8]
            if high_confidence_patterns:
                key_pattern = high_confidence_patterns[0]
                insights.append(f"Key behavior: {key_pattern.pattern_name} - {key_pattern.business_impact}")

        except Exception as e:
            logger.warning(f"Key insights extraction error: {e}")

        return insights[:5]  # Return top 5 insights


# Convenience functions
def analyze_single_customer(
    customer_data: Dict[str, Any],
    purchase_history: List[Dict[str, Any]],
    engagement_data: Optional[Dict[str, Any]] = None,
    enable_ml: bool = True,
) -> Dict[str, Any]:
    """
    Quick analysis of a single customer.

    Args:
        customer_data: Customer profile data
        purchase_history: Purchase history records
        engagement_data: Optional engagement metrics
        enable_ml: Enable machine learning features

    Returns:
        Comprehensive customer analysis results
    """
    analyzer = CustomerDataAnalyzer(enable_ml_clustering=enable_ml)
    return analyzer.generate_customer_insights(customer_data, purchase_history, engagement_data)


def batch_analyze_customers(customer_datasets: List[Dict[str, Any]], enable_clustering: bool = True) -> Dict[str, Any]:
    """
    Analyze multiple customers and perform clustering.

    Args:
        customer_datasets: List of customer data dictionaries
        enable_clustering: Enable customer clustering analysis

    Returns:
        Batch analysis results including clustering insights
    """
    analyzer = CustomerDataAnalyzer(enable_ml_clustering=enable_clustering)

    results = {"individual_analyses": [], "clustering_results": None, "batch_insights": {}}

    # Analyze each customer individually
    for data in customer_datasets:
        customer_data = data.get("customer_data", {})
        purchase_history = data.get("purchase_history", [])
        engagement_data = data.get("engagement_data", {})

        analysis = analyzer.generate_customer_insights(customer_data, purchase_history, engagement_data)
        results["individual_analyses"].append(analysis)

    # Perform clustering if enabled
    if enable_clustering and len(customer_datasets) >= 3:
        clustering_results = analyzer.cluster_customers(customer_datasets)
        results["clustering_results"] = clustering_results

    # Generate batch insights
    results["batch_insights"] = _generate_batch_insights(results["individual_analyses"])

    return results


def _generate_batch_insights(individual_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate insights across multiple customer analyses."""
    if not individual_analyses:
        return {}

    try:
        # Aggregate statistics
        total_customers = len(individual_analyses)

        # Risk distribution
        risk_levels = [
            analysis.get("risk_assessments", {}).get("churn_risk", {}).get("risk_level", "medium")
            for analysis in individual_analyses
        ]
        risk_distribution = Counter(risk_levels)

        # Segment distribution
        segments = [analysis.get("segment", {}).get("category", "unknown") for analysis in individual_analyses]
        segment_distribution = Counter(segments)

        # Value tier distribution
        value_tiers = [
            analysis.get("summary", {}).get("customer_value_tier", "bronze") for analysis in individual_analyses
        ]
        value_distribution = Counter(value_tiers)

        batch_insights = {
            "total_customers_analyzed": total_customers,
            "risk_distribution": dict(risk_distribution),
            "segment_distribution": dict(segment_distribution),
            "value_tier_distribution": dict(value_distribution),
            "high_risk_customers": len([r for r in risk_levels if r in ["critical", "high"]]),
            "high_value_customers": len([v for v in value_tiers if v in ["platinum", "gold"]]),
            "summary": f"Analyzed {total_customers} customers with {risk_distribution.get('critical', 0) + risk_distribution.get('high', 0)} high-risk cases",
        }

        return batch_insights

    except Exception as e:
        logger.warning(f"Batch insights generation error: {e}")
        return {"error": str(e)}
