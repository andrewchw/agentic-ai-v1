"""
Results page component for displaying AI analysis results and data merging
Enhanced with data merging functionality in Task 6.3
"""

import streamlit as st
import pandas as pd
from src.utils.data_merging import DataMerger, MergeStrategy, MergeResult
from typing import Dict, Any, Optional


def render_results_page():
    """Render the analysis results page with data merging functionality"""

    st.markdown("## 📊 Analysis Results")
    
    # Data Merging Section (Task 6.3)
    st.markdown("### 🔗 Data Merging & Alignment")
    
    # Check if both datasets are available
    has_customer_data = "customer_data" in st.session_state
    has_purchase_data = "purchase_data" in st.session_state
    
    if has_customer_data and has_purchase_data:
        render_data_merging_section()
    else:
        st.warning("⚠️ Data merging requires both customer and purchase data to be uploaded first.")
        
        missing = []
        if not has_customer_data:
            missing.append("Customer Data")
        if not has_purchase_data:
            missing.append("Purchase Data")
            
        st.info(f"📤 Missing: {', '.join(missing)}. Please upload data in the Upload Data page.")
    
    st.markdown("---")

    st.info(
        "📋 **Note:** This page will be fully implemented in Task 12 - "
        "Results Dashboard Implementation"
    )

    # Mock results structure
    st.markdown("### 🎯 Lead Analysis Summary")

    # Mock metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Customers Analyzed", value="0", help="Number of customer records processed"
        )

    with col2:
        st.metric(
            label="High Priority Leads", value="0", help="Customers with high conversion potential"
        )

    with col3:
        st.metric(label="Recommended Actions", value="0", help="AI-generated sales recommendations")

    with col4:
        st.metric(label="Avg. Lead Score", value="0.0", help="Average lead prioritization score")

    st.markdown("---")

    # Mock results table
    st.markdown("### 📋 Prioritized Lead Recommendations")

    st.markdown(
        """
    **Preview of Results Table:**

    | Customer ID | Priority | Last Purchase | Engagement | Suggested Action | Lead Score |
    |-------------|----------|---------------|------------|------------------|------------|
    | CUST_001 | 🔴 High | 30 days ago | Active | 5G Plan Upgrade | 8.5 |
    | CUST_002 | 🟡 Medium | 60 days ago | Moderate | Data Add-on | 6.2 |
    | CUST_003 | 🟢 Low | 120 days ago | Low | Retention Call | 3.8 |
    """
    )


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
            help="How to handle records that don't match between datasets"
        )
        
    with col2:
        show_sensitive = st.toggle(
            "Show Sensitive Data",
            value=False,
            help="Show unmasked sensitive information in merged results",
            key="results_privacy_toggle"
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
            show_sensitive=show_sensitive
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
            "Merged Records", 
            metadata.get("merged_shape", [0, 0])[0],
            help="Total number of records after merging"
        )
    
    with col2:
        st.metric(
            "Quality Score", 
            f"{quality_report.get('quality_score', 0.0):.2f}",
            help="Data quality score (0.0 - 1.0)"
        )
    
    with col3:
        st.metric(
            "Processing Time", 
            f"{metadata.get('processing_time_seconds', 0.0):.3f}s",
            help="Time taken to complete the merge"
        )
    
    with col4:
        merge_strategy = metadata.get('merge_strategy', 'unknown')
        st.metric(
            "Merge Strategy", 
            merge_strategy.title(),
            help="Strategy used for the merge operation"
        )
    
    # Data quality information
    if quality_report:
        st.markdown("#### 📋 Data Quality Report")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Customer Records:** {quality_report.get('total_customer_records', 0)}")
            st.info(f"**Purchase Records:** {quality_report.get('total_purchase_records', 0)}")
            st.info(f"**Matched Records:** {quality_report.get('matched_records', 0)}")
            
        with col2:
            unmatched_customer = quality_report.get('unmatched_customer_ids', [])
            unmatched_purchase = quality_report.get('unmatched_purchase_ids', [])
            
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
            show_sensitive_data = metadata.get('show_sensitive', False)
        
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
        st.dataframe(
            display_data.head(preview_rows), 
            use_container_width=True,
            height=400
        )
        
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
                use_show_sensitive = metadata.get('show_sensitive', False)
                
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
                    mime="text/csv"
                )
    
    with col2:
        if st.button("📋 View Quality Report"):
            st.json(quality_report)
    
    with col3:
        if st.button("🔧 View Metadata"):
            st.json(metadata)

    st.info("Actual results will appear here after data upload and AI analysis")

    # Mock filters and controls
    st.markdown("### 🔧 Analysis Controls")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"], disabled=True)

    with col2:
        st.selectbox("Sort by", ["Lead Score", "Last Purchase", "Engagement"], disabled=True)

    with col3:
        st.button("📥 Export Results", disabled=True)

    # Three HK specific offers preview
    st.markdown("---")
    st.markdown("### 🎯 Three HK Offer Categories")

    offer_categories = [
        "📱 Device Upgrade Offers",
        "📡 5G Plan Upsells",
        "📊 Data Add-on Promotions",
        "👨‍👩‍👧‍👦 Family Plan Proposals",
        "📺 Streaming Service Bundles",
        "🛡️ Mobile Insurance Offers",
        "🌍 International Roaming Packs",
        "⌚ Smartwatch Plans",
        "🎁 Loyalty Rewards",
        "🔄 Retention Campaigns",
    ]

    cols = st.columns(2)
    for i, offer in enumerate(offer_categories):
        with cols[i % 2]:
            st.info(f"{offer} - *Coming in Task 11*")

    # Development roadmap
    st.markdown("---")
    st.markdown("### 🚧 Development Roadmap for Results")

    st.markdown(
        """
    **Task 9-12 will build:**
    - ✅ AI agent analysis engine
    - ✅ Lead scoring algorithms
    - ✅ Three HK offer matching
    - ✅ Interactive results dashboard
    - ✅ Export and reporting features
    """
    )
