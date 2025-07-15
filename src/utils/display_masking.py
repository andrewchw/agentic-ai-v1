"""
Display Masking Module for UI Privacy Control
Part of Task 5.1 - Dual-Layer Privacy Architecture

This module provides reversible display masking with toggle control.
Original data remains accessible locally - only display is masked.
"""

import re
from typing import Dict, Any, Optional, List
from enum import Enum


class FieldType(Enum):
    """Enumeration of sensitive field types for masking"""

    NAME = "name"
    EMAIL = "email"
    HKID = "hkid"
    PHONE = "phone"
    ADDRESS = "address"
    ACCOUNT_ID = "account_id"
    CREDIT_CARD = "credit_card"
    OTHER = "other"


class DisplayMasking:
    """
    Main class for handling display masking with toggle control
    """

    def __init__(self, default_show_sensitive: bool = False):
        """
        Initialize display masking

        Args:
            default_show_sensitive: Default visibility setting
        """
        self.show_sensitive = default_show_sensitive
        self.field_patterns = self._init_field_patterns()

    def _init_field_patterns(self) -> Dict[str, str]:
        """Initialize regex patterns for field identification"""
        return {
            "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "hkid": r"^[A-Z]{1,2}[0-9]{6}\([0-9A]\)$",
            "phone": r"^(\+852\s?)?[2-9][0-9]{3}\s?[0-9]{4}$",
            "name": r"^[A-Za-z\s]{2,50}$",
            "account_id": r"^[A-Z0-9]{6,12}$",
        }

    def set_visibility(self, show_sensitive: bool):
        """Toggle sensitivity visibility"""
        self.show_sensitive = show_sensitive

    def identify_field_type(self, value: str, column_name: str = "") -> FieldType:
        """
        Automatically identify field type based on value and column name

        Args:
            value: The data value to analyze
            column_name: Optional column name for context

        Returns:
            FieldType: Identified field type
        """
        if not value or not isinstance(value, str):
            return FieldType.OTHER

        # Check column name patterns first
        column_lower = column_name.lower()
        if any(keyword in column_lower for keyword in ["email", "mail"]):
            return FieldType.EMAIL
        elif any(keyword in column_lower for keyword in ["name", "customer", "client"]):
            return FieldType.NAME
        elif any(keyword in column_lower for keyword in ["phone", "mobile", "tel"]):
            return FieldType.PHONE
        elif any(keyword in column_lower for keyword in ["hkid", "id_card", "identity"]):
            return FieldType.HKID
        elif any(keyword in column_lower for keyword in ["address", "addr"]):
            return FieldType.ADDRESS
        elif any(keyword in column_lower for keyword in ["account", "customer_id"]):
            return FieldType.ACCOUNT_ID

        # Check value patterns
        if re.match(self.field_patterns["email"], value):
            return FieldType.EMAIL
        elif re.match(self.field_patterns["hkid"], value):
            return FieldType.HKID
        elif re.match(self.field_patterns["phone"], value):
            return FieldType.PHONE
        elif re.match(self.field_patterns["account_id"], value):
            return FieldType.ACCOUNT_ID
        elif re.match(self.field_patterns["name"], value):
            return FieldType.NAME

        return FieldType.OTHER

    def mask_name(self, name: str) -> str:
        """
        Mask name with pattern: "John Doe" → "J*** D***"

        Args:
            name: Original name

        Returns:
            str: Masked name
        """
        if not name or len(name) < 2:
            return name

        parts = name.split()
        masked_parts = []

        for part in parts:
            if len(part) <= 1:
                masked_parts.append(part)
            else:
                masked_parts.append(part[0] + "*" * (len(part) - 1))

        return " ".join(masked_parts)

    def mask_email(self, email: str) -> str:
        """
        Mask email with pattern: "john@example.com" → "j***@*****.com"

        Args:
            email: Original email

        Returns:
            str: Masked email
        """
        if not email or "@" not in email:
            return email

        local, domain = email.split("@", 1)

        # Mask local part
        if len(local) <= 1:
            masked_local = local
        else:
            masked_local = local[0] + "*" * (len(local) - 1)

        # Mask domain
        if "." in domain:
            domain_parts = domain.split(".")
            domain_name = domain_parts[0]
            domain_ext = ".".join(domain_parts[1:])

            if len(domain_name) <= 2:
                masked_domain = domain_name
            else:
                masked_domain = "*" * len(domain_name)

            masked_domain += "." + domain_ext
        else:
            masked_domain = "*" * len(domain)

        return f"{masked_local}@{masked_domain}"

    def mask_hkid(self, hkid: str) -> str:
        """
        Mask HKID with pattern: "A123456(7)" → "A******(*)"

        Args:
            hkid: Original HKID

        Returns:
            str: Masked HKID
        """
        if not hkid or len(hkid) < 3:
            return hkid

        # Pattern: A123456(7) → A******(*)
        if "(" in hkid and ")" in hkid:
            prefix = hkid[0]  # Keep first letter
            suffix_start = hkid.find("(")
            masked = prefix + "*" * (suffix_start - 1) + "(*)"
            return masked

        return hkid[0] + "*" * (len(hkid) - 1)

    def mask_phone(self, phone: str) -> str:
        """
        Mask phone with pattern: "+852 1234 5678" → "+852 ****5678"

        Args:
            phone: Original phone number

        Returns:
            str: Masked phone number
        """
        if not phone:
            return phone

        # Keep country code and last 4 digits
        clean_phone = re.sub(r"[^\d+]", "", phone)

        if len(clean_phone) >= 8:
            if clean_phone.startswith("+852"):
                # Hong Kong format
                return f"+852 ****{clean_phone[-4:]}"
            else:
                # Generic format
                return f"****{clean_phone[-4:]}"

        return "*" * len(phone)

    def mask_address(self, address: str) -> str:
        """
        Mask address keeping only general area information

        Args:
            address: Original address

        Returns:
            str: Masked address
        """
        if not address:
            return address

        # Keep only last part (usually area/district)
        parts = address.split(",")
        if len(parts) > 1:
            return "*** " + parts[-1].strip()

        return "*** " + address.split()[-1] if address.split() else address

    def mask_account_id(self, account_id: str) -> str:
        """
        Mask account ID with pattern: "ACC123456" → "ACC****56"

        Args:
            account_id: Original account ID

        Returns:
            str: Masked account ID
        """
        if not account_id or len(account_id) < 4:
            return account_id

        # Keep first 3 and last 2 characters
        if len(account_id) <= 5:
            return account_id[:2] + "*" * (len(account_id) - 2)

        return account_id[:3] + "*" * (len(account_id) - 5) + account_id[-2:]

    def mask_value(self, value: str, field_type: FieldType) -> str:
        """
        Apply appropriate masking based on field type

        Args:
            value: Original value
            field_type: Type of field

        Returns:
            str: Masked value
        """
        if not value:
            return value

        masking_functions = {
            FieldType.NAME: self.mask_name,
            FieldType.EMAIL: self.mask_email,
            FieldType.HKID: self.mask_hkid,
            FieldType.PHONE: self.mask_phone,
            FieldType.ADDRESS: self.mask_address,
            FieldType.ACCOUNT_ID: self.mask_account_id,
        }

        masking_func = masking_functions.get(field_type)
        if masking_func:
            return masking_func(value)

        # Default masking for unknown types
        return value[:2] + "*" * (len(value) - 2) if len(value) > 2 else value

    def process_value(
        self, value: str, field_type: Optional[FieldType] = None, column_name: str = ""
    ) -> str:
        """
        Process value based on visibility setting

        Args:
            value: Original value
            field_type: Optional field type (auto-detected if None)
            column_name: Optional column name for context

        Returns:
            str: Original or masked value based on settings
        """
        if self.show_sensitive:
            return value

        if field_type is None:
            field_type = self.identify_field_type(value, column_name)

        # Only mask sensitive field types
        if field_type in [
            FieldType.NAME,
            FieldType.EMAIL,
            FieldType.HKID,
            FieldType.PHONE,
            FieldType.ADDRESS,
            FieldType.ACCOUNT_ID,
        ]:
            return self.mask_value(value, field_type)

        return value

    def process_dataframe(
        self, df, sensitive_columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Process entire dataframe with masking

        Args:
            df: Original dataframe
            sensitive_columns: Optional list of sensitive column names

        Returns:
            dict: Processed dataframe info and masking status
        """
        if self.show_sensitive:
            return {"dataframe": df, "masked": False, "message": "Showing original data"}

        # Create a copy for masking
        masked_df = df.copy()

        for column in df.columns:
            if sensitive_columns and column not in sensitive_columns:
                continue

            # Process each value in the column
            masked_df[column] = df[column].apply(
                lambda x: self.process_value(str(x), column_name=column) if x is not None else x
            )

        return {
            "dataframe": masked_df,
            "masked": True,
            "message": "Displaying masked data (toggle to show original)",
        }


# Global instance for easy access
display_masker = DisplayMasking()


def mask_for_display(
    value: str,
    show_sensitive: bool = False,
    field_type: Optional[FieldType] = None,
    column_name: str = "",
) -> str:
    """
    Convenience function for masking individual values

    Args:
        value: Original value
        show_sensitive: Whether to show sensitive data
        field_type: Optional field type
        column_name: Optional column name

    Returns:
        str: Masked or original value
    """
    display_masker.set_visibility(show_sensitive)
    return display_masker.process_value(value, field_type, column_name)
