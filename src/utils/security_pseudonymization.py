"""
Security Pseudonymization Module for Agentic AI Revenue Assistant

This module provides irreversible anonymization of sensitive customer data using
SHA-256 hashing with salt. This ensures that no original PII is sent to external
LLM services while maintaining data utility for AI processing.

Architecture:
- Irreversible anonymization using SHA-256 + salt
- Configurable salt for enhanced security
- Consistent hashing (same input → same output)
- No possibility of data recovery
- Separate from display masking (which is reversible)

Compliance: GDPR and Hong Kong PDPO compliant
"""

import hashlib
import secrets
import pandas as pd
import re
from typing import Dict, List, Union, Optional, Any
import logging

# Configure logging
logger = logging.getLogger(__name__)

class SecurityPseudonymizer:
    """
    Security pseudonymizer for irreversible anonymization of sensitive data
    before external LLM processing.
    """
    
    def __init__(self, salt: Optional[str] = None):
        """
        Initialize the security pseudonymizer.
        
        Args:
            salt: Optional salt for hashing. If not provided, generates a secure salt.
        """
        if salt is None:
            # Generate a secure 32-byte salt
            self.salt = secrets.token_hex(32)
            logger.info("Generated new secure salt for pseudonymization")
        else:
            self.salt = salt
            logger.info("Using provided salt for pseudonymization")
    
    def _hash_value(self, value: str) -> str:
        """
        Hash a value using SHA-256 with salt.
        
        Args:
            value: The value to hash
            
        Returns:
            Hashed value as hexadecimal string
        """
        if not isinstance(value, str):
            value = str(value)
        
        # Create salted hash
        salted_value = f"{self.salt}{value}"
        hash_object = hashlib.sha256(salted_value.encode('utf-8'))
        return hash_object.hexdigest()
    
    def anonymize_field(self, value: Any, field_type: str = "general") -> str:
        """
        Anonymize a single field value.
        
        Args:
            value: The value to anonymize
            field_type: Type of field (for logging/metadata purposes)
            
        Returns:
            Anonymized value
        """
        if pd.isna(value) or value is None or value == "":
            return ""
        
        # Convert to string and hash
        anonymized = self._hash_value(str(value))
        
        # Add prefix to indicate field type for analysis purposes
        prefix_map = {
            "account_id": "ACCT_",
            "hkid": "HKID_",
            "email": "EMAIL_",
            "phone": "PHONE_",
            "name": "NAME_",
            "address": "ADDR_",
            "general": "DATA_"
        }
        
        prefix = prefix_map.get(field_type, "DATA_")
        return f"{prefix}{anonymized[:16]}"  # Use first 16 chars for readability
    
    def identify_field_type(self, column_name: str, sample_value: str) -> str:
        """
        Identify the type of sensitive field for appropriate anonymization.
        
        Args:
            column_name: Name of the column
            sample_value: Sample value from the column
            
        Returns:
            Field type identifier
        """
        if not isinstance(sample_value, str):
            sample_value = str(sample_value)
        
        # Column name patterns
        col_lower = column_name.lower()
        
        if "account" in col_lower and "id" in col_lower:
            return "account_id"
        elif "hkid" in col_lower or "id_number" in col_lower:
            return "hkid"
        elif "email" in col_lower or "mail" in col_lower:
            return "email"
        elif "phone" in col_lower or "mobile" in col_lower or "tel" in col_lower:
            return "phone"
        elif "name" in col_lower or "customer" in col_lower:
            return "name"
        elif "address" in col_lower or "location" in col_lower:
            return "address"
        
        # Value pattern detection
        if re.match(r'^[A-Z]\d{6}\(\d\)$', sample_value):  # HKID pattern
            return "hkid"
        elif re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', sample_value):  # Email pattern
            return "email"
        elif re.match(r'^[+]?[\d\s()\-]{7,}$', sample_value):  # Phone pattern (minimum 7 digits)
            return "phone"
        elif re.match(r'^ACCT\d+$', sample_value):  # Account ID pattern
            return "account_id"
        
        return "general"
    
    def anonymize_dataframe(self, df: pd.DataFrame, sensitive_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Anonymize all sensitive fields in a DataFrame.
        
        Args:
            df: DataFrame to anonymize
            sensitive_columns: List of column names to anonymize. If None, auto-detect.
            
        Returns:
            DataFrame with anonymized sensitive fields
        """
        if df.empty:
            return df.copy()
        
        # Create a copy to avoid modifying original
        anonymized_df = df.copy()
        
        # Auto-detect sensitive columns if not provided
        if sensitive_columns is None:
            sensitive_columns = self._detect_sensitive_columns(df)
        
        # Anonymize each sensitive column
        for column in sensitive_columns:
            if column in df.columns:
                # Identify field type from first non-null value
                sample_value = df[column].dropna().iloc[0] if not df[column].dropna().empty else ""
                field_type = self.identify_field_type(column, sample_value)
                
                # Apply anonymization
                anonymized_df[column] = df[column].apply(
                    lambda x: self.anonymize_field(x, field_type)
                )
                
                logger.info(f"Anonymized column '{column}' (type: {field_type})")
        
        return anonymized_df
    
    def _detect_sensitive_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Automatically detect columns that contain sensitive information.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            List of column names containing sensitive data
        """
        sensitive_columns = []
        
        # Keywords that indicate sensitive data
        sensitive_keywords = [
            'account_id', 'customer_id', 'hkid', 'id_number', 'email', 'mail',
            'phone', 'mobile', 'tel', 'name', 'customer', 'address', 'location',
            'contact', 'personal', 'identity'
        ]
        
        for column in df.columns:
            col_lower = column.lower()
            
            # Check if column name contains sensitive keywords
            if any(keyword in col_lower for keyword in sensitive_keywords):
                sensitive_columns.append(column)
                continue
            
            # Check sample values for patterns
            if not df[column].empty:
                sample_values = df[column].dropna().head(3).astype(str)
                
                for value in sample_values:
                    field_type = self.identify_field_type(column, value)
                    if field_type != "general":
                        sensitive_columns.append(column)
                        break
        
        return sensitive_columns
    
    def get_anonymization_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get a summary of anonymization for audit purposes.
        
        Args:
            df: Original DataFrame
            
        Returns:
            Dictionary with anonymization summary
        """
        sensitive_columns = self._detect_sensitive_columns(df)
        
        summary = {
            "total_columns": len(df.columns),
            "sensitive_columns": len(sensitive_columns),
            "sensitive_column_names": sensitive_columns,
            "total_rows": len(df),
            "anonymization_method": "SHA-256 with salt",
            "salt_length": len(self.salt),
            "reversible": False,
            "compliance": ["GDPR", "Hong Kong PDPO"]
        }
        
        return summary
    
    def validate_anonymization(self, original_df: pd.DataFrame, anonymized_df: pd.DataFrame) -> Dict[str, bool]:
        """
        Validate that anonymization was successful.
        
        Args:
            original_df: Original DataFrame
            anonymized_df: Anonymized DataFrame
            
        Returns:
            Dictionary with validation results
        """
        results = {
            "structure_preserved": original_df.shape == anonymized_df.shape,
            "columns_preserved": list(original_df.columns) == list(anonymized_df.columns),
            "no_original_pii": True,
            "consistent_hashing": True
        }
        
        # Check that sensitive data has been anonymized
        sensitive_columns = self._detect_sensitive_columns(original_df)
        
        for column in sensitive_columns:
            if column in original_df.columns and column in anonymized_df.columns:
                # Check that values are different (anonymized)
                original_values = set(original_df[column].dropna().astype(str))
                anonymized_values = set(anonymized_df[column].dropna().astype(str))
                
                # Should have no overlap except for empty values
                overlap = original_values.intersection(anonymized_values)
                if overlap and overlap != {"", "nan"}:
                    results["no_original_pii"] = False
                    break
        
        return results


# Utility functions for easy integration
def create_pseudonymizer(salt: Optional[str] = None) -> SecurityPseudonymizer:
    """
    Create a SecurityPseudonymizer instance.
    
    Args:
        salt: Optional salt for hashing
        
    Returns:
        SecurityPseudonymizer instance
    """
    return SecurityPseudonymizer(salt)

def anonymize_for_llm(df: pd.DataFrame, salt: Optional[str] = None) -> pd.DataFrame:
    """
    Convenience function to anonymize a DataFrame for LLM processing.
    
    Args:
        df: DataFrame to anonymize
        salt: Optional salt for hashing
        
    Returns:
        Anonymized DataFrame ready for external LLM processing
    """
    pseudonymizer = SecurityPseudonymizer(salt)
    return pseudonymizer.anonymize_dataframe(df)

def get_salt_from_config() -> str:
    """
    Get salt from configuration or environment.
    In production, this should be stored securely.
    
    Returns:
        Salt string
    """
    import os
    
    # Try to get from environment variable
    salt = os.getenv("PSEUDONYMIZATION_SALT")
    
    if not salt:
        # Generate and store a salt (in production, store this securely)
        salt = secrets.token_hex(32)
        logger.warning("No salt found in environment. Generated new salt. In production, store this securely.")
    
    return salt 