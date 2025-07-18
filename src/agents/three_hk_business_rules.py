"""
Three HK Business Rules and Offer Matching Engine for Agentic AI Revenue Assistant

This module implements comprehensive business rules, product catalog, and offer matching
logic specifically for Three HK telecommunications services. It provides sophisticated
matching algorithms that consider customer profiles, market segments, compliance
requirements, and campaign management.

Key Features:
- Complete Three HK product catalog with eligibility criteria
- Advanced offer matching algorithms with personalization
- Campaign management and promotional logic
- Regulatory compliance and suitability checks
- Cross-sell and upsell recommendation engine
- Pricing strategies and competitive positioning
- Integration with customer analysis and lead scoring
- Hong Kong telecom market specialization
"""

import os
import json
import time
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import math
from decimal import Decimal

# Import existing components
try:
    from .customer_analysis import CustomerDataAnalyzer, FeatureSet, CustomerSegment
    from .lead_scoring import LeadScore, LeadPriority, LeadQualification
except ImportError:
    from customer_analysis import CustomerDataAnalyzer, FeatureSet, CustomerSegment
    from lead_scoring import LeadScore, LeadPriority, LeadQualification

# Configure logging
logger = logging.getLogger(__name__)


class ProductCategory(Enum):
    """Three HK product categories."""

    MOBILE_PLANS = "mobile_plans"
    DATA_PLANS = "data_plans"
    BUSINESS_SOLUTIONS = "business_solutions"
    FAMILY_PLANS = "family_plans"
    DEVICE_BUNDLES = "device_bundles"
    VALUE_ADDED_SERVICES = "value_added_services"
    ROAMING_SERVICES = "roaming_services"
    ENTERPRISE_SOLUTIONS = "enterprise_solutions"


class OfferType(Enum):
    """Types of offers available."""

    PLAN_UPGRADE = "plan_upgrade"
    NEW_SUBSCRIPTION = "new_subscription"
    ADD_ON_SERVICE = "add_on_service"
    DEVICE_BUNDLE = "device_bundle"
    RETENTION_OFFER = "retention_offer"
    PROMOTIONAL_DISCOUNT = "promotional_discount"
    LOYALTY_REWARD = "loyalty_reward"
    CROSS_SELL = "cross_sell"


class EligibilityStatus(Enum):
    """Eligibility status for offers."""

    ELIGIBLE = "eligible"
    NOT_ELIGIBLE = "not_eligible"
    CONDITIONALLY_ELIGIBLE = "conditionally_eligible"
    REQUIRES_VERIFICATION = "requires_verification"


@dataclass
class ThreeHKProduct:
    """Comprehensive Three HK product definition."""

    # Product identification
    product_id: str
    product_name: str
    category: ProductCategory

    # Pricing and terms
    monthly_price: Decimal
    setup_fee: Decimal = Decimal("0.00")
    contract_duration_months: int = 12
    currency: str = "HKD"

    # Features and benefits
    features: List[str] = None
    data_allowance_gb: Optional[float] = None
    voice_minutes: Optional[int] = None
    sms_allowance: Optional[int] = None

    # Eligibility criteria
    min_monthly_spend: Decimal = Decimal("200.00")
    max_monthly_spend: Optional[Decimal] = None
    required_tenure_months: int = 0
    excluded_segments: List[str] = None
    required_segments: List[str] = None

    # Geographic restrictions
    available_locations: List[str] = None  # If None, available everywhere
    excluded_locations: List[str] = None

    # Business rules
    max_concurrent_subscriptions: int = 1
    requires_credit_check: bool = False
    requires_income_verification: bool = False

    # Campaign and promotional
    promotional_discount: Decimal = Decimal("0.00")
    promotion_end_date: Optional[str] = None
    campaign_code: Optional[str] = None

    # Target segments
    target_segments: List[str] = None
    priority_segments: List[str] = None

    def __post_init__(self):
        if self.features is None:
            self.features = []
        if self.excluded_segments is None:
            self.excluded_segments = []
        if self.required_segments is None:
            self.required_segments = []
        if self.target_segments is None:
            self.target_segments = []
        if self.priority_segments is None:
            self.priority_segments = []


@dataclass
class OfferMatch:
    """Container for matched offer with eligibility and personalization."""

    # Product and offer details
    product: ThreeHKProduct
    offer_type: OfferType
    eligibility_status: EligibilityStatus

    # Personalization
    match_score: float  # 0-100 relevance score
    confidence_level: float  # 0-1 confidence in recommendation

    # Pricing and value
    recommended_price: Decimal
    discount_amount: Decimal = Decimal("0.00")
    estimated_monthly_value: Decimal = Decimal("0.00")

    # Timing and conditions
    offer_valid_until: Optional[str] = None
    conditions: List[str] = None
    next_review_date: Optional[str] = None

    # Sales strategy
    presentation_priority: int = 1  # 1 = highest priority
    sales_approach: str = ""
    key_selling_points: List[str] = None
    potential_objections: List[str] = None

    # Business context
    cross_sell_opportunities: List[str] = None
    upsell_potential: Optional[str] = None
    retention_value: float = 0.0

    def __post_init__(self):
        if self.conditions is None:
            self.conditions = []
        if self.key_selling_points is None:
            self.key_selling_points = []
        if self.potential_objections is None:
            self.potential_objections = []
        if self.cross_sell_opportunities is None:
            self.cross_sell_opportunities = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return asdict(self)


class ThreeHKBusinessRulesEngine:
    """
    Comprehensive business rules and offer matching engine for Three HK.

    This engine implements sophisticated business logic for product eligibility,
    offer matching, campaign management, and regulatory compliance specifically
    designed for Three HK's Hong Kong telecom operations.
    """

    def __init__(self):
        """Initialize the Three HK business rules engine."""

        # Hong Kong telecom regulatory parameters
        self.regulatory_params = {
            "data_privacy_compliance": True,
            "consumer_protection_act": True,
            "telecom_licensing_requirements": True,
            "age_verification_required": 18,
            "income_verification_threshold": Decimal("50000.00"),  # Annual HKD
            "cooling_off_period_days": 7,
            "contract_disclosure_required": True,
        }

        # Three HK specific business parameters
        self.business_params = {
            "min_customer_age": 18,
            "max_family_lines": 8,
            "loyalty_tenure_months": 24,
            "premium_spend_threshold": Decimal("1000.00"),
            "enterprise_min_lines": 10,
            "credit_score_threshold": 650,
            "maximum_concurrent_offers": 3,
            "offer_validity_days": 30,
        }

        # Market positioning parameters
        self.market_params = {
            "competitive_price_factor": 0.95,  # Price 5% below market
            "premium_positioning_multiplier": 1.15,
            "discount_limit_percentage": 0.30,  # Max 30% discount
            "loyalty_discount_percentage": 0.10,  # 10% loyalty discount
            "retention_max_discount": 0.25,  # Max 25% retention discount
        }

        # Initialize product catalog
        self.product_catalog = self._initialize_product_catalog()

        # Initialize business rules
        self.eligibility_rules = self._initialize_eligibility_rules()
        self.pricing_rules = self._initialize_pricing_rules()
        self.campaign_rules = self._initialize_campaign_rules()

        logger.info("Three HK Business Rules Engine initialized with comprehensive product catalog")

    def match_offers_for_customer(
        self,
        customer_features: FeatureSet,
        lead_score: LeadScore,
        customer_segment: CustomerSegment,
        current_products: List[str] = None,
        market_context: Optional[Dict[str, Any]] = None,
    ) -> List[OfferMatch]:
        """
        Match relevant Three HK offers for a specific customer.

        Args:
            customer_features: Customer feature analysis
            lead_score: Lead scoring results
            customer_segment: Customer segmentation
            current_products: Currently subscribed products
            market_context: Market and competitive context

        Returns:
            List of matched offers ranked by relevance
        """
        try:
            current_products = current_products or []
            market_context = market_context or {}

            matched_offers = []

            # Evaluate each product for eligibility and relevance
            for product in self.product_catalog:

                # Check basic eligibility
                eligibility_result = self._evaluate_product_eligibility(
                    product, customer_features, customer_segment, current_products
                )

                if eligibility_result["status"] != EligibilityStatus.NOT_ELIGIBLE:

                    # Calculate match score
                    match_score = self._calculate_match_score(product, customer_features, lead_score, customer_segment)

                    if match_score >= 30.0:  # Minimum match threshold

                        # Determine offer type
                        offer_type = self._determine_offer_type(
                            product, customer_features, current_products, lead_score
                        )

                        # Calculate personalized pricing
                        pricing_result = self._calculate_personalized_pricing(
                            product, customer_features, lead_score, market_context
                        )

                        # Generate sales strategy
                        sales_strategy = self._generate_sales_strategy(
                            product, customer_features, lead_score, customer_segment
                        )

                        # Create offer match
                        offer_match = OfferMatch(
                            product=product,
                            offer_type=offer_type,
                            eligibility_status=eligibility_result["status"],
                            match_score=match_score,
                            confidence_level=eligibility_result["confidence"],
                            recommended_price=pricing_result["final_price"],
                            discount_amount=pricing_result["discount_amount"],
                            estimated_monthly_value=pricing_result["value_estimate"],
                            offer_valid_until=self._calculate_offer_expiry(),
                            conditions=eligibility_result["conditions"],
                            presentation_priority=self._calculate_presentation_priority(match_score, lead_score),
                            sales_approach=sales_strategy["approach"],
                            key_selling_points=sales_strategy["selling_points"],
                            potential_objections=sales_strategy["objections"],
                            cross_sell_opportunities=self._identify_cross_sell_opportunities(
                                product, customer_features
                            ),
                            upsell_potential=self._assess_upsell_potential(product, customer_features),
                            retention_value=self._calculate_retention_value(product, customer_features),
                        )

                        matched_offers.append(offer_match)

            # Sort offers by match score and presentation priority
            matched_offers.sort(key=lambda x: (x.match_score, -x.presentation_priority), reverse=True)

            # Limit to maximum concurrent offers
            max_offers = self.business_params["maximum_concurrent_offers"]
            final_offers = matched_offers[:max_offers]

            logger.info(f"Matched {len(final_offers)} offers for customer segment {customer_segment.value}")

            return final_offers

        except Exception as e:
            logger.error(f"Offer matching failed: {e}")
            return []

    def validate_offer_compliance(self, offer_match: OfferMatch, customer_features: FeatureSet) -> Dict[str, Any]:
        """
        Validate offer compliance with Three HK business rules and regulations.

        Args:
            offer_match: Offer to validate
            customer_features: Customer profile

        Returns:
            Compliance validation results
        """
        try:
            compliance_result = {
                "is_compliant": True,
                "compliance_score": 100.0,
                "violations": [],
                "warnings": [],
                "required_actions": [],
                "documentation_required": [],
            }

            # Age verification compliance
            if offer_match.product.requires_income_verification:
                if customer_features.age_group == "young_adult":
                    compliance_result["required_actions"].append("Income verification required")
                    compliance_result["documentation_required"].append("Proof of income")

            # Spend verification
            if offer_match.product.min_monthly_spend > Decimal(str(customer_features.monthly_spend)):
                if offer_match.product.min_monthly_spend > self.business_params["premium_spend_threshold"]:
                    compliance_result["warnings"].append("Customer may not meet minimum spend requirement")
                    compliance_result["compliance_score"] -= 10.0

            # Credit check requirement
            if offer_match.product.requires_credit_check:
                compliance_result["required_actions"].append("Credit check verification")
                compliance_result["documentation_required"].append("Credit assessment")

            # Contract disclosure
            if self.regulatory_params["contract_disclosure_required"]:
                compliance_result["required_actions"].append("Contract terms disclosure")
                compliance_result["documentation_required"].append("Signed disclosure acknowledgment")

            # Data privacy consent
            if self.regulatory_params["data_privacy_compliance"]:
                compliance_result["required_actions"].append("Data privacy consent verification")
                compliance_result["documentation_required"].append("Privacy consent form")

            # Determine final compliance status
            if len(compliance_result["violations"]) > 0:
                compliance_result["is_compliant"] = False
            elif compliance_result["compliance_score"] < 80.0:
                compliance_result["is_compliant"] = False
                compliance_result["violations"].append("Compliance score below threshold")

            return compliance_result

        except Exception as e:
            logger.error(f"Compliance validation failed: {e}")
            return {
                "is_compliant": False,
                "compliance_score": 0.0,
                "violations": [f"Validation error: {str(e)}"],
                "warnings": [],
                "required_actions": [],
                "documentation_required": [],
            }

    def get_campaign_offers(
        self, campaign_code: Optional[str] = None, target_segment: Optional[str] = None, active_only: bool = True
    ) -> List[ThreeHKProduct]:
        """
        Get available campaign offers based on criteria.

        Args:
            campaign_code: Specific campaign code
            target_segment: Target customer segment
            active_only: Only return currently active campaigns

        Returns:
            List of campaign products
        """
        try:
            campaign_offers = []
            current_date = datetime.now()

            for product in self.product_catalog:
                # Check campaign code
                if campaign_code and product.campaign_code != campaign_code:
                    continue

                # Check if product has any promotional component
                if not product.campaign_code and product.promotional_discount <= 0:
                    continue

                # Check if campaign is active
                if active_only and product.promotion_end_date:
                    end_date = datetime.fromisoformat(product.promotion_end_date)
                    if current_date > end_date:
                        continue

                # Check target segment
                if target_segment:
                    if (
                        target_segment not in product.target_segments
                        and target_segment not in product.priority_segments
                    ):
                        continue

                campaign_offers.append(product)

            # Sort by promotional value
            campaign_offers.sort(key=lambda x: x.promotional_discount, reverse=True)

            logger.info(f"Retrieved {len(campaign_offers)} campaign offers")

            return campaign_offers

        except Exception as e:
            logger.error(f"Campaign offer retrieval failed: {e}")
            return []

    def _initialize_product_catalog(self) -> List[ThreeHKProduct]:
        """Initialize comprehensive Three HK product catalog."""
        catalog = []

        # Premium 5G Plans
        catalog.append(
            ThreeHKProduct(
                product_id="THREE_5G_UNLIMITED_PREMIUM",
                product_name="5G Unlimited Premium",
                category=ProductCategory.MOBILE_PLANS,
                monthly_price=Decimal("799.00"),
                features=[
                    "Unlimited 5G Data",
                    "Priority Network Access",
                    "International Roaming",
                    "Premium Customer Support",
                    "Cloud Storage 100GB",
                    "Streaming Services",
                ],
                data_allowance_gb=None,  # Unlimited
                voice_minutes=None,  # Unlimited
                sms_allowance=None,  # Unlimited
                min_monthly_spend=Decimal("600.00"),
                required_segments=["premium_business", "urban_professional", "high_value_loyalist"],
                target_segments=["premium_business", "urban_professional", "enterprise_client"],
                priority_segments=["premium_business"],
                requires_credit_check=True,
            )
        )

        # Business Solutions
        catalog.append(
            ThreeHKProduct(
                product_id="THREE_BUSINESS_PRO_ENTERPRISE",
                product_name="Business Pro Enterprise",
                category=ProductCategory.BUSINESS_SOLUTIONS,
                monthly_price=Decimal("1299.00"),
                setup_fee=Decimal("500.00"),
                contract_duration_months=24,
                features=[
                    "Multi-line Management",
                    "VPN Access",
                    "Priority Support 24/7",
                    "Cloud Integration",
                    "Advanced Analytics",
                    "Dedicated Account Manager",
                ],
                min_monthly_spend=Decimal("1000.00"),
                required_segments=["enterprise_client", "premium_business"],
                max_concurrent_subscriptions=5,
                requires_credit_check=True,
                requires_income_verification=True,
            )
        )

        # Family Plans
        catalog.append(
            ThreeHKProduct(
                product_id="THREE_FAMILY_SHARE_PLUS",
                product_name="Family Share Plus",
                category=ProductCategory.FAMILY_PLANS,
                monthly_price=Decimal("899.00"),
                features=[
                    "4 Lines Included",
                    "Shared Data Pool 200GB",
                    "Parental Controls",
                    "Family Locator",
                    "Content Filtering",
                    "Multi-device Support",
                ],
                data_allowance_gb=200.0,
                voice_minutes=None,  # Unlimited
                min_monthly_spend=Decimal("400.00"),
                required_segments=["family_subscriber"],
                target_segments=["family_subscriber", "suburban_family", "mid_career"],
            )
        )

        # Budget-Friendly Options
        catalog.append(
            ThreeHKProduct(
                product_id="THREE_SMART_VALUE",
                product_name="Smart Value Plan",
                category=ProductCategory.MOBILE_PLANS,
                monthly_price=Decimal("299.00"),
                features=["25GB Data", "Unlimited Local Calls", "Unlimited SMS", "Basic Roaming", "Music Streaming"],
                data_allowance_gb=25.0,
                voice_minutes=None,  # Unlimited local
                min_monthly_spend=Decimal("200.00"),
                target_segments=["budget_conscious", "young_digital", "student"],
                priority_segments=["young_digital"],
                promotional_discount=Decimal("50.00"),
                campaign_code="STUDENT2024",
            )
        )

        # Data Add-ons
        catalog.append(
            ThreeHKProduct(
                product_id="THREE_DATA_BOOSTER_50GB",
                product_name="Data Booster 50GB",
                category=ProductCategory.VALUE_ADDED_SERVICES,
                monthly_price=Decimal("199.00"),
                features=["Additional 50GB Data", "Rollover Unused Data", "5G Speed", "No Speed Throttling"],
                data_allowance_gb=50.0,
                min_monthly_spend=Decimal("300.00"),
                max_concurrent_subscriptions=3,
            )
        )

        # International Roaming
        catalog.append(
            ThreeHKProduct(
                product_id="THREE_GLOBAL_ROAMING_PREMIUM",
                product_name="Global Roaming Premium",
                category=ProductCategory.ROAMING_SERVICES,
                monthly_price=Decimal("399.00"),
                features=[
                    "150+ Countries Coverage",
                    "Daily Data Allowance 2GB",
                    "Free Incoming Calls",
                    "Premium Support Abroad",
                ],
                target_segments=["premium_business", "enterprise_client", "frequent_traveler"],
                requires_credit_check=True,
            )
        )

        # Device Bundles
        catalog.append(
            ThreeHKProduct(
                product_id="THREE_DEVICE_BUNDLE_FLAGSHIP",
                product_name="Flagship Device Bundle",
                category=ProductCategory.DEVICE_BUNDLES,
                monthly_price=Decimal("599.00"),
                setup_fee=Decimal("0.00"),  # Waived for bundle
                contract_duration_months=24,
                features=[
                    "Latest Flagship Device",
                    "Device Insurance",
                    "Express Replacement",
                    "Trade-in Program",
                    "Accessories Package",
                ],
                min_monthly_spend=Decimal("500.00"),
                requires_credit_check=True,
                promotional_discount=Decimal("100.00"),
                campaign_code="DEVICE2024",
            )
        )

        # Value-Added Services
        catalog.append(
            ThreeHKProduct(
                product_id="THREE_DIGITAL_LIFESTYLE",
                product_name="Digital Lifestyle Bundle",
                category=ProductCategory.VALUE_ADDED_SERVICES,
                monthly_price=Decimal("149.00"),
                features=[
                    "Streaming Services Bundle",
                    "Cloud Storage 500GB",
                    "Antivirus Protection",
                    "WiFi Calling",
                    "Call Recording",
                ],
                target_segments=["young_digital", "urban_professional", "tech_enthusiast"],
            )
        )

        return catalog

    def _initialize_eligibility_rules(self) -> Dict[str, Any]:
        """Initialize eligibility rules."""
        return {
            "age_requirements": {
                "minimum_age": self.business_params["min_customer_age"],
                "senior_verification": 65,
                "parental_consent_required": 18,
            },
            "tenure_requirements": {
                "new_customer_eligible": ["promotional_offers", "welcome_packages"],
                "loyalty_required": ["premium_upgrades", "exclusive_offers"],
                "minimum_months": 3,
            },
            "spend_requirements": {
                "budget_tier": {"min": 200, "max": 499},
                "standard_tier": {"min": 500, "max": 999},
                "premium_tier": {"min": 1000, "max": None},
            },
            "segment_restrictions": {
                "enterprise_only": ["enterprise_solutions", "bulk_services"],
                "family_only": ["family_plans", "parental_controls"],
                "premium_only": ["vip_services", "concierge_support"],
            },
        }

    def _initialize_pricing_rules(self) -> Dict[str, Any]:
        """Initialize pricing rules."""
        return {
            "discount_rules": {
                "loyalty_discount": {"tenure_24_months": 0.10, "tenure_36_months": 0.15, "vip_customer": 0.20},
                "volume_discount": {"family_4_lines": 0.15, "enterprise_10_lines": 0.20, "enterprise_50_lines": 0.30},
                "retention_discount": {"churn_risk_high": 0.25, "competitive_offer": 0.20, "contract_renewal": 0.10},
            },
            "pricing_strategies": {
                "penetration_pricing": {"new_market": 0.20, "competitive_response": 0.15},
                "premium_pricing": {"exclusive_features": 1.20, "luxury_positioning": 1.30},
                "value_pricing": {"price_sensitive": 0.90, "budget_conscious": 0.85},
            },
        }

    def _initialize_campaign_rules(self) -> Dict[str, Any]:
        """Initialize campaign rules."""
        return {
            "seasonal_campaigns": {
                "chinese_new_year": {"discount": 0.20, "duration_days": 30},
                "summer_promotion": {"discount": 0.15, "duration_days": 60},
                "back_to_school": {"discount": 0.25, "duration_days": 45},
            },
            "segment_campaigns": {
                "student_discount": {"discount": 0.30, "verification_required": True},
                "senior_citizen": {"discount": 0.20, "age_verification": True},
                "corporate_bundle": {"discount": 0.25, "minimum_lines": 10},
            },
            "product_campaigns": {
                "5g_adoption": {"discount": 0.15, "device_bundle": True},
                "data_upgrade": {"discount": 0.10, "min_data_usage": 30},
            },
        }

    def _evaluate_product_eligibility(
        self,
        product: ThreeHKProduct,
        customer_features: FeatureSet,
        customer_segment: CustomerSegment,
        current_products: List[str],
    ) -> Dict[str, Any]:
        """Evaluate if customer is eligible for a product."""
        result = {"status": EligibilityStatus.ELIGIBLE, "confidence": 1.0, "conditions": [], "reasons": []}

        try:
            # Check minimum spend requirement
            if product.min_monthly_spend > Decimal(str(customer_features.monthly_spend)):
                if product.min_monthly_spend > self.business_params["premium_spend_threshold"]:
                    result["status"] = EligibilityStatus.NOT_ELIGIBLE
                    result["reasons"].append(f"Minimum spend requirement: HKD {product.min_monthly_spend}")
                    return result
                else:
                    result["status"] = EligibilityStatus.CONDITIONALLY_ELIGIBLE
                    result["conditions"].append("Spend increase required")
                    result["confidence"] *= 0.7

            # Check segment requirements
            if product.required_segments:
                if customer_segment.value not in product.required_segments:
                    result["status"] = EligibilityStatus.NOT_ELIGIBLE
                    result["reasons"].append(f"Customer segment not eligible: {customer_segment.value}")
                    return result

            # Check excluded segments
            if customer_segment.value in product.excluded_segments:
                result["status"] = EligibilityStatus.NOT_ELIGIBLE
                result["reasons"].append(f"Customer segment excluded: {customer_segment.value}")
                return result

            # Check tenure requirements
            tenure_months = self._extract_tenure_months(customer_features)
            if tenure_months < product.required_tenure_months:
                result["status"] = EligibilityStatus.CONDITIONALLY_ELIGIBLE
                result["conditions"].append(f"Minimum tenure: {product.required_tenure_months} months")
                result["confidence"] *= 0.8

            # Check current product conflicts
            if product.product_id in current_products:
                result["status"] = EligibilityStatus.NOT_ELIGIBLE
                result["reasons"].append("Customer already has this product")
                return result

            # Check credit requirements
            if product.requires_credit_check:
                if customer_features.churn_risk_score > 0.7:
                    result["status"] = EligibilityStatus.REQUIRES_VERIFICATION
                    result["conditions"].append("Credit check required")
                    result["confidence"] *= 0.6

            return result

        except Exception as e:
            logger.error(f"Eligibility evaluation failed: {e}")
            return {
                "status": EligibilityStatus.NOT_ELIGIBLE,
                "confidence": 0.0,
                "conditions": [],
                "reasons": [f"Evaluation error: {str(e)}"],
            }

    def _calculate_match_score(
        self,
        product: ThreeHKProduct,
        customer_features: FeatureSet,
        lead_score: LeadScore,
        customer_segment: CustomerSegment,
    ) -> float:
        """Calculate relevance match score (0-100)."""
        try:
            match_score = 0.0

            # Segment match (30%)
            if customer_segment.value in product.priority_segments:
                match_score += 30.0
            elif customer_segment.value in product.target_segments:
                match_score += 20.0
            elif customer_segment.value not in product.excluded_segments:
                match_score += 10.0

            # Spend alignment (25%)
            spend_ratio = customer_features.monthly_spend / float(product.min_monthly_spend)
            if spend_ratio >= 1.5:
                match_score += 25.0
            elif spend_ratio >= 1.0:
                match_score += 20.0
            elif spend_ratio >= 0.8:
                match_score += 10.0

            # Lead score integration (20%)
            if lead_score.overall_score >= 80:
                match_score += 20.0
            elif lead_score.overall_score >= 60:
                match_score += 15.0
            elif lead_score.overall_score >= 40:
                match_score += 10.0

            # Usage pattern match (15%)
            if product.data_allowance_gb:
                if customer_features.data_usage_gb > product.data_allowance_gb * 0.8:
                    match_score += 15.0
                elif customer_features.data_usage_gb > product.data_allowance_gb * 0.5:
                    match_score += 10.0
            else:  # Unlimited plans
                if customer_features.data_usage_gb > 50:
                    match_score += 15.0

            # Engagement and satisfaction (10%)
            if customer_features.satisfaction_score >= 8.0:
                match_score += 10.0
            elif customer_features.satisfaction_score >= 6.0:
                match_score += 5.0

            return min(100.0, max(0.0, match_score))

        except Exception as e:
            logger.error(f"Match score calculation failed: {e}")
            return 0.0

    def _determine_offer_type(
        self, product: ThreeHKProduct, customer_features: FeatureSet, current_products: List[str], lead_score: LeadScore
    ) -> OfferType:
        """Determine the type of offer based on context."""
        try:
            # Retention offer for high churn risk
            if customer_features.churn_risk_score >= 0.7:
                return OfferType.RETENTION_OFFER

            # Loyalty reward for long-term customers
            tenure_months = self._extract_tenure_months(customer_features)
            if tenure_months >= self.business_params["loyalty_tenure_months"]:
                return OfferType.LOYALTY_REWARD

            # Cross-sell if customer has other products
            if current_products and product.category != ProductCategory.MOBILE_PLANS:
                return OfferType.CROSS_SELL

            # Plan upgrade if current spend suggests upgrade potential
            if customer_features.upsell_propensity >= 0.6 and product.category == ProductCategory.MOBILE_PLANS:
                return OfferType.PLAN_UPGRADE

            # Device bundle for device-related products
            if product.category == ProductCategory.DEVICE_BUNDLES:
                return OfferType.DEVICE_BUNDLE

            # Promotional discount if campaign active
            if product.promotional_discount > 0:
                return OfferType.PROMOTIONAL_DISCOUNT

            # Default to new subscription
            return OfferType.NEW_SUBSCRIPTION

        except Exception as e:
            logger.error(f"Offer type determination failed: {e}")
            return OfferType.NEW_SUBSCRIPTION

    def _calculate_personalized_pricing(
        self,
        product: ThreeHKProduct,
        customer_features: FeatureSet,
        lead_score: LeadScore,
        market_context: Dict[str, Any],
    ) -> Dict[str, Decimal]:
        """Calculate personalized pricing for the offer."""
        try:
            base_price = product.monthly_price
            discount_amount = Decimal("0.00")

            # Loyalty discount
            tenure_months = self._extract_tenure_months(customer_features)
            if tenure_months >= 24:
                discount_amount += base_price * Decimal("0.10")

            # Retention discount for churn risk
            if customer_features.churn_risk_score >= 0.7:
                retention_discount = min(
                    base_price * Decimal("0.25"), base_price * Decimal(str(customer_features.churn_risk_score * 0.3))
                )
                discount_amount += retention_discount

            # High-value customer discount
            if lead_score.revenue_potential >= 80:
                discount_amount += base_price * Decimal("0.05")

            # Promotional discount
            if product.promotional_discount > 0:
                discount_amount += product.promotional_discount

            # Apply maximum discount limit
            max_discount = base_price * Decimal(str(self.market_params["discount_limit_percentage"]))
            discount_amount = min(discount_amount, max_discount)

            final_price = base_price - discount_amount

            # Calculate estimated monthly value
            value_estimate = self._estimate_monthly_value(product, customer_features)

            return {
                "base_price": base_price,
                "discount_amount": discount_amount,
                "final_price": final_price,
                "value_estimate": value_estimate,
            }

        except Exception as e:
            logger.error(f"Personalized pricing calculation failed: {e}")
            return {
                "base_price": product.monthly_price,
                "discount_amount": Decimal("0.00"),
                "final_price": product.monthly_price,
                "value_estimate": product.monthly_price,
            }

    def _generate_sales_strategy(
        self,
        product: ThreeHKProduct,
        customer_features: FeatureSet,
        lead_score: LeadScore,
        customer_segment: CustomerSegment,
    ) -> Dict[str, Any]:
        """Generate sales strategy for the offer."""
        try:
            strategy = {"approach": "", "selling_points": [], "objections": []}

            # Determine approach based on lead score and segment
            if lead_score.lead_priority == LeadPriority.CRITICAL:
                strategy["approach"] = "Immediate personalized consultation with retention specialist"
            elif lead_score.lead_priority == LeadPriority.HIGH:
                strategy["approach"] = "Priority follow-up with customized presentation"
            elif customer_segment == CustomerSegment.PREMIUM_BUSINESS:
                strategy["approach"] = "Executive-level consultation with business case presentation"
            elif customer_segment == CustomerSegment.YOUNG_DIGITAL:
                strategy["approach"] = "Digital-first engagement with interactive demonstrations"
            else:
                strategy["approach"] = "Standard consultative sales approach"

            # Generate selling points based on product features and customer profile
            if "Unlimited" in product.features:
                strategy["selling_points"].append("Never worry about data limits again")

            if "Priority" in str(product.features):
                strategy["selling_points"].append("Get premium network priority during peak times")

            if customer_features.roaming_usage == 0 and "Roaming" in str(product.features):
                strategy["selling_points"].append("Perfect for your upcoming international travel")

            if customer_features.satisfaction_score < 7.0:
                strategy["selling_points"].append("Enhanced customer support and service quality")

            # Anticipate objections based on customer profile
            if customer_features.spend_category in ["budget", "minimal"]:
                strategy["objections"].append("Price concerns - emphasize value and long-term savings")

            if customer_features.churn_risk_score > 0.5:
                strategy["objections"].append("Loyalty concerns - highlight retention benefits")

            if customer_features.tenure_category == "new":
                strategy["objections"].append("Commitment hesitation - offer flexible terms")

            return strategy

        except Exception as e:
            logger.error(f"Sales strategy generation failed: {e}")
            return {
                "approach": "Standard consultative approach",
                "selling_points": ["Quality service", "Competitive pricing"],
                "objections": ["Price sensitivity", "Feature complexity"],
            }

    def _identify_cross_sell_opportunities(self, product: ThreeHKProduct, customer_features: FeatureSet) -> List[str]:
        """Identify cross-sell opportunities."""
        opportunities = []

        if product.category == ProductCategory.MOBILE_PLANS:
            if customer_features.roaming_usage == 0:
                opportunities.append("International Roaming Package")
            if customer_features.data_usage_gb > 40:
                opportunities.append("Data Booster Add-on")
            opportunities.append("Device Insurance")

        elif product.category == ProductCategory.BUSINESS_SOLUTIONS:
            opportunities.extend(["Cloud Storage Upgrade", "Advanced Analytics", "VPN Service"])

        elif product.category == ProductCategory.FAMILY_PLANS:
            opportunities.extend(["Parental Control Premium", "Family Safety Services", "Additional Lines"])

        return opportunities

    def _assess_upsell_potential(self, product: ThreeHKProduct, customer_features: FeatureSet) -> Optional[str]:
        """Assess upsell potential for the product."""
        if customer_features.upsell_propensity >= 0.7:
            if product.category == ProductCategory.MOBILE_PLANS:
                return "High potential for premium plan upgrade"
            elif product.category == ProductCategory.BUSINESS_SOLUTIONS:
                return "Enterprise solution expansion opportunity"
        elif customer_features.upsell_propensity >= 0.5:
            return "Moderate upsell potential with proper positioning"

        return None

    def _calculate_retention_value(self, product: ThreeHKProduct, customer_features: FeatureSet) -> float:
        """Calculate retention value of the offer."""
        base_retention = 0.5

        # Higher retention value for premium products
        if product.monthly_price >= Decimal("800.00"):
            base_retention += 0.3

        # Adjust for customer churn risk
        base_retention += (1.0 - customer_features.churn_risk_score) * 0.2

        # Adjust for satisfaction
        if customer_features.satisfaction_score >= 8.0:
            base_retention += 0.1

        return min(1.0, base_retention)

    def _calculate_presentation_priority(self, match_score: float, lead_score: LeadScore) -> int:
        """Calculate presentation priority (1 = highest)."""
        if match_score >= 80 and lead_score.lead_priority == LeadPriority.CRITICAL:
            return 1
        elif match_score >= 70 and lead_score.lead_priority in [LeadPriority.HIGH, LeadPriority.CRITICAL]:
            return 2
        elif match_score >= 60:
            return 3
        elif match_score >= 40:
            return 4
        else:
            return 5

    def _calculate_offer_expiry(self) -> str:
        """Calculate offer expiry date."""
        expiry_date = datetime.now() + timedelta(days=self.business_params["offer_validity_days"])
        return expiry_date.isoformat()

    def _extract_tenure_months(self, customer_features: FeatureSet) -> int:
        """Extract tenure in months from customer features."""
        tenure_mapping = {"new": 3, "recent": 9, "established": 18, "loyal": 36}
        return tenure_mapping.get(customer_features.tenure_category, 3)

    def _estimate_monthly_value(self, product: ThreeHKProduct, customer_features: FeatureSet) -> Decimal:
        """Estimate monthly value for the customer."""
        # Simplified value estimation
        base_value = product.monthly_price

        # Adjust for usage patterns
        if product.data_allowance_gb and customer_features.data_usage_gb > 0:
            usage_ratio = customer_features.data_usage_gb / product.data_allowance_gb
            if usage_ratio > 0.8:
                base_value *= Decimal("1.2")  # High utilization increases value

        return base_value


# Convenience functions for integration


def match_offers_for_lead(
    customer_features: FeatureSet,
    lead_score: LeadScore,
    customer_segment: CustomerSegment,
    current_products: List[str] = None,
) -> List[OfferMatch]:
    """
    Convenience function to match offers for a lead.

    Args:
        customer_features: Customer analysis features
        lead_score: Lead scoring results
        customer_segment: Customer segmentation
        current_products: Currently subscribed products

    Returns:
        List of matched offers
    """
    engine = ThreeHKBusinessRulesEngine()
    return engine.match_offers_for_customer(customer_features, lead_score, customer_segment, current_products)


def get_active_campaigns(target_segment: str = None) -> List[ThreeHKProduct]:
    """
    Convenience function to get active campaigns.

    Args:
        target_segment: Target customer segment

    Returns:
        List of active campaign products
    """
    engine = ThreeHKBusinessRulesEngine()
    return engine.get_campaign_offers(target_segment=target_segment, active_only=True)


if __name__ == "__main__":
    # Example usage
    logger.info("Three HK Business Rules Engine ready for use")
