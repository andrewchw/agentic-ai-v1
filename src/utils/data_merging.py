"""
Data Merging and Alignment Logic - Task 6.3
Part of the Agentic AI Revenue Assistant

This module implements logic to merge customer profile and purchase history data
by Account ID, handling edge cases and maintaining privacy protection.

Features:
- Account ID-based data alignment
- Handling of mismatched IDs, missing records, and duplicates
- Privacy masking integration (respects toggle state)
- Unified data structure for AI analysis
- Comprehensive error handling and data quality reporting

Compliance: GDPR and Hong Kong PDPO compliant with privacy-first design
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class MergeStrategy(Enum):
    """Merge strategy options"""

    INNER = "inner"  # Only records with matching Account IDs
    LEFT = "left"  # All customer records + matching purchase data
    RIGHT = "right"  # All purchase records + matching customer data
    OUTER = "outer"  # All records from both datasets


@dataclass
class MergeResult:
    """Result of data merging operation"""

    success: bool
    message: str
    merged_data: Optional[pd.DataFrame]
    display_data: Optional[pd.DataFrame]  # Privacy-masked version
    metadata: Dict[str, Any]
    quality_report: Dict[str, Any]
    errors: List[str]


@dataclass
class DataQualityReport:
    """Data quality and alignment report"""

    total_customer_records: int
    total_purchase_records: int
    matched_records: int
    unmatched_customer_ids: List[str]
    unmatched_purchase_ids: List[str]
    duplicate_customer_ids: List[str]
    duplicate_purchase_ids: List[str]
    missing_account_ids: Dict[str, int]  # dataset -> count
    data_types_consistent: bool
    quality_score: float  # 0.0 to 1.0


class DataMerger:
    """
    Data merging and alignment system for customer and purchase data.

    Provides Account ID-based data alignment with privacy protection,
    quality validation, and comprehensive error handling.
    """

    def __init__(self):
        """Initialize the data merger"""
        self.account_id_column = "Account ID"
        logger.info("DataMerger initialized")

    def merge_datasets(
        self,
        customer_data_dict: Dict[str, Any],
        purchase_data_dict: Dict[str, Any],
        strategy: MergeStrategy = MergeStrategy.LEFT,
        show_sensitive: bool = False,
    ) -> MergeResult:
        """
        Merge customer and purchase datasets by Account ID.

        Args:
            customer_data_dict: Customer data from session state (processed format)
            purchase_data_dict: Purchase data from session state (processed format)
            strategy: Merge strategy (inner, left, right, outer)
            show_sensitive: Whether to show sensitive data in output

        Returns:
            MergeResult with merged data and quality report
        """
        try:
            start_time = datetime.now()

            # Extract dataframes based on privacy setting
            if show_sensitive:
                customer_df = customer_data_dict.get("original_data")
                purchase_df = purchase_data_dict.get("original_data")
                customer_display = customer_data_dict.get("original_data")
                purchase_display = purchase_data_dict.get("original_data")
            else:
                customer_df = customer_data_dict.get("original_data")  # Need original for merging logic
                purchase_df = purchase_data_dict.get("original_data")
                customer_display = customer_data_dict.get("display_data")  # Masked for display
                purchase_display = purchase_data_dict.get("display_data")

            if customer_df is None or purchase_df is None:
                return MergeResult(
                    success=False,
                    message="Missing customer or purchase data",
                    merged_data=None,
                    display_data=None,
                    metadata={},
                    quality_report={},
                    errors=["Customer or purchase data not available"],
                )

            # Validate Account ID column exists
            validation_result = self._validate_datasets(customer_df, purchase_df)
            if not validation_result["valid"]:
                return MergeResult(
                    success=False,
                    message=validation_result["message"],
                    merged_data=None,
                    display_data=None,
                    metadata={},
                    quality_report={},
                    errors=validation_result["errors"],
                )

            # Generate data quality report
            quality_report = self._generate_quality_report(customer_df, purchase_df)

            # Perform the merge operation
            merge_result = self._perform_merge(customer_df, purchase_df, strategy)
            display_result = self._perform_merge(customer_display, purchase_display, strategy)

            if not merge_result["success"]:
                return MergeResult(
                    success=False,
                    message=merge_result["message"],
                    merged_data=None,
                    display_data=None,
                    metadata={},
                    quality_report=quality_report.__dict__,
                    errors=merge_result["errors"],
                )

            # Create metadata
            processing_time = (datetime.now() - start_time).total_seconds()
            metadata = {
                "merge_strategy": strategy.value,
                "merge_timestamp": datetime.now().isoformat(),
                "processing_time_seconds": processing_time,
                "show_sensitive": show_sensitive,
                "source_customer_shape": customer_df.shape,
                "source_purchase_shape": purchase_df.shape,
                "merged_shape": merge_result["merged_data"].shape,
                "quality_score": quality_report.quality_score,
            }

            logger.info(f"Data merge completed successfully in {processing_time:.3f}s")
            logger.info(
                f"Merged {quality_report.matched_records} records with quality score {quality_report.quality_score:.2f}"
            )

            return MergeResult(
                success=True,
                message=f"Successfully merged {quality_report.matched_records} records using {strategy.value} join",
                merged_data=merge_result["merged_data"],
                display_data=display_result["merged_data"],
                metadata=metadata,
                quality_report=quality_report.__dict__,
                errors=[],
            )

        except Exception as e:
            error_msg = f"Error during data merge: {str(e)}"
            logger.error(error_msg)
            return MergeResult(
                success=False,
                message=error_msg,
                merged_data=None,
                display_data=None,
                metadata={},
                quality_report={},
                errors=[error_msg],
            )

    def _validate_datasets(self, customer_df: pd.DataFrame, purchase_df: pd.DataFrame) -> Dict[str, Any]:
        """Validate datasets for merging compatibility"""
        errors = []

        # Check for Account ID column in both datasets
        if self.account_id_column not in customer_df.columns:
            errors.append(f"Customer data missing '{self.account_id_column}' column")

        if self.account_id_column not in purchase_df.columns:
            errors.append(f"Purchase data missing '{self.account_id_column}' column")

        if errors:
            return {"valid": False, "message": "Dataset validation failed", "errors": errors}

        # Check for empty Account ID values
        customer_null_ids = customer_df[self.account_id_column].isnull().sum()
        purchase_null_ids = purchase_df[self.account_id_column].isnull().sum()

        warnings = []
        if customer_null_ids > 0:
            warnings.append(f"Customer data has {customer_null_ids} null Account IDs")
        if purchase_null_ids > 0:
            warnings.append(f"Purchase data has {purchase_null_ids} null Account IDs")

        return {"valid": True, "message": "Validation passed", "errors": [], "warnings": warnings}

    def _generate_quality_report(self, customer_df: pd.DataFrame, purchase_df: pd.DataFrame) -> DataQualityReport:
        """Generate comprehensive data quality report"""

        # Get unique Account IDs from each dataset
        customer_ids = set(customer_df[self.account_id_column].dropna().astype(str))
        purchase_ids = set(purchase_df[self.account_id_column].dropna().astype(str))

        # Find matches and mismatches
        matched_ids = customer_ids.intersection(purchase_ids)
        unmatched_customer = list(customer_ids - purchase_ids)
        unmatched_purchase = list(purchase_ids - customer_ids)

        # Check for duplicates
        customer_duplicates = customer_df[customer_df[self.account_id_column].duplicated()][
            self.account_id_column
        ].tolist()
        purchase_duplicates = purchase_df[purchase_df[self.account_id_column].duplicated()][
            self.account_id_column
        ].tolist()

        # Count missing Account IDs
        missing_ids = {
            "customer": customer_df[self.account_id_column].isnull().sum(),
            "purchase": purchase_df[self.account_id_column].isnull().sum(),
        }

        # Calculate quality score
        total_unique_ids = len(customer_ids.union(purchase_ids))
        if total_unique_ids > 0:
            match_rate = len(matched_ids) / total_unique_ids
            duplicate_penalty = (len(customer_duplicates) + len(purchase_duplicates)) / (
                len(customer_df) + len(purchase_df)
            )
            missing_penalty = sum(missing_ids.values()) / (len(customer_df) + len(purchase_df))
            quality_score = max(0.0, match_rate - duplicate_penalty - missing_penalty)
        else:
            quality_score = 0.0

        return DataQualityReport(
            total_customer_records=len(customer_df),
            total_purchase_records=len(purchase_df),
            matched_records=len(matched_ids),
            unmatched_customer_ids=unmatched_customer[:10],  # Limit for display
            unmatched_purchase_ids=unmatched_purchase[:10],
            duplicate_customer_ids=customer_duplicates,
            duplicate_purchase_ids=purchase_duplicates,
            missing_account_ids=missing_ids,
            data_types_consistent=True,  # Can be enhanced with type checking
            quality_score=quality_score,
        )

    def _perform_merge(
        self, customer_df: pd.DataFrame, purchase_df: pd.DataFrame, strategy: MergeStrategy
    ) -> Dict[str, Any]:
        """Perform the actual merge operation"""
        try:
            # Clean Account IDs (remove null values and convert to string)
            customer_clean = customer_df.dropna(subset=[self.account_id_column]).copy()
            purchase_clean = purchase_df.dropna(subset=[self.account_id_column]).copy()

            customer_clean[self.account_id_column] = customer_clean[self.account_id_column].astype(str)
            purchase_clean[self.account_id_column] = purchase_clean[self.account_id_column].astype(str)

            # Add prefixes to avoid column name conflicts
            customer_clean = customer_clean.add_prefix("customer_").rename(
                columns={f"customer_{self.account_id_column}": self.account_id_column}
            )
            purchase_clean = purchase_clean.add_prefix("purchase_").rename(
                columns={f"purchase_{self.account_id_column}": self.account_id_column}
            )

            # Perform merge based on strategy
            merged_df = pd.merge(
                customer_clean,
                purchase_clean,
                on=self.account_id_column,
                how=strategy.value,
                suffixes=("_customer", "_purchase"),
            )

            return {
                "success": True,
                "message": f"Merge completed with {len(merged_df)} records",
                "merged_data": merged_df,
                "errors": [],
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Merge operation failed: {str(e)}",
                "merged_data": None,
                "errors": [str(e)],
            }
