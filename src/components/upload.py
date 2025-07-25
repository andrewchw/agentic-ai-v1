"""
Upload page component for CSV file upload functionality
Enhanced implementation for Task 3 - CSV File Upload Component with Privacy Pipeline Integration
"""

import streamlit as st
import pandas as pd
import os
import chardet
import tempfile
from io import StringIO
from typing import Tuple, Dict, Any
from src.utils.privacy_pipeline import privacy_pipeline, PipelineResult
from src.utils.product_catalog_db import catalog_db, get_catalog_stats, is_catalog_available

# File size limits (in bytes)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_PREVIEW_ROWS = 5


def process_data_through_privacy_pipeline(
    df: pd.DataFrame, identifier: str, filename: str
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Process uploaded data through the complete privacy pipeline.

    Args:
        df: DataFrame with potentially sensitive data
        identifier: Unique identifier for this dataset
        filename: Original filename for metadata

    Returns:
        Tuple of (success, message, processed_data_dict)
    """
    try:
        # Create metadata for processing
        metadata = {
            "filename": filename,
            "uploaded_at": pd.Timestamp.now().isoformat(),
            "original_shape": df.shape,
            "original_columns": list(df.columns),
        }

        # Process through privacy pipeline
        with st.spinner("🔒 Processing data through privacy pipeline..."):
            result: PipelineResult = privacy_pipeline.process_upload(df, identifier, metadata)

        if result.success:
            # Prepare processed data for session state
            processed_data = {
                "original_data": df,  # Keep for reference (will be encrypted)
                "pseudonymized_data": result.pseudonymized_data,  # For external LLM processing
                "display_data": result.display_data,  # For UI display with masking
                "storage_key": result.storage_key,  # Reference to encrypted storage
                "metadata": result.metadata,
                "filename": filename,
                "processed_at": pd.Timestamp.now().isoformat(),
            }

            return True, result.message, processed_data
        else:
            error_msg = f"Privacy pipeline processing failed: {result.message}"
            if result.errors:
                error_msg += f" Errors: {'; '.join(result.errors)}"
            return False, error_msg, {}

    except Exception as e:
        return False, f"Error processing data through privacy pipeline: {str(e)}", {}


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
        return {"encoding": None, "confidence": 0, "language": None, "error": str(e)}


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
        utf8_content = text_content.encode("utf-8").decode("utf-8")

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
        detected_encoding = encoding_result.get("encoding")
        confidence = encoding_result.get("confidence", 0)

        if not detected_encoding:
            return False, "Could not detect file encoding", "", encoding_result

        # If already UTF-8 with high confidence, return as-is
        if detected_encoding.lower() in ["utf-8", "ascii"] and confidence > 0.7:
            try:
                content = file_content.decode("utf-8")
                return (
                    True,
                    f"File is already UTF-8 encoded (confidence: {confidence:.2f})",
                    content,
                    encoding_result,
                )
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
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=ext, delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_file.name

        return True, f"Corrected file saved as: {corrected_filename}", corrected_filename

    except Exception as e:
        return False, f"Error saving corrected file: {str(e)}", ""


def validate_flexible_columns(df_columns, expected_column_groups):
    """
    Validate columns with flexible naming (supports both spaces and underscores)
    
    Args:
        df_columns: List of actual column names in the DataFrame
        expected_column_groups: List of lists, each containing alternative names for a required column
        
    Returns:
        tuple: (is_valid, missing_columns_list)
    """
    missing_columns = []
    
    for column_group in expected_column_groups:
        # Check if any variant of the column exists
        if isinstance(column_group, list):
            found = any(col in df_columns for col in column_group)
            if not found:
                missing_columns.append(column_group[0])  # Use the first variant as the "primary" name
        else:
            # Single column name
            if column_group not in df_columns:
                missing_columns.append(column_group)
    
    return len(missing_columns) == 0, missing_columns


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

    if not uploaded_file.name.lower().endswith(".csv"):
        return False, "Please upload a CSV file", None

    # Check file size
    if uploaded_file.size > MAX_FILE_SIZE:
        return (
            False,
            f"File size ({uploaded_file.size/1024/1024:.1f}MB) exceeds limit ({MAX_FILE_SIZE/1024/1024:.0f}MB)",
            None,
        )

    encoding_messages = []

    try:
        if auto_correct_encoding:
            # Use automatic encoding detection and correction
            success, encoding_message, corrected_content, encoding_info = auto_detect_and_correct_encoding(
                uploaded_file
            )

            if success:
                encoding_messages.append(f"🔧 {encoding_message}")
                # Parse CSV from corrected content
                df = pd.read_csv(StringIO(corrected_content))
            else:
                return False, f"Encoding detection failed: {encoding_message}", None
        else:
            # Use original method (UTF-8 first, then fallbacks)
            try:
                string_data = uploaded_file.read().decode("utf-8")
                df = pd.read_csv(StringIO(string_data))
                encoding_messages.append("✅ UTF-8 encoding confirmed")
            except UnicodeDecodeError:
                # Try with GBK encoding as fallback
                uploaded_file.seek(0)
                string_data = uploaded_file.read().decode("gbk")
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
            with open(file_path, "rb") as f:
                file_content = f.read()

            encoding_result = detect_file_encoding(file_content)
            detected_encoding = encoding_result.get("encoding", "utf-8")
            confidence = encoding_result.get("confidence", 0)

            if detected_encoding:
                try:
                    df = pd.read_csv(file_path, encoding=detected_encoding)
                    message = (
                        f"Sample data loaded successfully (detected: {detected_encoding}, "
                        f"confidence: {confidence:.2f})"
                    )
                    return True, message, df
                except Exception:
                    pass  # Fall back to manual detection

        # Manual fallback method
        try:
            # Try UTF-8 first
            df = pd.read_csv(file_path, encoding="utf-8")
            return True, "Sample data loaded successfully (UTF-8)", df
        except UnicodeDecodeError:
            try:
                # Try GBK encoding as fallback
                df = pd.read_csv(file_path, encoding="gbk")
                return True, "Sample data loaded successfully (GBK encoding)", df
            except Exception as e:
                return False, f"Error with file encoding: {str(e)}", None

    except Exception as e:
        return False, f"Error loading sample data: {str(e)}", None


def display_data_preview(processed_data_dict, title, max_rows=MAX_PREVIEW_ROWS):
    """Display a preview of the processed dataframe with privacy controls and pipeline information"""
    st.markdown(f"#### 📊 {title}")

    # Extract data from processed dict
    original_df = processed_data_dict.get("original_data")
    display_df = processed_data_dict.get("display_data")
    metadata = processed_data_dict.get("metadata", {})

    if original_df is None or display_df is None:
        st.error("❌ Processed data not available")
        return

    # Show basic info and privacy controls
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Rows", len(original_df))
    with col2:
        st.metric("Columns", len(original_df.columns))
    with col3:
        st.metric("Size", f"{original_df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    with col4:
        # Privacy toggle control
        show_sensitive = st.toggle(
            "Show Sensitive Data",
            value=False,
            help="Toggle to show/hide sensitive information",
            key=f"privacy_toggle_{title}",
        )

    # Use appropriate data based on privacy setting
    if show_sensitive:
        preview_df = original_df
        st.success("👁️ Showing original data (sensitive data visible)")
    else:
        preview_df = display_df
        st.info("🔒 Showing privacy-protected data (PII masked)")

    # Show privacy pipeline information
    if metadata.get("pii_fields_identified"):
        pii_fields = metadata["pii_fields_identified"]
        st.info(f"🔍 Privacy Analysis: {len(pii_fields)} PII fields identified: {', '.join(pii_fields[:5])}")
        if len(pii_fields) > 5:
            st.caption(f"... and {len(pii_fields) - 5} more fields")

    # Show column info
    st.markdown("**Columns:**")
    st.write(", ".join(original_df.columns.tolist()))

    # Show preview
    st.markdown(f"**First {min(max_rows, len(preview_df))} rows:**")
    st.dataframe(preview_df.head(max_rows), use_container_width=True)

    # Show data types and privacy details
    with st.expander("📋 Column Details & Privacy Analysis"):
        col_info = pd.DataFrame(
            {
                "Column": original_df.columns,
                "Data Type": original_df.dtypes.astype(str),
                "Non-Null Count": original_df.count(),
                "Null Count": original_df.isnull().sum(),
            }
        )

        # Add PII identification results if available
        if metadata.get("identification_results"):
            identification_results = metadata["identification_results"]
            pii_info = []
            for col in original_df.columns:
                if col in identification_results:
                    result = identification_results[col]
                    if result["is_sensitive"]:
                        pii_info.append(f"{result['field_type']} (conf: {result['confidence']:.2f})")
                    else:
                        pii_info.append("Non-PII")
                else:
                    pii_info.append("Unknown")
            col_info["PII Classification"] = pii_info

        st.dataframe(col_info, use_container_width=True)

        # Show processing statistics
        if metadata.get("processing_stats"):
            stats = metadata["processing_stats"]
            st.markdown("**Processing Performance:**")
            st.caption(f"Total processing time: {stats['processing_time_seconds']:.3f}s")
            st.caption(
                f"PII fields processed: {stats['pii_fields_identified']} identified, "
                f"{stats['pii_fields_pseudonymized']} pseudonymized, "
                f"{stats['pii_fields_masked']} masked"
            )


def render_upload_page():
    """Render the data upload page"""

    st.markdown("## 📂 Upload Customer Data")
    
    # Auto-load persistent product catalog into session if available
    if is_catalog_available() and "product_catalog" not in st.session_state:
        catalog_df = catalog_db.load_catalog()
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
            st.session_state["catalog_filename"] = "persistent_catalog.json"

    st.markdown(
        """
    Upload your customer data and purchase history files to begin the AI-powered lead generation analysis.
    All data will be immediately pseudonymized for privacy protection.
    """
    )

    # Expected columns for validation (flexible - supports both spaces and underscores)
    CUSTOMER_COLUMNS_FLEXIBLE = [
        ["Account ID", "Account_ID"],
        ["Family Name", "Family_Name"],
        ["Given Name", "Given_Name"],
        ["Gender"],
        ["Email"],
        ["Birth Date", "Date_of_Birth"],
        ["Customer Type", "Customer_Type"],
        ["Customer Class", "Customer_Class"],
        # Brand removed - not required since it's always Three HK
    ]
    PURCHASE_COLUMNS = ["Account ID", "Account_ID"]  # More flexible for purchase history
    
    # Product catalog expected columns (flexible)
    PRODUCT_CATALOG_COLUMNS_FLEXIBLE = [
        ["Plan_ID"],
        ["Plan_Name"],
        ["Plan_Type"],
        ["Category"],
        ["Base_Price"]
    ]

    # File upload tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Customer Data", "📈 Purchase History", "📦 Product Catalog", "📂 Sample Data"])

    with tab1:
        st.markdown("### 📊 Customer Profile Data")
        st.markdown("Upload customer demographics, account information, and contact details.")

        # Encoding options
        with st.expander("🔧 Advanced Encoding Options", expanded=False):
            auto_correct_encoding = st.checkbox(
                "Automatic encoding detection and correction",
                value=True,
                help="Automatically detect file encoding (UTF-8, GBK, etc.) and convert to UTF-8 "
                "for proper Chinese character display",
            )

            if auto_correct_encoding:
                st.info(
                    "✨ **Smart Encoding Detection**: Files will be automatically analyzed "
                    "and converted to UTF-8 for optimal Chinese character support."
                )
            else:
                st.warning("⚠️ **Manual Mode**: Files must be UTF-8 encoded. GBK fallback available.")

        uploaded_customer_file = st.file_uploader(
            "Choose customer data CSV file",
            type=["csv"],
            help="Upload customer profile and demographic data (Max 10MB)",
            key="customer_upload",
        )

        if uploaded_customer_file:
            with st.spinner("Validating and processing customer data..."):
                # First validate the basic file format
                is_valid, message, df = validate_csv_file(
                    uploaded_customer_file,
                    expected_columns=None,  # Skip basic column validation
                    auto_correct_encoding=auto_correct_encoding,
                )
                
                if is_valid:
                    # Then do flexible column validation
                    columns_valid, missing_columns = validate_flexible_columns(
                        df.columns.tolist(), CUSTOMER_COLUMNS_FLEXIBLE
                    )
                    
                    if not columns_valid:
                        is_valid = False
                        message = f"Missing required columns: {', '.join(missing_columns)}"

                if is_valid:
                    st.success(f"✅ {message}")

                    # Process through privacy pipeline
                    pipeline_success, pipeline_message, processed_data = process_data_through_privacy_pipeline(
                        df, "customer_data", uploaded_customer_file.name
                    )

                    if pipeline_success:
                        st.success(f"🔒 {pipeline_message}")
                        display_data_preview(processed_data, "Customer Data Preview")

                        # Store processed data in session state
                        st.session_state["customer_data"] = processed_data
                        st.session_state["customer_filename"] = uploaded_customer_file.name

                        # Show privacy compliance information
                        st.info(
                            "✅ Data successfully processed with full privacy protection - "
                            "original PII encrypted, display data masked, "
                            "pseudonymized data ready for AI processing"
                        )

                        # Show processing summary
                        metadata = processed_data.get("metadata", {})
                        if metadata.get("pii_fields_identified"):
                            pii_count = len(metadata["pii_fields_identified"])
                            st.caption(f"🔍 Privacy Analysis: {pii_count} PII fields identified and protected")
                    else:
                        st.error(f"❌ Privacy pipeline processing failed: {pipeline_message}")
                        # Clean up session state on failure
                        if "customer_data" in st.session_state:
                            del st.session_state["customer_data"]

                else:
                    st.error(f"❌ {message}")
                    if "customer_data" in st.session_state:
                        del st.session_state["customer_data"]

    with tab2:
        st.markdown("### 📈 Purchase History Data")
        st.markdown("Upload transaction records, service usage, and engagement metrics.")

        # Encoding options for purchase history
        with st.expander("🔧 Advanced Encoding Options", expanded=False):
            auto_correct_encoding_purchase = st.checkbox(
                "Automatic encoding detection and correction",
                value=True,
                help="Automatically detect file encoding (UTF-8, GBK, etc.) and convert to UTF-8 "
                "for proper Chinese character display",
                key="purchase_encoding_option",
            )

            if auto_correct_encoding_purchase:
                st.info(
                    "✨ **Smart Encoding Detection**: Files will be automatically analyzed "
                    "and converted to UTF-8 for optimal Chinese character support."
                )
            else:
                st.warning("⚠️ **Manual Mode**: Files must be UTF-8 encoded. GBK fallback available.")

        uploaded_purchase_file = st.file_uploader(
            "Choose purchase history CSV file",
            type=["csv"],
            help="Upload transaction and engagement data (Max 10MB)",
            key="purchase_upload",
        )

        if uploaded_purchase_file:
            with st.spinner("Validating and processing purchase history..."):
                # First validate the basic file format
                is_valid, message, df = validate_csv_file(
                    uploaded_purchase_file,
                    expected_columns=None,  # Skip basic column validation for purchase history
                    auto_correct_encoding=auto_correct_encoding_purchase,
                )
                
                if is_valid:
                    # Check for Account ID column (flexible naming)
                    has_account_id = any(col in df.columns for col in PURCHASE_COLUMNS)
                    if not has_account_id:
                        is_valid = False
                        message = f"Missing required column: Account ID (or Account_ID)"

                if is_valid:
                    st.success(f"✅ {message}")

                    # Process through privacy pipeline
                    pipeline_success, pipeline_message, processed_data = process_data_through_privacy_pipeline(
                        df, "purchase_data", uploaded_purchase_file.name
                    )

                    if pipeline_success:
                        st.success(f"🔒 {pipeline_message}")
                        display_data_preview(processed_data, "Purchase History Preview")

                        # Store processed data in session state
                        st.session_state["purchase_data"] = processed_data
                        st.session_state["purchase_filename"] = uploaded_purchase_file.name

                        # Show privacy compliance information
                        st.info(
                            "✅ Data successfully processed with full privacy protection - "
                            "original PII encrypted, display data masked, "
                            "pseudonymized data ready for AI processing"
                        )

                        # Show processing summary
                        metadata = processed_data.get("metadata", {})
                        if metadata.get("pii_fields_identified"):
                            pii_count = len(metadata["pii_fields_identified"])
                            st.caption(f"🔍 Privacy Analysis: {pii_count} PII fields identified and protected")
                    else:
                        st.error(f"❌ Privacy pipeline processing failed: {pipeline_message}")
                        # Clean up session state on failure
                        if "purchase_data" in st.session_state:
                            del st.session_state["purchase_data"]

                else:
                    st.error(f"❌ {message}")
                    if "purchase_data" in st.session_state:
                        del st.session_state["purchase_data"]

    with tab3:
        st.markdown("### 📦 Product Catalog Management")
        
        # Show current catalog status
        if is_catalog_available():
            stats = get_catalog_stats()
            st.success(f"✅ Product catalog loaded: {stats['total_plans']} plans available")
            
            # Show catalog summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Plans", stats['total_plans'])
            with col2:
                st.metric("Categories", len(stats['categories']))
            with col3:
                st.metric("Avg Price", f"HK${stats['price_range']['avg']:.0f}")
            
            # Show current catalog preview
            with st.expander("📋 Current Catalog Preview", expanded=False):
                current_catalog = catalog_db.load_catalog()
                st.dataframe(current_catalog.head(10), use_container_width=True)
                st.caption(f"Showing first 10 of {len(current_catalog)} plans. Last updated: {stats['last_updated'][:19]}")
            
            # Option to clear catalog
            if st.button("🗑️ Clear Current Catalog", type="secondary"):
                if catalog_db.clear_catalog():
                    st.success("✅ Product catalog cleared!")
                    st.rerun()
                else:
                    st.error("❌ Failed to clear catalog")
        else:
            st.info("📦 No product catalog currently loaded. Upload one below or it will load from the default database.")
        
        st.markdown("#### Upload New Catalog")
        st.markdown("Upload a new product catalog to replace the current one (persists across sessions).")

        uploaded_catalog_file = st.file_uploader(
            "Choose product catalog CSV file",
            type=["csv"],
            help="Upload product catalog with plans and pricing (Max 10MB) - will be saved permanently",
            key="catalog_upload",
        )

        if uploaded_catalog_file:
            with st.spinner("Validating and processing product catalog..."):
                # First validate the basic file format
                is_valid, message, df = validate_csv_file(
                    uploaded_catalog_file,
                    expected_columns=None,  # Skip basic column validation
                    auto_correct_encoding=True,
                )
                
                if is_valid:
                    # Then do flexible column validation
                    columns_valid, missing_columns = validate_flexible_columns(
                        df.columns.tolist(), PRODUCT_CATALOG_COLUMNS_FLEXIBLE
                    )
                    
                    if not columns_valid:
                        is_valid = False
                        message = f"Missing required columns: {', '.join(missing_columns)}"

                if is_valid:
                    st.success(f"✅ {message}")

                    # Save to persistent database
                    with st.spinner("💾 Saving catalog to persistent database..."):
                        save_success = catalog_db.save_catalog_from_csv_upload(df, uploaded_catalog_file.name)
                    
                    if save_success:
                        st.success("💾 Product catalog saved to persistent database!")
                        
                        # Also store in session state for immediate use
                        processed_data = {
                            "original_data": df,
                            "catalog_data": df,  # Same as original since no PII to protect
                            "metadata": {
                                "filename": uploaded_catalog_file.name,
                                "uploaded_at": pd.Timestamp.now().isoformat(),
                                "original_shape": df.shape,
                                "original_columns": list(df.columns),
                                "data_type": "product_catalog",
                                "persistent": True  # Indicates this is saved persistently
                            }
                        }
                        st.session_state["product_catalog"] = processed_data
                        st.session_state["catalog_filename"] = uploaded_catalog_file.name
                        
                        # Display updated statistics
                        updated_stats = get_catalog_stats()
                        st.success(f"📦 Catalog updated: {updated_stats['total_plans']} plans now available")
                        
                        # Display preview
                        st.markdown("#### 📊 New Catalog Preview")
                        st.dataframe(df.head(MAX_PREVIEW_ROWS), use_container_width=True)
                        
                        # Show catalog statistics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Plans", len(df))
                        with col2:
                            if "Plan_Type" in df.columns:
                                st.metric("Plan Types", df["Plan_Type"].nunique())
                            elif "Category" in df.columns:
                                st.metric("Categories", df["Category"].nunique())
                        with col3:
                            if "Base_Price" in df.columns:
                                avg_price = df["Base_Price"].mean() if pd.api.types.is_numeric_dtype(df["Base_Price"]) else "N/A"
                                if avg_price != "N/A":
                                    st.metric("Avg Price", f"HK${avg_price:.0f}")

                        st.success(
                            "✅ Product catalog permanently saved! "
                            "It will be available across all sessions without re-uploading."
                        )
                        
                        # Auto-refresh to show the updated catalog status
                        st.rerun()
                    else:
                        st.error("❌ Failed to save catalog to database")
                        # Still store in session for this session
                        processed_data = {
                            "original_data": df,
                            "catalog_data": df,
                            "metadata": {
                                "filename": uploaded_catalog_file.name,
                                "uploaded_at": pd.Timestamp.now().isoformat(),
                                "original_shape": df.shape,
                                "original_columns": list(df.columns),
                                "data_type": "product_catalog",
                                "persistent": False
                            }
                        }
                        st.session_state["product_catalog"] = processed_data
                        st.session_state["catalog_filename"] = uploaded_catalog_file.name

                else:
                    st.error(f"❌ {message}")
                    if "product_catalog" in st.session_state:
                        del st.session_state["product_catalog"]

    with tab4:
        st.markdown("### 📂 Sample Data Available")
        st.markdown("Preview and use the provided sample datasets to test the system.")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📊 Load Customer Sample", type="secondary"):
                with st.spinner("Loading customer sample data..."):
                    is_valid, message, df = load_sample_data("sample-customer-data-20250715.csv")

                    if is_valid and df is not None:
                        st.success(f"✅ {message}")

                        # Process through privacy pipeline
                        pipeline_success, pipeline_message, processed_data = process_data_through_privacy_pipeline(
                            df, "sample_customer_data", "sample-customer-data-20250715.csv"
                        )

                        if pipeline_success:
                            st.success(f"🔒 {pipeline_message}")
                            display_data_preview(processed_data, "Sample Customer Data")

                            # Option to use this data
                            if st.button("Use This Sample Data", key="use_customer_sample"):
                                st.session_state["customer_data"] = processed_data
                                st.session_state["customer_filename"] = "sample-customer-data-20250715.csv"
                                st.success("Sample customer data loaded for analysis!")
                                st.rerun()
                        else:
                            st.error(f"❌ Privacy pipeline processing failed: {pipeline_message}")
                    else:
                        st.error(f"❌ {message}")

        with col2:
            if st.button("📈 Load Purchase Sample", type="secondary"):
                with st.spinner("Loading purchase sample data..."):
                    is_valid, message, df = load_sample_data("sample_purchase_history.csv")

                    if is_valid and df is not None:
                        st.success(f"✅ {message}")

                        # Process through privacy pipeline
                        pipeline_success, pipeline_message, processed_data = process_data_through_privacy_pipeline(
                            df, "sample_purchase_data", "sample_purchase_history.csv"
                        )

                        if pipeline_success:
                            st.success(f"🔒 {pipeline_message}")
                            display_data_preview(processed_data, "Sample Purchase History")

                            # Option to use this data
                            if st.button("Use This Sample Data", key="use_purchase_sample"):
                                st.session_state["purchase_data"] = processed_data
                                st.session_state["purchase_filename"] = "sample_purchase_history.csv"
                                st.success("Sample purchase data loaded for analysis!")
                                st.rerun()
                        else:
                            st.error(f"❌ Privacy pipeline processing failed: {pipeline_message}")
                    else:
                        st.error(f"❌ {message}")

    # Data Status Summary
    st.markdown("---")
    st.markdown("### 📊 Current Data Status")

    col1, col2, col3 = st.columns(3)

    with col1:
        if "customer_data" in st.session_state:
            customer_data = st.session_state["customer_data"]
            st.success(f"✅ Customer Data: {st.session_state.get('customer_filename', 'Unknown')}")

            # Handle both old format (DataFrame) and new format (dict)
            if isinstance(customer_data, dict):
                original_df = customer_data.get("original_data")
                if original_df is not None:
                    st.caption(f"Rows: {len(original_df)} | Privacy: Protected")
                    # Show PII information
                    metadata = customer_data.get("metadata", {})
                    pii_fields = metadata.get("pii_fields_identified", [])
                    if pii_fields:
                        st.caption(f"🔍 {len(pii_fields)} PII fields protected")
                else:
                    st.caption("Processed data available")
            else:
                # Legacy format
                st.caption(f"Rows: {len(customer_data)} | Privacy: Not processed")
        else:
            st.warning("⏳ No customer data uploaded")

    with col2:
        if "purchase_data" in st.session_state:
            purchase_data = st.session_state["purchase_data"]
            st.success(f"✅ Purchase Data: {st.session_state.get('purchase_filename', 'Unknown')}")

            # Handle both old format (DataFrame) and new format (dict)
            if isinstance(purchase_data, dict):
                original_df = purchase_data.get("original_data")
                if original_df is not None:
                    st.caption(f"Rows: {len(original_df)} | Privacy: Protected")
                    # Show PII information
                    metadata = purchase_data.get("metadata", {})
                    pii_fields = metadata.get("pii_fields_identified", [])
                    if pii_fields:
                        st.caption(f"🔍 {len(pii_fields)} PII fields protected")
                else:
                    st.caption("Processed data available")
            else:
                # Legacy format
                st.caption(f"Rows: {len(purchase_data)} | Privacy: Not processed")
        else:
            st.warning("⏳ No purchase data uploaded")

    with col3:
        if "product_catalog" in st.session_state:
            catalog_data = st.session_state["product_catalog"]
            st.success(f"✅ Product Catalog: {st.session_state.get('catalog_filename', 'Unknown')}")

            # Product catalog format
            if isinstance(catalog_data, dict):
                original_df = catalog_data.get("original_data")
                if original_df is not None:
                    st.caption(f"Plans: {len(original_df)} | Ready for analysis")
                    # Show plan type distribution if available
                    if "Plan_Type" in original_df.columns:
                        plan_types = original_df["Plan_Type"].nunique()
                        st.caption(f"📦 {plan_types} plan types available")
                else:
                    st.caption("Catalog data available")
            else:
                # Legacy format
                st.caption(f"Plans: {len(catalog_data)} | Format: Legacy")
        else:
            st.warning("⏳ No product catalog uploaded")

    # Next Steps
    has_customer = "customer_data" in st.session_state
    has_purchase = "purchase_data" in st.session_state  
    has_catalog = "product_catalog" in st.session_state
    
    if has_customer and has_purchase:
        customer_data = st.session_state["customer_data"]
        purchase_data = st.session_state["purchase_data"]

        # Check if data is properly processed through privacy pipeline
        customer_processed = isinstance(customer_data, dict) and "pseudonymized_data" in customer_data
        purchase_processed = isinstance(purchase_data, dict) and "pseudonymized_data" in purchase_data

        if customer_processed and purchase_processed:
            # Enhanced success message based on catalog availability
            if has_catalog:
                st.success("🎉 All datasets uploaded and processed! Ready for enhanced AI analysis with product catalog.")
                catalog_info = "📦 Product catalog will enhance recommendation accuracy and plan matching"
            else:
                st.success("🎉 Core datasets uploaded and privacy-processed! Ready to proceed to secure data analysis.")
                catalog_info = "💡 Consider uploading a product catalog for more accurate plan recommendations"

            # Show privacy summary
            customer_pii_count = len(customer_data.get("metadata", {}).get("pii_fields_identified", []))
            purchase_pii_count = len(purchase_data.get("metadata", {}).get("pii_fields_identified", []))
            total_pii_fields = customer_pii_count + purchase_pii_count

            st.info(
                f"🔒 Privacy Protection Summary: {total_pii_fields} total PII fields "
                f"identified and protected across both datasets"
            )
            
            st.info(catalog_info)

            # Analysis Configuration Section
            st.markdown("---")
            st.markdown("### ⚙️ Analysis Configuration")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Get current customer count for reference
                if isinstance(customer_data, dict) and "original_data" in customer_data:
                    total_customers = len(customer_data["original_data"])
                else:
                    total_customers = len(customer_data) if isinstance(customer_data, pd.DataFrame) else 0
                
                st.info(f"📊 **Total customers available:** {total_customers}")
                
                # Customer analysis limit selector
                max_customers = min(total_customers, 100)  # Cap at 100 for performance
                default_customers = min(total_customers, 5)  # Default to 5 for backwards compatibility
                
                customers_to_analyze = st.number_input(
                    "🎯 **Customers to analyze**",
                    min_value=1,
                    max_value=max_customers,
                    value=default_customers,
                    step=1,
                    help=f"Select how many customers to analyze (1-{max_customers}). More customers = more comprehensive insights but longer processing time."
                )
                
                # Store in session state for use in analysis
                st.session_state["customers_to_analyze"] = customers_to_analyze
                
            with col2:
                st.markdown("**📈 Processing Estimates:**")
                if customers_to_analyze <= 5:
                    time_estimate = "< 1 minute"
                    recommendation = "✅ **Recommended** - Quick insights"
                elif customers_to_analyze <= 20:
                    time_estimate = "1-3 minutes" 
                    recommendation = "⚡ **Balanced** - Good depth vs speed"
                elif customers_to_analyze <= 50:
                    time_estimate = "3-8 minutes"
                    recommendation = "🔍 **Comprehensive** - Deep insights"
                else:
                    time_estimate = "8-15 minutes"
                    recommendation = "🏢 **Enterprise** - Maximum coverage"
                
                st.caption(f"⏱️ Estimated time: {time_estimate}")
                st.caption(recommendation)
                
                if customers_to_analyze > 20:
                    st.warning("⚠️ Large datasets may take longer to process")

            if st.button("🚀 Proceed to Secure Analysis", type="primary"):
                st.info("✅ Ready for AI analysis! All PII has been securely processed:")
                analysis_features = [
                    "**Original data**: Encrypted and stored locally",
                    "**Pseudonymized data**: Available for external LLM processing (no PII)",
                    "**Display data**: Masked for UI viewing with toggle control"
                ]
                
                if has_catalog:
                    analysis_features.append("**Product catalog**: Available for enhanced recommendations")
                
                st.markdown("- " + "\n- ".join(analysis_features))
                st.success("Data processing and AI analysis will be implemented in upcoming tasks!")
                # This will link to the next page/component in future tasks
        else:
            st.warning(
                "⚠️ Both datasets are uploaded but need privacy processing. "
                "Please re-upload files to ensure privacy protection."
            )
    else:
        missing_data = []
        if not has_customer:
            missing_data.append("customer data")
        if not has_purchase:
            missing_data.append("purchase history")
            
        if has_catalog and not has_customer and not has_purchase:
            st.info("📋 Product catalog uploaded! Now upload customer and purchase data to begin analysis.")
        else:
            st.info(f"📋 Upload {' and '.join(missing_data)} to continue with the analysis.")

    # Privacy and Security Notice
    st.markdown("---")
    st.markdown("### 🔒 Privacy & Security - Integrated Protection")
    st.success(
        """
    **Multi-Layer Privacy Protection (Implemented):**
    - **Immediate Encryption**: Original PII data encrypted with AES-256-GCM upon upload
    - **Automatic PII Detection**: 13 types of sensitive data identified with Hong Kong-specific patterns
    - **Dual Privacy Layers**:
      - Security Pseudonymization (SHA-256 hashing) for external AI processing
      - Display Masking (reversible) for UI viewing with toggle control
    - **Zero External PII Transmission**: Only anonymized data sent to AI services
    - **Local Processing**: All privacy operations performed on your device
    - **Compliance**: GDPR and Hong Kong PDPO compliant design
    """
    )

    # Show technical details in expandable section
    with st.expander("🔧 Technical Privacy Implementation"):
        st.markdown(
            """
        **Security Features:**
        - **Encryption**: AES-256-GCM with PBKDF2-SHA256 key derivation (100,000 iterations)
        - **Salt & Nonce**: Unique per encryption operation
        - **Hashing**: SHA-256 with configurable salt (minimum 32 bytes)
        - **Access Control**: Master password protection with secure verification
        - **Audit Logging**: All privacy operations logged for compliance
        - **Integrity Verification**: Tamper detection for stored data
        - **Secure Deletion**: Cryptographic data wiping capabilities

        **Supported PII Types:**
        Account ID, HKID, Email, Phone, Name, Address, Passport, Driver's License,
        Credit Card, Bank Account, IP Address, Date of Birth, General

        **Performance:**
        - Field identification: 1000+ rows/ms
        - Display masking: 3000+ rows/sec
        - Encryption/decryption: Real-time processing
        """
        )

    # File Requirements
    with st.expander("📋 File Requirements & Format Guidelines"):
        st.markdown(
            """
        **Customer Data CSV Requirements:**
        - Must include: Account ID (or Account_ID), Family Name (or Family_Name), Given Name (or Given_Name), Gender, Email, Birth Date (or Date_of_Birth), Customer Type (or Customer_Type), Customer Class (or Customer_Class)
        - Optional: Chinese Given Name, ID Type, ID Number, Company Name (or Company_Name), Brand
        - File size limit: 10MB
        - Encoding: UTF-8
        - Note: Column names can use either spaces or underscores

        **Purchase History CSV Requirements:**
        - Must include: Account ID
        - Recommended: Purchase History columns, Engagement Data
        - File size limit: 10MB
        - Encoding: UTF-8

        **Product Catalog CSV Requirements:**
        - Must include: Plan_ID, Plan_Name, Plan_Type, Category, Base_Price
        - Recommended: Setup_Fee, Data_Allowance, Features, Target_Segment
        - File size limit: 10MB
        - Encoding: UTF-8

        **General Guidelines:**
        - Use standard CSV format with comma separators
        - Include column headers in the first row
        - Ensure Account IDs match between customer and purchase files
        """
        )
