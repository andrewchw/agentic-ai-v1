"""
Model Selection Component for Streamlit
======================================

Provides a user interface for selecting and managing free AI models
with real-time status monitoring and automatic failover configuration.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
from typing import Dict, Any

from src.utils.free_models_manager import get_free_models_manager
from src.utils.smart_litellm_client import get_smart_litellm_client

def render_model_selection_sidebar():
    """Render model selection and status in the sidebar"""
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 AI Model Configuration")
    
    models_manager = get_free_models_manager()
    smart_client = get_smart_litellm_client()
    
    # Get current models and status
    available_models = models_manager.get_available_models()
    current_model = models_manager.get_current_model()
    
    # Model selection dropdown
    model_names = {key: f"{model.name} ({model.provider})" 
                   for key, model in available_models.items()}
    
    current_key = models_manager.current_model_id
    
    selected_key = st.sidebar.selectbox(
        "🎯 Preferred Model",
        options=list(model_names.keys()),
        index=list(model_names.keys()).index(current_key) if current_key in model_names else 0,
        format_func=lambda x: model_names[x],
        help="Select your preferred free AI model. The system will automatically fallback to alternatives if needed."
    )
    
    # Save preference if changed
    if selected_key != current_key:
        models_manager.save_user_preference(selected_key)
        st.sidebar.success(f"✅ Switched to {available_models[selected_key].name}")
        st.rerun()
    
    # Current model info
    current_model = available_models[selected_key]
    
    with st.sidebar.expander("📊 Current Model Details", expanded=False):
        st.write(f"**Name:** {current_model.name}")
        st.write(f"**Provider:** {current_model.provider}")
        st.write(f"**Context:** {current_model.context_window:,} tokens")
        st.write(f"**Max Output:** {current_model.max_tokens:,} tokens")
        st.write(f"**Good For:** {', '.join(current_model.good_for)}")
        
        # Health status
        is_available = models_manager._is_model_available(current_model)
        if is_available:
            st.success("🟢 Available")
        else:
            st.error(f"🔴 Issues (Failures: {current_model.failure_count})")
    
    # Quick actions
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🔄 Reset All", help="Reset failure counts for all models"):
            models_manager.reset_model_failures()
            st.success("Reset complete!")
            st.rerun()
    
    with col2:
        if st.button("📊 Status", help="View detailed model status"):
            st.session_state.show_model_status = True

def render_model_status_page():
    """Render detailed model status page"""
    
    st.title("🤖 AI Models Status Dashboard")
    st.markdown("Monitor the health and performance of all available free AI models")
    
    models_manager = get_free_models_manager()
    smart_client = get_smart_litellm_client()
    
    # Get comprehensive status
    status_summary = models_manager.get_model_status_summary()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Models", 
            status_summary["total_models"],
            help="Total number of configured free models"
        )
    
    with col2:
        st.metric(
            "Available Models", 
            status_summary["available_models"],
            delta=f"{status_summary['available_models'] - (status_summary['total_models'] - status_summary['available_models'])}",
            help="Models currently available for use"
        )
    
    with col3:
        current_info = smart_client.get_model_info()
        st.metric(
            "Current Model", 
            current_info["current_model"],
            help="Currently selected model"
        )
    
    with col4:
        availability_pct = (status_summary["available_models"] / status_summary["total_models"]) * 100
        st.metric(
            "Availability", 
            f"{availability_pct:.0f}%",
            delta=f"{availability_pct - 80:.0f}%" if availability_pct >= 80 else f"{availability_pct - 80:.0f}%",
            help="Percentage of models currently available"
        )
    
    # Models table
    st.markdown("### 📋 Models Overview")
    
    models_data = []
    for key, model in models_manager.get_available_models().items():
        is_current = key == models_manager.current_model_id
        is_available = models_manager._is_model_available(model)
        
        models_data.append({
            "Model": model.name,
            "Provider": model.provider,
            "Status": "🟢 Available" if is_available else f"🔴 Issues ({model.failure_count} failures)",
            "Current": "⭐ Yes" if is_current else "No",
            "Context": f"{model.context_window:,}",
            "Good For": ", ".join(model.good_for[:2]) + ("..." if len(model.good_for) > 2 else ""),
            "Last Used": model.last_used.split('T')[0] if model.last_used else "Never",
            "Failures": model.failure_count
        })
    
    df = pd.DataFrame(models_data)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.TextColumn("Status", width="medium"),
            "Context": st.column_config.TextColumn("Context Window", width="small"),
            "Failures": st.column_config.NumberColumn("Failures", min_value=0, max_value=100)
        }
    )
    
    # Availability chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Model Availability")
        
        available_count = sum(1 for model in models_manager.get_available_models().values() 
                             if models_manager._is_model_available(model))
        unavailable_count = len(models_manager.get_available_models()) - available_count
        
        fig_pie = px.pie(
            values=[available_count, unavailable_count],
            names=["Available", "Issues"],
            color_discrete_map={"Available": "#00D4AA", "Issues": "#FF6B6B"},
            title="Model Availability Status"
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.markdown("### 🚨 Failure Analysis")
        
        failure_data = []
        for model in models_manager.get_available_models().values():
            if model.failure_count > 0:
                failure_data.append({
                    "Model": model.name,
                    "Failures": model.failure_count
                })
        
        if failure_data:
            df_failures = pd.DataFrame(failure_data)
            fig_bar = px.bar(
                df_failures,
                x="Model",
                y="Failures",
                title="Failure Count by Model",
                color="Failures",
                color_continuous_scale="Reds"
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.success("🎉 No model failures recorded!")
    
    # Test model functionality
    st.markdown("### 🧪 Test Model Functionality")
    
    test_message = st.text_input(
        "Test Message",
        value="Hello! Please respond with a simple greeting.",
        help="Send a test message to verify model functionality"
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧠 Test Current Model", type="primary"):
            with st.spinner("Testing current model..."):
                try:
                    response = smart_client.completion(
                        messages=[{"role": "user", "content": test_message}],
                        use_case="general",
                        max_tokens=100
                    )
                    st.success("✅ Current model working!")
                    st.write("**Response:**", response.choices[0].message.content)
                    
                except Exception as e:
                    st.error(f"❌ Current model failed: {str(e)}")
    
    with col2:
        if st.button("🔄 Test All Models"):
            with st.spinner("Testing all available models..."):
                results = []
                for key, model in models_manager.get_available_models().items():
                    if models_manager._is_model_available(model):
                        try:
                            # Temporarily switch to this model for testing
                            original_model = models_manager.current_model_id
                            models_manager.current_model_id = key
                            
                            response = smart_client.completion(
                                messages=[{"role": "user", "content": test_message}],
                                use_case="general",
                                max_tokens=50
                            )
                            
                            results.append({
                                "Model": model.name,
                                "Status": "✅ Success",
                                "Response": response.choices[0].message.content[:100] + "..."
                            })
                            
                            # Restore original model
                            models_manager.current_model_id = original_model
                            
                        except Exception as e:
                            results.append({
                                "Model": model.name,
                                "Status": f"❌ Failed: {str(e)[:50]}...",
                                "Response": "N/A"
                            })
                
                if results:
                    st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
    
    with col3:
        if st.button("📊 Refresh Status"):
            st.rerun()
    
    # Advanced configuration
    with st.expander("⚙️ Advanced Configuration", expanded=False):
        st.markdown("#### Failure Handling Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Failure Threshold:** {models_manager.failure_threshold} attempts")
            st.info(f"**Cooldown Period:** {models_manager.cooldown_minutes} minutes")
        
        with col2:
            if st.button("Reset Specific Model"):
                reset_model = st.selectbox(
                    "Select Model to Reset",
                    options=list(models_manager.get_available_models().keys()),
                    format_func=lambda x: models_manager.get_available_models()[x].name
                )
                
                if st.button(f"Reset {models_manager.get_available_models()[reset_model].name}"):
                    models_manager.reset_model_failures(reset_model)
                    st.success(f"Reset failure count for {models_manager.get_available_models()[reset_model].name}")
                    st.rerun()

def render_model_selection_in_main():
    """Render model selection component in main area (for full-page display)"""
    
    st.markdown("### 🤖 AI Model Configuration")
    
    models_manager = get_free_models_manager()
    
    # Get current models and status
    available_models = models_manager.get_available_models()
    
    # Create columns for layout
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Model selection
        model_options = []
        model_keys = []
        
        for key, model in available_models.items():
            is_available = models_manager._is_model_available(model)
            status_icon = "🟢" if is_available else "🔴"
            
            display_name = f"{status_icon} {model.name} ({model.provider})"
            model_options.append(display_name)
            model_keys.append(key)
        
        current_index = model_keys.index(models_manager.current_model_id) if models_manager.current_model_id in model_keys else 0
        
        selected_index = st.selectbox(
            "Select AI Model",
            range(len(model_options)),
            index=current_index,
            format_func=lambda x: model_options[x],
            help="Choose your preferred free AI model"
        )
        
        selected_key = model_keys[selected_index]
        
        # Update preference if changed
        if selected_key != models_manager.current_model_id:
            models_manager.save_user_preference(selected_key)
            st.success(f"✅ Switched to {available_models[selected_key].name}")
    
    with col2:
        # Current model stats
        current_model = available_models[selected_key]
        st.metric("Context Window", f"{current_model.context_window:,}")
        st.metric("Max Tokens", f"{current_model.max_tokens:,}")
    
    with col3:
        # Actions
        if st.button("🔄 Reset Failures", use_container_width=True):
            models_manager.reset_model_failures()
            st.success("All models reset!")
            st.rerun()
        
        if st.button("📊 Full Status", use_container_width=True):
            st.session_state.show_model_status = True
            st.rerun()
    
    # Model details
    selected_model = available_models[selected_key]
    
    with st.expander("📋 Model Details", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Provider:** {selected_model.provider}")
            st.write(f"**Description:** {selected_model.description}")
            st.write(f"**Good For:** {', '.join(selected_model.good_for)}")
        
        with col2:
            is_available = models_manager._is_model_available(selected_model)
            st.write(f"**Status:** {'🟢 Available' if is_available else f'🔴 Issues ({selected_model.failure_count} failures)'}")
            st.write(f"**Last Used:** {selected_model.last_used.split('T')[0] if selected_model.last_used else 'Never'}")
            st.write(f"**Rate Limit Info:** {selected_model.rate_limit_info}")


# Page state management for model status
def init_model_selection_state():
    """Initialize session state for model selection"""
    if 'show_model_status' not in st.session_state:
        st.session_state.show_model_status = False

def should_show_model_status():
    """Check if model status page should be shown"""
    return st.session_state.get('show_model_status', False)

def hide_model_status():
    """Hide model status page"""
    st.session_state.show_model_status = False
