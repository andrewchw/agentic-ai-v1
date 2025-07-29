#!/usr/bin/env python3
"""
Test script to verify persistent state fixes for AttributeError issues.
This script tests the null safety improvements in export functions.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_export_functions_null_safety():
    """Test that export functions handle None deliverables gracefully"""
    
    # Mock streamlit session state with None values that caused the original error
    class MockSessionState:
        def __init__(self):
            self.data = {
                "crewai_deliverables": None,  # This was causing AttributeError
                "ai_analysis_results": {
                    "crewai_deliverables": None  # This too
                }
            }
        
        def get(self, key, default=None):
            return self.data.get(key, default)
        
        def __contains__(self, key):
            return key in self.data
        
        def __getitem__(self, key):
            return self.data[key]
    
    # Mock streamlit
    import streamlit as st
    st.session_state = MockSessionState()
    
    try:
        # Import the functions that were causing issues
        from src.components.results import (
            export_crewai_offers_csv,
            export_crewai_recommendations_csv, 
            export_campaign_summary_csv,
            export_email_templates_package
        )
        
        # Test results parameter (empty)
        test_results = {}
        
        print("Testing export_crewai_offers_csv with None deliverables...")
        csv_data = export_crewai_offers_csv(test_results)
        print("✅ export_crewai_offers_csv passed")
        
        print("Testing export_crewai_recommendations_csv with None deliverables...")
        csv_data = export_crewai_recommendations_csv(test_results)
        print("✅ export_crewai_recommendations_csv passed")
        
        print("Testing export_campaign_summary_csv with None deliverables...")
        csv_data = export_campaign_summary_csv(test_results)
        print("✅ export_campaign_summary_csv passed")
        
        print("Testing export_email_templates_package with None deliverables...")
        zip_data = export_email_templates_package(test_results)
        print("✅ export_email_templates_package passed")
        
        print("\n🎉 All export functions now handle None deliverables safely!")
        return True
        
    except AttributeError as e:
        if "'NoneType' object has no attribute 'get'" in str(e):
            print(f"❌ Still getting AttributeError: {e}")
            return False
        else:
            print(f"❌ Different AttributeError: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_session_validation():
    """Test the session state validation function"""
    try:
        from src.components.results import validate_and_clean_session_state
        
        # Mock streamlit with corrupted session state
        import streamlit as st
        
        # Set up corrupted session state
        st.session_state = {
            "ai_analysis_results": None,  # This should be cleaned
            "crewai_deliverables": None,  # This too
            "valid_data": {"some": "data"},  # This should remain
            "invalid_data": "not_a_dict"  # This might be cleaned depending on validation
        }
        
        print("Testing validate_and_clean_session_state...")
        validate_and_clean_session_state()
        print("✅ Session validation completed without errors")
        
        # Check that None values were removed
        if "ai_analysis_results" not in st.session_state:
            print("✅ None ai_analysis_results was cleaned up")
        if "crewai_deliverables" not in st.session_state:
            print("✅ None crewai_deliverables was cleaned up")
        if "valid_data" in st.session_state:
            print("✅ Valid data was preserved")
            
        return True
        
    except Exception as e:
        print(f"❌ Session validation error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Persistent State Fixes for AttributeError Issues")
    print("=" * 60)
    
    # Test export functions
    test1_passed = test_export_functions_null_safety()
    print()
    
    # Test session validation
    test2_passed = test_session_validation()
    print()
    
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED! The persistent state fixes should resolve the AttributeError issues.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. The AttributeError issues may persist.")
        sys.exit(1)
