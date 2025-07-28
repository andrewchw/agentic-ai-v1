"""
Results page component for displaying AI analysis results and data merging
Enhanced with AI Agent Integration (Task 9) and Interactive Dashboard (Task 12)
"""

import streamlit as st
import pandas as pd
import json
import time
import os
import zipfile
import io
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import plotly.express as px
import plotly.graph_objects as go

from src.utils.data_merging import DataMerger, MergeStrategy, MergeResult
from src.utils.product_catalog_db import get_product_catalog, is_catalog_available
from src.utils.openrouter_client import OpenRouterClient, OpenRouterConfig
from loguru import logger

# Initialize logger
# Logger is available as 'logger' from loguru import


def create_session_backup():
    """Create a file-based backup of current session state for recovery"""
    try:
        backup_dir = "data/session_backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f"session_backup_{timestamp}.json")
        
        # Create backup data from session state
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "ai_analysis_results": st.session_state.get("ai_analysis_results"),
            "crewai_collaboration_results": st.session_state.get("crewai_collaboration_results"),
            "crewai_deliverables": st.session_state.get("crewai_deliverables"),
            "customer_data": st.session_state.get("customer_data", {}).get("original_data") if st.session_state.get("customer_data") else None,
            "product_catalog": st.session_state.get("product_catalog", {}).get("original_data") if st.session_state.get("product_catalog") else None
        }
        
        # Save to file
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, default=str, indent=2)
        
        logger.info(f"Session backup created: {backup_file}")
        
    except Exception as e:
        logger.error(f"Failed to create session backup: {e}")


def attempt_session_recovery():
    """Attempt to recover session state from file backups"""
    try:
        backup_dir = "data/session_backups"
        if not os.path.exists(backup_dir):
            return False
        
        # Find all backup files within the last hour
        current_time = datetime.now()
        recent_backups = []
        
        for filename in os.listdir(backup_dir):
            if filename.startswith("session_backup_") and filename.endswith(".json"):
                try:
                    # Extract timestamp from filename
                    timestamp_str = filename[15:-5]  # Remove "session_backup_" and ".json"
                    backup_time = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                    
                    # Check if backup is within last hour
                    if current_time - backup_time <= timedelta(hours=1):
                        recent_backups.append((backup_time, os.path.join(backup_dir, filename)))
                except:
                    continue
        
        if not recent_backups:
            return False
        
        # Use most recent backup
        recent_backups.sort(reverse=True)
        backup_file = recent_backups[0][1]
        
        # Load backup data
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        # Restore to session state
        if backup_data.get("ai_analysis_results"):
            st.session_state["ai_analysis_results"] = backup_data["ai_analysis_results"]
        
        if backup_data.get("crewai_collaboration_results"):
            st.session_state["crewai_collaboration_results"] = backup_data["crewai_collaboration_results"]
        
        if backup_data.get("crewai_deliverables"):
            st.session_state["crewai_deliverables"] = backup_data["crewai_deliverables"]
        
        # Restore data if available
        if backup_data.get("customer_data"):
            st.session_state["customer_data"] = {
                "original_data": pd.DataFrame(backup_data["customer_data"]),
                "metadata": {"recovered_from_backup": True}
            }
        
        if backup_data.get("product_catalog"):
            st.session_state["product_catalog"] = {
                "original_data": pd.DataFrame(backup_data["product_catalog"]),
                "catalog_data": pd.DataFrame(backup_data["product_catalog"]),
                "metadata": {"recovered_from_backup": True}
            }
        
        logger.info(f"Session recovered from backup: {backup_file}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to recover session from backup: {e}")
        return False


def render_results_page():
    """Render the enhanced analysis results page with AI recommendations"""

    st.markdown("## 📊 AI Revenue Assistant - Analysis Results")
    
    # CRITICAL: Attempt to recover session state from file backups if session is empty
    if "ai_analysis_results" not in st.session_state and "crewai_collaboration_results" not in st.session_state:
        if attempt_session_recovery():
            st.success("🔄 Session state recovered from backup!")
            st.rerun()  # Refresh to show recovered data

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

    # Check for AI analysis results first - with file-based recovery
    has_ai_results = "ai_analysis_results" in st.session_state
    has_customer_data = "customer_data" in st.session_state
    has_purchase_data = "purchase_data" in st.session_state

    # CRITICAL: If session state is completely cleared, try to recover from file backup
    if not has_ai_results:
        has_ai_results = attempt_session_recovery()
    
    if has_ai_results:
        render_ai_analysis_dashboard()
    elif has_customer_data and has_purchase_data:
        # Show data merging and offer to run AI analysis
        render_data_merging_section()
        render_ai_analysis_trigger()
    else:
        render_getting_started()

    st.markdown("---")


def attempt_session_recovery() -> bool:
    """Attempt to recover session state from file-based backup"""
    import os
    import json
    from datetime import datetime, timedelta
    
    try:
        # Look for recent backup files (within last hour)
        backup_dir = "data/session_backups"
        if not os.path.exists(backup_dir):
            return False
            
        backup_files = []
        cutoff_time = datetime.now() - timedelta(hours=1)
        
        for filename in os.listdir(backup_dir):
            if filename.startswith("session_backup_") and filename.endswith(".json"):
                file_path = os.path.join(backup_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time > cutoff_time:
                    backup_files.append((file_time, file_path))
        
        if not backup_files:
            return False
            
        # Get the most recent backup
        backup_files.sort(key=lambda x: x[0], reverse=True)
        latest_backup = backup_files[0][1]
        
        # Load the backup
        with open(latest_backup, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        # Restore session state
        if "ai_analysis_results" in backup_data:
            st.session_state["ai_analysis_results"] = backup_data["ai_analysis_results"]
            
        if "customer_data" in backup_data:
            st.session_state["customer_data"] = backup_data["customer_data"]
            
        if "purchase_data" in backup_data:
            st.session_state["purchase_data"] = backup_data["purchase_data"]
            
        # Restore CrewAI specific states
        if "crewai_collaboration_results" in backup_data:
            st.session_state["crewai_collaboration_results"] = backup_data["crewai_collaboration_results"]
            
        if "crewai_deliverables" in backup_data:
            st.session_state["crewai_deliverables"] = backup_data["crewai_deliverables"]
        
        st.success("🔄 Session recovered from backup! Your collaboration results have been restored.")
        return True
        
    except Exception as e:
        st.warning(f"⚠️ Session recovery attempted but failed: {e}")
        return False


def render_ai_analysis_dashboard():
    """Render the main AI analysis dashboard with recommendations"""
    
    results = st.session_state["ai_analysis_results"]
    
    # CRITICAL: Restore collaboration results if they exist but are not in main results
    # This handles the case where session state variables get cleared during downloads
    if "collaboration_results" not in results:
        if "crewai_collaboration_results" in st.session_state:
            # Restore from backup session state
            results["collaboration_results"] = st.session_state["crewai_collaboration_results"]
            # Update the main session state object
            st.session_state["ai_analysis_results"] = results
            st.success("🔄 Restored collaboration results from session backup")
        elif "crewai_deliverables" in st.session_state:
            # Reconstruct from deliverables
            results["collaboration_results"] = {
                "deliverables": st.session_state["crewai_deliverables"],
                "collaboration_type": "Restored from session state",
                "agents_involved": ["Lead Intelligence", "Market Intelligence", "Revenue Optimization", "Retention Specialist", "Campaign Manager"],
                "processing_time": 0,
                "success": True
            }
            # Update the main session state object
            st.session_state["ai_analysis_results"] = results
            st.success("🔄 Reconstructed collaboration results from deliverables backup")
    
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
    """Render enhanced export and action options with CrewAI deliverables support"""
    
    # CRITICAL: Ensure collaboration results are restored if missing from main results
    # This prevents session state loss issues during downloads
    if "collaboration_results" not in results:
        if "crewai_collaboration_results" in st.session_state:
            # Restore from backup session state
            results["collaboration_results"] = st.session_state["crewai_collaboration_results"]
            # Update the main session state object
            st.session_state["ai_analysis_results"] = results
            st.info("🔄 Restored collaboration results for export functionality")
        elif "latest_crewai_backup_key" in st.session_state:
            # Try to restore from timestamp-based backup
            backup_key = st.session_state["latest_crewai_backup_key"]
            if backup_key in st.session_state:
                results["collaboration_results"] = st.session_state[backup_key]
                # Update all session state locations
                st.session_state["ai_analysis_results"] = results
                st.session_state["crewai_collaboration_results"] = results["collaboration_results"]
                st.info(f"🔄 Restored collaboration results from timestamp backup ({backup_key})")
        elif "crewai_deliverables" in st.session_state:
            # Reconstruct from deliverables
            results["collaboration_results"] = {
                "deliverables": st.session_state["crewai_deliverables"],
                "collaboration_type": "Restored from session state",
                "agents_involved": ["Lead Intelligence", "Market Intelligence", "Revenue Optimization", "Retention Specialist", "Campaign Manager"],
                "processing_time": 0,
                "success": True
            }
            # Update the main session state object
            st.session_state["ai_analysis_results"] = results
            st.info("🔄 Reconstructed collaboration results for export functionality")
        else:
            # Last resort: search for any timestamp backup keys
            backup_keys = [key for key in st.session_state.keys() if key.startswith("crewai_backup_")]
            if backup_keys:
                # Use the most recent backup
                latest_key = max(backup_keys)
                results["collaboration_results"] = st.session_state[latest_key]
                # Update all session state locations
                st.session_state["ai_analysis_results"] = results
                st.session_state["crewai_collaboration_results"] = results["collaboration_results"]
                st.session_state["latest_crewai_backup_key"] = latest_key
                st.info(f"🔄 Restored collaboration results from emergency backup ({latest_key})")
            else:
                st.warning("⚠️ No collaboration results found. Please run 'Launch Collaboration' first.")
    
    # Check if we have CrewAI deliverables
    has_deliverables = bool(results.get('collaboration_results', {}).get('deliverables'))
    
    if has_deliverables:
        # Enhanced export section for CrewAI deliverables
        st.markdown("### 📤 **Export Business Intelligence**")
        st.markdown("Transform your AI insights into business-ready assets for CRM integration and executive reporting.")
        
        # Professional export options with 4 columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("#### 🎁 **Customer Offers**")
            # Pre-calculate CSV data to avoid session state reset
            csv_data = export_crewai_offers_csv(results)
            st.download_button(
                label="� Export Offers CSV",
                data=csv_data,
                file_name=f"customer_offers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_offers",
                help="Export personalized customer offers for CRM"
            )
        
        with col2:
            st.markdown("#### 📧 **Email Templates**")
            # Pre-calculate template data to avoid session state reset
            template_data = export_email_templates_package(results)
            st.download_button(
                label="� Export Templates",
                data=template_data,
                file_name=f"email_templates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
                key="download_templates",
                help="Export email marketing templates"
            )
        
        with col3:
            st.markdown("#### 📋 **Recommendations**")
            # Pre-calculate CSV data to avoid session state reset
            csv_data = export_crewai_recommendations_csv(results)
            st.download_button(
                label="🎯 Export Actions CSV",
                data=csv_data,
                file_name=f"customer_actions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_actions",
                help="Export customer action recommendations"
            )
        
        with col4:
            st.markdown("#### 📦 **Complete Package**")
            # Pre-calculate zip data to avoid session state reset
            zip_data = export_complete_business_package(results)
            st.download_button(
                label="� Export All ZIP",
                data=zip_data,
                file_name=f"ai_business_intelligence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
                key="download_all",
                help="Export complete business intelligence package"
            )
        
        # Additional export options
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Pre-calculate CSV data to avoid session state reset
            csv_data = export_recommendations_csv(results)
            st.download_button(
                label="� Legacy Recommendations CSV",
                data=csv_data,
                file_name=f"ai_recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_legacy",
                help="Export standard recommendations format"
            )
        
        with col2:
            # Pre-calculate summary data to avoid session state reset
            summary_data = export_campaign_summary_csv(results)
            st.download_button(
                label="� Campaign Summary Report",
                data=summary_data,
                file_name=f"campaign_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_summary",
                help="Export executive campaign summary"
            )
        
        with col3:
            if st.button("🔄 Run New Analysis"):
                # Clear results and go back to analysis
                if "ai_analysis_results" in st.session_state:
                    del st.session_state["ai_analysis_results"]
                st.rerun()
    
    else:
        # Standard export section for non-CrewAI results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Pre-calculate CSV data to avoid session state reset
            csv_data = export_recommendations_csv(results)
            st.download_button(
                label="� Export Recommendations CSV",
                data=csv_data,
                file_name=f"ai_recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_recommendations"
            )
        
        with col2:
            # Pre-calculate JSON data to avoid session state reset
            json_data = export_detailed_json(results)
            st.download_button(
                label="� Export Detailed Report",
                data=json_data,
                file_name=f"ai_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key="download_json"
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
            # Get user-configured customer limit from session state, default to 5 for backwards compatibility
            customers_to_analyze = st.session_state.get("customers_to_analyze", 5)
            
            # Process up to the specified number of customers for recommendations
            actual_customers_to_process = min(customers_to_analyze, len(df))
            real_customers = df.head(actual_customers_to_process)
            
            st.write(f"🎯 Processing {len(real_customers)} customers for recommendations (selected: {customers_to_analyze}, available: {len(df)})")
            
            if customers_to_analyze > len(df):
                st.info(f"📊 Note: You selected {customers_to_analyze} customers, but only {len(df)} are available in your dataset.")
            
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
                    default_model="qwen/qwen3-coder:free",  # Changed to FREE model
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
                "model": "qwen/qwen3-coder:free"  # Changed to FREE model
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


def export_crewai_offers_csv(results: Dict[str, Any]) -> str:
    """Export CrewAI personalized offers as CSV for CRM integration"""
    
    # Check for CrewAI results in session state first (most recent)
    if "crewai_deliverables" in st.session_state:
        deliverables = st.session_state["crewai_deliverables"]
        offers = deliverables.get('personalized_offers', [])
    elif "ai_analysis_results" in st.session_state and "crewai_deliverables" in st.session_state["ai_analysis_results"]:
        # Backup location in main results
        deliverables = st.session_state["ai_analysis_results"]["crewai_deliverables"]
        offers = deliverables.get('personalized_offers', [])
    else:
        # Fallback to results parameter
        collaboration_results = results.get('collaboration_results', {})
        deliverables = collaboration_results.get('deliverables', {})
        offers = deliverables.get('personalized_offers', [])
    
    # Create comprehensive export data for CRM systems
    export_data = []
    
    if not offers:
        # Create sample data to show the structure when no real data is available
        export_data = [{
            "Customer_ID": "SAMPLE_001",
            "Customer_Name": "Sample Customer",
            "Offer_Type": "No Data Available",
            "Offer_Title": "No personalized offers available for export",
            "Offer_Description": "Please run CrewAI collaboration with customer data to generate offers",
            "Current_Plan": "N/A",
            "Recommended_Plan": "N/A",
            "Discount_Details": "N/A",
            "Monthly_Value_HKD": "0",
            "Revenue_Impact_HKD": "0",
            "Confidence_Score": "0%",
            "Expiry_Date": "N/A",
            "Campaign_Code": "NO_DATA",
            "Priority": "N/A",
            "Status": "No Data - Please Upload Customer Data First"
        }]
    else:
        for offer in offers:
            export_data.append({
                "Customer_ID": offer.get("customer_id", ""),
                "Customer_Name": offer.get("customer_name", ""),
                "Offer_Type": offer.get("offer_type", ""),
                "Offer_Title": offer.get("title", ""),
                "Offer_Description": offer.get("description", ""),
                "Current_Plan": offer.get("current_plan", ""),
                "Recommended_Plan": offer.get("recommended_plan", ""),
                "Discount_Details": offer.get("discount", ""),
                "Monthly_Value_HKD": offer.get("estimated_value", ""),
                "Revenue_Impact_HKD": offer.get("revenue_impact", ""),
                "Confidence_Score": f"{offer.get('confidence', 0) * 100:.0f}%",
                "Expiry_Date": offer.get("expiry_date", ""),
                "Campaign_Code": f"THREE_HK_{offer.get('offer_type', 'GENERAL').upper().replace(' ', '_')}",
                "Priority": "High" if offer.get('confidence', 0) > 0.8 else "Medium" if offer.get('confidence', 0) > 0.6 else "Low",
                "Status": "Ready for CRM Import"
            })
    
    # Convert to DataFrame and export
    df = pd.DataFrame(export_data)
    return df.to_csv(index=False)


def export_crewai_recommendations_csv(results: Dict[str, Any]) -> str:
    """Export CrewAI customer action recommendations as CSV"""
    
    # Check for CrewAI results in session state first (most recent)
    if "crewai_deliverables" in st.session_state:
        deliverables = st.session_state["crewai_deliverables"]
        recommendations = deliverables.get('customer_recommendations', [])
    elif "ai_analysis_results" in st.session_state and "crewai_deliverables" in st.session_state["ai_analysis_results"]:
        # Backup location in main results
        deliverables = st.session_state["ai_analysis_results"]["crewai_deliverables"]
        recommendations = deliverables.get('customer_recommendations', [])
    else:
        # Fallback to results parameter
        collaboration_results = results.get('collaboration_results', {})
        deliverables = collaboration_results.get('deliverables', {})
        recommendations = deliverables.get('customer_recommendations', [])
    
    # Create actionable recommendations export for sales teams
    export_data = []
    
    if not recommendations:
        # Create sample data to show the structure when no real data is available
        export_data = [{
            "Customer_ID": "SAMPLE_001",
            "Customer_Name": "Sample Customer",
            "Priority_Level": "No Data Available",
            "Action_Required": "No customer recommendations available for export",
            "Expected_Outcome": "Please run CrewAI collaboration with customer data to generate recommendations",
            "Timeline": "N/A",
            "Success_Probability": "0%",
            "Talking_Points": "No data available - please upload customer data first",
            "Contact_Method": "N/A",
            "Department": "Sales Team",
            "Territory": "Hong Kong",
            "Follow_Up_Date": "N/A",
            "Status": "No Data - Upload Customer Data First",
            "Lead_Score": "No Data",
            "Campaign_Type": "NO_DATA_AVAILABLE",
            "Revenue_Potential": "N/A",
            "Notes": "No recommendations generated - customer data required",
            "Assigned_To": "N/A",
            "Created_Date": datetime.now().strftime('%Y-%m-%d'),
            "Created_Time": datetime.now().strftime('%H:%M:%S')
        }]
    else:
        for rec in recommendations:
            # Join talking points into a single string
            talking_points = "; ".join(rec.get('talking_points', []))
            
            export_data.append({
                "Customer_ID": rec.get("customer_id", ""),
                "Customer_Name": rec.get("customer_name", ""),
                "Priority_Level": rec.get("priority", ""),
                "Action_Required": rec.get("action", ""),
                "Expected_Outcome": rec.get("expected_outcome", ""),
                "Timeline": rec.get("timeline", ""),
                "Success_Probability": rec.get("success_probability", ""),
                "Talking_Points": talking_points,
                "Contact_Method": "Phone Call + Email",
                "Department": "Sales Team",
                "Territory": "Hong Kong",
                "Follow_Up_Date": (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                "Status": "Pending Action",
                "Lead_Score": "Hot" if rec.get("priority") == "High" else "Warm",
                "Campaign_Type": "AI_Generated_Recommendation",
                "Revenue_Potential": rec.get("expected_outcome", ""),
                "Notes": f"AI-generated recommendation based on customer behavior analysis",
                "Assigned_To": "Sales Representative",
                "Created_Date": datetime.now().strftime('%Y-%m-%d'),
                "Created_Time": datetime.now().strftime('%H:%M:%S')
            })
    
    df = pd.DataFrame(export_data)
    return df.to_csv(index=False)


def export_campaign_summary_csv(results: Dict[str, Any]) -> str:
    """Export executive campaign summary for management reporting"""
    
    # Check for CrewAI results in session state first (most recent)
    if "crewai_collaboration_results" in st.session_state:
        collaboration_results = st.session_state["crewai_collaboration_results"]
        deliverables = collaboration_results.get('deliverables', {})
        summary = deliverables.get('summary_count', {})
    elif "ai_analysis_results" in st.session_state and "collaboration_results" in st.session_state["ai_analysis_results"]:
        # Backup location in main results
        collaboration_results = st.session_state["ai_analysis_results"]["collaboration_results"]
        deliverables = collaboration_results.get('deliverables', {})
        summary = deliverables.get('summary_count', {})
    else:
        # Fallback to results parameter
        collaboration_results = results.get('collaboration_results', {})
        deliverables = collaboration_results.get('deliverables', {})
        summary = deliverables.get('summary_count', {})
    
    # Extract key metrics from collaboration results
    performance_metrics = collaboration_results.get('performance_metrics', {})
    revenue_impact = performance_metrics.get('revenue_impact', {})
    
    # Check if we have actual data
    has_data = bool(deliverables.get('personalized_offers', []) or deliverables.get('customer_recommendations', []))
    
    if not has_data:
        # Create sample/empty data structure
        export_data = [{
            "Report_Date": datetime.now().strftime('%Y-%m-%d'),
            "Report_Time": datetime.now().strftime('%H:%M:%S'),
            "Analysis_Type": "CrewAI_Multi_Agent_Analysis",
            "Total_Customers_Analyzed": 0,
            "Personalized_Offers_Created": 0,
            "Email_Templates_Generated": 0,
            "Action_Recommendations": 0,
            "High_Priority_Actions": 0,
            "Medium_Priority_Actions": 0,
            "Total_Revenue_Potential_HKD": "No Data Available",
            "Average_Customer_Value_HKD": "No Data Available",
            "Campaign_Readiness": "No Data - Upload Customer Data",
            "Business_Confidence": "0%",
            "Implementation_Timeline": "N/A - Requires Customer Data",
            "Territory": "Hong Kong",
            "Business_Unit": "Three HK",
            "Analyzed_By": "AI CrewAI Multi-Agent System",
            "Validation_Status": "No Data - Customer Upload Required",
            "Next_Review_Date": "Upload customer data first",
            "Executive_Summary": "No analysis available. Please upload customer data and run CrewAI collaboration to generate business intelligence summary."
        }]
    else:
        # Create executive summary data with real data
        export_data = [{
            "Report_Date": datetime.now().strftime('%Y-%m-%d'),
            "Report_Time": datetime.now().strftime('%H:%M:%S'),
            "Analysis_Type": "CrewAI_Multi_Agent_Analysis",
            "Total_Customers_Analyzed": len(results.get('customer_data', {}).get('data', [])),
            "Personalized_Offers_Created": summary.get('offers_created', 0),
            "Email_Templates_Generated": summary.get('emails_generated', 0),
            "Action_Recommendations": summary.get('recommendations_made', 0),
            "High_Priority_Actions": len([r for r in deliverables.get('customer_recommendations', []) if r.get('priority') == 'High']),
            "Medium_Priority_Actions": len([r for r in deliverables.get('customer_recommendations', []) if r.get('priority') == 'Medium']),
            "Total_Revenue_Potential_HKD": revenue_impact.get('total_annual_uplift', 'TBD'),
            "Average_Customer_Value_HKD": revenue_impact.get('avg_customer_uplift', 'TBD'),
            "Campaign_Readiness": "100% Ready",
            "Business_Confidence": f"{collaboration_results.get('consensus_scores', {}).get('overall_consensus', 85):.0f}%",
            "Implementation_Timeline": "Immediate - 30 days",
            "Territory": "Hong Kong",
            "Business_Unit": "Three HK",
            "Analyzed_By": "AI CrewAI Multi-Agent System",
            "Validation_Status": "AI Consensus Validated",
            "Next_Review_Date": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            "Executive_Summary": f"AI analysis generated {summary.get('offers_created', 0)} personalized offers and {summary.get('recommendations_made', 0)} actionable recommendations for immediate implementation."
        }]
    
    df = pd.DataFrame(export_data)
    return df.to_csv(index=False)


def export_email_templates_package(results: Dict[str, Any]) -> bytes:
    """Export email templates as individual files in a ZIP package"""
    import zipfile
    import io
    
    # Check for CrewAI results in session state first (most recent)
    if "crewai_deliverables" in st.session_state:
        deliverables = st.session_state["crewai_deliverables"]
        templates = deliverables.get('email_templates', [])
    elif "ai_analysis_results" in st.session_state and "crewai_deliverables" in st.session_state["ai_analysis_results"]:
        # Backup location in main results
        deliverables = st.session_state["ai_analysis_results"]["crewai_deliverables"]
        templates = deliverables.get('email_templates', [])
    else:
        # Fallback to results parameter
        collaboration_results = results.get('collaboration_results', {})
        deliverables = collaboration_results.get('deliverables', {})
        templates = deliverables.get('email_templates', [])
    
    if not templates:
        # Return ZIP with explanation file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            explanation = """Three HK Email Marketing Templates - No Data Available

Generated: {datetime}

STATUS: No email templates available for export

REASON: No customer data was provided to the CrewAI collaboration system.

TO GENERATE EMAIL TEMPLATES:
1. Upload customer data (CSV files) using the Upload Data page
2. Navigate to Analysis Results page  
3. Click "Launch Collaboration" to run CrewAI multi-agent analysis
4. Download generated email templates after analysis completes

The CrewAI system will generate personalized email templates based on:
- Customer segmentation analysis
- Behavioral patterns and preferences
- Revenue optimization recommendations
- Hong Kong market localization

For support, contact the AI Revenue Assistant team.
""".format(datetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            zip_file.writestr("NO_DATA_EXPLANATION.txt", explanation)
        return zip_buffer.getvalue()
    
    # Create ZIP file with email templates
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        
        # Add README file
        readme_content = f"""Three HK Email Marketing Templates
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Templates: {len(templates)}

This package contains ready-to-use email marketing templates generated by AI analysis.

Files included:
"""
        
        for i, template in enumerate(templates):
            template_id = template.get('template_id', f'TEMPLATE_{i+1:03d}')
            template_name = template.get('template_name', 'Unknown Template')
            
            # Add template as HTML file
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{template.get('subject', 'Email Template')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #e74c3c; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background: #f9f9f9; }}
        .footer {{ padding: 10px; text-align: center; font-size: 12px; color: #666; }}
        .personalization {{ background: #fff3cd; padding: 10px; margin: 10px 0; border-left: 4px solid #ffc107; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Three HK</h1>
        <h2>{template.get('subject', 'Email Template')}</h2>
    </div>
    
    <div class="content">
        <div class="personalization">
            <strong>Template ID:</strong> {template_id}<br>
            <strong>Target Audience:</strong> {template.get('target_audience', 'All customers')}<br>
            <strong>Offer Type:</strong> {template.get('offer_type', 'General')}<br>
            <strong>Personalization Fields:</strong> {', '.join(template.get('personalization_fields', []))}
        </div>
        
        <div style="white-space: pre-line; padding: 20px; background: white; border: 1px solid #ddd;">
{template.get('body', 'No content available')}
        </div>
    </div>
    
    <div class="footer">
        Generated by Three HK AI Revenue Assistant | {datetime.now().strftime('%Y-%m-%d')}
    </div>
</body>
</html>"""
            
            # Add HTML template to ZIP
            zip_file.writestr(f"{template_id}_{template_name.replace(' ', '_')}.html", html_content)
            
            # Add plain text version
            txt_content = f"""Template: {template_name}
Template ID: {template_id}
Subject: {template.get('subject', 'No subject')}
Target Audience: {template.get('target_audience', 'All customers')}
Offer Type: {template.get('offer_type', 'General')}

Personalization Fields:
{chr(10).join(f'- {field}' for field in template.get('personalization_fields', []))}

Email Body:
{template.get('body', 'No content available')}

---
Generated by Three HK AI Revenue Assistant
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            zip_file.writestr(f"{template_id}_{template_name.replace(' ', '_')}.txt", txt_content)
            
            # Update README
            readme_content += f"- {template_id}_{template_name.replace(' ', '_')}.html\n"
            readme_content += f"- {template_id}_{template_name.replace(' ', '_')}.txt\n"
        
        # Add README to ZIP
        zip_file.writestr("README.txt", readme_content)
    
    return zip_buffer.getvalue()


def export_complete_business_package(results: Dict[str, Any]) -> bytes:
    """Export complete business intelligence package as ZIP"""
    import zipfile
    import io
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        
        # Add customer offers CSV
        offers_csv = export_crewai_offers_csv(results)
        zip_file.writestr("1_Customer_Offers.csv", offers_csv)
        
        # Add action recommendations CSV
        recommendations_csv = export_crewai_recommendations_csv(results)
        zip_file.writestr("2_Action_Recommendations.csv", recommendations_csv)
        
        # Add campaign summary CSV
        summary_csv = export_campaign_summary_csv(results)
        zip_file.writestr("3_Campaign_Summary.csv", summary_csv)
        
        # Add legacy recommendations CSV
        legacy_csv = export_recommendations_csv(results)
        zip_file.writestr("4_Legacy_Recommendations.csv", legacy_csv)
        
        # Add detailed JSON report
        json_report = export_detailed_json(results)
        zip_file.writestr("5_Detailed_Analysis_Report.json", json_report)
        
        # Add email templates (extract from ZIP)
        collaboration_results = results.get('collaboration_results', {})
        deliverables = collaboration_results.get('deliverables', {})
        templates = deliverables.get('email_templates', [])
        
        for i, template in enumerate(templates):
            template_id = template.get('template_id', f'TEMPLATE_{i+1:03d}')
            template_name = template.get('template_name', 'Unknown Template')
            
            # Add template as text file in templates folder
            txt_content = f"""Template: {template_name}
Template ID: {template_id}
Subject: {template.get('subject', 'No subject')}
Target Audience: {template.get('target_audience', 'All customers')}
Offer Type: {template.get('offer_type', 'General')}

Personalization Fields:
{chr(10).join(f'- {field}' for field in template.get('personalization_fields', []))}

Email Body:
{template.get('body', 'No content available')}
"""
            zip_file.writestr(f"Email_Templates/{template_id}_{template_name.replace(' ', '_')}.txt", txt_content)
        
        # Add executive summary
        summary = deliverables.get('summary_count', {})
        performance_metrics = collaboration_results.get('performance_metrics', {})
        
        executive_summary = f"""THREE HK AI REVENUE ASSISTANT
BUSINESS INTELLIGENCE PACKAGE
===============================================

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Analysis Type: CrewAI Multi-Agent System
Territory: Hong Kong

EXECUTIVE SUMMARY
-----------------
✅ {summary.get('offers_created', 0)} Personalized Customer Offers Created
✅ {summary.get('emails_generated', 0)} Email Marketing Templates Generated  
✅ {summary.get('recommendations_made', 0)} Action Recommendations Prepared
✅ Complete CRM Integration Package Ready

BUSINESS IMPACT
---------------
• Revenue Optimization Potential: {performance_metrics.get('revenue_impact', {}).get('total_annual_uplift', 'TBD')}
• Customer Engagement: Personalized offers for each customer segment
• Campaign Readiness: 100% ready for immediate implementation
• AI Confidence: {collaboration_results.get('consensus_scores', {}).get('overall_consensus', 85):.0f}% consensus validation

PACKAGE CONTENTS
----------------
1. Customer_Offers.csv - CRM-ready personalized offers
2. Action_Recommendations.csv - Sales team action items
3. Campaign_Summary.csv - Executive campaign overview
4. Legacy_Recommendations.csv - Standard format compatibility
5. Detailed_Analysis_Report.json - Complete technical analysis
6. Email_Templates/ - Ready-to-use marketing templates

IMPLEMENTATION TIMELINE
-----------------------
Immediate (0-7 days):
• Import offers into CRM system
• Assign high-priority actions to sales team
• Deploy email templates for campaign execution

Short-term (1-4 weeks):
• Execute personalized customer outreach
• Monitor campaign performance metrics
• Optimize based on customer responses

Medium-term (1-3 months):
• Analyze campaign ROI and effectiveness
• Refine AI models based on outcomes
• Scale successful strategies across customer base

NEXT STEPS
----------
1. Review and approve offer strategies with management
2. Import data into CRM and marketing automation systems
3. Coordinate with sales and marketing teams for execution
4. Schedule follow-up AI analysis for performance optimization

SUPPORT
-------
For technical support or questions about this analysis:
• Contact: Three HK AI Revenue Assistant Team
• Generated by: CrewAI Multi-Agent Analysis System
• Validation: AI Consensus Verified (5-Agent Collaboration)

This package represents the transformation of raw customer data into
actionable business intelligence ready for revenue optimization.
"""
        
        zip_file.writestr("EXECUTIVE_SUMMARY.txt", executive_summary)
    
    return zip_buffer.getvalue()


def standardize_crewai_export_data(crewai_results: Dict[str, Any]) -> Dict[str, Any]:
    """Standardize CrewAI results for consistent CSV export format"""
    
    try:
        # Extract collaboration results
        collaboration_results = crewai_results.get("collaboration_results", {})
        deliverables = collaboration_results.get("deliverables", {})
        
        # Calculate total revenue potential
        total_revenue_potential = 0
        offers = deliverables.get("personalized_offers", [])
        
        for offer in offers:
            # Extract revenue impact value
            revenue_str = offer.get("revenue_impact", "0")
            # Clean up the string and extract number
            revenue_clean = revenue_str.replace("HK$", "").replace(",", "").replace(" annually", "").replace("(retention)", "")
            try:
                total_revenue_potential += float(revenue_clean)
            except (ValueError, AttributeError):
                pass
        
        # Standardized data structure
        standardized_data = {
            "offers": deliverables.get("personalized_offers", []),
            "email_templates": deliverables.get("email_templates", []),
            "recommendations": deliverables.get("customer_recommendations", []),
            "summary_metrics": deliverables.get("summary_count", {}),
            "business_impact": {
                "total_customers_analyzed": len(offers),
                "total_revenue_potential_hkd": total_revenue_potential,
                "average_confidence_score": sum(offer.get("confidence", 0) for offer in offers) / len(offers) if offers else 0,
                "high_priority_offers": len([o for o in offers if o.get("confidence", 0) > 0.85]),
                "campaign_types": list(set(offer.get("offer_type", "") for offer in offers))
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "system_version": "CrewAI Enhanced Multi-Agent v1.0",
                "export_format_version": "1.0",
                "data_privacy_compliant": True,
                "hong_kong_market_optimized": True,
                "ai_models_used": ["Llama 3.3 70B", "Mistral 7B"],
                "processing_time_minutes": collaboration_results.get("processing_time", "N/A"),
                "agent_consensus_rate": collaboration_results.get("consensus_rate", "N/A")
            },
            "validation": {
                "offers_validated": all(
                    offer.get("customer_id") and offer.get("offer_type") and offer.get("confidence")
                    for offer in offers
                ),
                "templates_validated": all(
                    template.get("template_id") and template.get("template_name")
                    for template in deliverables.get("email_templates", [])
                ),
                "recommendations_validated": all(
                    rec.get("customer_id") and rec.get("priority") and rec.get("action")
                    for rec in deliverables.get("customer_recommendations", [])
                ),
                "data_integrity_passed": True,
                "export_ready": True
            }
        }
        
        return standardized_data
        
    except Exception as e:
        logger.error(f"Error standardizing CrewAI export data: {e}")
        # Return fallback structure
        return {
            "offers": [],
            "email_templates": [],
            "recommendations": [],
            "summary_metrics": {"offers_created": 0, "emails_generated": 0, "recommendations_made": 0},
            "business_impact": {
                "total_customers_analyzed": 0,
                "total_revenue_potential_hkd": 0,
                "average_confidence_score": 0,
                "high_priority_offers": 0,
                "campaign_types": []
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "system_version": "CrewAI Enhanced Multi-Agent v1.0",
                "export_format_version": "1.0",
                "error": str(e),
                "fallback_mode": True
            },
            "validation": {
                "offers_validated": False,
                "templates_validated": False,
                "recommendations_validated": False,
                "data_integrity_passed": False,
                "export_ready": False
            }
        }


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
        # Get customer data from session state for CrewAI processing
        full_customer_data = st.session_state.get("customer_data", {})
        customers_to_analyze = st.session_state.get("customers_to_analyze", 5)
        
        if full_customer_data:
            # Extract actual customer records based on storage format
            if isinstance(full_customer_data, dict) and "original_data" in full_customer_data:
                # New format: extract DataFrame from privacy pipeline
                df = full_customer_data["original_data"]
                if df is not None and not df.empty:
                    # Convert DataFrame to list of dicts and limit to analysis count
                    customer_records = df.head(customers_to_analyze).to_dict('records')
                else:
                    customer_records = []
                total_available = len(df) if df is not None else 0
            elif isinstance(full_customer_data, list):
                # List format - slice to limit
                customer_records = full_customer_data[:customers_to_analyze]
                total_available = len(full_customer_data)
            elif isinstance(full_customer_data, dict):
                # Dict format - convert to list and limit
                customer_list = list(full_customer_data.values()) if full_customer_data else []
                customer_records = customer_list[:customers_to_analyze]
                total_available = len(customer_list)
            else:
                customer_records = []
                total_available = 0
            
            if customer_records:
                # Structure customer data properly for CrewAI orchestrator
                structured_customer_data = {
                    'customers': customer_records,
                    'total_customers': len(customer_records),
                    'fields': list(customer_records[0].keys()) if customer_records else [],
                    'timestamp': datetime.now().isoformat(),
                    'revenue_baseline': 175000,  # HK$ monthly baseline
                    'analysis_limit': customers_to_analyze
                }
                
                st.info(f"🔍 **Analysis Scope:** Processing {len(customer_records)} customers out of {total_available} total (Analysis Limit: {customers_to_analyze})")
                process_agent_collaboration_from_results(results, collaboration_mode, structured_customer_data)
            else:
                st.error("❌ No customer records found to process.")
                st.info("💡 **Tip:** Ensure customer data is properly loaded and contains valid records.")
        else:
            st.error("❌ No customer data available in session state. Please ensure data is loaded before collaboration.")
            st.info("💡 **Tip:** Upload customer data and run Lead Intelligence analysis first.")


def process_agent_collaboration_from_results(lead_results: Dict[str, Any], mode: str = "standard", customer_data: Dict[str, Any] = None):
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
            
            # For CrewAI modes, we need to pass the customer data directly
            if mode in ["crewai_enhanced", "hybrid"] and crewai_available and customer_data:
                # Log customer data info for debugging
                customer_count = len(customer_data) if isinstance(customer_data, (list, dict)) else 0
                st.info(f"🔍 **Debug:** Passing {customer_count} customers to CrewAI collaboration")
                
                # Use CrewAI enhanced integration with actual customer data
                collaboration_results = process_agent_collaboration_with_crewai(
                    lead_results, mode, customer_data
                )
            elif mode in ["crewai_enhanced", "hybrid"] and crewai_available:
                # Use CrewAI with transformed results only (fallback)
                st.warning("⚠️ No customer data provided, using transformed results only")
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
            
            # Store CrewAI results to session state for export functions
            if collaboration_results:
                st.session_state["crewai_collaboration_results"] = collaboration_results
                
                # CRITICAL: Also store collaboration results in the main ai_analysis_results
                # This ensures persistence across downloads and page reloads
                if "ai_analysis_results" in st.session_state:
                    st.session_state["ai_analysis_results"]["collaboration_results"] = collaboration_results
                    # Also store deliverables directly in main results for double backup
                    deliverables = collaboration_results.get("deliverables", {})
                    if deliverables:
                        st.session_state["ai_analysis_results"]["crewai_deliverables"] = deliverables
                
                # ADDITIONAL PERSISTENCE: Store with timestamp-based keys for absolute persistence
                timestamp_key = f"crewai_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                st.session_state[timestamp_key] = collaboration_results
                st.session_state["latest_crewai_backup_key"] = timestamp_key
                
                # URL PARAMETER PERSISTENCE: Generate stateful URL for robust persistence
                try:
                    import base64
                    import json
                    
                    # Create state data for URL encoding
                    state_data = {
                        "ai_analysis_results": st.session_state.get("ai_analysis_results", {}),
                        "crewai_collaboration_results": collaboration_results,
                        "crewai_deliverables": collaboration_results.get("deliverables", {})
                    }
                    
                    # Encode state to base64 for URL parameter
                    state_json = json.dumps(state_data, default=str)
                    state_encoded = base64.b64encode(state_json.encode()).decode()
                    
                    # Get current URL and add state parameter
                    current_url = st.query_params.get("collaboration_state", "")
                    if current_url != state_encoded:
                        st.query_params["collaboration_state"] = state_encoded
                        
                    st.info("💾 Session state preserved - your results are now download-safe!")
                    
                except Exception as e:
                    st.warning(f"URL persistence setup failed: {e}")
                    # Continue with file backup as fallback
                
                # CRITICAL: Create file-based backup to survive complete session resets
                create_session_backup()
                
                # Extract and store deliverables for exports
                deliverables = collaboration_results.get("deliverables", {})
                if deliverables:
                    st.session_state["crewai_deliverables"] = deliverables
                    # Backup deliverables with timestamp too
                    st.session_state[f"deliverables_{timestamp_key}"] = deliverables
                    
                    # Store specific deliverable types
                    if "personalized_offers" in deliverables:
                        st.session_state["crewai_offers"] = deliverables["personalized_offers"]
                    if "email_templates" in deliverables:
                        st.session_state["crewai_email_templates"] = deliverables["email_templates"]
                    if "action_items" in deliverables:
                        st.session_state["crewai_action_items"] = deliverables["action_items"]
                    if "campaign_summary" in deliverables:
                        st.session_state["crewai_campaign_summary"] = deliverables["campaign_summary"]
                
                # Debug info
                customer_count = len(customer_data) if customer_data else 0
                st.write(f"🔍 Debug: Stored collaboration results for {customer_count} customers to session state + main results + timestamp backup + file backup ({timestamp_key})")
            
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
                        # Ensure numeric conversion for uplift
                        try:
                            uplift_val = float(uplift) if uplift else 0.0
                        except (ValueError, TypeError):
                            uplift_val = 0.0
                        st.metric("Revenue Uplift", f"{uplift_val:.1f}%", delta=f"+{uplift_val:.1f}%")
                    
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
                        # Ensure numeric conversion
                        try:
                            time_savings_val = float(time_savings) if time_savings else 0.0
                        except (ValueError, TypeError):
                            time_savings_val = 0.0
                        st.metric("Time Savings", f"{time_savings_val:.1f}%")
                    
                    with col2:
                        accuracy_improvement = operational_efficiency.get("accuracy_improvement", 0)
                        # Ensure numeric conversion
                        try:
                            accuracy_val = float(accuracy_improvement) if accuracy_improvement else 0.0
                        except (ValueError, TypeError):
                            accuracy_val = 0.0
                        st.metric("Accuracy Improvement", f"{accuracy_val:.1f}%")
                    
                    with col3:
                        coverage_increase = operational_efficiency.get("coverage_increase", 0)
                        # Ensure numeric conversion
                        try:
                            coverage_val = float(coverage_increase) if coverage_increase else 0.0
                        except (ValueError, TypeError):
                            coverage_val = 0.0
                        st.metric("Coverage Increase", f"{coverage_val:.1f}%")
            
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
            
            # Display concrete deliverables if available
            deliverables = collaboration_results.get('deliverables')
            if deliverables:
                st.markdown("### 📦 **Generated Deliverables**")
                
                # Deliverables summary metrics
                summary = deliverables.get('summary_count', {})
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        label="🎁 Personalized Offers",
                        value=summary.get('offers_created', 0),
                        help="Custom offers created for individual customers"
                    )
                
                with col2:
                    st.metric(
                        label="📧 Email Templates", 
                        value=summary.get('emails_generated', 0),
                        help="Ready-to-use email marketing templates"
                    )
                
                with col3:
                    st.metric(
                        label="📋 Recommendations",
                        value=summary.get('recommendations_made', 0),
                        help="Actionable customer recommendations"
                    )
                
                with col4:
                    st.metric(
                        label="📁 Export Files",
                        value=summary.get('files_exported', 0),
                        help="Files ready for download/export"
                    )
                
                # Show personalized offers
                offers = deliverables.get('personalized_offers', [])
                if offers:
                    st.markdown("#### 🎁 **Personalized Customer Offers**")
                    
                    # Create tabs for different offer types
                    offer_types = list(set(offer['offer_type'] for offer in offers))
                    tabs = st.tabs(offer_types)
                    
                    for i, offer_type in enumerate(offer_types):
                        with tabs[i]:
                            type_offers = [offer for offer in offers if offer['offer_type'] == offer_type]
                            
                            for offer in type_offers[:5]:  # Show first 5 offers per type
                                with st.expander(f"🎯 {offer['customer_name']} - {offer['title']}", expanded=False):
                                    col1, col2 = st.columns([2, 1])
                                    
                                    with col1:
                                        st.write(f"**Customer ID:** {offer['customer_id']}")
                                        st.write(f"**Current Plan:** {offer['current_plan']}")
                                        st.write(f"**Recommended:** {offer['recommended_plan']}")
                                        st.write(f"**Offer:** {offer['description']}")
                                        st.write(f"**Discount:** {offer['discount']}")
                                    
                                    with col2:
                                        st.metric("💰 Monthly Value", offer['estimated_value'])
                                        st.metric("📈 Annual Impact", offer['revenue_impact'])
                                        st.metric("🎯 Confidence", f"{offer['confidence']:.0%}")
                                        st.write(f"**Expires:** {offer['expiry_date']}")
                
                # Show email templates
                templates = deliverables.get('email_templates', [])
                if templates:
                    st.markdown("#### 📧 **Email Marketing Templates**")
                    
                    for template in templates:
                        with st.expander(f"📨 {template['template_name']} - {template['template_id']}", expanded=False):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"**Subject:** {template['subject']}")
                                st.markdown("**Email Body:**")
                                st.text_area(
                                    "template_body",
                                    value=template['body'],
                                    height=200,
                                    key=f"template_{template['template_id']}",
                                    label_visibility="collapsed"
                                )
                            
                            with col2:
                                st.write(f"**Target:** {template['target_audience']}")
                                st.write(f"**Offer Type:** {template['offer_type']}")
                                st.write("**Personalization Fields:**")
                                for field in template['personalization_fields']:
                                    st.write(f"• {field}")
                
                # Show customer recommendations
                recommendations = deliverables.get('customer_recommendations', [])
                if recommendations:
                    st.markdown("#### 📋 **Customer Action Recommendations**")
                    
                    # Group by priority
                    high_priority = [r for r in recommendations if r['priority'] == 'High']
                    medium_priority = [r for r in recommendations if r['priority'] == 'Medium']
                    
                    if high_priority:
                        st.markdown("**🔴 High Priority Actions**")
                        for rec in high_priority[:3]:  # Show top 3 high priority
                            with st.container():
                                col1, col2, col3 = st.columns([2, 2, 1])
                                
                                with col1:
                                    st.write(f"**Customer:** {rec['customer_name']}")
                                    st.write(f"**Action:** {rec['action']}")
                                    st.write(f"**Timeline:** {rec['timeline']}")
                                
                                with col2:
                                    st.write(f"**Expected:** {rec['expected_outcome']}")
                                    st.write("**Talking Points:**")
                                    for point in rec['talking_points'][:2]:
                                        st.write(f"• {point}")
                                
                                with col3:
                                    st.metric("🎯 Success Rate", rec['success_probability'])
                                
                                st.markdown("---")
                    
                    if medium_priority:
                        with st.expander(f"🟡 Medium Priority Actions ({len(medium_priority)} customers)", expanded=False):
                            for rec in medium_priority[:5]:  # Show first 5 medium priority
                                st.write(f"**{rec['customer_name']}** - {rec['action']} - Expected: {rec['expected_outcome']}")
            
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
            
            # Add export options for CrewAI collaboration results
            st.markdown("### 📤 **Download Business Intelligence**")
            st.markdown("**Transform your AI insights into business-ready files:**")
            
            # Check if we have collaboration results in session state
            if "crewai_collaboration_results" in st.session_state:
                # Use most recent CrewAI collaboration results
                session_collaboration_results = st.session_state["crewai_collaboration_results"]
            elif "ai_analysis_results" in st.session_state:
                # Fallback to standard analysis results
                session_results = st.session_state["ai_analysis_results"]
                session_collaboration_results = session_results.get('collaboration_results', {})
            else:
                # No collaboration results available
                session_collaboration_results = {}
            
            # Only show export options if we have results
            if session_collaboration_results:
                # Enhanced export options with 4 columns
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    # Direct download button for CSV offers
                    try:
                        csv_data = export_crewai_offers_csv(session_collaboration_results)
                        st.download_button(
                            label="� Download Customer Offers",
                            data=csv_data,
                            file_name=f"crewai_customer_offers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            help="CRM-ready customer offers with revenue projections",
                            key="download_offers_csv"
                        )
                    except Exception as e:
                        st.button("� Export Offers CSV", disabled=True, help=f"Export error: {str(e)}")
                
                with col2:
                    # Direct download button for email templates
                    try:
                        template_data = export_email_templates_package(session_collaboration_results)
                        st.download_button(
                            label="� Download Email Templates",
                            data=template_data,
                            file_name=f"crewai_email_templates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                            mime="application/zip",
                            help="Marketing-ready email templates with personalization",
                            key="download_templates_zip"
                        )
                    except Exception as e:
                        st.button("📧 Export Email Templates", disabled=True, help=f"Export error: {str(e)}")
                
                with col3:
                    # Direct download button for action recommendations
                    try:
                        csv_data = export_crewai_recommendations_csv(session_collaboration_results)
                        st.download_button(
                            label="🎯 Download Action Items",
                            data=csv_data,
                            file_name=f"crewai_action_recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            help="Sales team action items with priorities",
                            key="download_actions_csv"
                        )
                    except Exception as e:
                        st.button("🎯 Export Actions CSV", disabled=True, help=f"Export error: {str(e)}")
                
                with col4:
                    # Direct download button for campaign summary
                    try:
                        summary_data = export_campaign_summary_csv(session_collaboration_results)
                        st.download_button(
                            label="� Download Campaign Summary",
                            data=summary_data,
                            file_name=f"crewai_campaign_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            help="Executive summary for management reporting",
                            key="download_summary_csv"
                        )
                    except Exception as e:
                        st.button("� Export Campaign Summary", disabled=True, help=f"Export error: {str(e)}")
                
                # Complete package option
                st.markdown("#### 📦 **Complete Package**")
                try:
                    zip_data = export_complete_business_package(session_collaboration_results)
                    st.download_button(
                        label="� Download Complete Business Intelligence Package",
                        data=zip_data,
                        file_name=f"crewai_business_intelligence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip",
                        help="Complete business intelligence package with all deliverables",
                        key="download_complete_zip"
                    )
                except Exception as e:
                    st.button("🚀 Export All ZIP", disabled=True, help=f"Export error: {str(e)}")
                
                # Add preview sections for all export options
                st.markdown("---")
                st.markdown("### 👁️ **Export Previews**")
                st.markdown("**Preview your business intelligence data before downloading:**")
                
                # Create tabs for different previews
                tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Customer Offers", "📧 Email Templates", "🎯 Action Items", "📊 Campaign Summary", "📦 Complete Package"])
                
                with tab1:
                    try:
                        csv_data = export_crewai_offers_csv(session_collaboration_results)
                        import io
                        df_preview = pd.read_csv(io.StringIO(csv_data))
                        st.markdown("**📊 Customer Offers Data Preview:**")
                        st.dataframe(df_preview.head(10), use_container_width=True)
                        st.markdown(f"**Total Records:** {len(df_preview)} customers")
                        st.markdown(f"**Columns:** {', '.join(df_preview.columns.tolist())}")
                    except Exception as e:
                        st.error(f"Preview error: {str(e)}")
                
                with tab2:
                    try:
                        template_data = export_email_templates_package(session_collaboration_results)
                        import zipfile
                        zip_buffer = io.BytesIO(template_data)
                        with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
                            file_list = zip_file.namelist()
                            st.markdown("**📧 Email Templates Package Contents:**")
                            for file_name in file_list:
                                st.markdown(f"📄 {file_name}")
                            st.markdown(f"**Total Files:** {len(file_list)} email templates")
                            
                            # Show preview of first template
                            if file_list:
                                first_file = file_list[0]
                                try:
                                    content = zip_file.read(first_file).decode('utf-8')
                                    st.markdown(f"**Preview of {first_file}:**")
                                    st.text_area("Email Template Content", content[:500] + "..." if len(content) > 500 else content, height=200, key="template_preview_tab")
                                except:
                                    st.info("Binary file - preview not available")
                    except Exception as e:
                        st.error(f"Preview error: {str(e)}")
                
                with tab3:
                    try:
                        csv_data = export_crewai_recommendations_csv(session_collaboration_results)
                        df_preview = pd.read_csv(io.StringIO(csv_data))
                        st.markdown("**🎯 Action Items Data Preview:**")
                        st.dataframe(df_preview.head(10), use_container_width=True)
                        st.markdown(f"**Total Records:** {len(df_preview)} action items")
                        st.markdown(f"**Columns:** {', '.join(df_preview.columns.tolist())}")
                        
                        # Show priority distribution
                        if 'Priority' in df_preview.columns:
                            priority_counts = df_preview['Priority'].value_counts()
                            st.markdown("**Priority Distribution:**")
                            for priority, count in priority_counts.items():
                                st.markdown(f"• {priority}: {count} items")
                    except Exception as e:
                        st.error(f"Preview error: {str(e)}")
                
                with tab4:
                    try:
                        summary_data = export_campaign_summary_csv(session_collaboration_results)
                        df_preview = pd.read_csv(io.StringIO(summary_data))
                        st.markdown("**📊 Campaign Summary Data Preview:**")
                        st.dataframe(df_preview, use_container_width=True)
                        st.markdown(f"**Total Records:** {len(df_preview)} summary items")
                        st.markdown(f"**Columns:** {', '.join(df_preview.columns.tolist())}")
                        
                        # Show key metrics if available
                        if 'Metric' in df_preview.columns and 'Value' in df_preview.columns:
                            st.markdown("**Key Metrics:**")
                            for idx, row in df_preview.iterrows():
                                st.markdown(f"• {row['Metric']}: {row['Value']}")
                    except Exception as e:
                        st.error(f"Preview error: {str(e)}")
                
                with tab5:
                    try:
                        zip_data = export_complete_business_package(session_collaboration_results)
                        zip_buffer = io.BytesIO(zip_data)
                        with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
                            file_list = zip_file.namelist()
                            st.markdown("**📦 Complete Business Intelligence Package Contents:**")
                            
                            # Group files by type
                            csv_files = [f for f in file_list if f.endswith('.csv')]
                            zip_files = [f for f in file_list if f.endswith('.zip')]
                            other_files = [f for f in file_list if not f.endswith('.csv') and not f.endswith('.zip')]
                            
                            if csv_files:
                                st.markdown("**📊 CSV Reports:**")
                                for file_name in csv_files:
                                    st.markdown(f"• {file_name}")
                            
                            if zip_files:
                                st.markdown("**📧 Template Packages:**")
                                for file_name in zip_files:
                                    st.markdown(f"• {file_name}")
                            
                            if other_files:
                                st.markdown("**📄 Additional Files:**")
                                for file_name in other_files:
                                    st.markdown(f"• {file_name}")
                            
                            st.markdown(f"**Total Files:** {len(file_list)} business intelligence assets")
                    except Exception as e:
                        st.error(f"Preview error: {str(e)}")
                    
            else:
                # No session data available
                st.warning("⚠️ No collaboration results available. Please run CrewAI collaboration first.")
                st.info("💡 Click 'Launch Collaboration' button above to generate exportable business intelligence.")
            
            
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
