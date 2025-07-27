#!/usr/bin/env python3
"""
Test script to verify the CrewAI deliverables data flow fix
"""
import streamlit as st
import sys
import os
sys.path.append('.')

# Check if our session state simulation works
print('Testing CrewAI deliverables data flow...')

# Simulate what the orchestrator should generate
sample_deliverables = {
    'personalized_offers': [
        {
            'customer_id': 'CUST_001',
            'customer_name': 'John Wong',
            'offer_type': 'Business Upgrade',
            'title': '5G Enterprise Pro - Exclusive Upgrade',
            'description': 'Upgrade to our 5G Enterprise Pro plan with 20% discount for the first 6 months',
            'current_plan': '5G Pro',
            'recommended_plan': '5G Enterprise Pro',
            'discount': '20% for 6 months',
            'estimated_value': 'HK$720/month',
            'revenue_impact': 'HK$1,920 annually',
            'confidence': 0.87,
            'expiry_date': '2025-08-25'
        }
    ],
    'email_templates': [
        {
            'template_id': 'BUS_UPGRADE_001',
            'template_name': 'Business 5G Enterprise Upgrade',
            'subject': 'Exclusive 5G Enterprise Pro Upgrade',
            'body': 'Dear customer...',
            'target_audience': 'Business customers',
            'offer_type': 'Business Upgrade'
        }
    ]
}

# Test export function
from src.components.results import export_crewai_offers_csv

# Simulate session state having the deliverables
class MockSessionState:
    def __init__(self):
        self.data = {'crewai_deliverables': sample_deliverables}
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def __contains__(self, key):
        return key in self.data
    
    def __getitem__(self, key):
        return self.data[key]

# Mock streamlit session state
st.session_state = MockSessionState()

# Test export
result = export_crewai_offers_csv({})
print('Export result (first 200 chars):')
print(result[:200] + '...' if len(result) > 200 else result)

print('✅ Data flow test completed')
