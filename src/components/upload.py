"""
Upload page component for CSV file upload functionality
Enhanced implementation for Task 3 - CSV File Upload Component
"""

import streamlit as st
import pandas as pd
import os
import chardet
import tempfile
import shutil
from io import StringIO
from typing import Tuple, Dict, Any
from config.app_config import config

# File size limits (in bytes)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_PREVIEW_ROWS = 5

def detect_file_encoding(file_content: bytes) -> Any:
    """
    Automatically detect the encoding of a file using chardet
    
    Args:
        file_content: Raw bytes from the file
        
    Returns:
        dict: Detection result with encoding, confidence, and language
    """
    try:
        result = chardet.detect(file_content)
        return result
    except Exception as e:
        return {'encoding': None, 'confidence': 0, 'language': None, 'error': str(e)}

def convert_to_utf8(file_content: bytes, detected_encoding: str) -> tuple[bool, str, str]:
    """
    Convert file content from detected encoding to UTF-8
    
    Args:
        file_content: Raw bytes from the file
        detected_encoding: Encoding detected by chardet
        
    Returns:
        tuple: (success, message, utf8_content)
    """
    try:
        # Decode with detected encoding
        text_content = file_content.decode(detected_encoding)
        
        # Re-encode as UTF-8
        utf8_content = text_content.encode('utf-8').decode('utf-8')
        
        return True, f"Successfully converted from {detected_encoding} to UTF-8", utf8_content
        
    except Exception as e:
        return False, f"Failed to convert from {detected_encoding} to UTF-8: {str(e)}", ""

def auto_detect_and_correct_encoding(uploaded_file) -> tuple[bool, str, str, dict]:
    """
    Automatically detect and correct file encoding to UTF-8
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        tuple: (success, message, corrected_content, encoding_info)
    """
    try:
        # Read raw bytes
        file_content = uploaded_file.read()
        uploaded_file.seek(0)  # Reset file pointer
        
        # Detect encoding
        encoding_result = detect_file_encoding(file_content)
        detected_encoding = encoding_result.get('encoding')
        confidence = encoding_result.get('confidence', 0)
        
        if not detected_encoding:
            return False, "Could not detect file encoding", "", encoding_result
        
        # If already UTF-8 with high confidence, return as-is
        if detected_encoding.lower() in ['utf-8', 'ascii'] and confidence > 0.7:
            try:
                content = file_content.decode('utf-8')
                return True, f"File is already UTF-8 encoded (confidence: {confidence:.2f})", content, encoding_result
            except UnicodeDecodeError:
                pass  # Continue with conversion process
        
        # Convert to UTF-8
        success, message, utf8_content = convert_to_utf8(file_content, detected_encoding)
        
        if success:
            encoding_info = f"Detected: {detected_encoding} (confidence: {confidence:.2f})"
            full_message = f"{message}. {encoding_info}"
            return True, full_message, utf8_content, encoding_result
        else:
            return False, message, "", encoding_result
            
    except Exception as e:
        return False, f"Error in encoding detection/correction: {str(e)}", "", {}

def save_corrected_file(content: str, original_filename: str) -> tuple[bool, str, str]:
    """
    Save the corrected UTF-8 content to a new file
    
    Args:
        content: UTF-8 corrected content
        original_filename: Original filename for reference
        
    Returns:
        tuple: (success, message, new_filename)
    """
    try:
        # Create corrected filename
        name, ext = os.path.splitext(original_filename)
        corrected_filename = f"{name}_utf8_corrected{ext}"
        
        # Save to temporary location (in practice, you might want to save to a specific directory)
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix=ext, delete=False) as tmp_file:
            tmp_file.write(content)
            temp_path = tmp_file.name
        
        return True, f"Corrected file saved as: {corrected_filename}", corrected_filename
        
    except Exception as e:
        return False, f"Error saving corrected file: {str(e)}", ""

def validate_csv_file(uploaded_file, expected_columns=None, auto_correct_encoding=True):
    """
    Validate uploaded CSV file with automatic encoding detection and correction
    
    Args:
        uploaded_file: Streamlit uploaded file object
        expected_columns: List of expected column names (optional)
        auto_correct_encoding: Whether to use automatic encoding detection (default: True)
    
    Returns:
        tuple: (is_valid, message, dataframe)
    """
    if uploaded_file is None:
        return False, "No file uploaded", None
    
    if not uploaded_file.name.lower().endswith('.csv'):
        return False, "Please upload a CSV file", None
    
    # Check file size
    if uploaded_file.size > MAX_FILE_SIZE:
        return False, f"File size ({uploaded_file.size/1024/1024:.1f}MB) exceeds limit ({MAX_FILE_SIZE/1024/1024:.0f}MB)", None
    
    encoding_messages = []
    
    try:
        if auto_correct_encoding:
            # Use automatic encoding detection and correction
            success, encoding_message, corrected_content, encoding_info = auto_detect_and_correct_encoding(uploaded_file)
            
            if success:
                encoding_messages.append(f"🔧 {encoding_message}")
                # Parse CSV from corrected content
                df = pd.read_csv(StringIO(corrected_content))
            else:
                return False, f"Encoding detection failed: {encoding_message}", None
        else:
            # Use original method (UTF-8 first, then fallbacks)
            try:
                string_data = uploaded_file.read().decode('utf-8')
                df = pd.read_csv(StringIO(string_data))
                encoding_messages.append("✅ UTF-8 encoding confirmed")
            except UnicodeDecodeError:
                # Try with GBK encoding as fallback
                uploaded_file.seek(0)
                string_data = uploaded_file.read().decode('gbk')
                df = pd.read_csv(StringIO(string_data))
                encoding_messages.append("🔧 Converted from GBK to UTF-8")
        
        # Reset file pointer for potential reuse
        uploaded_file.seek(0)
        
        # Basic validation
        if df.empty:
            return False, "File is empty", None
        
        # Check for expected columns if provided
        if expected_columns:
            missing_columns = set(expected_columns) - set(df.columns)
            if missing_columns:
                return False, f"Missing required columns: {', '.join(missing_columns)}", None
        
        # Combine messages
        success_message = "File validation successful"
        if encoding_messages:
            success_message += f" ({', '.join(encoding_messages)})"
        
        return True, success_message, df
        
    except Exception as e:
        return False, f"Error reading file: {str(e)}", None

def load_sample_data(file_path, auto_detect_encoding=True):
    """
    Load sample data from project files with automatic encoding detection
    
    Args:
        file_path: Path to the sample data file
        auto_detect_encoding: Whether to use automatic encoding detection (default: True)
        
    Returns:
        tuple: (success, message, dataframe)
    """
    try:
        if not os.path.exists(file_path):
            return False, f"Sample file not found: {file_path}", None
            
        if auto_detect_encoding:
            # Use automatic encoding detection
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            encoding_result = detect_file_encoding(file_content)
            detected_encoding = encoding_result.get('encoding', 'utf-8')
            confidence = encoding_result.get('confidence', 0)
            
            if detected_encoding:
                try:
                    df = pd.read_csv(file_path, encoding=detected_encoding)
                    message = f"Sample data loaded successfully (detected: {detected_encoding}, confidence: {confidence:.2f})"
                    return True, message, df
                except Exception:
                    pass  # Fall back to manual detection
        
        # Manual fallback method
        try:
            # Try UTF-8 first
            df = pd.read_csv(file_path, encoding='utf-8')
            return True, "Sample data loaded successfully (UTF-8)", df
        except UnicodeDecodeError:
            try:
                # Try GBK encoding as fallback
                df = pd.read_csv(file_path, encoding='gbk')
                return True, "Sample data loaded successfully (GBK encoding)", df
            except Exception as e:
                return False, f"Error with file encoding: {str(e)}", None
        
    except Exception as e:
        return False, f"Error loading sample data: {str(e)}", None

def display_data_preview(df, title, max_rows=MAX_PREVIEW_ROWS):
    """Display a preview of the dataframe"""
    st.markdown(f"#### 📊 {title}")
    
    # Show basic info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows", len(df))
    with col2:
        st.metric("Columns", len(df.columns))
    with col3:
        st.metric("Size", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    
    # Show column info
    st.markdown("**Columns:**")
    st.write(", ".join(df.columns.tolist()))
    
    # Show preview
    st.markdown(f"**First {min(max_rows, len(df))} rows:**")
    st.dataframe(df.head(max_rows), use_container_width=True)
    
    # Show data types
    with st.expander("📋 Column Details"):
        col_info = pd.DataFrame({
            'Column': df.columns,
            'Data Type': df.dtypes.astype(str),
            'Non-Null Count': df.count(),
            'Null Count': df.isnull().sum()
        })
        st.dataframe(col_info, use_container_width=True)

def render_upload_page():
    """Render the data upload page"""
    
    st.markdown("## 📂 Upload Customer Data")
    
    st.markdown("""
    Upload your customer data and purchase history files to begin the AI-powered lead generation analysis. 
    All data will be immediately pseudonymized for privacy protection.
    """)
    
    # Expected columns for validation
    CUSTOMER_COLUMNS = ['Account ID', 'Family Name', 'Given Name', 'Gender', 'Email', 
                       'Birth Date', 'Customer Type', 'Customer Class', 'Brand']
    PURCHASE_COLUMNS = ['Account ID']  # More flexible for purchase history
    
    # File upload tabs
    tab1, tab2, tab3 = st.tabs(["📊 Customer Data", "📈 Purchase History", "📂 Sample Data"])
    
    with tab1:
        st.markdown("### 📊 Customer Profile Data")
        st.markdown("Upload customer demographics, account information, and contact details.")
        
        # Encoding options
        with st.expander("🔧 Advanced Encoding Options", expanded=False):
            auto_correct_encoding = st.checkbox(
                "Automatic encoding detection and correction",
                value=True,
                help="Automatically detect file encoding (UTF-8, GBK, etc.) and convert to UTF-8 for proper Chinese character display"
            )
            
            if auto_correct_encoding:
                st.info("✨ **Smart Encoding Detection**: Files will be automatically analyzed and converted to UTF-8 for optimal Chinese character support.")
            else:
                st.warning("⚠️ **Manual Mode**: Files must be UTF-8 encoded. GBK fallback available.")
        
        uploaded_customer_file = st.file_uploader(
            "Choose customer data CSV file",
            type=['csv'],
            help="Upload customer profile and demographic data (Max 10MB)",
            key="customer_upload"
        )
        
        if uploaded_customer_file:
            with st.spinner("Validating and processing customer data..."):
                is_valid, message, df = validate_csv_file(
                    uploaded_customer_file, 
                    CUSTOMER_COLUMNS, 
                    auto_correct_encoding=auto_correct_encoding
                )
                
                if is_valid:
                    st.success(f"✅ {message}")
                    display_data_preview(df, "Customer Data Preview")
                    
                    # Store in session state for later use
                    st.session_state['customer_data'] = df
                    st.session_state['customer_filename'] = uploaded_customer_file.name
                    
                    # Privacy reminder
                    st.info("🔒 Data will be pseudonymized before any AI processing")
                    
                else:
                    st.error(f"❌ {message}")
                    if 'customer_data' in st.session_state:
                        del st.session_state['customer_data']
    
    with tab2:
        st.markdown("### 📈 Purchase History Data")
        st.markdown("Upload transaction records, service usage, and engagement metrics.")
        
        # Encoding options for purchase history
        with st.expander("🔧 Advanced Encoding Options", expanded=False):
            auto_correct_encoding_purchase = st.checkbox(
                "Automatic encoding detection and correction",
                value=True,
                help="Automatically detect file encoding (UTF-8, GBK, etc.) and convert to UTF-8 for proper Chinese character display",
                key="purchase_encoding_option"
            )
            
            if auto_correct_encoding_purchase:
                st.info("✨ **Smart Encoding Detection**: Files will be automatically analyzed and converted to UTF-8 for optimal Chinese character support.")
            else:
                st.warning("⚠️ **Manual Mode**: Files must be UTF-8 encoded. GBK fallback available.")
        
        uploaded_purchase_file = st.file_uploader(
            "Choose purchase history CSV file", 
            type=['csv'],
            help="Upload transaction and engagement data (Max 10MB)",
            key="purchase_upload"
        )
        
        if uploaded_purchase_file:
            with st.spinner("Validating and processing purchase history..."):
                is_valid, message, df = validate_csv_file(
                    uploaded_purchase_file, 
                    PURCHASE_COLUMNS, 
                    auto_correct_encoding=auto_correct_encoding_purchase
                )
                
                if is_valid:
                    st.success(f"✅ {message}")
                    display_data_preview(df, "Purchase History Preview")
                    
                    # Store in session state for later use
                    st.session_state['purchase_data'] = df
                    st.session_state['purchase_filename'] = uploaded_purchase_file.name
                    
                    # Privacy reminder
                    st.info("🔒 Data will be pseudonymized before any AI processing")
                    
                else:
                    st.error(f"❌ {message}")
                    if 'purchase_data' in st.session_state:
                        del st.session_state['purchase_data']
    
    with tab3:
        st.markdown("### 📂 Sample Data Available")
        st.markdown("Preview and use the provided sample datasets to test the system.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Load Customer Sample", type="secondary"):
                with st.spinner("Loading customer sample data..."):
                    is_valid, message, df = load_sample_data("sample-customer-data-20250715.csv")
                    
                    if is_valid:
                        st.success(f"✅ {message}")
                        display_data_preview(df, "Sample Customer Data")
                        
                        # Option to use this data
                        if st.button("Use This Sample Data", key="use_customer_sample"):
                            st.session_state['customer_data'] = df
                            st.session_state['customer_filename'] = "sample-customer-data-20250715.csv"
                            st.success("Sample customer data loaded for analysis!")
                            st.rerun()
                    else:
                        st.error(f"❌ {message}")
        
        with col2:
            if st.button("📈 Load Purchase Sample", type="secondary"):
                with st.spinner("Loading purchase sample data..."):
                    is_valid, message, df = load_sample_data("sample_purchase_history.csv")
                    
                    if is_valid:
                        st.success(f"✅ {message}")
                        display_data_preview(df, "Sample Purchase History")
                        
                        # Option to use this data
                        if st.button("Use This Sample Data", key="use_purchase_sample"):
                            st.session_state['purchase_data'] = df
                            st.session_state['purchase_filename'] = "sample_purchase_history.csv"
                            st.success("Sample purchase data loaded for analysis!")
                            st.rerun()
                    else:
                        st.error(f"❌ {message}")
    
    # Data Status Summary
    st.markdown("---")
    st.markdown("### 📊 Current Data Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'customer_data' in st.session_state:
            st.success(f"✅ Customer Data: {st.session_state.get('customer_filename', 'Unknown')}")
            st.caption(f"Rows: {len(st.session_state['customer_data'])}")
        else:
            st.warning("⏳ No customer data uploaded")
    
    with col2:
        if 'purchase_data' in st.session_state:
            st.success(f"✅ Purchase Data: {st.session_state.get('purchase_filename', 'Unknown')}")
            st.caption(f"Rows: {len(st.session_state['purchase_data'])}")
        else:
            st.warning("⏳ No purchase data uploaded")
    
    # Next Steps
    if 'customer_data' in st.session_state and 'purchase_data' in st.session_state:
        st.success("🎉 Both datasets uploaded! Ready to proceed to data processing.")
        
        if st.button("🚀 Proceed to Analysis", type="primary"):
            st.info("Data processing and AI analysis will be implemented in upcoming tasks!")
            # This will link to the next page/component in future tasks
    else:
        st.info("📋 Upload both customer and purchase data files to continue with the analysis.")
    
    # Privacy and Security Notice
    st.markdown("---")
    st.markdown("### 🔒 Privacy & Security")
    st.warning("""
    **Privacy Protection Measures:**
    - All uploaded data is processed locally on your device
    - Personal information will be pseudonymized before AI analysis
    - No raw customer data is sent to external AI services
    - Data is not permanently stored unless explicitly saved
    """)
    
    # File Requirements
    with st.expander("📋 File Requirements & Format Guidelines"):
        st.markdown("""
        **Customer Data CSV Requirements:**
        - Must include: Account ID, Family Name, Given Name, Gender, Email, Birth Date, Customer Type, Customer Class, Brand
        - Optional: Chinese Given Name, ID Type, ID Number, Company Name
        - File size limit: 10MB
        - Encoding: UTF-8
        
        **Purchase History CSV Requirements:**
        - Must include: Account ID
        - Recommended: Purchase History columns, Engagement Data
        - File size limit: 10MB
        - Encoding: UTF-8
        
        **General Guidelines:**
        - Use standard CSV format with comma separators
        - Include column headers in the first row
        - Ensure Account IDs match between customer and purchase files
        """) 