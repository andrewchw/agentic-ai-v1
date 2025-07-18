"""
Agentic AI Revenue Assistant - Agent Package

This package contains the core AI agent orchestration and reasoning system
for the Hong Kong telecom revenue optimization platform.

Key Components:
- CoreAgent: Main orchestration and workflow management
- PerceptionModule: Data intake and preprocessing
- ReasoningModule: Business logic and decision making
- ActionModule: Workflow execution and integration

Usage:
    from src.agents import CoreAgent, create_agent, quick_customer_processing

    # Create agent instance
    agent = create_agent(enable_privacy=True)

    # Process customer
    result = agent.process_customer(customer_data, purchase_history)

    # Quick processing
    result = quick_customer_processing(customer_data, purchase_history)
"""

from .core_agent import (
    # Main agent class
    CoreAgent,
    # Agent modules
    PerceptionModule,
    ReasoningModule,
    ActionModule,
    # Data structures
    AgentContext,
    AgentDecision,
    AgentAction,
    # Enums
    AgentState,
    ProcessingMode,
    # Convenience functions
    create_agent,
    quick_customer_processing,
)

from .customer_analysis import (
    # Customer analysis engine
    CustomerDataAnalyzer,
    # Data structures
    FeatureSet,
    PatternAnalysis,
    # Enums
    CustomerSegment,
    # Convenience functions
    analyze_single_customer,
    batch_analyze_customers,
)

from .three_hk_business_rules import (
    # Business rules engine
    ThreeHKBusinessRulesEngine,
    # Data structures
    ThreeHKProduct,
    OfferMatch,
    # Enums
    ProductCategory,
    OfferType,
    EligibilityStatus,
    # Convenience functions
    match_offers_for_lead,
    get_active_campaigns,
)

from .lead_scoring import (
    # Lead scoring engine
    LeadScoringEngine,
    # Data structures
    LeadScore,
    PrioritizedLead,
    # Enums
    LeadPriority,
    LeadQualification,
    ScoringCategory,
    # Convenience functions
    score_single_lead,
    batch_score_and_prioritize,
)

__version__ = "1.0.0"
__author__ = "Agentic AI Team"

# Package metadata
__all__ = [
    # Core agent components
    "CoreAgent",
    "PerceptionModule",
    "ReasoningModule",
    "ActionModule",
    "AgentContext",
    "AgentDecision",
    "AgentAction",
    "AgentState",
    "ProcessingMode",
    "create_agent",
    "quick_customer_processing",
    # Customer analysis components
    "CustomerDataAnalyzer",
    "FeatureSet",
    "PatternAnalysis",
    "CustomerSegment",
    "analyze_single_customer",
    "batch_analyze_customers",
    # Lead scoring components
    "LeadScoringEngine",
    "LeadScore",
    "PrioritizedLead",
    "LeadPriority",
    "LeadQualification",
    "ScoringCategory",
    "score_single_lead",
    "batch_score_and_prioritize",
    # Three HK business rules components
    "ThreeHKBusinessRulesEngine",
    "ThreeHKProduct",
    "OfferMatch",
    "ProductCategory",
    "OfferType",
    "EligibilityStatus",
    "match_offers_for_lead",
    "get_active_campaigns",
]
