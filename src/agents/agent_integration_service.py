"""
Agent Integration Service
========================

Service to integrate Lead Intelligence Agent results with the Agent Protocol
for automatic multi-agent collaboration workflows.

This service bridges the gap between:
1. Lead Intelligence Agent Dashboard (generates analysis results)
2. Agent Protocol Server (handles agent communication)
3. Revenue Optimization Agent (processes collaboration requests)

Author: Agentic AI Revenue Assistant
Date: 2025-07-23
"""

import requests
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import time

logger = logging.getLogger(__name__)

class AgentIntegrationService:
    """
    Service for integrating Lead Intelligence Agent with Agent Protocol
    for automatic multi-agent collaboration.
    """
    
    def __init__(self, agent_protocol_url: str = "http://127.0.0.1:8080"):
        """Initialize the integration service."""
        self.agent_protocol_url = agent_protocol_url
        self.api_base = f"{agent_protocol_url}/ap/v1"
        self.enabled = True
        self.collaboration_history = []
        
    def check_agent_protocol_availability(self) -> bool:
        """Check if Agent Protocol server is available."""
        try:
            response = requests.get(f"{self.api_base}/agent/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Agent Protocol not available: {e}")
            return False
    
    def send_analysis_to_revenue_agent(self, analysis_results: Dict[str, Any]) -> Optional[str]:
        """
        Send Lead Intelligence analysis results to Revenue Optimization Agent
        via Agent Protocol for further processing.
        """
        if not self.enabled or not self.check_agent_protocol_availability():
            logger.info("Agent collaboration disabled or protocol unavailable")
            return None
            
        try:
            # Prepare collaboration request payload
            collaboration_payload = self._prepare_collaboration_payload(analysis_results)
            
            # Send to Agent Protocol
            response = requests.post(
                f"{self.api_base}/agent/tasks",
                json=collaboration_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                task_data = response.json()
                task_id = task_data.get('task_id')
                
                logger.info(f"Successfully triggered agent collaboration: {task_id}")
                
                # Record collaboration
                self.collaboration_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'task_id': task_id,
                    'source_agent': 'lead_intelligence',
                    'target_agent': 'revenue_optimization',
                    'collaboration_type': 'analysis_handoff',
                    'status': 'initiated'
                })
                
                return task_id
            else:
                logger.error(f"Failed to trigger collaboration: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error sending analysis to revenue agent: {e}")
            return None
    
    def _prepare_collaboration_payload(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare collaboration payload for Agent Protocol."""
        
        # Extract key insights from analysis results
        key_insights = []
        collaboration_requests = []
        
        # Process analysis results
        if 'patterns' in analysis_results:
            patterns = analysis_results['patterns']
            
            # High-value customer insights
            if 'high_value_segments' in patterns:
                key_insights.append({
                    'type': 'high_value_segments',
                    'data': patterns['high_value_segments'],
                    'priority': 'high'
                })
                collaboration_requests.append({
                    'request_type': 'optimization_strategy',
                    'focus': 'high_value_customer_retention',
                    'data_context': patterns['high_value_segments']
                })
            
            # Churn risk insights
            if 'churn_indicators' in patterns:
                key_insights.append({
                    'type': 'churn_risk',
                    'data': patterns['churn_indicators'],
                    'priority': 'urgent'
                })
                collaboration_requests.append({
                    'request_type': 'retention_strategy',
                    'focus': 'churn_prevention',
                    'data_context': patterns['churn_indicators']
                })
            
            # Lead scoring insights
            if 'lead_scores' in patterns:
                key_insights.append({
                    'type': 'lead_scoring',
                    'data': patterns['lead_scores'],
                    'priority': 'medium'
                })
                collaboration_requests.append({
                    'request_type': 'upsell_strategy',
                    'focus': 'lead_conversion',
                    'data_context': patterns['lead_scores']
                })
        
        # Prepare Agent Protocol task payload
        return {
            "input": f"""
LEAD INTELLIGENCE ANALYSIS HANDOFF
=================================

Analysis completed by Lead Intelligence Agent for Hong Kong Telecom market.
Requesting Revenue Optimization Agent collaboration for strategic recommendations.

ANALYSIS SUMMARY:
- Customer segments analyzed: {analysis_results.get('customer_count', 'Unknown')}
- Analysis timestamp: {datetime.now().isoformat()}
- Key patterns identified: {len(key_insights)}
- Collaboration requests: {len(collaboration_requests)}

KEY INSIGHTS:
{json.dumps(key_insights, indent=2)}

COLLABORATION REQUESTS:
{json.dumps(collaboration_requests, indent=2)}

REVENUE OPTIMIZATION TASKS REQUESTED:
1. Develop ARPU optimization strategies for high-value segments
2. Create retention offers for churn-risk customers  
3. Design upsell campaigns for qualified leads
4. Provide strategic recommendations for Hong Kong telecom market

Please process these insights and provide revenue optimization recommendations.
            """.strip(),
            "additional_input": {
                "source_agent": "lead_intelligence",
                "target_agent": "revenue_optimization", 
                "collaboration_type": "analysis_handoff",
                "priority": "high",
                "market_focus": "hong_kong_telecom",
                "analysis_data": analysis_results,
                "collaboration_requests": collaboration_requests
            }
        }
    
    def monitor_collaboration_task(self, task_id: str, timeout: int = 30) -> Dict[str, Any]:
        """Monitor the progress of a collaboration task."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.api_base}/agent/tasks/{task_id}", timeout=5)
                if response.status_code == 200:
                    task_data = response.json()
                    status = task_data.get('status', 'unknown')
                    
                    if status == 'completed':
                        # Update collaboration history
                        for collab in self.collaboration_history:
                            if collab.get('task_id') == task_id:
                                collab['status'] = 'completed'
                                collab['completed_at'] = datetime.now().isoformat()
                                break
                        
                        return {
                            'status': 'completed',
                            'task_data': task_data,
                            'collaboration_successful': True
                        }
                    elif status == 'failed':
                        return {
                            'status': 'failed',
                            'task_data': task_data,
                            'collaboration_successful': False
                        }
                    
                # Task still in progress, wait and retry
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error monitoring collaboration task {task_id}: {e}")
                break
        
        return {
            'status': 'timeout',
            'collaboration_successful': False,
            'message': f'Collaboration task {task_id} timed out after {timeout} seconds'
        }
    
    def trigger_full_collaboration_workflow(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trigger a complete collaboration workflow:
        1. Send analysis to Revenue Agent
        2. Monitor task completion  
        3. Return collaboration results
        """
        workflow_start = datetime.now()
        
        # Step 1: Send analysis to Revenue Agent
        task_id = self.send_analysis_to_revenue_agent(analysis_results)
        
        if not task_id:
            return {
                'success': False,
                'error': 'Failed to initiate collaboration',
                'workflow_duration': 0
            }
        
        # Step 2: Monitor collaboration progress
        logger.info(f"Monitoring collaboration task: {task_id}")
        collaboration_result = self.monitor_collaboration_task(task_id, timeout=45)
        
        workflow_duration = (datetime.now() - workflow_start).total_seconds()
        
        return {
            'success': collaboration_result['collaboration_successful'],
            'task_id': task_id,
            'collaboration_result': collaboration_result,
            'workflow_duration': workflow_duration,
            'analysis_summary': {
                'customer_count': analysis_results.get('customer_count', 0),
                'patterns_found': len(analysis_results.get('patterns', {})),
                'collaboration_requests': len(analysis_results.get('patterns', {}).get('collaboration_requests', []))
            }
        }
    
    def get_collaboration_history(self) -> List[Dict[str, Any]]:
        """Get the history of agent collaborations."""
        return self.collaboration_history.copy()
    
    def get_collaboration_status(self) -> Dict[str, Any]:
        """Get current collaboration status and metrics."""
        total_collaborations = len(self.collaboration_history)
        completed_collaborations = len([c for c in self.collaboration_history if c.get('status') == 'completed'])
        
        return {
            'service_enabled': self.enabled,
            'agent_protocol_available': self.check_agent_protocol_availability(),
            'total_collaborations': total_collaborations,
            'completed_collaborations': completed_collaborations,
            'success_rate': (completed_collaborations / total_collaborations * 100) if total_collaborations > 0 else 0,
            'recent_collaborations': self.collaboration_history[-5:] if self.collaboration_history else []
        }
    
    def enable_collaboration(self):
        """Enable agent collaboration."""
        self.enabled = True
        logger.info("Agent collaboration enabled")
    
    def disable_collaboration(self):
        """Disable agent collaboration.""" 
        self.enabled = False
        logger.info("Agent collaboration disabled")


# Global integration service instance
integration_service = AgentIntegrationService()


def get_integration_service() -> AgentIntegrationService:
    """Get the global integration service instance."""
    return integration_service


# Convenience functions for easy integration
def trigger_agent_collaboration(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to trigger agent collaboration from analysis results.
    
    This can be called from the Lead Intelligence Dashboard when analysis completes.
    """
    return integration_service.trigger_full_collaboration_workflow(analysis_results)


def get_collaboration_status() -> Dict[str, Any]:
    """Get current collaboration status."""
    return integration_service.get_collaboration_status()


def is_collaboration_enabled() -> bool:
    """Check if agent collaboration is enabled and available."""
    status = integration_service.get_collaboration_status()
    return status['service_enabled'] and status['agent_protocol_available']
