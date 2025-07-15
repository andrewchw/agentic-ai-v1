"""
Enhanced Sensitive Field Identification Module for Agentic AI Revenue Assistant

This module provides comprehensive and accurate identification of sensitive fields
in customer data, with enhanced support for Hong Kong-specific identifiers and
configurable detection rules.

Features:
- Expanded PII type coverage (passport, driver's license, credit card, etc.)
- Hong Kong-specific pattern matching
- Context-aware field identification
- Confidence scoring for detection accuracy
- Configurable sensitivity rules
- Performance optimization for large datasets
- Integration with both security pseudonymization and display masking

Compliance: GDPR and Hong Kong PDPO compliant
"""

import re
import pandas as pd
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)


class FieldType(Enum):
    """Enumeration of supported field types"""

    ACCOUNT_ID = "account_id"
    HKID = "hkid"
    EMAIL = "email"
    PHONE = "phone"
    NAME = "name"
    ADDRESS = "address"
    PASSPORT = "passport"
    DRIVERS_LICENSE = "drivers_license"
    CREDIT_CARD = "credit_card"
    BANK_ACCOUNT = "bank_account"
    IP_ADDRESS = "ip_address"
    DATE_OF_BIRTH = "date_of_birth"
    GENERAL = "general"


@dataclass
class FieldPattern:
    """Definition of a field pattern for identification"""

    field_type: FieldType
    column_keywords: List[str]
    value_patterns: List[str]
    confidence_weight: float
    description: str
    hong_kong_specific: bool = False


@dataclass
class FieldIdentificationResult:
    """Result of field identification process"""

    field_type: FieldType
    confidence: float
    matched_pattern: str
    method: str  # 'column_name', 'value_pattern', 'hybrid'
    is_sensitive: bool


class EnhancedFieldIdentifier:
    """
    Enhanced field identifier with comprehensive PII coverage and
    Hong Kong-specific pattern matching.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the enhanced field identifier.

        Args:
            config_path: Path to configuration file with custom patterns
        """
        self.patterns = self._load_default_patterns()
        self.sensitivity_threshold = 0.6  # Minimum confidence for sensitive classification

        if config_path:
            self._load_custom_patterns(config_path)

    def _load_default_patterns(self) -> List[FieldPattern]:
        """Load default field patterns for identification"""
        return [
            # Account and Customer IDs
            FieldPattern(
                field_type=FieldType.ACCOUNT_ID,
                column_keywords=["account", "customer_id", "acct", "id", "reference"],
                value_patterns=[r"^ACCT\d+$", r"^[A-Z]{2,4}\d{6,12}$", r"^\d{8,15}$"],
                confidence_weight=0.9,
                description="Account and customer identification numbers",
            ),
            # Hong Kong Identity Documents
            FieldPattern(
                field_type=FieldType.HKID,
                column_keywords=["hkid", "id_number", "identity", "id_card", "hong_kong_id"],
                value_patterns=[r"^[A-Z]\d{6}\(\d\)$", r"^[A-Z]{1,2}\d{6}\(\d\)$"],
                confidence_weight=0.95,
                description="Hong Kong Identity Document numbers",
                hong_kong_specific=True,
            ),
            # Email Addresses
            FieldPattern(
                field_type=FieldType.EMAIL,
                column_keywords=["email", "mail", "e_mail", "contact_email"],
                value_patterns=[r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"],
                confidence_weight=0.95,
                description="Email addresses",
            ),
            # Phone Numbers (Hong Kong and International)
            FieldPattern(
                field_type=FieldType.PHONE,
                column_keywords=["phone", "mobile", "tel", "telephone", "contact", "number"],
                value_patterns=[
                    r"^[+]?852[\s\-]?\d{4}[\s\-]?\d{4}$",  # Hong Kong format
                    r"^[+]?[\d\s()\-]{7,15}$",  # International format
                    r"^\d{8}$",  # Hong Kong local format
                    r"^[+]?1[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{4}$",  # US format
                ],
                confidence_weight=0.8,
                description="Phone numbers including Hong Kong formats",
            ),
            # Personal Names
            FieldPattern(
                field_type=FieldType.NAME,
                column_keywords=[
                    "name",
                    "customer",
                    "person",
                    "contact",
                    "first_name",
                    "last_name",
                    "full_name",
                ],
                value_patterns=[
                    r"^[A-Z][a-z]+\s[A-Z][a-z]+$",  # First Last
                    r"^[A-Z][a-z]+\s[A-Z][a-z]+\s[A-Z][a-z]+$",  # First Middle Last
                    r"^[A-Z][a-z]+,\s[A-Z][a-z]+$",  # Last, First
                    r"^[\u4e00-\u9fff]{2,4}$",  # Chinese characters
                    r"^[A-Z][a-z]+\s[\u4e00-\u9fff]{2,4}$",  # Mixed English/Chinese
                ],
                confidence_weight=0.7,
                description="Personal names including Chinese characters",
            ),
            # Addresses
            FieldPattern(
                field_type=FieldType.ADDRESS,
                column_keywords=["address", "location", "street", "home", "residence", "postal"],
                value_patterns=[
                    r"^\d+\s[A-Z][a-z]+\s(St|Ave|Rd|Dr|Blvd|Lane)",  # Western format
                    r"^.+,\s(Hong Kong|Kowloon|New Territories)$",  # Hong Kong format
                    r"^Flat\s\d+[A-Z]?,\s\d+[A-Z]?\s.+$",  # Hong Kong flat format
                    r"^.+\s\d{5}$",  # With postal code
                ],
                confidence_weight=0.8,
                description="Addresses including Hong Kong formats",
                hong_kong_specific=True,
            ),
            # Passport Numbers
            FieldPattern(
                field_type=FieldType.PASSPORT,
                column_keywords=["passport", "travel_document", "passport_number"],
                value_patterns=[
                    r"^[A-Z]\d{8}$",  # Hong Kong passport format
                    r"^[A-Z]{2}\d{7}$",  # UK passport format
                    r"^[A-Z]\d{7}$",  # US passport format
                    r"^[A-Z0-9]{6,9}$",  # General passport format
                ],
                confidence_weight=0.9,
                description="Passport numbers including Hong Kong format",
            ),
            # Driver's License
            FieldPattern(
                field_type=FieldType.DRIVERS_LICENSE,
                column_keywords=["license", "licence", "driving", "driver", "dl"],
                value_patterns=[
                    r"^[A-Z]\d{8}$",  # Hong Kong driving license
                    r"^[A-Z]{1,2}\d{6,8}$",  # General format
                    r"^\d{8,10}$",  # Numeric format
                ],
                confidence_weight=0.85,
                description="Driver's license numbers",
            ),
            # Credit Card Numbers
            FieldPattern(
                field_type=FieldType.CREDIT_CARD,
                column_keywords=["credit_card", "card", "payment", "cc", "card_number"],
                value_patterns=[
                    r"^4\d{12}(\d{3})?$",  # Visa
                    r"^5[1-5]\d{14}$",  # MasterCard
                    r"^3[47]\d{13}$",  # American Express
                    r"^\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}$",  # General format
                ],
                confidence_weight=0.95,
                description="Credit card numbers",
            ),
            # Bank Account Numbers
            FieldPattern(
                field_type=FieldType.BANK_ACCOUNT,
                column_keywords=["bank", "account", "banking", "acc_no", "account_number"],
                value_patterns=[
                    r"^\d{3}-\d{6}-\d{3}$",  # Hong Kong format
                    r"^\d{9,18}$",  # General numeric format
                    r"^[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}[A-Z0-9]{1,31}$",  # IBAN format
                ],
                confidence_weight=0.9,
                description="Bank account numbers including Hong Kong format",
            ),
            # IP Addresses
            FieldPattern(
                field_type=FieldType.IP_ADDRESS,
                column_keywords=["ip", "ip_address", "address", "network"],
                value_patterns=[
                    r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",  # IPv4
                    r"^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$",  # IPv6
                ],
                confidence_weight=0.9,
                description="IP addresses",
            ),
            # Date of Birth
            FieldPattern(
                field_type=FieldType.DATE_OF_BIRTH,
                column_keywords=["birth", "dob", "date_of_birth", "birthday", "born"],
                value_patterns=[
                    r"^\d{4}-\d{2}-\d{2}$",  # YYYY-MM-DD
                    r"^\d{2}/\d{2}/\d{4}$",  # MM/DD/YYYY
                    r"^\d{2}-\d{2}-\d{4}$",  # DD-MM-YYYY
                ],
                confidence_weight=0.8,
                description="Date of birth",
            ),
        ]

    def _load_custom_patterns(self, config_path: str):
        """Load custom field patterns from configuration file"""
        try:
            with open(config_path, "r") as f:
                config = json.load(f)

            custom_patterns = []
            for pattern_data in config.get("custom_patterns", []):
                pattern = FieldPattern(
                    field_type=FieldType(pattern_data["field_type"]),
                    column_keywords=pattern_data["column_keywords"],
                    value_patterns=pattern_data["value_patterns"],
                    confidence_weight=pattern_data.get("confidence_weight", 0.5),
                    description=pattern_data.get("description", ""),
                    hong_kong_specific=pattern_data.get("hong_kong_specific", False),
                )
                custom_patterns.append(pattern)

            self.patterns.extend(custom_patterns)
            logger.info(f"Loaded {len(custom_patterns)} custom patterns from {config_path}")

        except Exception as e:
            logger.warning(f"Failed to load custom patterns from {config_path}: {e}")

    def identify_field(
        self, column_name: str, sample_values: List[str]
    ) -> FieldIdentificationResult:
        """
        Identify field type using enhanced logic with confidence scoring.

        Args:
            column_name: Name of the column
            sample_values: List of sample values from the column

        Returns:
            FieldIdentificationResult with type, confidence, and metadata
        """
        if not sample_values:
            return FieldIdentificationResult(
                field_type=FieldType.GENERAL,
                confidence=0.0,
                matched_pattern="",
                method="no_data",
                is_sensitive=False,
            )

        # Clean and prepare sample values
        cleaned_values = [str(v).strip() for v in sample_values if pd.notna(v) and str(v).strip()]
        if not cleaned_values:
            return FieldIdentificationResult(
                field_type=FieldType.GENERAL,
                confidence=0.0,
                matched_pattern="",
                method="no_valid_data",
                is_sensitive=False,
            )

        best_match = None
        best_confidence = 0.0
        best_method = ""
        best_pattern = ""

        col_lower = column_name.lower()

        # Try each pattern
        for pattern in self.patterns:
            confidence = 0.0
            method = ""
            matched_pattern = ""

            # Check column name match
            column_match = any(keyword in col_lower for keyword in pattern.column_keywords)
            if column_match:
                confidence += 0.4 * pattern.confidence_weight
                method = "column_name"

            # Check value pattern match
            value_matches = 0
            total_values = len(cleaned_values[:5])  # Check first 5 values

            for value in cleaned_values[:5]:
                for value_pattern in pattern.value_patterns:
                    if re.match(value_pattern, value):
                        value_matches += 1
                        matched_pattern = value_pattern
                        break

            if value_matches > 0:
                value_confidence = (value_matches / total_values) * 0.8 * pattern.confidence_weight
                confidence += value_confidence
                if method:
                    method = "hybrid"
                else:
                    method = "value_pattern"

            # Update best match
            if confidence > best_confidence:
                best_match = pattern
                best_confidence = confidence
                best_method = method
                best_pattern = matched_pattern

        # Determine final result
        if best_match:
            return FieldIdentificationResult(
                field_type=best_match.field_type,
                confidence=best_confidence,
                matched_pattern=best_pattern,
                method=best_method,
                is_sensitive=best_confidence >= self.sensitivity_threshold,
            )
        else:
            return FieldIdentificationResult(
                field_type=FieldType.GENERAL,
                confidence=0.0,
                matched_pattern="",
                method="no_match",
                is_sensitive=False,
            )

    def analyze_dataframe(self, df: pd.DataFrame) -> Dict[str, FieldIdentificationResult]:
        """
        Analyze all columns in a DataFrame for sensitive fields.

        Args:
            df: DataFrame to analyze

        Returns:
            Dictionary mapping column names to identification results
        """
        results = {}

        for column in df.columns:
            # Get sample values (up to 10 non-null values)
            sample_values = df[column].dropna().head(10).tolist()

            # Identify field type
            result = self.identify_field(column, sample_values)
            results[column] = result

            logger.debug(
                f"Column '{column}': {result.field_type.value} (confidence: {result.confidence:.2f})"
            )

        return results

    def get_sensitive_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Get list of sensitive columns from DataFrame.

        Args:
            df: DataFrame to analyze

        Returns:
            List of column names identified as sensitive
        """
        analysis = self.analyze_dataframe(df)
        return [col for col, result in analysis.items() if result.is_sensitive]

    def get_field_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get comprehensive field analysis summary.

        Args:
            df: DataFrame to analyze

        Returns:
            Summary dictionary with statistics and breakdown
        """
        analysis = self.analyze_dataframe(df)

        # Count by field type
        field_counts = {}
        sensitive_count = 0
        high_confidence_count = 0

        for result in analysis.values():
            field_type = result.field_type.value
            field_counts[field_type] = field_counts.get(field_type, 0) + 1

            if result.is_sensitive:
                sensitive_count += 1
            if result.confidence >= 0.8:
                high_confidence_count += 1

        # Hong Kong specific fields
        hk_specific_count = sum(
            1
            for result in analysis.values()
            if result.field_type in [FieldType.HKID, FieldType.ADDRESS] and result.is_sensitive
        )

        return {
            "total_columns": len(df.columns),
            "sensitive_columns": sensitive_count,
            "high_confidence_columns": high_confidence_count,
            "field_type_breakdown": field_counts,
            "hong_kong_specific_fields": hk_specific_count,
            "sensitivity_threshold": self.sensitivity_threshold,
            "analysis_details": {
                col: {
                    "field_type": result.field_type.value,
                    "confidence": result.confidence,
                    "method": result.method,
                    "is_sensitive": result.is_sensitive,
                }
                for col, result in analysis.items()
            },
        }

    def export_configuration(self, filepath: str):
        """Export current configuration to JSON file"""
        config = {"sensitivity_threshold": self.sensitivity_threshold, "patterns": []}

        for pattern in self.patterns:
            config["patterns"].append(
                {
                    "field_type": pattern.field_type.value,
                    "column_keywords": pattern.column_keywords,
                    "value_patterns": pattern.value_patterns,
                    "confidence_weight": pattern.confidence_weight,
                    "description": pattern.description,
                    "hong_kong_specific": pattern.hong_kong_specific,
                }
            )

        with open(filepath, "w") as f:
            json.dump(config, f, indent=2)

        logger.info(f"Configuration exported to {filepath}")

    def set_sensitivity_threshold(self, threshold: float):
        """Set the sensitivity threshold for field classification"""
        if 0.0 <= threshold <= 1.0:
            self.sensitivity_threshold = threshold
            logger.info(f"Sensitivity threshold set to {threshold}")
        else:
            raise ValueError("Threshold must be between 0.0 and 1.0")


# Utility functions for integration
def create_field_identifier(config_path: Optional[str] = None) -> EnhancedFieldIdentifier:
    """Create an EnhancedFieldIdentifier instance"""
    return EnhancedFieldIdentifier(config_path)


def analyze_dataframe_fields(
    df: pd.DataFrame, config_path: Optional[str] = None
) -> Dict[str, FieldIdentificationResult]:
    """Convenience function to analyze DataFrame fields"""
    identifier = EnhancedFieldIdentifier(config_path)
    return identifier.analyze_dataframe(df)


def get_sensitive_columns_enhanced(
    df: pd.DataFrame, config_path: Optional[str] = None
) -> List[str]:
    """Convenience function to get sensitive columns with enhanced identification"""
    identifier = EnhancedFieldIdentifier(config_path)
    return identifier.get_sensitive_columns(df)
