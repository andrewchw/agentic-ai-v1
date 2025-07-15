"""
Integrated Display Masking System - Task 5.4
Part of the dual-layer privacy architecture for Agentic AI Revenue Assistant

This module integrates the EnhancedFieldIdentifier with comprehensive display masking
for all 13 supported PII types, providing toggle-controlled masking in the UI.

Features:
- Integration with EnhancedFieldIdentifier for accurate field detection
- Support for all 13 PII types including Hong Kong-specific patterns
- Toggle control for showing/hiding sensitive data
- Confidence-based masking decisions
- Reversible masking (original data accessible locally)
- Performance optimized for large datasets

Compliance: GDPR and Hong Kong PDPO compliant
"""

import re
import pandas as pd
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

# Import the enhanced field identification module
from .enhanced_field_identification import (
    EnhancedFieldIdentifier,
    FieldType,
)

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class MaskingResult:
    """Result of masking operation"""

    original_value: str
    masked_value: str
    field_type: FieldType
    confidence: float
    is_masked: bool


class IntegratedDisplayMasking:
    """
    Integrated display masking system that combines enhanced field identification
    with comprehensive masking for all supported PII types.
    """

    def __init__(
        self,
        default_show_sensitive: bool = False,
        confidence_threshold: float = 0.5,
        config_path: Optional[str] = None,
    ):
        """
        Initialize integrated display masking system

        Args:
            default_show_sensitive: Default visibility setting for sensitive data
            confidence_threshold: Minimum confidence for field identification
            config_path: Optional path to custom patterns configuration
        """
        self.show_sensitive = default_show_sensitive
        self.confidence_threshold = confidence_threshold

        # Initialize the enhanced field identifier
        self.field_identifier = EnhancedFieldIdentifier(config_path=config_path)

        # Initialize masking patterns for all field types
        self.masking_patterns = self._init_masking_patterns()

        logger.info("Integrated display masking system initialized")

    def _init_masking_patterns(self) -> Dict[FieldType, str]:
        """Initialize masking patterns for each field type"""
        return {
            FieldType.ACCOUNT_ID: "preserve_prefix_suffix",  # ACC****56
            FieldType.HKID: "preserve_prefix_pattern",  # A******(*)
            FieldType.EMAIL: "preserve_structure",  # j***@*****.com
            FieldType.PHONE: "preserve_country_last4",  # +852 ****5678
            FieldType.NAME: "preserve_initials",  # J*** D***
            FieldType.ADDRESS: "preserve_area_only",  # *** Kowloon
            FieldType.PASSPORT: "preserve_country_pattern",  # HK******
            FieldType.DRIVERS_LICENSE: "preserve_prefix",  # DL****
            FieldType.CREDIT_CARD: "preserve_last4",  # ****-****-****-1234
            FieldType.BANK_ACCOUNT: "preserve_bank_last4",  # ***-***-1234
            FieldType.IP_ADDRESS: "preserve_network",  # 192.168.***.***
            FieldType.DATE_OF_BIRTH: "preserve_year_only",  # ****/****/1990
            FieldType.GENERAL: "default_masking",  # Standard masking
        }

    def set_visibility(self, show_sensitive: bool):
        """Toggle sensitivity visibility"""
        self.show_sensitive = show_sensitive
        logger.debug(f"Visibility set to: {'sensitive' if show_sensitive else 'masked'}")

    def set_confidence_threshold(self, threshold: float):
        """Set confidence threshold for field identification"""
        if 0.0 <= threshold <= 1.0:
            self.confidence_threshold = threshold
            logger.debug(f"Confidence threshold set to: {threshold}")
        else:
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")

    def mask_account_id(self, value: str) -> str:
        """Mask account ID: ACC123456 → ACC****56"""
        if len(value) <= 2:
            return value
        elif len(value) <= 5:
            return value[:1] + "*" * (len(value) - 1)
        return value[:3] + "*" * (len(value) - 5) + value[-2:]

    def mask_hkid(self, value: str) -> str:
        """Mask HKID: A123456(7) → A******(*), AB123456(8) → A******(*)"""
        if "(" in value and ")" in value:
            # For HKIDs like A123456(7) or AB123456(8)
            # Always show just first letter and mask the rest
            prefix = value[0]
            suffix_start = value.find("(")
            return prefix + "*" * (suffix_start - 1) + "(*)"
        return value[0] + "*" * (len(value) - 1)

    def mask_email(self, value: str) -> str:
        """Mask email: john@example.com → j***@*****.com"""
        if "@" not in value:
            return value

        local, domain = value.split("@", 1)

        # Mask local part
        masked_local = local[0] + "*" * (len(local) - 1) if len(local) > 1 else local

        # Mask domain
        if "." in domain:
            domain_parts = domain.split(".")
            domain_name = domain_parts[0]
            domain_ext = ".".join(domain_parts[1:])

            # Don't mask very short domain names (1-2 chars)
            if len(domain_name) <= 2:
                masked_domain = domain_name
            else:
                masked_domain = "*" * len(domain_name)
            masked_domain += "." + domain_ext
        else:
            masked_domain = "*" * len(domain)

        return f"{masked_local}@{masked_domain}"

    def mask_phone(self, value: str) -> str:
        """Mask phone: +852 1234 5678 → +852 ****5678"""
        # Remove formatting but preserve structure
        clean_phone = re.sub(r"[^\d+]", "", value)

        if clean_phone.startswith("+852") and len(clean_phone) >= 12:
            # Hong Kong format
            return f"+852 ****{clean_phone[-4:]}"
        elif len(clean_phone) >= 8:
            # Generic format - preserve last 4 digits
            return f"****{clean_phone[-4:]}"

        return "*" * len(value)

    def mask_name(self, value: str) -> str:
        """Mask name: John Doe → J*** D***"""
        parts = value.split()
        masked_parts = []

        for part in parts:
            if len(part) <= 1:
                masked_parts.append(part)
            else:
                masked_parts.append(part[0] + "*" * (len(part) - 1))

        return " ".join(masked_parts)

    def mask_address(self, value: str) -> str:
        """Mask address: Flat 5A, 123 Nathan Road, Kowloon → *** Kowloon"""
        parts = value.split(",")
        if len(parts) > 1:
            # Keep only the last part (usually area/district)
            return "*** " + parts[-1].strip()

        # If no comma, keep last word
        words = value.split()
        return "*** " + words[-1] if words else value

    def mask_passport(self, value: str) -> str:
        """Mask passport: HK1234567 → HK*****67"""
        if len(value) <= 4:
            return value[:2] + "*" * (len(value) - 2)
        return value[:2] + "*" * (len(value) - 4) + value[-2:]

    def mask_drivers_license(self, value: str) -> str:
        """Mask driver's license: DL123456789 → DL*****789"""
        if len(value) <= 5:
            return value[:2] + "*" * (len(value) - 2)
        return value[:2] + "*" * (len(value) - 5) + value[-3:]

    def mask_credit_card(self, value: str) -> str:
        """Mask credit card: 1234-5678-9012-3456 → ****-****-****-3456"""
        # Remove spaces and dashes for processing
        clean_value = re.sub(r"[^\d]", "", value)

        if len(clean_value) >= 12:
            # Preserve last 4 digits
            masked_digits = "*" * (len(clean_value) - 4) + clean_value[-4:]

            # Restore original formatting if present
            if "-" in value:
                # Format as ****-****-****-1234
                formatted = "-".join(
                    [masked_digits[i : i + 4] for i in range(0, len(masked_digits), 4)]
                )
                return formatted
            elif " " in value:
                # Format with spaces
                formatted = " ".join(
                    [masked_digits[i : i + 4] for i in range(0, len(masked_digits), 4)]
                )
                return formatted

            return masked_digits

        return "*" * len(value)

    def mask_bank_account(self, value: str) -> str:
        """Mask bank account: 123-456-789012 → ***-***-9012"""
        if "-" in value:
            parts = value.split("-")
            if len(parts) >= 2:
                # Mask all but last part
                masked_parts = ["*" * len(part) for part in parts[:-1]]
                masked_parts.append(parts[-1])
                return "-".join(masked_parts)

        # Fallback: preserve last 4 characters
        if len(value) > 4:
            return "*" * (len(value) - 4) + value[-4:]

        return value

    def mask_ip_address(self, value: str) -> str:
        """Mask IP address: 192.168.1.100 → 192.168.***.***"""
        parts = value.split(".")
        if len(parts) == 4:
            # Keep first two octets, mask last two
            return f"{parts[0]}.{parts[1]}.***,***"

        return value

    def mask_date_of_birth(self, value: str) -> str:
        """Mask date of birth: 1990-05-15 → ****-**-15"""
        # Common date formats: YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY
        if "-" in value:
            parts = value.split("-")
            if len(parts) == 3:
                return f"****-**-{parts[-1]}"
        elif "/" in value:
            parts = value.split("/")
            if len(parts) == 3:
                # Keep only day part
                return "**/**/***"

        return "*" * (len(value) - 2) + value[-2:] if len(value) > 2 else value

    def mask_general(self, value: str) -> str:
        """Default masking for general/unknown field types"""
        if len(value) <= 2:
            return value
        elif len(value) <= 4:
            return value[0] + "*" * (len(value) - 1)
        else:
            return value[:2] + "*" * (len(value) - 4) + value[-2:]

    def get_masking_function(self, field_type: FieldType):
        """Get appropriate masking function for field type"""
        masking_functions = {
            FieldType.ACCOUNT_ID: self.mask_account_id,
            FieldType.HKID: self.mask_hkid,
            FieldType.EMAIL: self.mask_email,
            FieldType.PHONE: self.mask_phone,
            FieldType.NAME: self.mask_name,
            FieldType.ADDRESS: self.mask_address,
            FieldType.PASSPORT: self.mask_passport,
            FieldType.DRIVERS_LICENSE: self.mask_drivers_license,
            FieldType.CREDIT_CARD: self.mask_credit_card,
            FieldType.BANK_ACCOUNT: self.mask_bank_account,
            FieldType.IP_ADDRESS: self.mask_ip_address,
            FieldType.DATE_OF_BIRTH: self.mask_date_of_birth,
            FieldType.GENERAL: self.mask_general,
        }

        return masking_functions.get(field_type, self.mask_general)

    def mask_value(self, value: str, field_type: FieldType) -> str:
        """Apply appropriate masking based on field type"""
        if not value or not isinstance(value, str):
            return str(value) if value is not None else ""

        masking_func = self.get_masking_function(field_type)
        return masking_func(value)

    def process_value(
        self, value: str, column_name: str = "", force_field_type: Optional[FieldType] = None
    ) -> MaskingResult:
        """
        Process a single value with integrated field identification and masking

        Args:
            value: Original value to process
            column_name: Column name for context
            force_field_type: Override automatic field type detection

        Returns:
            MaskingResult: Complete masking result with metadata
        """
        if not value or not isinstance(value, str):
            return MaskingResult(
                original_value=str(value) if value is not None else "",
                masked_value=str(value) if value is not None else "",
                field_type=FieldType.GENERAL,
                confidence=0.0,
                is_masked=False,
            )

        # Use forced field type or auto-detect
        if force_field_type:
            field_type = force_field_type
            confidence = 1.0
        else:
            # Use enhanced field identification
            identification_result = self.field_identifier.identify_field(column_name, [value])
            field_type = identification_result.field_type
            confidence = identification_result.confidence

        # Determine if masking should be applied
        should_mask = (
            not self.show_sensitive
            and confidence >= self.confidence_threshold
            and field_type != FieldType.GENERAL
        )

        # Apply masking if needed
        if should_mask:
            masked_value = self.mask_value(value, field_type)
        else:
            masked_value = value

        return MaskingResult(
            original_value=value,
            masked_value=masked_value,
            field_type=field_type,
            confidence=confidence,
            is_masked=should_mask,
        )

    def process_dataframe(
        self,
        df: pd.DataFrame,
        sensitive_columns: Optional[List[str]] = None,
        column_field_types: Optional[Dict[str, FieldType]] = None,
    ) -> Dict[str, Any]:
        """
        Process entire dataframe with integrated masking

        Args:
            df: Original dataframe
            sensitive_columns: Optional list of columns to process (None = all columns)
            column_field_types: Optional mapping of column names to field types

        Returns:
            dict: Processing results with masked dataframe and metadata
        """
        logger.info(f"Processing dataframe with {len(df)} rows, {len(df.columns)} columns")

        # Create a copy for masking
        result_df = df.copy()
        masking_metadata = {}
        total_masked_fields = 0

        # Determine columns to process
        columns_to_process = sensitive_columns if sensitive_columns else df.columns

        for column in columns_to_process:
            if column not in df.columns:
                logger.warning(f"Column '{column}' not found in dataframe")
                continue

            # Get field type for column (forced or auto-detected)
            force_field_type = column_field_types.get(column) if column_field_types else None

            # Process each value in the column
            column_results = []
            masked_count = 0

            for value in df[column]:
                if pd.isna(value):
                    column_results.append(value)
                    continue

                result = self.process_value(
                    str(value), column_name=column, force_field_type=force_field_type
                )

                column_results.append(result.masked_value)
                if result.is_masked:
                    masked_count += 1

            # Update result dataframe
            result_df[column] = column_results
            total_masked_fields += masked_count

            # Store metadata
            if masked_count > 0:
                # Get field identification for this column
                sample_values = df[column].dropna().astype(str).head(5).tolist()
                if sample_values:
                    identification = self.field_identifier.identify_field(column, sample_values)
                    masking_metadata[column] = {
                        "field_type": identification.field_type.value,
                        "confidence": identification.confidence,
                        "masked_count": masked_count,
                        "total_count": len(df[column].dropna()),
                        "masking_percentage": (masked_count / len(df[column].dropna())) * 100,
                    }

        logger.info(
            f"Masking complete: {total_masked_fields} fields masked across {len(masking_metadata)} columns"
        )

        return {
            "dataframe": result_df,
            "original_dataframe": df,
            "is_masked": not self.show_sensitive,
            "masking_metadata": masking_metadata,
            "total_masked_fields": total_masked_fields,
            "show_sensitive": self.show_sensitive,
            "confidence_threshold": self.confidence_threshold,
            "message": self._generate_status_message(total_masked_fields, len(masking_metadata)),
        }

    def _generate_status_message(self, masked_fields: int, masked_columns: int) -> str:
        """Generate user-friendly status message"""
        if self.show_sensitive:
            return "🔓 Showing original sensitive data"
        elif masked_fields > 0:
            return f"🔒 {masked_fields} sensitive fields masked across {masked_columns} columns"
        else:
            return "✅ No sensitive data detected"

    def toggle_visibility(self) -> bool:
        """Toggle visibility setting and return new state"""
        self.show_sensitive = not self.show_sensitive
        logger.info(f"Visibility toggled to: {'sensitive' if self.show_sensitive else 'masked'}")
        return self.show_sensitive

    def get_field_type_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary of detected field types in dataframe"""
        summary = {}

        for column in df.columns:
            sample_values = df[column].dropna().astype(str).head(10).tolist()
            if sample_values:
                identification = self.field_identifier.identify_field(column, sample_values)
                summary[column] = {
                    "field_type": identification.field_type.value,
                    "confidence": identification.confidence,
                    "sample_count": len(sample_values),
                    "total_count": len(df[column].dropna()),
                }

        return summary


# Global instance for easy access
integrated_display_masker = IntegratedDisplayMasking()


def mask_for_display(
    value: str,
    show_sensitive: bool = False,
    column_name: str = "",
    field_type: Optional[FieldType] = None,
) -> str:
    """
    Convenience function for masking individual values with enhanced field identification

    Args:
        value: Original value
        show_sensitive: Whether to show sensitive data
        column_name: Column name for context
        field_type: Optional forced field type

    Returns:
        str: Masked or original value
    """
    integrated_display_masker.set_visibility(show_sensitive)
    result = integrated_display_masker.process_value(value, column_name, field_type)
    return result.masked_value


def process_dataframe_for_display(
    df: pd.DataFrame, show_sensitive: bool = False, sensitive_columns: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Convenience function for processing dataframes with enhanced masking

    Args:
        df: Original dataframe
        show_sensitive: Whether to show sensitive data
        sensitive_columns: Optional list of sensitive columns

    Returns:
        dict: Processing results
    """
    integrated_display_masker.set_visibility(show_sensitive)
    return integrated_display_masker.process_dataframe(df, sensitive_columns)
