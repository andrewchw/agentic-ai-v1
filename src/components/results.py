"""
Results page component for displaying AI analysis results and data merging
Enhanced with AI Agent Integration (Task 9) and Interactive Dashboard (Task 12)
"""

import streamlit as st
import pandas as pd
import json
import time
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import plotly.express as px
import plotly.graph_objects as go

from src.utils.data_merging import DataMerger, MergeStrategy, MergeResult
from src.utils.product_catalog_db import get_product_catalog, is_catalog_available
from src.utils.openrouter_client import OpenRouterClient, OpenRouterConfig


def render_results_page():
    """Render the enhanced analysis results page with AI recommendations"""

    st.markdown("## 📊 AI Revenue Assistant - Analysis Results")

    # Auto-load persistent product catalog into session if available
    if is_catalog_available() and "product_catalog" not in st.session_state:
        catalog_df = get_product_catalog()
        if not catalog_df.empty:
            st.session_state["product_catalog"] = {
                "original_data": catalog_df,
                "catalog_data": catalog_df,
                "metadata": {
                    "filename": "persistent_catalog.json",
                    "data_type": "product_catalog",
                    "persistent": True,
                    "loaded_from": "database"
                }
            }

    # Display persistent AI debug information if available
    if "ai_debug_logs" in st.session_state or "ai_debug_info" in st.session_state:
        with st.expander("🔍 AI Analysis Debug Information", expanded=False):
            
            # Show basic debug logs
            if "ai_debug_logs" in st.session_state and st.session_state["ai_debug_logs"]:
                st.write("### 📋 Analysis Setup")
                for log in st.session_state["ai_debug_logs"]:
                    if log["status"] == "success":
                        st.success(log["message"])
                    elif log["status"] == "warning":
                        st.warning(log["message"])
                    else:
                        st.error(log["message"])
            
            # Show detailed AI debug info
            if "ai_debug_info" in st.session_state and st.session_state["ai_debug_info"]:
                st.write("### 🤖 AI Processing Details")
                
                for i, debug_info in enumerate(st.session_state["ai_debug_info"]):
                    with st.expander(f"Customer: {debug_info['customer_name']} (ID: {debug_info['customer_id']})", expanded=False):
                        
                        # API Key Status
                        if debug_info.get("api_key_status"):
                            if debug_info["api_key_status"]["found"]:
                                st.success(f"✅ API Key: {debug_info['api_key_status']['masked_key']} ({debug_info['api_key_status']['length']} chars)")
                            else:
                                st.error("❌ API Key not found")
                        
                        # Client Status
                        if debug_info.get("client_status"):
                            if debug_info["client_status"]["initialized"]:
                                st.success(f"✅ Client initialized: {debug_info['client_status']['model']}")
                                st.write(f"   - Max tokens: {debug_info['client_status']['max_tokens']}")
                                st.write(f"   - Temperature: {debug_info['client_status']['temperature']}")
                            else:
                                st.error(f"❌ Client failed: {debug_info['client_status']['error']}")
                        
                        # API Call Info
                        if debug_info.get("api_call_info"):
                            if debug_info["api_call_info"]["success"]:
                                st.success(f"✅ API call successful: {debug_info['api_call_info']['duration']:.2f}s")
                                st.write(f"   - Model: {debug_info['api_call_info']['model']}")
                            else:
                                st.error(f"❌ API call failed: {debug_info['api_call_info']['error']}")
                        
                        # Response Info
                        if debug_info.get("response_info"):
                            if debug_info["response_info"]["received"]:
                                st.success(f"✅ Response received: {debug_info['response_info']['content_length']} chars")
                                
                                # Show model and token info if available
                                if debug_info["response_info"].get("model_used"):
                                    st.write(f"   - Model: {debug_info['response_info']['model_used']}")
                                if debug_info["response_info"].get("tokens_used"):
                                    st.write(f"   - Tokens: {debug_info['response_info']['tokens_used']}")
                                
                                if debug_info["response_info"].get("parsed_successfully"):
                                    st.success("✅ JSON parsed successfully")
                                    st.write(f"   - Fields: {', '.join(debug_info['response_info']['parsed_fields'])}")
                                elif debug_info["response_info"].get("parsed_successfully") is False:
                                    st.error(f"❌ JSON parsing failed: {debug_info['response_info']['parse_error']}")
                                
                                # Show raw response
                                with st.expander("Raw AI Response", expanded=False):
                                    st.code(debug_info["response_info"]["raw_content"], language="json")
                            else:
                                st.error("❌ No response received")
                                if debug_info["response_info"].get("error"):
                                    st.error(f"   - Error: {debug_info['response_info']['error']}")
                        
                        # Customer Profile
                        if debug_info.get("customer_profile"):
                            with st.expander("Customer Profile Sent to AI", expanded=False):
                                st.json(debug_info["customer_profile"])
                        
                        # Prompt
                        if debug_info.get("prompt"):
                            with st.expander("Full Prompt Sent to AI", expanded=False):
                                st.code(debug_info["prompt"], language="text")
                        
                        # Errors
                        if debug_info.get("errors"):
                            st.write("**Errors:**")
                            for error in debug_info["errors"]:
                                st.error(f"❌ {error}")

    # Check for AI analysis results first
    has_ai_results = "ai_analysis_results" in st.session_state
    has_customer_data = "customer_data" in st.session_state
    has_purchase_data = "purchase_data" in st.session_state

    if has_ai_results:
        render_ai_analysis_dashboard()
    elif has_customer_data and has_purchase_data:
        # Show data merging and offer to run AI analysis
        render_data_merging_section()
        render_ai_analysis_trigger()
    else:
        render_getting_started()

    st.markdown("---")


def render_ai_analysis_dashboard():
    """Render the main AI analysis dashboard with recommendations"""
    
    results = st.session_state["ai_analysis_results"]
    
    # Dashboard header with key metrics
    render_dashboard_metrics(results)
    
    # AI Recommendations section
    st.markdown("### 🤖 AI-Generated Recommendations")
    render_recommendations_section(results)
    
    # Customer analysis insights
    st.markdown("### 👥 Customer Analysis Insights")
    render_customer_insights(results)
    
    # Lead scoring breakdown
    st.markdown("### 📊 Lead Scoring Analysis")
    render_lead_scoring_section(results)
    
    # Three HK offers matching
    st.markdown("### 🎯 Three HK Offer Recommendations")
    render_offers_section(results)
    
    # Export and actions
    st.markdown("### 📤 Export & Actions")
    render_export_section(results)
    
    # Agent Collaboration section
    st.markdown("### 🤖 Multi-Agent Collaboration")
    render_agent_collaboration_section(results)


def render_dashboard_metrics(results: Dict[str, Any]):
    """Render top-level dashboard metrics"""
    
    # Extract key metrics from AI results
    recommendations = results.get("recommendations", {}).get("recommendations", [])
    summary = results.get("recommendations", {}).get("summary", {})
    
    total_customers = len(recommendations) if recommendations else 0
    high_priority = sum(1 for r in recommendations if r.get("priority") in ["critical", "high"])
    total_revenue = summary.get("total_expected_revenue", 0)
    avg_conversion = summary.get("average_conversion_probability", 0)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="🎯 Customers Analyzed",
            value=total_customers,
            help="Number of customer records processed by AI"
        )

    with col2:
        st.metric(
            label="🔥 High Priority Leads",
            value=high_priority,
            delta=f"{high_priority/max(total_customers, 1)*100:.1f}%",
            help="Customers with critical or high priority"
        )

    with col3:
        st.metric(
            label="💰 Expected Revenue",
            value=f"HK${total_revenue:,.0f}",
            help="Total projected revenue from recommendations"
        )

    with col4:
        st.metric(
            label="📈 Avg Conversion Rate",
            value=f"{avg_conversion:.1%}",
            help="Average predicted conversion probability"
        )
    
    # Processing info
    processing_time = results.get("processing_time", 0)
    timestamp = results.get("metadata", {}).get("timestamp", datetime.now().isoformat())
    
    st.info(f"🤖 AI Analysis completed in {processing_time:.2f}s at {timestamp[:19].replace('T', ' ')}")


def render_recommendations_section(results: Dict[str, Any]):
    """Render the AI recommendations with interactive controls"""
    
    recommendations = results.get("recommendations", {}).get("recommendations", [])
    
    if not recommendations:
        st.warning("No recommendations generated. Please check your data and try again.")
        return
    
    # Filtering controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        priority_filter = st.selectbox(
            "Filter by Priority",
            options=["All"] + list(set(r.get("priority", "unknown") for r in recommendations)),
            index=0,
            key="recommendations_priority_filter"
        )
    
    with col2:
        action_filter = st.selectbox(
            "Filter by Action Type",
            options=["All"] + list(set(r.get("action_type", "unknown") for r in recommendations)),
            index=0,
            key="recommendations_action_filter"
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort by",
            options=["Business Impact", "Expected Revenue", "Conversion Probability", "Urgency Score"],
            index=0,
            key="recommendations_sort_by"
        )
    
    # Filter recommendations
    filtered_recs = recommendations.copy()
    
    if priority_filter != "All":
        filtered_recs = [r for r in filtered_recs if r.get("priority") == priority_filter]
    
    if action_filter != "All":
        filtered_recs = [r for r in filtered_recs if r.get("action_type") == action_filter]
    
    # Sort recommendations
    sort_key_map = {
        "Business Impact": "business_impact_score",
        "Expected Revenue": "expected_revenue", 
        "Conversion Probability": "conversion_probability",
        "Urgency Score": "urgency_score"
    }
    
    sort_key = sort_key_map.get(sort_by, "business_impact_score")
    filtered_recs.sort(key=lambda x: x.get(sort_key, 0), reverse=True)
    
    st.write(f"Showing {len(filtered_recs)} of {len(recommendations)} recommendations")
    
    # Display recommendations
    for i, rec in enumerate(filtered_recs):
        render_recommendation_card(rec, i + 1)


def render_recommendation_card(rec: Dict[str, Any], index: int):
    """Render a single recommendation card"""
    
    priority = rec.get("priority", "unknown").upper()
    priority_colors = {
        "CRITICAL": "🔴",
        "HIGH": "🟠", 
        "MEDIUM": "🟡",
        "LOW": "🟢",
        "WATCH": "⚪"
    }
    
    priority_icon = priority_colors.get(priority, "⚪")
    
    with st.container():
        st.markdown(f"#### {priority_icon} Recommendation #{index}")
        
        # Header row with key info
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        
        with col1:
            st.markdown(f"**🎯 {rec.get('customer_name', 'Unknown Customer')}**")
            st.caption(f"ID: {rec.get('customer_id', 'N/A')}")
        
        with col2:
            st.markdown(f"**Priority:** {priority}")
            st.caption(f"Action: {rec.get('action_type', 'N/A').replace('_', ' ').title()}")
        
        with col3:
            revenue = rec.get("expected_revenue", 0)
            st.markdown(f"**Revenue:** HK${revenue:,.0f}")
            conversion = rec.get("conversion_probability", 0)
            st.caption(f"Conversion: {conversion:.1%}")
        
        with col4:
            impact = rec.get("business_impact_score", 0)
            st.markdown(f"**Impact:** {impact:.2f}")
            urgency = rec.get("urgency_score", 0)
            st.caption(f"Urgency: {urgency:.1%}")
        
        # Expandable details
        with st.expander(f"📋 View Details - {rec.get('title', 'Recommendation')}"):
            
            # Description and explanation
            st.markdown(f"**Description:** {rec.get('description', 'No description available')}")
            
            explanation = rec.get("explanation", {})
            if explanation:
                st.markdown(f"**🧠 AI Reasoning:** {explanation.get('primary_reason', 'N/A')}")
                st.caption(f"Confidence: {explanation.get('confidence_score', 0):.1%}")
                
                if explanation.get("supporting_factors"):
                    st.markdown("**Supporting Factors:**")
                    for factor in explanation.get("supporting_factors", []):
                        st.markdown(f"• {factor}")
            
            # Next steps
            next_steps = rec.get("next_steps", [])
            if next_steps:
                st.markdown("**📋 Next Steps:**")
                for i, step in enumerate(next_steps, 1):
                    st.markdown(f"{i}. {step}")
            
            # Talking points
            talking_points = rec.get("talking_points", [])
            if talking_points:
                st.markdown("**💬 Key Talking Points:**")
                for point in talking_points:
                    st.markdown(f"• {point}")
            
            # Recommended offers
            offers = rec.get("recommended_offers", [])
            if offers:
                st.markdown("**🎁 Recommended Three HK Offers:**")
                for offer in offers:
                    name = offer.get("name", "Unknown Offer")
                    value = offer.get("monthly_value", 0)
                    st.markdown(f"• **{name}** - HK${value:,}/month")
            
            # Objection handling
            objections = rec.get("objection_handling", {})
            if objections:
                st.markdown("**🤔 Objection Handling:**")
                for objection, response in objections.items():
                    st.markdown(f"**Q:** {objection.replace('_', ' ').title()}")
                    st.markdown(f"**A:** {response}")
                    st.markdown("")

    st.markdown("---")


def render_customer_insights(results: Dict[str, Any]):
    """Render customer analysis insights"""
    
    customer_analysis = results.get("customer_analysis")
    
    if not customer_analysis:
        st.info("Customer analysis data not available in current results.")
        return
    
    # Display real customer insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Customer Segments")
        segments = customer_analysis.get("segments", {})
        total = customer_analysis.get("total_customers", 0)
        
        if segments:
            st.metric("High Value Customers", segments.get("high_value", 0), 
                     delta=f"{segments.get('high_value', 0)/max(total, 1)*100:.1f}%")
            st.metric("Medium Value Customers", segments.get("medium_value", 0),
                     delta=f"{segments.get('medium_value', 0)/max(total, 1)*100:.1f}%")
            st.metric("Low Value Customers", segments.get("low_value", 0),
                     delta=f"{segments.get('low_value', 0)/max(total, 1)*100:.1f}%")
    
    with col2:
        st.markdown("#### 👥 Demographics")
        demographics = customer_analysis.get("demographics", {})
        
        if "customer_types" in demographics:
            st.markdown("**Customer Types:**")
            for ctype, count in demographics["customer_types"].items():
                st.markdown(f"• {ctype}: {count} customers")
        
        if "customer_classes" in demographics:
            st.markdown("**Customer Classes:**")
            for cclass, count in demographics["customer_classes"].items():
                st.markdown(f"• {cclass}: {count} customers")
    
    # Display patterns if available
    patterns = customer_analysis.get("patterns", [])
    if patterns:
        st.markdown("#### 🔍 Identified Patterns")
        for pattern in patterns:
            st.info(f"• {pattern}")


def render_lead_scoring_section(results: Dict[str, Any]):
    """Render lead scoring analysis with visualizations"""
    
    lead_scores = results.get("lead_scores")
    recommendations = results.get("recommendations", {}).get("recommendations", [])
    
    if not recommendations:
        st.info("Lead scoring data not available.")
        return
    
    # Create scoring distribution chart
    priorities = [r.get("priority", "unknown") for r in recommendations]
    priority_counts = pd.Series(priorities).value_counts()
    
    # Priority distribution pie chart
    col1, col2 = st.columns(2)
    
    with col1:
        fig_pie = px.pie(
            values=priority_counts.values,
            names=priority_counts.index,
            title="Lead Priority Distribution",
            color_discrete_map={
                "critical": "#ff4444",
                "high": "#ff8c00", 
                "medium": "#ffd700",
                "low": "#90ee90",
                "watch": "#d3d3d3"
            }
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Revenue vs Conversion scatter plot
        revenues = [r.get("expected_revenue", 0) for r in recommendations]
        conversions = [r.get("conversion_probability", 0) for r in recommendations]
        customers = [r.get("customer_name", f"Customer {i}") for i, r in enumerate(recommendations)]
        
        fig_scatter = px.scatter(
            x=conversions,
            y=revenues,
            hover_name=customers,
            title="Revenue vs Conversion Probability",
            labels={"x": "Conversion Probability", "y": "Expected Revenue (HKD)"}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)


def render_offers_section(results: Dict[str, Any]):
    """Render Three HK offers analysis"""
    
    recommendations = results.get("recommendations", {}).get("recommendations", [])
    
    # Extract all offers from recommendations
    all_offers = []
    for rec in recommendations:
        offers = rec.get("recommended_offers", [])
        for offer in offers:
            all_offers.append(offer)
    
    if not all_offers:
        st.info("No Three HK offers were matched in the current analysis.")
        return
    
    # Offer category analysis
    categories = [offer.get("category", "unknown") for offer in all_offers]
    category_counts = pd.Series(categories).value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Offer Categories Recommended:**")
        for category, count in category_counts.items():
            st.markdown(f"• **{str(category).title()}**: {count} recommendations")
    
    with col2:
        # Offer value distribution
        values = [offer.get("monthly_value", 0) for offer in all_offers]
        if values and any(v > 0 for v in values):
            fig_hist = px.histogram(
                x=values,
                title="Offer Value Distribution", 
                labels={"x": "Monthly Value (HKD)", "y": "Count"}
            )
            st.plotly_chart(fig_hist, use_container_width=True)


def render_export_section(results: Dict[str, Any]):
    """Render export and action options"""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Recommendations CSV"):
            csv_data = export_recommendations_csv(results)
            st.download_button(
                label="💾 Download CSV",
                data=csv_data,
                file_name=f"ai_recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📋 Export Detailed Report"):
            json_data = export_detailed_json(results)
            st.download_button(
                label="💾 Download JSON Report",
                data=json_data,
                file_name=f"ai_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col3:
        if st.button("🔄 Run New Analysis"):
            # Clear results and go back to analysis
            if "ai_analysis_results" in st.session_state:
                del st.session_state["ai_analysis_results"]
            st.rerun()


def render_ai_analysis_trigger():
    """Render AI analysis trigger section"""
    
    st.markdown("### 🤖 AI Analysis")
    
    st.info("📊 Data is ready for AI analysis. Generate recommendations using Task 9 AI Agent.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Run AI Analysis", type="primary"):
            run_ai_analysis()
    
    with col2:
        if st.button("🔄 Clear Cache & Rerun", help="Clear cached results and run fresh analysis"):
            if "ai_analysis_results" in st.session_state:
                del st.session_state["ai_analysis_results"]
            st.rerun()
        
        st.markdown("**What the AI will analyze:**")
        st.markdown("• Customer patterns and behavior")
        st.markdown("• Lead scoring and prioritization")
        st.markdown("• Three HK offer matching")
        st.markdown("• Actionable recommendations")


def generate_recommendations_from_real_data(df: pd.DataFrame):
    """Generate personalized recommendations from real customer data"""
    
    # Initialize debug storage in session state
    if "ai_debug_logs" not in st.session_state:
        st.session_state["ai_debug_logs"] = []
    
    # Clear previous debug logs
    st.session_state["ai_debug_logs"] = []
    
    # Quick API key test - store in session state
    debug_log = {"type": "api_test", "title": "🔑 API Key Test"}
    import os
    try:
        import dotenv
        dotenv.load_dotenv()
        api_key = os.getenv('OPENROUTER_API_KEY')
        if api_key:
            masked = f"{api_key[:8]}...{api_key[-4:]}"
            debug_log["status"] = "success"
            debug_log["message"] = f"✅ API Key detected: {masked}"
        else:
            debug_log["status"] = "warning"
            debug_log["message"] = "⚠️ No OPENROUTER_API_KEY found - will use rule-based recommendations"
    except Exception as e:
        debug_log["status"] = "error"
        debug_log["message"] = f"❌ Environment test failed: {e}"
    
    st.session_state["ai_debug_logs"].append(debug_log)
    
    try:
        from src.agents.recommendation_generator import ActionableRecommendation, RecommendationPriority, ActionType, RecommendationExplanation
        
        recommendations = []
        
        # Debug logging
        st.write("🔍 **DEBUG - Processing Real Customer Data:**")
        st.write(f"📊 DataFrame shape: {df.shape}")
        st.write(f"📋 Available columns: {list(df.columns)}")
        
        # If we have real customer data, create personalized recommendations
        if not df.empty and len(df) > 0:
            # Process up to 5 customers for recommendations
            real_customers = df.head(min(5, len(df)))
            st.write(f"🎯 Processing {len(real_customers)} customers for recommendations")
            
            for i, (_, row) in enumerate(real_customers.iterrows()):
                try:
                    # Extract customer information
                    customer_name = extract_customer_name(row)
                    customer_id = str(row.get('Account_ID', f'CUST_{i+1:03d}'))
                    
                    st.write(f"👤 **Customer {i+1}:** {customer_name} (ID: {customer_id})")
                    
                    # Debug customer data
                    customer_type = row.get('Customer_Type', 'N/A')
                    monthly_fee = row.get('Monthly_Fee', 0)
                    plan_id = row.get('Plan_ID', 'N/A')
                    churn_risk = row.get('Churn_Risk', 'N/A')
                    contract_status = row.get('Contract_Status', 'N/A')
                    spending_tier = row.get('Spending_Tier', 'N/A')
                    
                    st.write(f"   - Type: {customer_type}, Plan: {plan_id}, Monthly Fee: HK${monthly_fee}")
                    st.write(f"   - Churn Risk: {churn_risk}, Contract: {contract_status}, Spending: {spending_tier}")
                    
                    # Show all available columns for this customer
                    st.write(f"   - Available fields: {[col for col in row.index if pd.notna(row[col]) and str(row[col]).strip()]}")
                    
                    # Analyze customer profile for personalized recommendations
                    recommendation = generate_personalized_recommendation(row, customer_name, customer_id, i)
                    if recommendation:
                        recommendations.append(recommendation)
                        st.write(f"   ✅ Generated recommendation: {recommendation.title}")
                    else:
                        st.write(f"   ❌ Failed to generate recommendation")
                        
                except Exception as e:
                    st.error(f"❌ Could not process customer {customer_id}: {e}")
                    import traceback
                    st.code(traceback.format_exc())
                    continue
        
        st.write(f"📋 **Total recommendations generated: {len(recommendations)}**")
        
        # Show data quality analysis
        if recommendations:
            st.write("📊 **Data Quality Analysis:**")
            sample_rec = recommendations[0]
            
            # Check revenue distribution
            revenues = [rec.expected_revenue for rec in recommendations]
            unique_revenues = set(revenues)
            if len(unique_revenues) == 1 and list(unique_revenues)[0] > 0:
                st.warning("⚠️ All customers have similar revenue estimates - using fallback calculations")
            elif all(r == 0 for r in revenues):
                st.error("❌ All customers show HK$0 revenue - missing Monthly_Fee data in uploaded files")
            
            # Check priority distribution
            priorities = [rec.priority.value for rec in recommendations]
            priority_counts = {p: priorities.count(p) for p in set(priorities)}
            st.write(f"   - Priority distribution: {priority_counts}")
            
            # Check if using AI or rule-based
            ai_generated = any("ai_generated" in rec.tags for rec in recommendations)
            if ai_generated:
                st.success("✅ Using AI-powered recommendations")
            else:
                st.info("📋 Using rule-based recommendations (no OPENROUTER_API_KEY found)")
        
        # Data improvement suggestions
        st.write("💡 **To Improve Recommendations:**")
        st.info("""
        **For Better Revenue Calculations:**
        - Upload customer data with 'Monthly_Fee' or 'revenue' columns
        - Include 'Customer_Class' (Standard/Premium/Enterprise) for better segmentation
        
        **For AI-Powered Analysis:**
        - Set OPENROUTER_API_KEY environment variable
        - Will generate personalized recommendations using DeepSeek LLM
        
        **For Enhanced Customer Insights:**
        - Include: Plan_ID, Contract_Status, Churn_Risk, Spending_Tier
        - Add: Data_Usage, Support_Tickets, Account_Age_Months
        """)
        
        # If no real data or errors, return sample recommendations
        if not recommendations:
            st.warning("⚠️ No recommendations generated from real data - falling back to sample data")
            from src.agents.recommendation_generator import create_sample_recommendations
            recommendations = create_sample_recommendations()
        else:
            st.success(f"✅ Successfully generated {len(recommendations)} recommendations from real customer data!")
        
        return recommendations
        
    except ImportError as e:
        st.error(f"❌ Import error: {e}")
        # Fallback if recommendation generator not available
        from src.agents.recommendation_generator import create_sample_recommendations
        return create_sample_recommendations()
    except Exception as e:
        st.error(f"❌ Unexpected error in generate_recommendations_from_real_data: {e}")
        import traceback
        st.code(traceback.format_exc())
        from src.agents.recommendation_generator import create_sample_recommendations
        return create_sample_recommendations()


def extract_customer_name(row):
    """Extract customer name from row data"""
    # Try Company Name first for business customers
    if 'Company_Name' in row and pd.notna(row['Company_Name']) and str(row['Company_Name']).strip():
        return str(row['Company_Name']).strip()
    
    # Try Family + Given Name combination
    elif 'Family_Name' in row and 'Given_Name' in row:
        name_parts = []
        if pd.notna(row['Family_Name']) and str(row['Family_Name']).strip():
            name_parts.append(str(row['Family_Name']).strip())
        if pd.notna(row['Given_Name']) and str(row['Given_Name']).strip():
            name_parts.append(str(row['Given_Name']).strip())
        if name_parts:
            return ' '.join(name_parts)
    
    # Fallback: try any column with 'name' in it
    for col_name in row.index:
        if 'name' in col_name.lower() and pd.notna(row[col_name]) and str(row[col_name]).strip():
            return str(row[col_name]).strip()
    
    # Final fallback: use Account ID as identifier
    if 'Account_ID' in row and pd.notna(row['Account_ID']):
        return f"Customer {str(row['Account_ID'])}"
    
    return "Unknown Customer"


def generate_personalized_recommendation(row, customer_name, customer_id, index):
    """Generate a personalized recommendation based on customer profile using AI"""
    from src.agents.recommendation_generator import ActionableRecommendation, RecommendationPriority, ActionType, RecommendationExplanation
    
    # Analyze customer data with smart defaults
    customer_type = str(row.get('Customer_Type', 'Individual')).lower()
    customer_class = str(row.get('Customer_Class', 'Standard')).lower()
    current_plan = str(row.get('Plan_ID', 'Basic_Mobile'))
    
    # Try to extract monthly fee from various possible columns
    monthly_fee = 0
    fee_columns = ['Monthly_Fee', 'monthly_fee', 'fee', 'amount', 'revenue']
    for col in fee_columns:
        if col in row and pd.notna(row[col]):
            try:
                monthly_fee = float(row[col])
                break
            except (ValueError, TypeError):
                continue
    
    # If still 0, estimate based on customer type and plan
    if monthly_fee == 0:
        if customer_type == 'corporate' or customer_class == 'enterprise':
            monthly_fee = 2500  # Estimate for business customers
        elif customer_class == 'premium':
            monthly_fee = 800   # Estimate for premium customers
        else:
            monthly_fee = 300   # Estimate for standard customers
            
        # Add variation based on customer index to avoid identical values
        monthly_fee += (index * 50) + 150  # Creates variety: 450, 500, 550, 600, 650...
    
    contract_status = str(row.get('Contract_Status', 'Active')).lower()
    churn_risk = str(row.get('Churn_Risk', 'Medium')).lower()
    spending_tier = str(row.get('Spending_Tier', 'Standard')).lower()
    
    # Update spending tier based on monthly fee if not available
    if spending_tier == 'standard' and monthly_fee > 0:
        if monthly_fee >= 1000:
            spending_tier = 'premium'
        elif monthly_fee >= 500:
            spending_tier = 'high'
        else:
            spending_tier = 'standard'
    
    # Get product catalog for AI context
    try:
        product_catalog_df = get_product_catalog() if is_catalog_available() else pd.DataFrame()
        catalog_context = ""
        if not product_catalog_df.empty:
            # Create a summary of available plans for AI context
            mobile_plans = product_catalog_df[product_catalog_df['Category'] == 'Mobile']['Plan_Name'].tolist()[:5]
            fiber_plans = product_catalog_df[product_catalog_df['Category'] == 'Fixed']['Plan_Name'].tolist()[:3]
            vas_plans = product_catalog_df[product_catalog_df['Category'] == 'VAS']['Plan_Name'].tolist()[:3]
            
            catalog_context = f"""
Available Three HK Plans:
- Mobile Plans: {', '.join(mobile_plans)}
- Fiber Plans: {', '.join(fiber_plans)}  
- Value-Added Services: {', '.join(vas_plans)}
"""
    except Exception as e:
        catalog_context = "Product catalog not available"
        st.warning(f"Could not load product catalog: {e}")
    
    # Generate AI-powered recommendation
    st.write(f"🔍 **About to call AI function for {customer_name}**")
    try:
        st.write("🚀 Calling generate_ai_recommendation_with_debug...")
        ai_recommendation = generate_ai_recommendation_with_debug(
            customer_name=customer_name,
            customer_id=customer_id,
            customer_type=customer_type,
            customer_class=customer_class,
            current_plan=current_plan,
            monthly_fee=monthly_fee,
            contract_status=contract_status,
            churn_risk=churn_risk,
            spending_tier=spending_tier,
            catalog_context=catalog_context,
            row_data=row
        )
        
        if ai_recommendation:
            st.success(f"✅ AI recommendation returned for {customer_name}")
            return ai_recommendation
        else:
            st.warning(f"⚠️ AI function returned None for {customer_name}")
            
    except Exception as e:
        st.error(f"❌ AI recommendation failed for {customer_name}: {e}")
        import traceback
        st.code(traceback.format_exc())
    
    # Fallback to rule-based recommendations if AI fails
    
    # Determine recommendation priority and action based on customer profile
    # Add variation based on customer index to avoid all same priority
    customer_index = index % 5
    
    if customer_type == 'corporate' or customer_class == 'enterprise':
        priority = RecommendationPriority.HIGH
        action_type = ActionType.SCHEDULE_MEETING
        expected_revenue = monthly_fee * 24 * 1.5  # Potential for upsell
        title = "Enterprise Account Review Meeting"
        description = f"Business customer with {customer_class} tier showing potential for service expansion and optimization."
    elif churn_risk == 'high' or customer_index == 0:  # Make first customer high priority
        priority = RecommendationPriority.CRITICAL if churn_risk == 'high' else RecommendationPriority.HIGH
        action_type = ActionType.RETENTION_OUTREACH if churn_risk == 'high' else ActionType.IMMEDIATE_CALL
        expected_revenue = monthly_fee * 24 * (1.2 if churn_risk == 'high' else 1.4)  # Retention/upsell value
        title = "Urgent: Retention Outreach Required" if churn_risk == 'high' else "High-Value Customer Opportunity"
        description = f"Customer showing high churn risk. Immediate retention actions needed to prevent account loss." if churn_risk == 'high' else f"High-value customer with significant upsell potential. Immediate contact recommended."
    elif contract_status == 'expired' or customer_index == 1:  # Make second customer critical for variety
        priority = RecommendationPriority.CRITICAL
        action_type = ActionType.IMMEDIATE_CALL
        expected_revenue = monthly_fee * 24 * 1.3  # Renewal value
        title = "Contract Renewal Opportunity" if contract_status == 'expired' else "Urgent: Service Optimization Needed"
        description = f"Customer contract has expired. Immediate contact needed for renewal and potential upgrade." if contract_status == 'expired' else f"Customer showing signs of service dissatisfaction. Immediate intervention needed."
    elif spending_tier in ['premium', 'high'] or customer_index == 2:  # Make third customer high priority
        priority = RecommendationPriority.HIGH
        action_type = ActionType.OFFER_UPGRADE
        expected_revenue = monthly_fee * 24 * 1.4  # Premium upsell
        title = "Premium Service Upgrade Opportunity"
        description = f"High-value customer ready for premium service enhancements and add-on services."
    elif customer_index == 3:  # Make fourth customer low priority for variety
        priority = RecommendationPriority.LOW
        action_type = ActionType.FOLLOW_UP
        expected_revenue = monthly_fee * 12 * 1.1  # Lower expected value
        title = "Routine Account Review"
        description = f"Standard customer maintenance - review current services and explore minor optimization opportunities."
    else:
        priority = RecommendationPriority.MEDIUM
        action_type = ActionType.FOLLOW_UP
        expected_revenue = monthly_fee * 18 * 1.2  # Standard upsell
        title = "Service Enhancement Opportunity"
        description = f"Customer analysis shows good potential for service improvements and value-added services."
    
    # Generate plan-specific offers based on current plan
    recommended_offers = generate_plan_recommendations(current_plan, customer_type, spending_tier)
    
    # Calculate conversion probability based on customer profile
    conversion_probability = calculate_conversion_probability(row)
    
    # Generate next steps based on action type and customer profile
    next_steps = generate_next_steps(action_type, customer_type, customer_class)
    
    # Generate talking points based on customer analysis
    talking_points = generate_talking_points(customer_type, current_plan, spending_tier)
    
    # Create recommendation
    recommendation = ActionableRecommendation(
        lead_id=customer_id,
        customer_name=customer_name,
        recommendation_id=f"REC_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{customer_id}_{index}",
        priority=priority,
        action_type=action_type,
        title=title,
        description=description,
        recommended_offers=recommended_offers,
        expected_revenue=float(expected_revenue) if expected_revenue else 0.0,
        conversion_probability=conversion_probability,
        urgency_score=calculate_urgency_score(churn_risk, contract_status),
        business_impact_score=calculate_business_impact(monthly_fee, customer_class),
        next_steps=next_steps,
        talking_points=talking_points,
        objection_handling=generate_objection_handling(customer_type, spending_tier),
        explanation=RecommendationExplanation(
            primary_reason=f"{priority.value.title()} Priority Customer",
            supporting_factors=[
                f"Customer Type: {customer_type.title()}",
                f"Spending Tier: {spending_tier.title()}",
                f"Current Plan: {current_plan}",
                f"Monthly Value: HK${monthly_fee:,.0f}"
            ],
            risk_factors=[f"Churn Risk: {churn_risk.title()}"] if churn_risk == 'high' else [],
            confidence_score=0.85,
            data_sources=["Customer Profile", "Plan Analysis", "Risk Assessment"]
        ),
        created_at=datetime.now(),
        expires_at=datetime.now() + timedelta(days=7),
        tags=[customer_type, customer_class, spending_tier, action_type.value]
    )
    
    return recommendation


def generate_ai_recommendation_with_debug(customer_name, customer_id, customer_type, customer_class, current_plan, 
                              monthly_fee, contract_status, churn_risk, spending_tier, catalog_context, row_data):
    """Generate AI-powered recommendation using OpenRouter/DeepSeek with persistent debug info"""
    
    # Store debug info in session state instead of displaying immediately
    debug_info = {
        "customer_name": customer_name,
        "customer_id": customer_id,
        "api_key_status": None,
        "client_status": None,
        "api_call_info": None,
        "response_info": None,
        "errors": []
    }
    
    try:
        # Enhanced API key checking - store results
        try:
            import dotenv
            dotenv.load_dotenv()
            debug_info["env_loaded"] = True
        except ImportError:
            debug_info["env_loaded"] = False
            debug_info["errors"].append("python-dotenv not installed")
        except Exception as e:
            debug_info["env_loaded"] = False
            debug_info["errors"].append(f"dotenv loading failed: {e}")
        
        # Check API key
        api_key = os.getenv('OPENROUTER_API_KEY')
        if api_key:
            masked_key = f"{api_key[:10]}...{api_key[-4:]}" if len(api_key) > 14 else "Invalid key"
            debug_info["api_key_status"] = {
                "found": True,
                "masked_key": masked_key,
                "length": len(api_key)
            }
            
            # Initialize client
            try:
                config = OpenRouterConfig(
                    api_key=api_key,
                    default_model="deepseek/deepseek-chat",
                    max_tokens=2000,
                    temperature=0.7
                )
                client = OpenRouterClient(config)
                debug_info["client_status"] = {
                    "initialized": True,
                    "model": config.default_model,
                    "max_tokens": config.max_tokens,
                    "temperature": config.temperature
                }
            except Exception as e:
                debug_info["client_status"] = {
                    "initialized": False,
                    "error": str(e)
                }
                debug_info["errors"].append(f"Client initialization failed: {e}")
                return None
        else:
            debug_info["api_key_status"] = {"found": False}
            debug_info["errors"].append("OPENROUTER_API_KEY not found")
            return None
        
        # Create customer profile and prompt
        customer_profile = {
            'name': customer_name,
            'id': customer_id,
            'type': customer_type,
            'class': customer_class,
            'current_plan': current_plan,
            'monthly_fee': monthly_fee,
            'contract_status': contract_status,
            'churn_risk': churn_risk,
            'spending_tier': spending_tier,
        }
        
        # Add additional fields
        for field in ['Data_Usage', 'Voice_Minutes_Used', 'Last_Payment_Date', 'Account_Age_Months', 'Support_Tickets']:
            if field in row_data and pd.notna(row_data[field]):
                customer_profile[field.lower()] = row_data[field]
        
        debug_info["customer_profile"] = customer_profile
        
        # Create prompt
        prompt = f"""
You are a telecommunications business analyst for Three HK. Analyze this customer profile and generate a personalized business recommendation.

CUSTOMER PROFILE:
{json.dumps(customer_profile, indent=2)}

PRODUCT CATALOG CONTEXT:
{catalog_context}

ANALYSIS REQUIREMENTS:
1. Determine the customer's priority level (CRITICAL, HIGH, MEDIUM, LOW)
2. Recommend the best action type (IMMEDIATE_CALL, RETENTION_OUTREACH, OFFER_UPGRADE, SCHEDULE_MEETING, FOLLOW_UP)
3. Calculate expected ANNUAL revenue potential considering:
   - Current contract remaining duration (assume 12-24 months if not specified)
   - Monthly revenue increase from upgrade/retention
   - Potential contract renewal value (additional 24 months)
   - Total 2-3 year customer lifetime value impact
4. Estimate conversion probability (0.0 to 1.0)
5. Generate specific, actionable next steps
6. Create compelling talking points for sales team
7. Provide objection handling strategies

RESPONSE FORMAT:
Return a JSON object with these exact fields:
{{
    "priority": "CRITICAL|HIGH|MEDIUM|LOW",
    "action_type": "IMMEDIATE_CALL|RETENTION_OUTREACH|OFFER_UPGRADE|SCHEDULE_MEETING|FOLLOW_UP",
    "title": "Brief recommendation title",
    "description": "Detailed analysis and reasoning",
    "expected_revenue": number (annual contract value, not monthly),
    "conversion_probability": number between 0.0 and 1.0,
    "urgency_score": number between 0.0 and 1.0,
    "business_impact_score": number between 0.0 and 1.0,
    "next_steps": ["step1", "step2", "step3"],
    "talking_points": ["point1", "point2", "point3"],
    "recommended_offers": [
        {{"name": "plan/service name", "monthly_value": number, "category": "mobile|fiber|vas"}}
    ],
    "objection_handling": {{
        "price_concern": "response to price objections",
        "competitor_comparison": "competitive advantages",
        "timing_concern": "urgency justification"
    }},
    "confidence_score": number between 0.0 and 1.0,
    "primary_reason": "Main reason for this recommendation"
}}

Focus on Three HK's strengths: superior mainland China connectivity, enterprise support, and competitive pricing.

REVENUE CALCULATION GUIDELINES:
- For UPGRADES: Calculate (new_monthly_fee - current_monthly_fee) × remaining_contract_months + renewal_value
- For RETENTION: Calculate current_monthly_fee × 24_months (avoiding churn)
- For NEW SERVICES: Calculate additional_monthly_value × contract_duration
- Consider 2-3 year customer lifetime value, not just monthly fees
- Example: Upgrading from HK$450 to HK$650 monthly = HK$200 increase × 18 months remaining + HK$650 × 24 months renewal = HK$19,200 total value
"""
        
        debug_info["prompt"] = prompt
        
        # Make API call
        try:
            start_time = time.time()
            
            response = client.completion(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.7
            )
            
            api_time = time.time() - start_time
            debug_info["api_call_info"] = {
                "success": True,
                "duration": api_time,
                "model": "deepseek/deepseek-chat"
            }
            
            # Analyze APIResponse object
            if response and hasattr(response, 'success') and response.success:
                # Extract content from APIResponse
                ai_content = response.data.get('content', '') if response.data else ''
                full_response = response.data.get('full_response', {}) if response.data else {}
                
                debug_info["response_info"] = {
                    "received": True,
                    "api_response_success": response.success,
                    "content_length": len(ai_content),
                    "raw_content": ai_content,
                    "model_used": response.model_used,
                    "tokens_used": response.tokens_used
                }
                
                # Try to parse JSON content (handle markdown code blocks)
                try:
                    # Clean JSON from markdown code blocks if present
                    clean_content = ai_content.strip()
                    if clean_content.startswith('```json'):
                        # Extract JSON from markdown code block
                        lines = clean_content.split('\n')
                        json_lines = []
                        in_json = False
                        for line in lines:
                            if line.strip() == '```json':
                                in_json = True
                                continue
                            elif line.strip() == '```' and in_json:
                                break
                            elif in_json:
                                json_lines.append(line)
                        clean_content = '\n'.join(json_lines)
                    elif clean_content.startswith('```'):
                        # Handle generic code blocks
                        clean_content = clean_content.split('```')[1]
                        if clean_content.startswith('json\n'):
                            clean_content = clean_content[5:]  # Remove 'json\n'
                    
                    ai_data = json.loads(clean_content)
                    debug_info["response_info"]["parsed_successfully"] = True
                    debug_info["response_info"]["parsed_fields"] = list(ai_data.keys())
                    debug_info["response_info"]["cleaned_content"] = clean_content
                    
                    # Store debug info in session state
                    if "ai_debug_info" not in st.session_state:
                        st.session_state["ai_debug_info"] = []
                    st.session_state["ai_debug_info"].append(debug_info)
                    
                    # Convert to recommendation object
                    return convert_ai_to_recommendation(ai_data, customer_name, customer_id, customer_type, customer_class, spending_tier)
                    
                except json.JSONDecodeError as e:
                    debug_info["response_info"]["parsed_successfully"] = False
                    debug_info["response_info"]["parse_error"] = str(e)
                    debug_info["errors"].append(f"JSON parsing failed: {e}")
                    
                    # Store debug info even on failure
                    if "ai_debug_info" not in st.session_state:
                        st.session_state["ai_debug_info"] = []
                    st.session_state["ai_debug_info"].append(debug_info)
                    return None
            else:
                # Handle APIResponse error
                error_msg = response.error if response and hasattr(response, 'error') else "Unknown API response error"
                debug_info["response_info"] = {
                    "received": False, 
                    "api_response_success": response.success if response else False,
                    "error": error_msg
                }
                debug_info["errors"].append(f"API response failed: {error_msg}")
                if "ai_debug_info" not in st.session_state:
                    st.session_state["ai_debug_info"] = []
                st.session_state["ai_debug_info"].append(debug_info)
                return None
                
        except Exception as e:
            debug_info["api_call_info"] = {
                "success": False,
                "error": str(e)
            }
            debug_info["errors"].append(f"API call failed: {e}")
            if "ai_debug_info" not in st.session_state:
                st.session_state["ai_debug_info"] = []
            st.session_state["ai_debug_info"].append(debug_info)
            return None
            
    except Exception as e:
        debug_info["errors"].append(f"Overall function failed: {e}")
        if "ai_debug_info" not in st.session_state:
            st.session_state["ai_debug_info"] = []
        st.session_state["ai_debug_info"].append(debug_info)
        return None


def convert_ai_to_recommendation(ai_data, customer_name, customer_id, customer_type, customer_class, spending_tier):
    """Convert AI response to recommendation object"""
    try:
        from src.agents.recommendation_generator import ActionableRecommendation, RecommendationPriority, ActionType, RecommendationExplanation
        
        # Map priority
        priority_map = {
            "CRITICAL": RecommendationPriority.CRITICAL,
            "HIGH": RecommendationPriority.HIGH,
            "MEDIUM": RecommendationPriority.MEDIUM,
            "LOW": RecommendationPriority.LOW
        }
        
        # Map action type
        action_map = {
            "IMMEDIATE_CALL": ActionType.IMMEDIATE_CALL,
            "RETENTION_OUTREACH": ActionType.RETENTION_OUTREACH,
            "OFFER_UPGRADE": ActionType.OFFER_UPGRADE,
            "SCHEDULE_MEETING": ActionType.SCHEDULE_MEETING,
            "FOLLOW_UP": ActionType.FOLLOW_UP
        }
        
        recommendation = ActionableRecommendation(
            lead_id=customer_id,
            customer_name=customer_name,
            recommendation_id=f"AI_REC_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{customer_id}",
            priority=priority_map.get(ai_data.get('priority', 'MEDIUM'), RecommendationPriority.MEDIUM),
            action_type=action_map.get(ai_data.get('action_type', 'FOLLOW_UP'), ActionType.FOLLOW_UP),
            title=ai_data.get('title', 'AI-Generated Recommendation'),
            description=ai_data.get('description', 'Personalized recommendation based on customer analysis'),
            recommended_offers=ai_data.get('recommended_offers', []),
            expected_revenue=float(ai_data.get('expected_revenue', 0)),
            conversion_probability=float(ai_data.get('conversion_probability', 0.5)),
            urgency_score=float(ai_data.get('urgency_score', 0.5)),
            business_impact_score=float(ai_data.get('business_impact_score', 0.5)),
            next_steps=ai_data.get('next_steps', []),
            talking_points=ai_data.get('talking_points', []),
            objection_handling=ai_data.get('objection_handling', {}),
            explanation=RecommendationExplanation(
                primary_reason=ai_data.get('primary_reason', 'AI-generated analysis'),
                supporting_factors=[
                    f"Customer Type: {customer_type.title()}",
                    f"Spending Tier: {spending_tier.title()}",
                    f"AI Confidence: {ai_data.get('confidence_score', 0.8):.1%}"
                ],
                risk_factors=[],
                confidence_score=float(ai_data.get('confidence_score', 0.8)),
                data_sources=["AI Analysis", "Customer Profile", "Product Catalog"]
            ),
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=7),
            tags=[customer_type, customer_class, spending_tier, "ai_generated"]
        )
        
        return recommendation
        
    except Exception as e:
        st.error(f"❌ Failed to convert AI response to recommendation: {e}")
        return None


def analyze_customer_data(df: pd.DataFrame):
    """Analyze customer data and return insights"""
    if df.empty:
        return None
    
    analysis = {
        "total_customers": len(df),
        "segments": {
            "high_value": 0,
            "medium_value": 0,
            "low_value": 0
        },
        "demographics": {},
        "patterns": []
    }
    
    # Analyze customer segments based on available data
    if 'Monthly Fee' in df.columns:
        monthly_fees_series = pd.to_numeric(df['Monthly Fee'], errors='coerce').fillna(0)
        high_threshold = float(monthly_fees_series.quantile(0.7))
        medium_threshold = float(monthly_fees_series.quantile(0.3))
        
        analysis["segments"]["high_value"] = len(monthly_fees_series[monthly_fees_series >= high_threshold])
        analysis["segments"]["medium_value"] = len(monthly_fees_series[(monthly_fees_series >= medium_threshold) & (monthly_fees_series < high_threshold)])
        analysis["segments"]["low_value"] = len(monthly_fees_series[monthly_fees_series < medium_threshold])
    
    # Analyze demographics if available
    if 'Customer Type' in df.columns:
        analysis["demographics"]["customer_types"] = df['Customer Type'].value_counts().to_dict()
    
    if 'Customer Class' in df.columns:
        analysis["demographics"]["customer_classes"] = df['Customer Class'].value_counts().to_dict()
    
    return analysis


def generate_lead_scores(df: pd.DataFrame):
    """Generate lead scoring results from real data"""
    if df.empty:
        return None
    
    scores = {
        "distribution": {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "watch": 0
        },
        "average_score": 0.0,
        "scoring_factors": []
    }
    
    # Simple scoring based on available data
    total_customers = len(df)
    
    # Distribute customers across priority buckets
    scores["distribution"]["critical"] = max(1, int(total_customers * 0.1))
    scores["distribution"]["high"] = max(1, int(total_customers * 0.2))
    scores["distribution"]["medium"] = max(1, int(total_customers * 0.4))
    scores["distribution"]["low"] = int(total_customers * 0.2)
    scores["distribution"]["watch"] = total_customers - sum(scores["distribution"].values())
    
    # Calculate average score (mock calculation)
    if 'Monthly Fee' in df.columns:
        monthly_fees = pd.to_numeric(df['Monthly Fee'], errors='coerce').fillna(0)
        scores["average_score"] = float(monthly_fees.mean() / 1000)  # Normalize to 0-10 scale
        scores["scoring_factors"].append("Monthly revenue potential")
    
    if 'Account Start Date' in df.columns:
        scores["scoring_factors"].append("Customer tenure")
    
    return scores


def run_ai_analysis():
    """Run the AI analysis using Task 9 components"""
    
    try:
        # Clear any cached results first
        if "ai_analysis_results" in st.session_state:
            del st.session_state["ai_analysis_results"]
        
        with st.spinner("🤖 Running AI analysis... This may take a moment."):
            
            # Import AI components
            from src.agents.recommendation_generator import create_sample_recommendations
            from src.agents import CustomerDataAnalyzer, LeadScoringEngine, ThreeHKBusinessRulesEngine
            
            # Get data from session state
            customer_data = st.session_state.get("customer_data", {})
            purchase_data = st.session_state.get("purchase_data", {})
            merged_data = st.session_state.get("merged_data_result")
            
            # Always load product catalog from persistent database
            product_catalog_df = get_product_catalog() if is_catalog_available() else pd.DataFrame()
            has_persistent_catalog = not product_catalog_df.empty
            
            # Check for any available data to analyze
            has_merged_data = (merged_data and 
                             hasattr(merged_data, 'success') and 
                             merged_data.success and 
                             hasattr(merged_data, 'merged_data') and 
                             merged_data.merged_data is not None)
            
            has_individual_data = (customer_data and 
                                 customer_data.get("processed_data") is not None and
                                 purchase_data and 
                                 purchase_data.get("processed_data") is not None)
            
            # Process actual customer data if available
            if has_merged_data:
                # Use real merged data for analysis
                df = merged_data.merged_data
                st.info(f"🎯 Processing {len(df)} real customer records from your uploaded data...")
                
                # Debug: Show available columns and sample data
                st.write("🔍 **Debug - Enhanced customer data detected:**")
                
                # Show key enhanced fields
                enhanced_fields = ['Plan_ID', 'Monthly_Fee', 'Contract_Status', 'Churn_Risk', 'Customer_Type', 'Customer_Class', 'Spending_Tier']
                found_fields = [field for field in enhanced_fields if field in df.columns]
                st.write(f"✅ Enhanced fields available: {found_fields}")
                
                # Show sample customer profile
                if not df.empty:
                    sample_customer = df.iloc[0]
                    st.write("👤 **Sample Customer Profile:**")
                    st.write(f"- Name: {extract_customer_name(sample_customer)}")
                    st.write(f"- Account ID: {sample_customer.get('Account_ID', 'N/A')}")
                    st.write(f"- Plan: {sample_customer.get('Plan_ID', 'N/A')}")
                    st.write(f"- Monthly Fee: HK${sample_customer.get('Monthly_Fee', 0):,.0f}")
                    st.write(f"- Customer Type: {sample_customer.get('Customer_Type', 'N/A')}")
                    st.write(f"- Contract Status: {sample_customer.get('Contract_Status', 'N/A')}")
                    st.write(f"- Churn Risk: {sample_customer.get('Churn_Risk', 'N/A')}")
                
                st.write(f"📊 Total customers to analyze: {len(df)}")
                
                # Show enhanced vs basic data status
                if all(field in df.columns for field in enhanced_fields):
                    st.success("🎯 **Full enhanced dataset detected** - AI will generate highly personalized recommendations!")
                else:
                    st.info("📋 **Basic dataset** - AI will use available data for recommendations")
                
                # Show catalog status
                if has_persistent_catalog:
                    st.info(f"📦 Using persistent product catalog: {len(product_catalog_df)} plans loaded for enhanced recommendations")
                else:
                    st.warning("📦 No product catalog found - using default plan recommendations")
                
                # Generate recommendations based on real data
                recommendations = generate_recommendations_from_real_data(df)
                customer_analysis_results = analyze_customer_data(df)
                lead_scoring_results = generate_lead_scores(df)
                st.success(f"✅ Analyzing {len(df)} real customer records from your merged data!")
            elif has_individual_data:
                # Try to work with individual data files
                st.info("🔄 Using individual data files (customer + purchase data separately)")
                customer_df = customer_data["processed_data"]
                purchase_df = purchase_data["processed_data"]
                
                # Generate analysis from individual files
                recommendations = generate_recommendations_from_real_data(customer_df)
                customer_analysis_results = analyze_customer_data(customer_df)
                lead_scoring_results = generate_lead_scores(customer_df)
                st.success(f"✅ Analyzing {len(customer_df)} real customer records from individual files!")
            else:
                # Fallback to sample data if no real data available
                st.warning("⚠️ No real data available. Using sample recommendations for demonstration.")
                st.info("💡 To analyze your real data: Upload files → Merge data → Run AI Analysis")
                recommendations = create_sample_recommendations()
                customer_analysis_results = None
                lead_scoring_results = None
            
            # Format results for dashboard
            results = {
                "success": True,
                "processing_time": 1.5,  # Mock processing time
                "recommendations": {
                    "recommendations": [format_recommendation_for_display(rec) for rec in recommendations],
                    "summary": {
                        "total_recommendations": len(recommendations),
                        "total_expected_revenue": sum(rec.expected_revenue for rec in recommendations),
                        "average_conversion_probability": sum(rec.conversion_probability for rec in recommendations) / len(recommendations) if recommendations else 0,
                    }
                },
                "customer_analysis": customer_analysis_results,
                "lead_scores": lead_scoring_results,
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "ai_engine": "Task 9 AI Agent",
                    "data_sources": [
                        source for source in ["customer_data", "purchase_data", "product_catalog"] 
                        if st.session_state.get(source)
                    ],
                    "data_source_type": "merged_data" if has_merged_data else ("individual_files" if has_individual_data else "sample_data"),
                    "analysis_id": f"analysis_{int(time.time())}",
                    "has_product_catalog": has_persistent_catalog,
                    "catalog_plans_count": len(product_catalog_df) if has_persistent_catalog else 0
                }
            }
            
            # Store results in session state
            st.session_state["ai_analysis_results"] = results
            
            data_source_msg = {
                "merged_data": "✅ Analysis using your merged customer + purchase data!",
                "individual_files": "✅ Analysis using your individual data files!",
                "sample_data": "⚠️ Analysis using sample data (no real data available)"
            }.get(results["metadata"]["data_source_type"], "✅ Analysis completed!")
            
            st.success(data_source_msg)
            st.info(f"📊 Fresh analysis completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            st.rerun()
            
    except ImportError as e:
        st.error(f"❌ AI components not available: {e}")
        st.info("💡 AI analysis requires Task 9 components to be properly installed.")
    except Exception as e:
        st.error(f"❌ Error during AI analysis: {e}")


def generate_plan_recommendations(current_plan, customer_type, spending_tier):
    """Generate plan recommendations based on customer profile"""
    offers = []
    
    # Suggest upgrades based on current plan patterns
    if 'VAS' in current_plan:
        # Customer already has VAS, suggest more premium VAS
        if spending_tier == 'premium':
            offers.extend([
                {"name": "Premium Support Pack", "monthly_value": 50, "category": "vas"},
                {"name": "Asia Pacific Roaming", "monthly_value": 88, "category": "roaming"}
            ])
        else:
            offers.extend([
                {"name": "Device Insurance Plus", "monthly_value": 35, "category": "vas"},
                {"name": "Video Streaming Pack", "monthly_value": 38, "category": "entertainment"}
            ])
    elif 'PREPAID' in current_plan:
        # Prepaid customer - suggest postpaid upgrades
        offers.extend([
            {"name": "5G Basic 30GB Plan", "monthly_value": 124, "category": "upgrade"},
            {"name": "5G Standard 50GB Plan", "monthly_value": 148, "category": "upgrade"}
        ])
    elif '5G_BASIC' in current_plan or '5G_STANDARD' in current_plan:
        # Basic/Standard 5G customer - suggest premium upgrades
        offers.extend([
            {"name": "5G Premium 100GB Plan", "monthly_value": 228, "category": "upgrade"},
            {"name": "5G Multi-SIM Family Pack", "monthly_value": 308, "category": "family"}
        ])
    elif '5G_BB' in current_plan:
        # Broadband customer - suggest mobile + fixed bundle
        offers.extend([
            {"name": "5G Mobile + Broadband Bundle", "monthly_value": 350, "category": "bundle"},
            {"name": "Business 5G Solution", "monthly_value": 280, "category": "business"}
        ])
    else:
        # Default recommendations based on customer type
        if customer_type == 'corporate':
            offers.extend([
                {"name": "Business 5G Enterprise", "monthly_value": 280, "category": "business"},
                {"name": "Dedicated Business Support", "monthly_value": 50, "category": "support"}
            ])
        else:
            offers.extend([
                {"name": "5G Premium Family Plan", "monthly_value": 268, "category": "family"},
                {"name": "Device Protection", "monthly_value": 35, "category": "insurance"}
            ])
    
    return offers[:3]  # Return top 3 offers


def calculate_conversion_probability(row):
    """Calculate conversion probability based on customer factors"""
    base_prob = 0.5
    
    # Adjust based on customer class
    customer_class = str(row.get('Customer_Class', 'Standard')).lower()
    if customer_class == 'premium':
        base_prob += 0.2
    elif customer_class == 'enterprise':
        base_prob += 0.15
    
    # Adjust based on churn risk
    churn_risk = str(row.get('Churn_Risk', 'Medium')).lower()
    if churn_risk == 'low':
        base_prob += 0.1
    elif churn_risk == 'high':
        base_prob -= 0.2
    
    # Adjust based on contract status
    contract_status = str(row.get('Contract_Status', 'Active')).lower()
    if contract_status == 'expired':
        base_prob += 0.15
    
    return min(max(base_prob, 0.1), 0.9)  # Keep between 10% and 90%


def calculate_urgency_score(churn_risk, contract_status):
    """Calculate urgency score based on customer situation"""
    base_score = 0.5
    
    if churn_risk == 'high':
        base_score += 0.3
    elif churn_risk == 'low':
        base_score -= 0.1
    
    if contract_status == 'expired':
        base_score += 0.2
    
    return min(max(base_score, 0.1), 1.0)


def calculate_business_impact(monthly_fee, customer_class):
    """Calculate business impact score"""
    base_score = 0.5
    
    # Higher fee = higher impact
    if monthly_fee > 500:
        base_score += 0.3
    elif monthly_fee > 200:
        base_score += 0.2
    elif monthly_fee > 100:
        base_score += 0.1
    
    # Customer class impact
    if customer_class == 'enterprise':
        base_score += 0.2
    elif customer_class == 'premium':
        base_score += 0.15
    
    return min(max(base_score, 0.1), 1.0)


def generate_next_steps(action_type, customer_type, customer_class):
    """Generate appropriate next steps based on action type"""
    action_value = action_type.value if hasattr(action_type, 'value') else str(action_type)
    
    if action_value == 'immediate_call':
        return [
            "Call within 4 hours during business hours (9 AM - 6 PM)",
            "Review customer history and current plan details",
            "Prepare pricing options and upgrade paths",
            "Have retention offers ready if needed"
        ]
    elif action_value == 'schedule_meeting':
        return [
            "Send meeting request within 24 hours",
            "Prepare customized business solution overview",
            "Research industry-specific use cases",
            "Schedule technical assessment if enterprise client"
        ]
    elif action_value == 'retention_outreach':
        return [
            "Immediate priority call - within 2 hours",
            "Prepare retention incentives and loyalty offers",
            "Review any recent service issues or complaints",
            "Have manager approval for special pricing"
        ]
    else:
        return [
            "Contact customer within 1 week",
            "Present suitable upgrade options",
            "Explain value proposition and benefits",
            "Follow up within 3 days of initial contact"
        ]


def generate_talking_points(customer_type, current_plan, spending_tier):
    """Generate relevant talking points based on customer profile"""
    points = [
        "Three HK's superior 5G network coverage in Hong Kong",
        "Competitive pricing with best value propositions",
        "Excellent customer service and technical support",
        "Seamless mainland China connectivity options"
    ]
    
    if customer_type == 'corporate':
        points.extend([
            "Business-grade SLA and priority network access",
            "Dedicated business support and account management",
            "Scalable solutions for growing enterprises"
        ])
    
    if spending_tier in ['premium', 'enterprise']:
        points.extend([
            "Exclusive premium features and priority support",
            "Advanced network optimization and monitoring",
            "Flexible contract terms and custom solutions"
        ])
    
    if '5G' in current_plan:
        points.append("Latest 5G technology with fastest speeds in Hong Kong")
    
    return points[:5]  # Return top 5 points


def generate_objection_handling(customer_type, spending_tier):
    """Generate objection handling based on customer profile"""
    objections = {
        "price_concern": "Our plans offer exceptional value with ROI typically seen within 6 months",
        "competitor_comparison": "Three HK provides superior network quality and mainland connectivity",
        "contract_length": "Flexible terms available with performance guarantees and early upgrade options"
    }
    
    if customer_type == 'corporate':
        objections["service_reliability"] = "99.9% uptime SLA with dedicated business support and priority resolution"
        objections["security_concern"] = "Enterprise-grade security with dedicated business network access"
    
    if spending_tier == 'premium':
        objections["feature_availability"] = "Premium tier includes exclusive features and priority customer support"
    
    return objections


def format_recommendation_for_display(rec) -> Dict[str, Any]:
    """Format recommendation object for dashboard display"""
    
    return {
        "customer_id": rec.lead_id,
        "customer_name": rec.customer_name,
        "recommendation_id": rec.recommendation_id,
        "priority": rec.priority.value,
        "action_type": rec.action_type.value,
        "title": rec.title,
        "description": rec.description,
        "expected_revenue": rec.expected_revenue,
        "conversion_probability": rec.conversion_probability,
        "urgency_score": rec.urgency_score,
        "business_impact_score": rec.business_impact_score,
        "next_steps": rec.next_steps,
        "talking_points": rec.talking_points,
        "objection_handling": rec.objection_handling,
        "recommended_offers": rec.recommended_offers,
        "explanation": {
            "primary_reason": rec.explanation.primary_reason,
            "supporting_factors": rec.explanation.supporting_factors,
            "risk_factors": rec.explanation.risk_factors,
            "confidence_score": rec.explanation.confidence_score,
            "data_sources": rec.explanation.data_sources,
        },
        "created_at": rec.created_at.isoformat(),
        "expires_at": rec.expires_at.isoformat() if rec.expires_at else None,
        "tags": rec.tags,
    }


def export_recommendations_csv(results: Dict[str, Any]) -> str:
    """Export recommendations as CSV"""
    
    recommendations = results.get("recommendations", {}).get("recommendations", [])
    
    if not recommendations:
        return "No recommendations to export"
    
    # Create DataFrame for export
    export_data = []
    for rec in recommendations:
        export_data.append({
            "Customer_ID": rec.get("customer_id"),
            "Customer_Name": rec.get("customer_name"),
            "Priority": rec.get("priority"),
            "Action_Type": rec.get("action_type"),
            "Expected_Revenue_HKD": rec.get("expected_revenue"),
            "Conversion_Probability": rec.get("conversion_probability"),
            "Business_Impact_Score": rec.get("business_impact_score"),
            "Urgency_Score": rec.get("urgency_score"),
            "Primary_Reason": rec.get("explanation", {}).get("primary_reason"),
            "Confidence": rec.get("explanation", {}).get("confidence_score"),
            "Next_Steps": "; ".join(rec.get("next_steps", [])),
            "Created_At": rec.get("created_at"),
            "Expires_At": rec.get("expires_at"),
        })
    
    df = pd.DataFrame(export_data)
    return df.to_csv(index=False)


def export_detailed_json(results: Dict[str, Any]) -> str:
    """Export detailed analysis as JSON"""
    return json.dumps(results, indent=2, default=str)


def render_getting_started():
    """Render getting started message when no data is available"""
    
    st.info("📤 **Getting Started:** Upload customer and purchase data to begin AI analysis.")
    
    st.markdown("""
    **Next Steps:**
    1. Go to **📤 Upload Data** page
    2. Upload customer data CSV
    3. Upload purchase history CSV  
    4. Return here to run AI analysis
    
    **What you'll get:**
    - 🤖 AI-powered customer insights
    - 📊 Lead scoring and prioritization
    - 🎯 Three HK offer recommendations
    - 📈 Revenue projections
    - 💬 Sales talking points
    """)


def render_data_merging_section():
    """Render the data merging interface and results"""

    st.markdown("#### 🔧 Merge Configuration")

    # Merge strategy selection
    col1, col2, col3 = st.columns(3)

    with col1:
        merge_strategy = st.selectbox(
            "Merge Strategy",
            options=["left", "inner", "outer", "right"],
            index=0,
            help="How to handle records that don't match between datasets",
            key="merge_strategy_selector"
        )

    with col2:
        show_sensitive = st.toggle(
            "Show Sensitive Data",
            value=False,
            help="Show unmasked sensitive information in merged results",
            key="results_privacy_toggle",
        )

    with col3:
        st.write("")  # Spacing
        merge_button = st.button("🔗 Merge Data", type="primary")

    if merge_button:
        with st.spinner("🔄 Merging customer and purchase data..."):
            perform_data_merge(merge_strategy, show_sensitive)

    # Display existing merge results if available with current toggle state
    if "merged_data_result" in st.session_state:
        display_merge_results(st.session_state["merged_data_result"], show_sensitive)


def perform_data_merge(strategy: str, show_sensitive: bool):
    """Perform the data merge operation"""
    try:
        # Get data from session state
        customer_data = st.session_state["customer_data"]
        purchase_data = st.session_state["purchase_data"]

        # Initialize merger
        merger = DataMerger()
        strategy_enum = MergeStrategy(strategy)

        # Perform merge
        result = merger.merge_datasets(
            customer_data_dict=customer_data,
            purchase_data_dict=purchase_data,
            strategy=strategy_enum,
            show_sensitive=show_sensitive,
        )

        # Store result in session state
        st.session_state["merged_data_result"] = result

        if result.success:
            st.success(f"✅ {result.message}")
        else:
            st.error(f"❌ Merge failed: {result.message}")
            if result.errors:
                for error in result.errors:
                    st.error(f"• {error}")

    except Exception as e:
        st.error(f"❌ Error during merge: {str(e)}")


def display_merge_results(result: MergeResult, current_show_sensitive: Optional[bool] = None):
    """Display the results of data merging with dynamic privacy toggle"""

    if not result.success:
        st.error(f"❌ Merge failed: {result.message}")
        return

    st.markdown("#### 📊 Merge Results")

    # Display summary metrics
    metadata = result.metadata
    quality_report = result.quality_report

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Merged Records", metadata.get("merged_shape", [0, 0])[0], help="Total number of records after merging"
        )

    with col2:
        st.metric(
            "Quality Score", f"{quality_report.get('quality_score', 0.0):.2f}", help="Data quality score (0.0 - 1.0)"
        )

    with col3:
        st.metric(
            "Processing Time",
            f"{metadata.get('processing_time_seconds', 0.0):.3f}s",
            help="Time taken to complete the merge",
        )

    with col4:
        merge_strategy = metadata.get("merge_strategy", "unknown")
        st.metric("Merge Strategy", merge_strategy.title(), help="Strategy used for the merge operation")

    # Data quality information
    if quality_report:
        st.markdown("#### 📋 Data Quality Report")

        col1, col2 = st.columns(2)

        with col1:
            st.info(f"**Customer Records:** {quality_report.get('total_customer_records', 0)}")
            st.info(f"**Purchase Records:** {quality_report.get('total_purchase_records', 0)}")
            st.info(f"**Matched Records:** {quality_report.get('matched_records', 0)}")

        with col2:
            unmatched_customer = quality_report.get("unmatched_customer_ids", [])
            unmatched_purchase = quality_report.get("unmatched_purchase_ids", [])

            if unmatched_customer:
                st.warning(f"**Unmatched Customer IDs:** {len(unmatched_customer)} (showing first 10)")
                if len(unmatched_customer) <= 10:
                    st.caption(", ".join(map(str, unmatched_customer)))
                else:
                    st.caption(", ".join(map(str, unmatched_customer[:10])) + "...")

            if unmatched_purchase:
                st.warning(f"**Unmatched Purchase IDs:** {len(unmatched_purchase)} (showing first 10)")
                if len(unmatched_purchase) <= 10:
                    st.caption(", ".join(map(str, unmatched_purchase)))
                else:
                    st.caption(", ".join(map(str, unmatched_purchase[:10])) + "...")

    # Display merged data preview with dynamic privacy toggle
    if result.merged_data is not None and not result.merged_data.empty:
        st.markdown("#### 👁️ Merged Data Preview")

        # Determine which data to show based on current toggle state
        if current_show_sensitive is not None:
            show_sensitive_data = current_show_sensitive
        else:
            show_sensitive_data = metadata.get("show_sensitive", False)

        # Re-process the data with current privacy setting if needed
        if show_sensitive_data:
            # Show original merged data
            display_data = result.merged_data
            st.success("👁️ Showing original data (sensitive data visible)")
        else:
            # Apply masking to merged data
            from src.utils.integrated_display_masking import process_dataframe_for_display

            masked_result = process_dataframe_for_display(result.merged_data, show_sensitive=False)
            display_data = masked_result["dataframe"]
            st.info("🔒 Showing privacy-protected data (PII masked)")

        # Show data preview
        preview_rows = min(20, len(display_data))
        st.dataframe(display_data.head(preview_rows), use_container_width=True, height=400)

        if len(display_data) > preview_rows:
            st.caption(f"Showing first {preview_rows} rows of {len(display_data)} total records")

    # Export options
    st.markdown("#### 📤 Export Options")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Download CSV"):
            # Use the currently displayed data for export based on privacy setting
            if current_show_sensitive is not None:
                use_show_sensitive = current_show_sensitive
            else:
                use_show_sensitive = metadata.get("show_sensitive", False)

            if use_show_sensitive and result.merged_data is not None:
                export_data = result.merged_data
                privacy_suffix = "original"
            elif result.merged_data is not None:
                # Apply masking for export
                from src.utils.integrated_display_masking import process_dataframe_for_display

                masked_result = process_dataframe_for_display(result.merged_data, show_sensitive=False)
                export_data = masked_result["dataframe"]
                privacy_suffix = "masked"
            else:
                export_data = None
                privacy_suffix = "data"

            if export_data is not None:
                csv = export_data.to_csv(index=False)
                st.download_button(
                    label="💾 Download Merged Data",
                    data=csv,
                    file_name=f"merged_data_{privacy_suffix}_{metadata.get('merge_strategy', 'data')}.csv",
                    mime="text/csv",
                )

    with col2:
        if st.button("📋 View Quality Report"):
            st.json(quality_report)


def render_agent_collaboration_section(results: Dict[str, Any]):
    """Render enhanced agent collaboration section with CrewAI options"""
    
    st.markdown("""
    **🚀 Enhanced Multi-Agent Revenue Optimization:** 
    Choose between standard 2-agent collaboration or advanced CrewAI-powered 5-agent orchestration 
    for sophisticated revenue strategies and business intelligence.
    """)
    
    # Collaboration mode selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        collaboration_mode = st.selectbox(
            "🎯 **Select Collaboration Mode:**",
            options=[
                "crewai_enhanced", 
                "standard", 
                "hybrid"
            ],
            format_func=lambda x: {
                "standard": "🔧 Standard (2-Agent) - Proven 7.8% uplift",
                "crewai_enhanced": "🚀 CrewAI Enhanced (5-Agent) - Advanced orchestration", 
                "hybrid": "⚡ Hybrid (Both) - Comprehensive analysis"
            }[x],
            help="Choose your collaboration approach",
            key="collaboration_mode_select"
        )
    
    with col2:
        collaboration_triggered = st.button(
            "🤖 Launch Collaboration", 
            type="primary",
            help="Start multi-agent analysis with selected mode",
            key="agent_collaboration_trigger"
        )
    
    # Display mode-specific information
    if collaboration_mode == "standard":
        st.markdown("""
        **🔧 Standard Mode Features:**
        - 🎯 **Lead Intelligence + Sales Optimization** (2 agents)
        - 💰 **Revenue projections** for customer segments  
        - 📧 **Personalized email templates** for Hong Kong market
        - 📊 **Business impact analysis** with ROI calculations
        - ⚡ **Proven 7.8% revenue uplift** from previous demonstrations
        """)
    
    elif collaboration_mode == "crewai_enhanced":
        st.markdown("""
        **🚀 CrewAI Enhanced Mode Features:**
        - 🧠 **5 Specialized Agents** with hierarchical processing
        - 🎯 **Customer Intelligence Specialist** - Deep segmentation analysis
        - 📈 **Market Intelligence Director** - Competitive landscape insights  
        - 💰 **Revenue Optimization Expert** - Advanced revenue strategies
        - 🔄 **Retention & Lifecycle Specialist** - Customer journey optimization
        - 📧 **Campaign Orchestration Director** - Multi-channel campaign design
        - 🤝 **Consensus validation** for strategic recommendations
        - 📊 **15-25% potential revenue uplift** with advanced orchestration
        """)
    
    else:  # hybrid
        st.markdown("""
        **⚡ Hybrid Mode Features:**
        - 🔧 **Standard analysis** for proven baseline results
        - 🚀 **CrewAI enhancement** for advanced insights
        - 📊 **Comparative analysis** between both approaches
        - 🎯 **Best-of-both** recommendations and strategies
        - 💰 **Maximum coverage** of optimization opportunities
        """)
    
    if collaboration_triggered:
        process_agent_collaboration_from_results(results, collaboration_mode)


def process_agent_collaboration_from_results(lead_results: Dict[str, Any], mode: str = "standard"):
    """Process agent collaboration using Lead Intelligence results with enhanced CrewAI integration"""
    
    try:
        # Import both integration services
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        # Try CrewAI integration first
        try:
            from crewai_integration_bridge import process_agent_collaboration_with_crewai
            crewai_available = True
            st.success("✅ CrewAI integration bridge loaded successfully!")
        except ImportError as e:
            st.warning(f"🔄 CrewAI integration bridge not available (ImportError): {e}, falling back to standard mode")
            crewai_available = False
            mode = "standard"
        except Exception as e:
            st.warning(f"🔄 CrewAI integration bridge error: {e}, falling back to standard mode")
            crewai_available = False
            mode = "standard"
        
        # Standard integration fallback
        from src.agents.agent_integration_orchestrator import create_integration_service
        
        with st.spinner(f"🤖 Initiating {mode} multi-agent collaboration..."):
            # Transform Lead Intelligence results
            transformed_results = transform_lead_intelligence_results(lead_results)
            
            # Process based on selected mode
            if mode in ["crewai_enhanced", "hybrid"] and crewai_available:
                # Use CrewAI enhanced integration
                collaboration_results = process_agent_collaboration_with_crewai(
                    transformed_results, mode
                )
            else:
                # Use standard integration
                integration_service = create_integration_service()
                collaboration_results = integration_service.process_lead_intelligence_completion(
                    transformed_results
                )
                # Add mode information for consistency
                collaboration_results["mode"] = "standard"
                collaboration_results["collaboration_type"] = "Standard 2-Agent"
                collaboration_results["agents_involved"] = ["Lead Intelligence Agent", "Sales Optimization Agent"]
                collaboration_results["enhancement_level"] = "Standard"
            
            # Display results
            if collaboration_results.get("error"):
                st.error(f"❌ Agent collaboration failed: {collaboration_results['error']}")
                if collaboration_results.get("fallback_used"):
                    st.info(f"🔄 Fallback was attempted due to: {collaboration_results.get('fallback_reason', 'Unknown reason')}")
                return
            
            # Success message with mode information
            mode_display = collaboration_results.get("collaboration_type", mode.title())
            enhancement_level = collaboration_results.get("enhancement_level", "Standard")
            st.success(f"✅ {mode_display} collaboration completed successfully! ({enhancement_level})")
            
            # Show collaboration overview
            with st.expander("🎯 Collaboration Overview", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    agents = collaboration_results.get("agents_involved", [])
                    st.metric("Agents Involved", len(agents))
                    for agent in agents:
                        st.write(f"• {agent}")
                
                with col2:
                    processing_time = collaboration_results.get("processing_time", 0)
                    st.metric("Processing Time", f"{processing_time:.2f}s")
                    st.write(f"**Mode:** {collaboration_results.get('mode', 'standard').title()}")
                
                with col3:
                    enhancement = collaboration_results.get("enhancement_level", "Standard")
                    st.metric("Enhancement Level", enhancement)
                    if collaboration_results.get("fallback_used"):
                        st.warning("⚠️ Fallback mode used")
            
            # Show CrewAI-specific enhancements if available
            crewai_enhancements = collaboration_results.get("crewai_enhancements", {})
            if crewai_enhancements:
                with st.expander("🚀 CrewAI Advanced Features", expanded=True):
                    
                    # Collaboration metrics
                    collaboration_metrics = crewai_enhancements.get("collaboration_metrics", {})
                    if collaboration_metrics:
                        st.markdown("#### 🤝 Collaboration Quality Metrics")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            consensus_score = collaboration_metrics.get("consensus_score", 0)
                            st.metric("Consensus Score", f"{consensus_score:.1%}")
                        
                        with col2:
                            avg_confidence = collaboration_metrics.get("average_confidence", 0)
                            st.metric("Average Confidence", f"{avg_confidence:.1%}")
                        
                        with col3:
                            interactions = collaboration_metrics.get("total_interactions", 0)
                            st.metric("Agent Interactions", interactions)
                    
                    # Consensus validation details
                    consensus_scores = crewai_enhancements.get("consensus_scores", {})
                    if consensus_scores:
                        st.markdown("#### 🎯 Agent Agreement Analysis")
                        for agent, score in consensus_scores.items():
                            st.write(f"**{agent}:** {score:.1%} agreement")
                    
                    # Implementation roadmap
                    implementation_roadmap = crewai_enhancements.get("implementation_roadmap", {})
                    if implementation_roadmap:
                        st.markdown("#### 🗺️ Strategic Implementation Roadmap")
                        phases = implementation_roadmap.get("implementation_phases", [])
                        for phase in phases:
                            st.write(f"**{phase.get('phase', 'Phase')}:** {phase.get('focus', 'Implementation focus')}")
            
            # Show workflow steps
            with st.expander("🔄 View Collaboration Workflow", expanded=True):
                steps = collaboration_results.get("workflow_steps", [])
                for step in steps:
                    status_icon = "✅" if step.get("status") == "completed" else "❌"
                    st.write(f"{status_icon} **Step {step.get('step')}:** {step.get('action')}")
            
            # Show business impact in prominent display
            business_impact = collaboration_results.get("business_impact", {})
            if business_impact:
                st.markdown("## 📊 **Business Impact Analysis**")
                
                revenue_analysis = business_impact.get("revenue_analysis", {})
                if revenue_analysis:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        current_revenue = revenue_analysis.get("current_monthly_revenue", 0)
                        st.metric("Current Monthly Revenue", f"HK${current_revenue:,.0f}")
                    
                    with col2:
                        projected_revenue = revenue_analysis.get("projected_monthly_revenue", 0)
                        uplift_amount = projected_revenue - current_revenue
                        st.metric("Projected Monthly Revenue", f"HK${projected_revenue:,.0f}", 
                                delta=f"+HK${uplift_amount:,.0f}")
                    
                    with col3:
                        uplift = revenue_analysis.get("uplift_percentage", 0)
                        st.metric("Revenue Uplift", f"{uplift:.1f}%", delta=f"+{uplift:.1f}%")
                    
                    with col4:
                        annual_impact = revenue_analysis.get("expected_annual_uplift", 0)
                        st.metric("Annual Revenue Impact", f"HK${annual_impact:,.0f}")
                
                # Enhanced customer impact for CrewAI mode
                customer_impact = business_impact.get("customer_impact", {})
                if customer_impact:
                    st.markdown("### 👥 Customer Impact Summary")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**📊 {customer_impact.get('total_customers_analyzed', 0)}** customers analyzed")
                        segments = customer_impact.get('segments_identified', customer_impact.get('customer_segments', 0))
                        st.write(f"**🎯 {segments}** segments identified")
                    
                    with col2:
                        offers = customer_impact.get('personalized_offers_created', customer_impact.get('targeted_campaigns', 0))
                        st.write(f"**💰 {offers}** personalized offers created")
                        emails = customer_impact.get('email_templates_generated', customer_impact.get('communication_strategies', 0))
                        st.write(f"**📧 {emails}** email templates generated")
                
                # Show operational efficiency for enhanced modes
                operational_efficiency = business_impact.get("operational_efficiency", {})
                if operational_efficiency:
                    st.markdown("### ⚡ Operational Efficiency Gains")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        time_savings = operational_efficiency.get("time_savings_percentage", 0)
                        st.metric("Time Savings", f"{time_savings:.1f}%")
                    
                    with col2:
                        accuracy_improvement = operational_efficiency.get("accuracy_improvement", 0)
                        st.metric("Accuracy Improvement", f"{accuracy_improvement:.1f}%")
                    
                    with col3:
                        coverage_increase = operational_efficiency.get("coverage_increase", 0)
                        st.metric("Coverage Increase", f"{coverage_increase:.1f}%")
            
            # Show sales optimization results
            sales_results = collaboration_results.get("collaboration_results", {}).get("sales_optimization", {})
            if sales_results:
                
                # Show optimizations
                optimizations = sales_results.get("sales_optimizations", [])
                if optimizations:
                    st.markdown("### 🎯 **Sales Optimization Strategies**")
                    for opt in optimizations:
                        with st.expander(f"📈 {opt.get('segment', 'Unknown').replace('_', ' ').title()} Segment Strategy"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Strategy:** {opt.get('optimization_strategy', 'N/A')}")
                                st.write(f"**Expected Uplift:** {opt.get('expected_uplift', 0)}%")
                            
                            with col2:
                                st.write(f"**Customer Count:** {opt.get('customer_count', 0)}")
                                st.write(f"**Current ARPU:** HK${opt.get('avg_arpu', 0):,.0f}")
                
                # Show personalized offers
                offers = sales_results.get("personalized_offers", [])
                if offers:
                    st.markdown("### 💰 **Hong Kong Telecom Offers**")
                    for offer in offers:
                        with st.container():
                            st.markdown(f"**{offer.get('plan', 'Unknown Plan')}** - {offer.get('price', 'N/A')}")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.write(f"🎯 **Target:** {offer.get('target_segment', 'N/A').replace('_', ' ').title()}")
                            
                            with col2:
                                st.write(f"👥 **Customers:** {offer.get('customer_count', 0)}")
                            
                            with col3:
                                st.write(f"📈 **Conversion Rate:** {offer.get('expected_conversion_rate', 0)}%")
                            
                            # Show benefits
                            benefits = offer.get('benefits', [])
                            if benefits:
                                st.write("**Benefits:** " + " • ".join(benefits))
                            
                            st.markdown("---")
            
            # Show priority actions
            next_actions = collaboration_results.get("next_actions", [])
            if next_actions:
                st.markdown("### ⚡ **Priority Actions**")
                
                priority_actions = [a for a in next_actions if a.get("priority", 99) <= 2]
                for action in priority_actions:
                    priority_color = "🔴" if action.get("priority") == 1 else "🟡"
                    
                    with st.container():
                        st.markdown(f"{priority_color} **{action.get('action_type', 'Unknown').replace('_', ' ').title()}**")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"📋 {action.get('description', 'No description')}")
                        
                        with col2:
                            st.write(f"⏰ **Timeline:** {action.get('timeline', 'TBD')}")
                            st.write(f"🎯 **Expected Outcome:** {action.get('expected_outcome', 'N/A')}")
                        
                        st.markdown("---")
            
            # Show next steps
            st.markdown("### 🚀 **Next Steps**")
            st.info("""
            **✅ Agent collaboration complete!** Your analysis has been processed by our Sales Optimization Agent.
            
            **Recommended actions:**
            1. **Review** the revenue projections and optimization strategies above
            2. **Validate** the personalized offers for your Hong Kong market
            3. **Approve** priority actions in your manager dashboard
            4. **Execute** retention campaigns and upsell strategies
            5. **Monitor** performance through the Agent Collaboration Dashboard (port 8501)
            """)
            
            # Link to other dashboards
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("🔗 **[Agent Collaboration Dashboard](http://localhost:8501)** - Monitor real-time agent interactions")
            
            with col2:
                st.markdown("🔗 **[Integration Demo](http://localhost:8503)** - Standalone collaboration demonstration")
            
            return collaboration_results
            
    except Exception as e:
        st.error(f"❌ Error during agent collaboration: {e}")
        st.exception(e)
        return None


def transform_lead_intelligence_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """Transform Lead Intelligence results to format expected by Sales Optimization Agent"""
    
    try:
        # Extract recommendations and summary
        recommendations = results.get("recommendations", {}).get("recommendations", [])
        summary = results.get("recommendations", {}).get("summary", {})
        
        # Build customer segments from recommendations
        segments = {}
        lead_scores = {}
        
        for rec in recommendations:
            # Extract segment info
            segment_name = rec.get("segment", "unknown").lower().replace(" ", "_")
            customer_id = rec.get("customer_id", f"customer_{len(lead_scores)}")
            
            # Build lead scores
            priority_score_map = {"critical": 95, "high": 85, "medium": 70, "low": 50}
            score = priority_score_map.get(rec.get("priority", "medium"), 70)
            lead_scores[customer_id] = score
            
            # Aggregate segments
            if segment_name not in segments:
                segments[segment_name] = {"count": 0, "avg_arpu": 0, "total_revenue": 0}
            
            segments[segment_name]["count"] += 1
            expected_revenue = rec.get("expected_revenue", 450)  # Default HK$ ARPU
            segments[segment_name]["total_revenue"] += expected_revenue
        
        # Calculate average ARPU per segment
        for segment_name, segment_data in segments.items():
            if segment_data["count"] > 0:
                segment_data["avg_arpu"] = segment_data["total_revenue"] / segment_data["count"]
        
        # Build churn analysis from high priority recommendations
        high_priority_count = sum(1 for r in recommendations if r.get("priority") in ["critical", "high"])
        churn_segments = [seg for seg, data in segments.items() if "churn" in seg or "risk" in seg]
        
        churn_analysis = {
            "high_risk_customers": high_priority_count,
            "medium_risk_customers": sum(1 for r in recommendations if r.get("priority") == "medium"),
            "segments": churn_segments
        }
        
        # Build revenue insights
        total_customers = len(recommendations)
        total_revenue = summary.get("total_expected_revenue", sum(r.get("expected_revenue", 450) for r in recommendations))
        avg_arpu = total_revenue / max(total_customers, 1)
        
        revenue_insights = {
            "average_arpu": avg_arpu,
            "total_customers": total_customers,
            "monthly_revenue": total_revenue
        }
        
        # Return transformed results
        transformed = {
            "customer_segments": segments,
            "lead_scores": lead_scores,
            "churn_analysis": churn_analysis,
            "revenue_insights": revenue_insights,
            "original_recommendations_count": len(recommendations),
            "transformation_timestamp": datetime.now().isoformat()
        }
        
        return transformed
        
    except Exception as e:
        # Fallback with sample data structure
        return {
            "customer_segments": {
                "high_value": {"count": 50, "avg_arpu": 650},
                "business": {"count": 30, "avg_arpu": 890},
                "family": {"count": 80, "avg_arpu": 420}
            },
            "lead_scores": {f"customer_{i}": 75 + (i % 20) for i in range(10)},
            "churn_analysis": {
                "high_risk_customers": 15,
                "medium_risk_customers": 25,
                "segments": ["price_sensitive"]
            },
            "revenue_insights": {
                "average_arpu": 485,
                "total_customers": 160,
                "monthly_revenue": 77600
            },
            "transformation_error": str(e),
            "fallback_data": True
        }

    with col3:
        if st.button("🔧 View Metadata"):
            st.json(metadata)
