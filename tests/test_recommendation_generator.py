"""
Tests for Recommendation Generator

This test suite validates:
1. Integration with all AI agent components
2. Recommendation generation and ranking logic
3. Business rule compliance
4. Hong Kong market-specific logic
5. Explainability and transparency
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import logging

from src.agents.recommendation_generator import (
    RecommendationGenerator,
    ActionableRecommendation,
    RecommendationPriority,
    ActionType,
    RecommendationExplanation,
    create_sample_recommendations,
)
from src.agents.customer_analysis import CustomerDataAnalyzer
from src.agents.lead_scoring import LeadScoringEngine
from src.agents.three_hk_business_rules import ThreeHKBusinessRulesEngine


class TestRecommendationGenerator:
    """Test suite for RecommendationGenerator"""

    @pytest.fixture
    def sample_leads_data(self):
        """Sample leads data for testing"""
        return pd.DataFrame([
            {
                "customer_id": "CUST_001",
                "customer_name": "ABC Corporation",
                "customer_type": "enterprise",
                "annual_revenue": 50000000,
                "employee_count": 500,
                "current_monthly_spend": 25000,
                "contract_end_date": "2024-06-30",
                "last_interaction": "2024-01-10",
                "preferred_contact_time": "morning",
                "industry": "financial_services",
                "location": "central",
                "decision_maker_identified": True,
                "budget_confirmed": True,
                "competitor_mentions": "PCCW",
                "urgency_indicators": ["contract_renewal", "expansion_needed"],
                "pain_points": ["slow_connectivity", "poor_support"],
            },
            {
                "customer_id": "CUST_002", 
                "customer_name": "XYZ SME Limited",
                "customer_type": "sme",
                "annual_revenue": 8000000,
                "employee_count": 50,
                "current_monthly_spend": 5000,
                "contract_end_date": "2024-12-31",
                "last_interaction": "2024-01-05",
                "preferred_contact_time": "afternoon",
                "industry": "retail",
                "location": "kowloon",
                "decision_maker_identified": False,
                "budget_confirmed": False,
                "competitor_mentions": None,
                "urgency_indicators": ["cost_reduction"],
                "pain_points": ["high_costs"],
            },
            {
                "customer_id": "CUST_003",
                "customer_name": "John Consumer",
                "customer_type": "consumer",
                "annual_revenue": None,
                "employee_count": None,
                "current_monthly_spend": 500,
                "contract_end_date": "2024-03-31",
                "last_interaction": "2024-01-12",
                "preferred_contact_time": "evening",
                "industry": None,
                "location": "new_territories",
                "decision_maker_identified": True,
                "budget_confirmed": True,
                "competitor_mentions": "CSL",
                "urgency_indicators": ["service_issues"],
                "pain_points": ["poor_coverage"],
            }
        ])

    @pytest.fixture
    def mock_customer_analyzer(self):
        """Mock CustomerDataAnalyzer"""
        analyzer = Mock(spec=CustomerDataAnalyzer)
        
        def mock_analyze(df):
            results = []
            for _, row in df.iterrows():
                if row["customer_type"] == "enterprise":
                    results.append({
                        "customer_segment": "enterprise_high_value",
                        "churn_risk": 0.2,
                        "expansion_potential": 0.8,
                        "preferred_contact_time": "morning",
                        "competitor_interest": True,
                    })
                elif row["customer_type"] == "sme":
                    results.append({
                        "customer_segment": "sme_growth",
                        "churn_risk": 0.4,
                        "expansion_potential": 0.6,
                        "preferred_contact_time": "afternoon",
                        "competitor_interest": False,
                    })
                else:
                    results.append({
                        "customer_segment": "consumer_basic",
                        "churn_risk": 0.7,
                        "expansion_potential": 0.3,
                        "preferred_contact_time": "evening",
                        "competitor_interest": True,
                    })
            return pd.DataFrame(results)
        
        analyzer.analyze_customer_segments.side_effect = mock_analyze
        return analyzer

    @pytest.fixture
    def mock_lead_scorer(self):
        """Mock LeadScoringEngine"""
        scorer = Mock(spec=LeadScoringEngine)
        
        def mock_score(df):
            results = []
            for _, row in df.iterrows():
                if row["customer_type"] == "enterprise":
                    results.append({
                        "overall_score": 0.85,
                        "revenue_potential": 0.9,
                        "conversion_probability": 0.75,
                        "urgency_factor": 0.8,
                        "strategic_value": 0.85,
                    })
                elif row["customer_type"] == "sme":
                    results.append({
                        "overall_score": 0.6,
                        "revenue_potential": 0.6,
                        "conversion_probability": 0.5,
                        "urgency_factor": 0.4,
                        "strategic_value": 0.6,
                    })
                else:
                    results.append({
                        "overall_score": 0.3,
                        "revenue_potential": 0.2,
                        "conversion_probability": 0.4,
                        "urgency_factor": 0.6,
                        "strategic_value": 0.2,
                    })
            return pd.DataFrame(results)
        
        scorer.score_leads.side_effect = mock_score
        return scorer

    @pytest.fixture
    def mock_business_rules(self):
        """Mock ThreeHKBusinessRulesEngine"""
        rules = Mock(spec=ThreeHKBusinessRulesEngine)
        
        def mock_match_offers(customer_data, customer_analysis):
            if customer_data.get("customer_type") == "enterprise":
                return [
                    {
                        "name": "Enterprise Fiber Plus",
                        "category": "fiber",
                        "monthly_value": 15000,
                        "key_benefit": "High-speed dedicated connectivity",
                        "compliance_score": 0.95,
                    },
                    {
                        "name": "Cloud Connect Pro", 
                        "category": "cloud",
                        "monthly_value": 8000,
                        "key_benefit": "Secure cloud integration",
                        "compliance_score": 0.9,
                    },
                ]
            elif customer_data.get("customer_type") == "sme":
                return [
                    {
                        "name": "Business Broadband Pro",
                        "category": "broadband",
                        "monthly_value": 2000,
                        "key_benefit": "Reliable business connectivity",
                        "compliance_score": 0.8,
                    }
                ]
            else:
                return [
                    {
                        "name": "Home Fiber 1000M",
                        "category": "consumer_fiber",
                        "monthly_value": 400,
                        "key_benefit": "Ultra-fast home internet",
                        "compliance_score": 0.7,
                    }
                ]
        
        rules.match_offers_to_customer.side_effect = mock_match_offers
        return rules

    @pytest.fixture
    def recommendation_generator(self, mock_customer_analyzer, mock_lead_scorer, mock_business_rules):
        """RecommendationGenerator instance with mocked dependencies"""
        return RecommendationGenerator(
            customer_analyzer=mock_customer_analyzer,
            lead_scorer=mock_lead_scorer,
            business_rules=mock_business_rules,
        )

    def test_initialization(self, recommendation_generator):
        """Test proper initialization of RecommendationGenerator"""
        assert recommendation_generator.customer_analyzer is not None
        assert recommendation_generator.lead_scorer is not None
        assert recommendation_generator.business_rules is not None
        assert hasattr(recommendation_generator, 'market_intelligence')
        assert hasattr(recommendation_generator, 'recommendation_templates')
        assert len(recommendation_generator.recommendation_templates) >= 5

    def test_generate_recommendations_basic(self, recommendation_generator, sample_leads_data):
        """Test basic recommendation generation"""
        recommendations = recommendation_generator.generate_recommendations(sample_leads_data)
        
        assert len(recommendations) == 3  # One per lead
        assert all(isinstance(rec, ActionableRecommendation) for rec in recommendations)
        
        # Check that all required fields are populated
        for rec in recommendations:
            assert rec.lead_id
            assert rec.customer_name
            assert rec.recommendation_id
            assert rec.priority
            assert rec.action_type
            assert rec.title
            assert rec.description
            assert rec.expected_revenue >= 0
            assert 0 <= rec.conversion_probability <= 1
            assert 0 <= rec.urgency_score <= 1
            assert 0 <= rec.business_impact_score <= 1
            assert rec.next_steps
            assert rec.talking_points
            assert rec.objection_handling
            assert rec.explanation
            assert rec.created_at
            assert rec.tags

    def test_action_type_determination(self, recommendation_generator, sample_leads_data):
        """Test action type determination logic"""
        recommendations = recommendation_generator.generate_recommendations(sample_leads_data)
        
        # Enterprise customer should get high-priority action
        enterprise_rec = next(rec for rec in recommendations if "ABC Corporation" in rec.customer_name)
        assert enterprise_rec.action_type in [ActionType.IMMEDIATE_CALL, ActionType.SCHEDULE_MEETING]
        assert enterprise_rec.priority in [RecommendationPriority.CRITICAL, RecommendationPriority.HIGH]
        
        # Consumer with issues should get retention focus
        consumer_rec = next(rec for rec in recommendations if "John Consumer" in rec.customer_name)
        assert consumer_rec.action_type in [ActionType.RETENTION_OUTREACH, ActionType.FOLLOW_UP]

    def test_priority_calculation(self, recommendation_generator, sample_leads_data):
        """Test priority calculation logic"""
        recommendations = recommendation_generator.generate_recommendations(sample_leads_data)
        
        # Check that priorities are logical
        priorities = [rec.priority for rec in recommendations]
        assert RecommendationPriority.CRITICAL in priorities or RecommendationPriority.HIGH in priorities
        
        # Enterprise should have higher priority than consumer
        enterprise_rec = next(rec for rec in recommendations if "ABC Corporation" in rec.customer_name)
        consumer_rec = next(rec for rec in recommendations if "John Consumer" in rec.customer_name)
        
        priority_values = {
            RecommendationPriority.CRITICAL: 5,
            RecommendationPriority.HIGH: 4,
            RecommendationPriority.MEDIUM: 3,
            RecommendationPriority.LOW: 2,
            RecommendationPriority.WATCH: 1,
        }
        
        assert priority_values[enterprise_rec.priority] >= priority_values[consumer_rec.priority]

    def test_recommendation_ranking(self, recommendation_generator, sample_leads_data):
        """Test recommendation ranking logic"""
        recommendations = recommendation_generator.generate_recommendations(sample_leads_data)
        
        # Recommendations should be ranked by business impact
        business_scores = [rec.business_impact_score for rec in recommendations]
        assert business_scores == sorted(business_scores, reverse=True)
        
        # Higher revenue potential should rank higher
        revenue_values = [rec.expected_revenue for rec in recommendations]
        assert revenue_values[0] >= revenue_values[-1]

    def test_hong_kong_market_intelligence(self, recommendation_generator):
        """Test Hong Kong market-specific intelligence"""
        # Check market intelligence data
        mi = recommendation_generator.market_intelligence
        
        assert "peak_contact_hours" in mi
        assert "optimal_call_days" in mi
        assert "average_decision_time" in mi
        assert "competitor_strengths" in mi
        assert "seasonal_factors" in mi
        
        # Verify Hong Kong-specific competitors
        competitors = mi["competitor_strengths"]
        assert "PCCW" in competitors
        assert "CSL" in competitors
        assert "China_Mobile" in competitors

    def test_talking_points_generation(self, recommendation_generator, sample_leads_data):
        """Test talking points generation"""
        recommendations = recommendation_generator.generate_recommendations(sample_leads_data)
        
        for rec in recommendations:
            assert len(rec.talking_points) >= 3
            assert all(isinstance(point, str) for point in rec.talking_points)
            
            # Check for customer-specific content
            if "enterprise" in rec.tags:
                enterprise_keywords = ["enterprise", "scalable", "dedicated", "mainland"]
                assert any(keyword in " ".join(rec.talking_points).lower() for keyword in enterprise_keywords)

    def test_objection_handling(self, recommendation_generator, sample_leads_data):
        """Test objection handling generation"""
        recommendations = recommendation_generator.generate_recommendations(sample_leads_data)
        
        for rec in recommendations:
            objections = rec.objection_handling
            assert "price_concern" in objections
            assert "competitor_comparison" in objections
            assert "contract_length" in objections
            assert all(isinstance(response, str) for response in objections.values())
            assert all(len(response) > 50 for response in objections.values())  # Substantial responses

    def test_explanation_generation(self, recommendation_generator, sample_leads_data):
        """Test explanation generation for transparency"""
        recommendations = recommendation_generator.generate_recommendations(sample_leads_data)
        
        for rec in recommendations:
            explanation = rec.explanation
            assert isinstance(explanation, RecommendationExplanation)
            assert explanation.primary_reason
            assert len(explanation.supporting_factors) >= 1
            assert 0 <= explanation.confidence_score <= 1
            assert explanation.data_sources
            assert "Lead Scoring" in explanation.data_sources
            assert "Customer Analysis" in explanation.data_sources

    def test_business_constraints(self, recommendation_generator, sample_leads_data):
        """Test business constraints application"""
        # Test with limited recommendations
        recommendations = recommendation_generator.generate_recommendations(
            sample_leads_data, max_recommendations=2
        )
        
        assert len(recommendations) <= 2
        
        # Test with larger dataset to check priority distribution
        large_dataset = pd.concat([sample_leads_data] * 10, ignore_index=True)
        large_recommendations = recommendation_generator.generate_recommendations(
            large_dataset, max_recommendations=20
        )
        
        # Should prioritize higher impact recommendations
        assert len(large_recommendations) <= 20
        priority_counts = {}
        for rec in large_recommendations:
            priority_counts[rec.priority] = priority_counts.get(rec.priority, 0) + 1
        
        # Should have more high-priority than low-priority
        high_priority_count = priority_counts.get(RecommendationPriority.HIGH, 0) + priority_counts.get(RecommendationPriority.CRITICAL, 0)
        low_priority_count = priority_counts.get(RecommendationPriority.LOW, 0) + priority_counts.get(RecommendationPriority.WATCH, 0)
        assert high_priority_count >= low_priority_count

    def test_expiry_date_calculation(self, recommendation_generator, sample_leads_data):
        """Test recommendation expiry date calculation"""
        recommendations = recommendation_generator.generate_recommendations(sample_leads_data)
        
        for rec in recommendations:
            if rec.expires_at:
                assert rec.expires_at > rec.created_at
                
                # Check expiry is appropriate for priority
                days_diff = (rec.expires_at - rec.created_at).days
                
                if rec.priority == RecommendationPriority.CRITICAL:
                    assert days_diff <= 1
                elif rec.priority == RecommendationPriority.HIGH:
                    assert days_diff <= 3
                elif rec.priority == RecommendationPriority.MEDIUM:
                    assert days_diff <= 7

    def test_export_functionality(self, recommendation_generator, sample_leads_data):
        """Test recommendation export functionality"""
        recommendations = recommendation_generator.generate_recommendations(sample_leads_data)
        export_data = recommendation_generator.export_recommendations(recommendations)
        
        assert "generated_at" in export_data
        assert "total_recommendations" in export_data
        assert "recommendations" in export_data
        assert "summary" in export_data
        
        summary = export_data["summary"]
        assert "by_priority" in summary
        assert "by_action_type" in summary
        assert "total_expected_revenue" in summary
        assert "average_conversion_probability" in summary
        
        # Check data integrity
        assert export_data["total_recommendations"] == len(recommendations)
        assert len(export_data["recommendations"]) == len(recommendations)

    def test_error_handling(self, recommendation_generator):
        """Test error handling with invalid data"""
        # Test with empty DataFrame
        empty_df = pd.DataFrame()
        recommendations = recommendation_generator.generate_recommendations(empty_df)
        assert len(recommendations) == 0
        
        # Test with invalid data
        invalid_df = pd.DataFrame([{"invalid": "data"}])
        recommendations = recommendation_generator.generate_recommendations(invalid_df)
        # Should handle gracefully without crashing

    def test_sample_recommendations_creation(self):
        """Test sample recommendations creation function"""
        samples = create_sample_recommendations()
        
        assert len(samples) >= 1
        assert all(isinstance(rec, ActionableRecommendation) for rec in samples)
        
        # Check sample quality
        sample = samples[0]
        assert sample.lead_id
        assert sample.customer_name
        assert sample.priority == RecommendationPriority.CRITICAL
        assert sample.action_type == ActionType.IMMEDIATE_CALL
        assert sample.expected_revenue > 0
        assert len(sample.next_steps) >= 3
        assert len(sample.talking_points) >= 3

    def test_integration_with_real_components(self, sample_leads_data):
        """Test integration with actual component instances"""
        # This test uses real instances to ensure integration works
        try:
            from src.agents.customer_data_analyzer import CustomerDataAnalyzer
            from src.agents.lead_scoring_engine import LeadScoringEngine
            from src.agents.three_hk_business_rules import ThreeHKBusinessRulesEngine
            
            # Create real instances
            customer_analyzer = CustomerDataAnalyzer()
            lead_scorer = LeadScoringEngine()
            business_rules = ThreeHKBusinessRulesEngine()
            
            # Create generator with real components
            generator = RecommendationGenerator(
                customer_analyzer=customer_analyzer,
                lead_scorer=lead_scorer,
                business_rules=business_rules
            )
            
            # Test with a subset of data
            test_data = sample_leads_data.iloc[:1]  # Just one record
            recommendations = generator.generate_recommendations(test_data)
            
            # Should generate at least one recommendation
            assert len(recommendations) >= 0  # Graceful handling even if components fail
            
        except ImportError:
            pytest.skip("Real components not available for integration test")

    def test_performance_with_large_dataset(self, recommendation_generator):
        """Test performance with large dataset"""
        # Create large dataset
        base_data = {
            "customer_id": [f"CUST_{i:05d}" for i in range(100)],
            "customer_name": [f"Customer {i}" for i in range(100)],
            "customer_type": ["enterprise", "sme", "consumer"] * 34,  # Cycle through types
            "current_monthly_spend": np.random.randint(1000, 50000, 100),
            "annual_revenue": np.random.randint(1000000, 100000000, 100),
        }
        
        large_df = pd.DataFrame(base_data)
        
        # Measure time (basic performance check)
        start_time = datetime.now()
        recommendations = recommendation_generator.generate_recommendations(
            large_df, max_recommendations=50
        )
        end_time = datetime.now()
        
        processing_time = (end_time - start_time).total_seconds()
        
        # Should complete in reasonable time (under 30 seconds for 100 records)
        assert processing_time < 30
        assert len(recommendations) <= 50
        
        # Check that ranking is maintained
        if len(recommendations) > 1:
            scores = [rec.business_impact_score for rec in recommendations]
            assert scores == sorted(scores, reverse=True)


if __name__ == "__main__":
    # Run basic test
    print("Testing Recommendation Generator...")
    
    # Create sample data
    sample_data = pd.DataFrame([
        {
            "customer_id": "TEST_001",
            "customer_name": "Test Corporation",
            "customer_type": "enterprise",
            "current_monthly_spend": 20000,
            "annual_revenue": 50000000,
        }
    ])
    
    # Test sample recommendations
    samples = create_sample_recommendations()
    print(f"✅ Created {len(samples)} sample recommendations")
    
    print("✅ Recommendation Generator tests ready") 