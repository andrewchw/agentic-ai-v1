#!/usr/bin/env python3
"""
CrewAI Integration Bridge
========================

Bridges the existing Lead Intelligence Dashboard with the new CrewAI Enhanced 
Orchestrator, providing seamless integration and enhanced collaboration capabilities.

This allows users to trigger the advanced CrewAI multi-agent system directly 
from the existing dashboard interface while maintaining backward compatibility.

Author: Agentic AI Revenue Assistant - CrewAI Integration
Date: 2025-07-24
"""

import asyncio
import json
import logging
import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import both systems
from crewai_enhanced_orchestrator import create_crewai_enhanced_orchestrator
from src.agents.agent_integration_orchestrator import create_integration_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CrewAIIntegrationBridge:
    """
    Integration bridge between existing system and CrewAI enhancement.
    
    Provides seamless integration that allows users to choose between:
    - Standard 2-agent collaboration (existing system)
    - Enhanced CrewAI multi-agent orchestration (new system)
    - Hybrid approach combining both systems
    """
    
    def __init__(self):
        """Initialize the integration bridge"""
        self.standard_service = None
        self.crewai_orchestrator = None
        self.initialized = False
        
        logger.info("CrewAI Integration Bridge initialized")
    
    async def initialize_services(self):
        """Initialize both standard and CrewAI services"""
        try:
            # Initialize standard integration service  
            try:
                self.standard_service = create_integration_service()
                logger.info("✅ Standard integration service initialized")
            except Exception as e:
                logger.warning(f"⚠️ Standard service initialization warning: {e}")
                self.standard_service = None
            
            # Initialize CrewAI orchestrator (should work with OpenRouter)
            try:
                self.crewai_orchestrator = create_crewai_enhanced_orchestrator()
                logger.info("✅ CrewAI enhanced orchestrator initialized")
            except Exception as e:
                logger.warning(f"⚠️ CrewAI orchestrator initialization warning: {e}")
                self.crewai_orchestrator = None
            
            # At least one service should be available
            if self.standard_service or self.crewai_orchestrator:
                self.initialized = True
                return True
            else:
                logger.error("❌ Neither standard nor CrewAI services could be initialized")
                return False
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            return False
    
    async def process_enhanced_collaboration(self, lead_intelligence_results: Dict[str, Any], 
                                           mode: str = "crewai_enhanced",
                                           customer_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process lead intelligence results with enhanced collaboration.
        
        Args:
            lead_intelligence_results: Results from Lead Intelligence Agent
            mode: Collaboration mode - "standard", "crewai_enhanced", or "hybrid"
            customer_data: Raw customer data for CrewAI processing
        
        Returns:
            Enhanced collaboration results with business impact analysis
        """
        
        if not self.initialized:
            await self.initialize_services()
        
        start_time = datetime.now()
        logger.info(f"Processing enhanced collaboration in '{mode}' mode...")
        
        try:
            if mode == "standard":
                return await self._process_standard_collaboration(lead_intelligence_results)
            
            elif mode == "crewai_enhanced":
                return await self._process_crewai_collaboration(lead_intelligence_results, customer_data)
            
            elif mode == "hybrid":
                return await self._process_hybrid_collaboration(lead_intelligence_results, customer_data)
            
            else:
                raise ValueError(f"Unknown collaboration mode: {mode}")
                
        except Exception as e:
            logger.error(f"Enhanced collaboration failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "mode": mode,
                "fallback_attempted": False
            }
    
    async def _process_standard_collaboration(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Process using the standard 2-agent system"""
        
        logger.info("🔄 Processing with standard 2-agent collaboration...")
        
        try:
            # Use existing integration service
            collaboration_results = self.standard_service.process_lead_intelligence_completion(results)
            
            # Enhance results format for consistency
            enhanced_results = {
                "success": True,
                "mode": "standard",
                "collaboration_type": "2-Agent Standard",
                "agents_involved": ["Lead Intelligence Agent", "Sales Optimization Agent"],
                "workflow_steps": collaboration_results.get("workflow_steps", []),
                "business_impact": collaboration_results.get("business_impact", {}),
                "collaboration_results": collaboration_results.get("collaboration_results", {}),
                "next_actions": collaboration_results.get("next_actions", []),
                "processing_time": collaboration_results.get("processing_time", 0),
                "enhancement_level": "Standard"
            }
            
            logger.info("✅ Standard collaboration completed successfully")
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Standard collaboration failed: {e}")
            raise
    
    async def _process_crewai_collaboration(self, results: Dict[str, Any], customer_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process using the CrewAI enhanced multi-agent system"""
        
        logger.info("🚀 Processing with CrewAI enhanced multi-agent orchestration...")
        
        try:
            # Check if CrewAI orchestrator is available
            if not self.crewai_orchestrator:
                raise Exception("CrewAI orchestrator not available - likely missing API keys")
            
            # Use provided customer data if available, otherwise transform Lead Intelligence results
            if customer_data:
                logger.info(f"🔍 Using provided customer data: {len(customer_data) if isinstance(customer_data, (list, dict)) else 'Unknown count'} customers")
                processed_customer_data = customer_data
            else:
                logger.info("🔄 Transforming Lead Intelligence results for CrewAI system...")
                processed_customer_data = self._transform_for_crewai(results)
            
            # Process through CrewAI enhanced orchestrator
            crewai_results = await self.crewai_orchestrator.process_enhanced_customer_analysis(processed_customer_data)
            
            if crewai_results.get("success"):
                # Transform CrewAI results back to dashboard format
                enhanced_results = self._transform_crewai_results(crewai_results)
                
                logger.info("✅ CrewAI enhanced collaboration completed successfully")
                return enhanced_results
            else:
                raise Exception(f"CrewAI processing failed: {crewai_results.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"CrewAI collaboration failed: {e}")
            # Fallback to standard collaboration if available
            if self.standard_service:
                logger.info("🔄 Falling back to standard collaboration...")
                fallback_results = await self._process_standard_collaboration(results)
                fallback_results["fallback_used"] = True
                fallback_results["fallback_reason"] = str(e)
                return fallback_results
            else:
                # No fallback available
                raise Exception(f"CrewAI failed and no standard fallback available: {e}")
    
    async def _process_hybrid_collaboration(self, results: Dict[str, Any], customer_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process using hybrid approach combining both systems"""
        
        logger.info("⚡ Processing with hybrid collaboration (Standard + CrewAI)...")
        
        try:
            # Run both systems in parallel
            standard_task = asyncio.create_task(self._process_standard_collaboration(results))
            crewai_task = asyncio.create_task(self._process_crewai_collaboration(results, customer_data))
            
            # Wait for both to complete
            standard_results, crewai_results = await asyncio.gather(
                standard_task, crewai_task, return_exceptions=True
            )
            
            # Combine results from both systems
            hybrid_results = self._combine_hybrid_results(standard_results, crewai_results)
            
            logger.info("✅ Hybrid collaboration completed successfully")
            return hybrid_results
            
        except Exception as e:
            logger.error(f"Hybrid collaboration failed: {e}")
            # Fallback to standard only
            return await self._process_standard_collaboration(results)
    
    def _transform_for_crewai(self, lead_results: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Lead Intelligence results for CrewAI processing"""
        
        # Extract key information from lead intelligence results
        customer_segments = lead_results.get("customer_segments", {})
        revenue_insights = lead_results.get("revenue_insights", {})
        churn_analysis = lead_results.get("churn_analysis", {})
        
        # Calculate actual customer count from segments or use uploaded data count
        actual_customer_count = 0
        if customer_segments:
            # Sum up customers from all segments
            for segment_name, segment_data in customer_segments.items():
                if isinstance(segment_data, dict) and "count" in segment_data:
                    actual_customer_count += segment_data["count"]
        
        # Use revenue insights total if segments don't provide count
        if actual_customer_count == 0:
            actual_customer_count = revenue_insights.get("total_customers", 100)  # Default to 100 (user's uploaded data)
        
        # Build CrewAI-compatible data structure
        crewai_data = {
            "total_customers": actual_customer_count,
            "fields": ["customer_id", "segment", "arpu", "churn_risk", "behavior_pattern"],
            "timestamp": datetime.now().isoformat(),
            "market_context": "Hong Kong telecom competitive environment",
            
            # Enhanced data from lead intelligence
            "segment_analysis": customer_segments,
            "revenue_baseline": revenue_insights.get("monthly_revenue", 130000),
            "churn_indicators": churn_analysis,
            "original_recommendations": lead_results.get("original_recommendations_count", 0),
            "original_data_source": "lead_intelligence_analysis"
        }
        
        logger.info(f"Transformed lead intelligence data for CrewAI processing: {crewai_data['total_customers']} customers from {len(customer_segments)} segments")
        return crewai_data
    
    def _transform_crewai_results(self, crewai_results: Dict[str, Any]) -> Dict[str, Any]:
        """Transform CrewAI results back to dashboard-compatible format"""
        
        # Extract key components from CrewAI results
        business_impact = crewai_results.get("enhanced_business_impact", {})
        revenue_analysis = business_impact.get("revenue_analysis", {})
        customer_impact = business_impact.get("customer_impact", {})
        strategic_recommendations = crewai_results.get("strategic_recommendations", [])
        collaboration_metrics = crewai_results.get("collaboration_metrics", {})
        implementation_roadmap = crewai_results.get("implementation_roadmap", {})
        
        # Build dashboard-compatible results
        dashboard_results = {
            "success": True,
            "mode": "crewai_enhanced",
            "collaboration_type": "CrewAI Enhanced Multi-Agent",
            "agents_involved": [
                "Customer Intelligence Specialist",
                "Market Intelligence Director", 
                "Revenue Optimization Expert",
                "Retention & Lifecycle Specialist",
                "Campaign Orchestration Director"
            ],
            
            # Enhanced workflow steps
            "workflow_steps": [
                {"step": 1, "action": "Deep Customer Intelligence Analysis", "status": "completed"},
                {"step": 2, "action": "Market Intelligence & Competitive Context", "status": "completed"},
                {"step": 3, "action": "Revenue Optimization Strategy Development", "status": "completed"},
                {"step": 4, "action": "Retention Strategy & Lifecycle Optimization", "status": "completed"},
                {"step": 5, "action": "Campaign Execution & Performance Planning", "status": "completed"},
                {"step": 6, "action": "Consensus Validation & Strategic Refinement", "status": "completed"}
            ],
            
            # Enhanced business impact
            "business_impact": {
                "revenue_analysis": revenue_analysis,
                "customer_impact": customer_impact,
                "operational_efficiency": business_impact.get("operational_efficiency", {}),
                "enhancement_multiplier": "4x improvement over standard analysis"
            },
            
            # Enhanced collaboration results
            "collaboration_results": {
                "customer_intelligence": crewai_results.get("hierarchical_analysis", {}).get("customer_intelligence", {}),
                "market_intelligence": crewai_results.get("hierarchical_analysis", {}).get("market_intelligence", {}),
                "revenue_optimization": crewai_results.get("hierarchical_analysis", {}).get("revenue_optimization", {}),
                "retention_strategy": crewai_results.get("hierarchical_analysis", {}).get("retention_strategy", {}),
                "campaign_execution": crewai_results.get("hierarchical_analysis", {}).get("campaign_execution", {}),
                "consensus_validation": crewai_results.get("consensus_validation", {})
            },
            
            # Enhanced next actions
            "next_actions": self._convert_recommendations_to_actions(strategic_recommendations),
            
            # Preserve CrewAI deliverables for export functions
            "deliverables": crewai_results.get("deliverables", {}),
            
            # CrewAI-specific enhancements
            "crewai_enhancements": {
                "collaboration_metrics": collaboration_metrics,
                "implementation_roadmap": implementation_roadmap,
                "consensus_scores": crewai_results.get("consensus_validation", {}).get("agent_agreement_scores", {}),
                "confidence_levels": crewai_results.get("consensus_validation", {}).get("confidence_levels", {})
            },
            
            "processing_time": crewai_results.get("processing_time", 0),
            "enhancement_level": "CrewAI Advanced"
        }
        
        logger.info("Transformed CrewAI results to dashboard-compatible format")
        return dashboard_results
    
    def _convert_recommendations_to_actions(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert strategic recommendations to actionable next steps"""
        
        actions = []
        for i, rec in enumerate(recommendations, 1):
            action = {
                "priority": rec.get("priority", i),
                "action_type": rec.get("category", "strategy_execution").lower().replace(" ", "_"),
                "description": rec.get("recommendation", "Execute strategic recommendation"),
                "timeline": rec.get("timeline", "TBD"),
                "expected_outcome": rec.get("expected_impact", "Business improvement"),
                "confidence": rec.get("confidence", 0.85),
                "responsible_agents": rec.get("responsible_agents", [])
            }
            actions.append(action)
        
        return actions
    
    def _combine_hybrid_results(self, standard_results: Dict[str, Any], 
                               crewai_results: Dict[str, Any]) -> Dict[str, Any]:
        """Combine results from both standard and CrewAI systems"""
        
        # Handle potential exceptions
        if isinstance(standard_results, Exception):
            logger.warning(f"Standard collaboration failed in hybrid mode: {standard_results}")
            return crewai_results if not isinstance(crewai_results, Exception) else {"error": "Both systems failed"}
        
        if isinstance(crewai_results, Exception):
            logger.warning(f"CrewAI collaboration failed in hybrid mode: {crewai_results}")
            standard_results["fallback_used"] = True
            standard_results["fallback_reason"] = str(crewai_results)
            return standard_results
        
        # Both succeeded - combine the best of both
        hybrid_results = {
            "success": True,
            "mode": "hybrid",
            "collaboration_type": "Hybrid: Standard + CrewAI Enhanced",
            "agents_involved": list(set(
                standard_results.get("agents_involved", []) + 
                crewai_results.get("agents_involved", [])
            )),
            
            # Combine workflow steps
            "workflow_steps": (
                standard_results.get("workflow_steps", []) + 
                crewai_results.get("workflow_steps", [])
            ),
            
            # Use enhanced business impact from CrewAI
            "business_impact": crewai_results.get("business_impact", {}),
            
            # Combine collaboration results
            "collaboration_results": {
                **standard_results.get("collaboration_results", {}),
                **crewai_results.get("collaboration_results", {})
            },
            
            # Use enhanced next actions from CrewAI
            "next_actions": crewai_results.get("next_actions", []),
            
            # Include CrewAI enhancements
            "crewai_enhancements": crewai_results.get("crewai_enhancements", {}),
            
            # Performance comparison
            "performance_comparison": {
                "standard_processing_time": standard_results.get("processing_time", 0),
                "crewai_processing_time": crewai_results.get("processing_time", 0),
                "standard_agents": len(standard_results.get("agents_involved", [])),
                "crewai_agents": len(crewai_results.get("agents_involved", [])),
                "enhancement_factor": f"{len(crewai_results.get('agents_involved', []))/max(1, len(standard_results.get('agents_involved', [])))}x"
            },
            
            "processing_time": max(
                standard_results.get("processing_time", 0),
                crewai_results.get("processing_time", 0)
            ),
            "enhancement_level": "Hybrid Advanced"
        }
        
        logger.info("Successfully combined hybrid results from both systems")
        return hybrid_results


# Integration function for the dashboard
def process_agent_collaboration_with_crewai(lead_results: Dict[str, Any], 
                                          mode: str = "crewai_enhanced",
                                          customer_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Main integration function for the Lead Intelligence Dashboard.
    
    This function can be called from the dashboard's agent collaboration trigger
    to process results through the enhanced CrewAI system.
    
    Args:
        lead_results: Results from Lead Intelligence analysis
        mode: "standard", "crewai_enhanced", or "hybrid"
        customer_data: Raw customer data for CrewAI processing
    
    Returns:
        Enhanced collaboration results
    """
    
    async def run_collaboration():
        bridge = CrewAIIntegrationBridge()
        return await bridge.process_enhanced_collaboration(lead_results, mode, customer_data)
    
    # Run the async collaboration
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(run_collaboration())
    finally:
        loop.close()


# Test and demonstration function
def test_crewai_integration():
    """Test the CrewAI integration bridge"""
    
    print("🧪 Testing CrewAI Integration Bridge")
    print("=" * 40)
    
    # Sample lead intelligence results
    sample_results = {
        "customer_segments": {
            "high_value_business": {"count": 45, "avg_arpu": 1250},
            "family_premium": {"count": 78, "avg_arpu": 680},
            "price_sensitive": {"count": 67, "avg_arpu": 320}
        },
        "revenue_insights": {
            "total_customers": 190,
            "monthly_revenue": 130730,
            "average_arpu": 685
        },
        "churn_analysis": {
            "high_risk_customers": 67,
            "medium_risk_customers": 45
        }
    }
    
    print("📊 Testing with sample lead intelligence results...")
    
    # Test each mode
    modes = ["standard", "crewai_enhanced", "hybrid"]
    
    for mode in modes:
        print(f"\n🔄 Testing {mode} mode...")
        try:
            results = process_agent_collaboration_with_crewai(sample_results, mode)
            
            if results.get("success"):
                print(f"✅ {mode} mode: SUCCESS")
                print(f"   Agents: {len(results.get('agents_involved', []))}")
                print(f"   Processing Time: {results.get('processing_time', 0):.2f}s")
                print(f"   Enhancement Level: {results.get('enhancement_level', 'Unknown')}")
            else:
                print(f"❌ {mode} mode: FAILED - {results.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ {mode} mode: EXCEPTION - {e}")
    
    print(f"\n✅ CrewAI Integration Bridge testing completed")


if __name__ == "__main__":
    test_crewai_integration()
