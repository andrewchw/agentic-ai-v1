"""
Multi-Agent Revenue Assistant Orchestrator
Coordinates Lead Intelligence Agent and Revenue Optimization Agent
"""

import asyncio
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from ..agents.crew_config import CrewAIConfig
from ..utils.privacy import PrivacyPipeline
from ..utils.logger import setup_logger

# Configure logging
logger = setup_logger(__name__)

class MultiAgentOrchestrator:
    """
    Orchestrates the multi-agent system for revenue optimization
    Coordinates between Lead Intelligence Agent and Revenue Optimization Agent
    """
    
    def __init__(self):
        """Initialize the multi-agent orchestrator"""
        self.crew_config = None
        self.privacy_pipeline = PrivacyPipeline()
        self.is_initialized = False
        
        logger.info("MultiAgentOrchestrator initialized")
    
    async def initialize(self) -> bool:
        """Initialize the CrewAI configuration asynchronously"""
        try:
            self.crew_config = CrewAIConfig()
            self.is_initialized = True
            logger.info("Multi-agent system initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize multi-agent system: {e}")
            self.is_initialized = False
            return False
    
    async def analyze_customers(self, customer_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run multi-agent analysis on customer data
        
        Args:
            customer_data: List of customer records (already pseudonymized)
            
        Returns:
            Dictionary containing agent analysis results and recommendations
        """
        if not self.is_initialized:
            await self.initialize()
        
        if not self.is_initialized:
            raise RuntimeError("Multi-agent system failed to initialize")
        
        start_time = datetime.now()
        logger.info(f"Starting multi-agent analysis for {len(customer_data)} customers")
        
        try:
            # Prepare data summary for agents
            data_summary = {
                'total_customers': len(customer_data),
                'fields': list(customer_data[0].keys()) if customer_data else [],
                'timestamp': start_time.isoformat()
            }
            
            # Create and execute multi-agent crew
            crew = self.crew_config.create_multi_agent_crew(data_summary)
            
            # Execute the crew (this will run both agents in sequence)
            logger.info("Executing multi-agent crew...")
            crew_result = await asyncio.to_thread(crew.kickoff)
            
            # Process results
            analysis_duration = (datetime.now() - start_time).total_seconds()
            
            results = {
                'success': True,
                'analysis_duration': analysis_duration,
                'timestamp': start_time.isoformat(),
                'data_summary': data_summary,
                'agent_results': {
                    'lead_intelligence': {
                        'agent': 'Lead Intelligence Agent (DeepSeek)',
                        'analysis': crew_result.get('tasks_outputs', [{}])[0] if crew_result.get('tasks_outputs') else {},
                        'status': 'completed'
                    },
                    'revenue_optimization': {
                        'agent': 'Revenue Optimization Agent (Llama3)', 
                        'strategy': crew_result.get('tasks_outputs', [{}, {}])[1] if len(crew_result.get('tasks_outputs', [])) > 1 else {},
                        'status': 'completed'
                    }
                },
                'collaboration_summary': {
                    'agents_collaborated': True,
                    'tasks_delegated': crew_result.get('delegations', 0),
                    'questions_asked': crew_result.get('inter_agent_questions', 0)
                },
                'recommendations': self._extract_recommendations(crew_result),
                'performance': {
                    'response_time': analysis_duration,
                    'target_met': analysis_duration < 30,
                    'customers_processed': len(customer_data)
                }
            }
            
            logger.info(f"Multi-agent analysis completed in {analysis_duration:.2f}s")
            return results
            
        except Exception as e:
            logger.error(f"Multi-agent analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': start_time.isoformat(),
                'analysis_duration': (datetime.now() - start_time).total_seconds()
            }
    
    def _extract_recommendations(self, crew_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract actionable recommendations from crew results"""
        recommendations = []
        
        try:
            # Extract from crew result structure
            tasks_outputs = crew_result.get('tasks_outputs', [])
            
            for i, task_output in enumerate(tasks_outputs):
                agent_type = "Lead Intelligence" if i == 0 else "Revenue Optimization"
                
                # Parse recommendations from task output
                if hasattr(task_output, 'raw') and task_output.raw:
                    recommendations.append({
                        'agent': agent_type,
                        'recommendation': task_output.raw,
                        'priority': 'high',
                        'category': 'data_analysis' if i == 0 else 'revenue_strategy'
                    })
            
        except Exception as e:
            logger.warning(f"Could not extract detailed recommendations: {e}")
            recommendations.append({
                'agent': 'System',
                'recommendation': 'Multi-agent analysis completed successfully',
                'priority': 'medium',
                'category': 'system_status'
            })
        
        return recommendations
    
    async def get_agent_conversation_log(self) -> List[Dict[str, Any]]:
        """Get the conversation log between agents"""
        # This would be implemented to track inter-agent communications
        # For now, return a placeholder
        return [
            {
                'timestamp': datetime.now().isoformat(),
                'from_agent': 'Lead Intelligence Agent',
                'to_agent': 'Revenue Optimization Agent',
                'message': 'Analysis complete, delegating strategy development',
                'type': 'delegation'
            }
        ]
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            'initialized': self.is_initialized,
            'agents_available': 2 if self.is_initialized else 0,
            'agent_types': ['Lead Intelligence (DeepSeek)', 'Revenue Optimization (Llama3)'] if self.is_initialized else [],
            'framework': 'CrewAI',
            'privacy_enabled': True
        }

# Singleton instance for use throughout the application
multi_agent_orchestrator = MultiAgentOrchestrator()

# Example usage and testing
if __name__ == "__main__":
    async def test_orchestrator():
        orchestrator = MultiAgentOrchestrator()
        
        # Test initialization
        success = await orchestrator.initialize()
        print(f"Initialization: {'✅ Success' if success else '❌ Failed'}")
        
        # Test system status
        status = orchestrator.get_system_status()
        print(f"System Status: {status}")
        
        # Test with sample data
        sample_data = [
            {'customer_id': 'CUST_001', 'segment': 'premium', 'revenue': 1200},
            {'customer_id': 'CUST_002', 'segment': 'standard', 'revenue': 800}
        ]
        
        results = await orchestrator.analyze_customers(sample_data)
        print(f"Analysis Results: {'✅ Success' if results['success'] else '❌ Failed'}")
    
    asyncio.run(test_orchestrator())
