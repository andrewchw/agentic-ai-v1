"""
End-to-End Business Analysis Workflow for Agentic AI Revenue Assistant

This module provides a comprehensive workflow that integrates all OpenRouter API
components to deliver complete business analysis capabilities for Hong Kong telecom
revenue optimization.

Key Features:
- Complete customer analysis pipeline
- Lead prioritization and scoring
- Sales recommendations generation
- Error handling and resilience
- Performance monitoring
- Integration with privacy pipeline
"""

import os
import json
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

from .openrouter_client import OpenRouterClient, OpenRouterConfig, APIResponse
from .enhanced_field_identification import EnhancedFieldIdentifier
from .integrated_display_masking import IntegratedDisplayMasking
from .security_pseudonymization import SecurityPseudonymizer

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class AnalysisRequest:
    """Request structure for business analysis workflow."""
    
    customer_data: Dict[str, Any]
    purchase_history: List[Dict[str, Any]]
    engagement_data: Optional[Dict[str, Any]] = None
    available_offers: Optional[List[Dict[str, Any]]] = None
    analysis_type: str = "complete"  # complete, patterns_only, scoring_only, recommendations_only
    context: str = "Three HK telecom analysis"
    customer_id: Optional[str] = None


@dataclass
class AnalysisResult:
    """Result structure for business analysis workflow."""
    
    success: bool
    customer_id: Optional[str] = None
    analysis_type: str = ""
    
    # Analysis results
    customer_patterns: Optional[Dict[str, Any]] = None
    lead_score: Optional[Dict[str, Any]] = None
    sales_recommendations: Optional[Dict[str, Any]] = None
    
    # Metadata
    processing_time: float = 0.0
    timestamp: str = ""
    tokens_used: int = 0
    requests_made: int = 0
    
    # Error information
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class BusinessAnalysisWorkflow:
    """
    Complete end-to-end business analysis workflow for revenue optimization.
    
    Integrates OpenRouter API, privacy pipeline, and business analysis logic
    to provide comprehensive customer insights and sales recommendations.
    """
    
    def __init__(
        self, 
        openrouter_config: Optional[OpenRouterConfig] = None,
        enable_privacy_masking: bool = True,
        enable_logging: bool = True
    ):
        """
        Initialize the business analysis workflow.
        
        Args:
            openrouter_config: OpenRouter API configuration
            enable_privacy_masking: Whether to use privacy masking
            enable_logging: Whether to enable enhanced logging
        """
        # Initialize OpenRouter client
        self.openrouter_client = OpenRouterClient(
            config=openrouter_config, 
            auto_configure=openrouter_config is None,
            enable_enhanced_logging=enable_logging
        )
        
        # Configure for business analysis
        self.openrouter_client.configure_for_business_analysis()
        
        # Initialize privacy components if enabled
        self.enable_privacy = enable_privacy_masking
        if enable_privacy_masking:
            try:
                self.field_identifier = EnhancedFieldIdentifier()
                self.display_masking = IntegratedDisplayMasking(self.field_identifier)
                self.security_pseudonymizer = SecurityPseudonymizer()
                logger.info("Privacy pipeline initialized for workflow")
            except Exception as e:
                logger.warning(f"Privacy pipeline initialization failed: {e}")
                self.enable_privacy = False
        
        # Workflow statistics
        self.total_requests = 0
        self.total_tokens_used = 0
        self.total_processing_time = 0.0
        self.successful_analyses = 0
        self.failed_analyses = 0
        
        logger.info("Business analysis workflow initialized")
    
    def analyze_customer_complete(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Perform complete customer analysis including patterns, scoring, and recommendations.
        
        Args:
            request: Analysis request with customer data
            
        Returns:
            Complete analysis result
        """
        start_time = time.time()
        result = AnalysisResult(
            success=False,
            customer_id=request.customer_id,
            analysis_type="complete"
        )
        
        try:
            logger.info(f"Starting complete analysis for customer {request.customer_id}")
            
            # Step 1: Analyze customer patterns
            patterns_result = self._analyze_customer_patterns(request)
            if not patterns_result.success:
                result.error_message = f"Pattern analysis failed: {patterns_result.error_message}"
                return result
            
            result.customer_patterns = patterns_result.customer_patterns
            
            # Step 2: Score lead priority
            scoring_result = self._score_lead_priority(request)
            if not scoring_result.success:
                result.error_message = f"Lead scoring failed: {scoring_result.error_message}"
                return result
            
            result.lead_score = scoring_result.lead_score
            
            # Step 3: Generate sales recommendations
            if request.available_offers:
                recommendations_result = self._generate_sales_recommendations(request, patterns_result.customer_patterns)
                if recommendations_result.success:
                    result.sales_recommendations = recommendations_result.sales_recommendations
                else:
                    logger.warning(f"Recommendations generation failed: {recommendations_result.error_message}")
            
            # Aggregate metadata
            result.processing_time = time.time() - start_time
            result.tokens_used = patterns_result.tokens_used + scoring_result.tokens_used + (recommendations_result.tokens_used if 'recommendations_result' in locals() else 0)
            result.requests_made = patterns_result.requests_made + scoring_result.requests_made + (recommendations_result.requests_made if 'recommendations_result' in locals() else 0)
            result.success = True
            
            # Update workflow statistics
            self.successful_analyses += 1
            self.total_requests += result.requests_made
            self.total_tokens_used += result.tokens_used
            self.total_processing_time += result.processing_time
            
            logger.info(f"Complete analysis successful for customer {request.customer_id} in {result.processing_time:.2f}s")
            
        except Exception as e:
            result.error_message = f"Workflow error: {str(e)}"
            result.error_details = {"exception_type": type(e).__name__, "exception_message": str(e)}
            result.processing_time = time.time() - start_time
            self.failed_analyses += 1
            logger.error(f"Complete analysis failed for customer {request.customer_id}: {e}")
        
        return result
    
    def _analyze_customer_patterns(self, request: AnalysisRequest) -> AnalysisResult:
        """Analyze customer purchase patterns and behaviors."""
        start_time = time.time()
        result = AnalysisResult(
            success=False,
            customer_id=request.customer_id,
            analysis_type="patterns"
        )
        
        try:
            # Prepare customer data (apply privacy masking if enabled)
            processed_customer_data = self._prepare_customer_data(request.customer_data)
            processed_purchase_history = self._prepare_purchase_history(request.purchase_history)
            
            # Call OpenRouter API for pattern analysis
            api_response = self.openrouter_client.analyze_customer_patterns(
                customer_data=processed_customer_data,
                purchase_history=processed_purchase_history,
                additional_context=request.context
            )
            
            if api_response.success:
                # Parse JSON response
                try:
                    patterns_data = json.loads(api_response.data["content"])
                    result.customer_patterns = patterns_data
                    result.success = True
                    logger.debug("Customer patterns analysis successful")
                except json.JSONDecodeError as e:
                    result.error_message = f"Failed to parse patterns JSON: {str(e)}"
                    logger.error(f"JSON parsing failed for patterns: {e}")
            else:
                result.error_message = api_response.error
                logger.error(f"Pattern analysis API call failed: {api_response.error}")
            
            # Set metadata
            result.processing_time = time.time() - start_time
            result.tokens_used = api_response.tokens_used or 0
            result.requests_made = 1
            
        except Exception as e:
            result.error_message = f"Pattern analysis error: {str(e)}"
            result.processing_time = time.time() - start_time
            logger.error(f"Pattern analysis exception: {e}")
        
        return result
    
    def _score_lead_priority(self, request: AnalysisRequest) -> AnalysisResult:
        """Generate lead priority score based on customer data."""
        start_time = time.time()
        result = AnalysisResult(
            success=False,
            customer_id=request.customer_id,
            analysis_type="scoring"
        )
        
        try:
            # Prepare data for scoring
            processed_customer_data = self._prepare_customer_data(request.customer_data)
            processed_engagement_data = self._prepare_engagement_data(request.engagement_data or {})
            processed_purchase_history = self._prepare_purchase_history(request.purchase_history)
            
            # Call OpenRouter API for lead scoring
            api_response = self.openrouter_client.score_lead_priority(
                customer_profile=processed_customer_data,
                engagement_data=processed_engagement_data,
                purchase_history=processed_purchase_history
            )
            
            if api_response.success:
                # Parse JSON response
                try:
                    scoring_data = json.loads(api_response.data["content"])
                    result.lead_score = scoring_data
                    result.success = True
                    logger.debug("Lead scoring analysis successful")
                except json.JSONDecodeError as e:
                    result.error_message = f"Failed to parse scoring JSON: {str(e)}"
                    logger.error(f"JSON parsing failed for scoring: {e}")
            else:
                result.error_message = api_response.error
                logger.error(f"Lead scoring API call failed: {api_response.error}")
            
            # Set metadata
            result.processing_time = time.time() - start_time
            result.tokens_used = api_response.tokens_used or 0
            result.requests_made = 1
            
        except Exception as e:
            result.error_message = f"Lead scoring error: {str(e)}"
            result.processing_time = time.time() - start_time
            logger.error(f"Lead scoring exception: {e}")
        
        return result
    
    def _generate_sales_recommendations(self, request: AnalysisRequest, customer_analysis: Dict[str, Any]) -> AnalysisResult:
        """Generate sales recommendations based on customer analysis."""
        start_time = time.time()
        result = AnalysisResult(
            success=False,
            customer_id=request.customer_id,
            analysis_type="recommendations"
        )
        
        try:
            # Prepare offers data
            available_offers = request.available_offers or self._get_default_three_hk_offers()
            
            # Call OpenRouter API for recommendations
            api_response = self.openrouter_client.generate_sales_recommendations(
                customer_analysis=customer_analysis,
                available_offers=available_offers,
                context=request.context
            )
            
            if api_response.success:
                # Parse JSON response
                try:
                    recommendations_data = json.loads(api_response.data["content"])
                    result.sales_recommendations = recommendations_data
                    result.success = True
                    logger.debug("Sales recommendations generation successful")
                except json.JSONDecodeError as e:
                    result.error_message = f"Failed to parse recommendations JSON: {str(e)}"
                    logger.error(f"JSON parsing failed for recommendations: {e}")
            else:
                result.error_message = api_response.error
                logger.error(f"Recommendations API call failed: {api_response.error}")
            
            # Set metadata
            result.processing_time = time.time() - start_time
            result.tokens_used = api_response.tokens_used or 0
            result.requests_made = 1
            
        except Exception as e:
            result.error_message = f"Recommendations error: {str(e)}"
            result.processing_time = time.time() - start_time
            logger.error(f"Recommendations exception: {e}")
        
        return result
    
    def _prepare_customer_data(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare customer data with privacy protection if enabled."""
        if not self.enable_privacy:
            return customer_data.copy()
        
        try:
            # Apply security pseudonymization for API transmission
            processed_data = {}
            for key, value in customer_data.items():
                processed_data[key] = self.security_pseudonymizer.anonymize_field(str(value), key)
            logger.debug("Customer data pseudonymized for API transmission")
            return processed_data
        except Exception as e:
            logger.warning(f"Privacy processing failed, using original data: {e}")
            return customer_data.copy()
    
    def _prepare_purchase_history(self, purchase_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare purchase history with privacy protection if enabled."""
        if not self.enable_privacy:
            return purchase_history.copy()
        
        try:
            # Apply security pseudonymization to each purchase record
            processed_history = []
            for purchase in purchase_history:
                processed_purchase = {}
                for key, value in purchase.items():
                    processed_purchase[key] = self.security_pseudonymizer.anonymize_field(str(value), key)
                processed_history.append(processed_purchase)
            
            logger.debug(f"Purchase history ({len(processed_history)} records) pseudonymized for API transmission")
            return processed_history
        except Exception as e:
            logger.warning(f"Privacy processing failed for purchase history, using original data: {e}")
            return purchase_history.copy()
    
    def _prepare_engagement_data(self, engagement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare engagement data with privacy protection if enabled."""
        if not self.enable_privacy:
            return engagement_data.copy()
        
        try:
            # Apply security pseudonymization
            processed_data = {}
            for key, value in engagement_data.items():
                processed_data[key] = self.security_pseudonymizer.anonymize_field(str(value), key)
            logger.debug("Engagement data pseudonymized for API transmission")
            return processed_data
        except Exception as e:
            logger.warning(f"Privacy processing failed for engagement data, using original data: {e}")
            return engagement_data.copy()
    
    def _get_default_three_hk_offers(self) -> List[Dict[str, Any]]:
        """Get default Three HK offers for recommendations."""
        return [
            {
                "offer_id": "THREE_5G_UNLIMITED",
                "name": "5G Unlimited Plan",
                "price": 599.00,
                "currency": "HKD",
                "features": ["Unlimited 5G Data", "International Roaming", "Priority Network"],
                "target_segment": "Premium"
            },
            {
                "offer_id": "THREE_BUSINESS_PRO",
                "name": "Business Pro Bundle",
                "price": 1299.00,
                "currency": "HKD",
                "features": ["Multiple Lines", "Cloud Storage", "Priority Support", "VPN Access"],
                "target_segment": "Business"
            },
            {
                "offer_id": "THREE_FAMILY_SHARE",
                "name": "Family Share Plan",
                "price": 899.00,
                "currency": "HKD",
                "features": ["4 Lines Included", "Shared Data Pool", "Parental Controls"],
                "target_segment": "Family"
            },
            {
                "offer_id": "THREE_STUDENT_SPECIAL",
                "name": "Student Special",
                "price": 299.00,
                "currency": "HKD",
                "features": ["Student Discount", "Education Apps", "Limited Data"],
                "target_segment": "Student"
            }
        ]
    
    def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get comprehensive workflow performance statistics."""
        return {
            "total_analyses": self.successful_analyses + self.failed_analyses,
            "successful_analyses": self.successful_analyses,
            "failed_analyses": self.failed_analyses,
            "success_rate": (self.successful_analyses / max(1, self.successful_analyses + self.failed_analyses)) * 100,
            "total_requests": self.total_requests,
            "total_tokens_used": self.total_tokens_used,
            "total_processing_time": self.total_processing_time,
            "average_processing_time": self.total_processing_time / max(1, self.successful_analyses),
            "average_tokens_per_analysis": self.total_tokens_used / max(1, self.successful_analyses),
            "openrouter_stats": self.openrouter_client.get_stats(),
            "privacy_enabled": self.enable_privacy
        }
    
    def validate_api_connectivity(self) -> bool:
        """Validate that the OpenRouter API is accessible and working."""
        try:
            return self.openrouter_client.validate_deepseek_model()
        except Exception as e:
            logger.error(f"API connectivity validation failed: {e}")
            return False
    
    def process_batch_analysis(self, requests: List[AnalysisRequest], max_concurrent: int = 3) -> List[AnalysisResult]:
        """
        Process multiple analysis requests efficiently.
        
        Args:
            requests: List of analysis requests
            max_concurrent: Maximum concurrent requests (respects rate limiting)
            
        Returns:
            List of analysis results
        """
        results = []
        
        for i, request in enumerate(requests):
            logger.info(f"Processing batch analysis {i+1}/{len(requests)}")
            
            # Add delay for rate limiting if processing multiple requests
            if i > 0:
                time.sleep(1)  # 1 second delay between requests
            
            result = self.analyze_customer_complete(request)
            results.append(result)
            
            # Log progress
            if result.success:
                logger.info(f"Batch analysis {i+1} completed successfully")
            else:
                logger.error(f"Batch analysis {i+1} failed: {result.error_message}")
        
        return results


# Convenience functions for quick workflow usage
def create_workflow(api_key: Optional[str] = None) -> BusinessAnalysisWorkflow:
    """Create a business analysis workflow with default configuration."""
    config = None
    if api_key:
        config = OpenRouterConfig(api_key=api_key)
    
    return BusinessAnalysisWorkflow(openrouter_config=config)


def quick_customer_analysis(
    customer_data: Dict[str, Any],
    purchase_history: List[Dict[str, Any]],
    api_key: Optional[str] = None
) -> AnalysisResult:
    """Perform quick customer analysis with minimal setup."""
    workflow = create_workflow(api_key)
    
    request = AnalysisRequest(
        customer_data=customer_data,
        purchase_history=purchase_history,
        customer_id=customer_data.get('customer_id', 'unknown')
    )
    
    return workflow.analyze_customer_complete(request) 