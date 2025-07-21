"""
Product Catalog Database Management
Persistent JSON-based storage for Three HK product catalog
"""

import json
import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Default path for the product catalog database
DEFAULT_CATALOG_PATH = "data/product_catalog.json"


class ProductCatalogDB:
    """Manages the persistent product catalog database"""
    
    def __init__(self, db_path: str = DEFAULT_CATALOG_PATH):
        """Initialize the product catalog database manager
        
        Args:
            db_path: Path to the JSON database file
        """
        self.db_path = Path(db_path)
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure the database file and directory exist"""
        # Create directory if it doesn't exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create empty database if file doesn't exist
        if not self.db_path.exists():
            self._create_empty_db()
    
    def _create_empty_db(self):
        """Create an empty product catalog database"""
        empty_db = {
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "version": "1.0",
                "total_plans": 0,
                "description": "Three HK Product Catalog - Persistent JSON Database"
            },
            "plans": []
        }
        self._save_db(empty_db)
    
    def _load_db(self) -> Dict[str, Any]:
        """Load the database from JSON file"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading database: {e}")
            self._create_empty_db()
            return self._load_db()
    
    def _save_db(self, data: Dict[str, Any]):
        """Save the database to JSON file"""
        # Update metadata
        data["metadata"]["last_updated"] = datetime.now().isoformat()
        data["metadata"]["total_plans"] = len(data.get("plans", []))
        
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_catalog(self) -> pd.DataFrame:
        """Load the product catalog as a pandas DataFrame
        
        Returns:
            DataFrame containing all plans
        """
        db = self._load_db()
        plans = db.get("plans", [])
        
        if not plans:
            return pd.DataFrame()
        
        return pd.DataFrame(plans)
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get catalog metadata
        
        Returns:
            Metadata dictionary
        """
        db = self._load_db()
        return db.get("metadata", {})
    
    def save_catalog_from_dataframe(self, df: pd.DataFrame, description: str = None) -> bool:
        """Save a DataFrame as the product catalog
        
        Args:
            df: DataFrame containing product catalog data
            description: Optional description for this catalog version
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert DataFrame to list of dictionaries
            plans = df.to_dict('records')
            
            # Prepare database structure
            db_data = {
                "metadata": {
                    "last_updated": datetime.now().isoformat(),
                    "version": "1.0",
                    "total_plans": len(plans),
                    "description": description or "Three HK Product Catalog - Updated via Upload"
                },
                "plans": plans
            }
            
            # Save to database
            self._save_db(db_data)
            return True
            
        except Exception as e:
            print(f"Error saving catalog: {e}")
            return False
    
    def save_catalog_from_csv_upload(self, uploaded_df: pd.DataFrame, filename: str) -> bool:
        """Save catalog from uploaded CSV file
        
        Args:
            uploaded_df: DataFrame from uploaded CSV
            filename: Original filename for tracking
            
        Returns:
            True if successful, False otherwise
        """
        description = f"Three HK Product Catalog - Uploaded from {filename}"
        return self.save_catalog_from_dataframe(uploaded_df, description)
    
    def get_plan_by_id(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific plan by Plan_ID
        
        Args:
            plan_id: The Plan_ID to search for
            
        Returns:
            Plan dictionary if found, None otherwise
        """
        df = self.load_catalog()
        if df.empty:
            return None
        
        if 'Plan_ID' not in df.columns:
            return None
        
        matching_plans = df[df['Plan_ID'] == plan_id]
        if matching_plans.empty:
            return None
        
        return matching_plans.iloc[0].to_dict()
    
    def get_plans_by_category(self, category: str) -> pd.DataFrame:
        """Get all plans in a specific category
        
        Args:
            category: Category to filter by (e.g., 'Mobile', 'Fixed', 'VAS')
            
        Returns:
            DataFrame containing matching plans
        """
        df = self.load_catalog()
        if df.empty or 'Category' not in df.columns:
            return pd.DataFrame()
        
        return df[df['Category'] == category]
    
    def get_plans_by_target_segment(self, segment: str) -> pd.DataFrame:
        """Get all plans targeting a specific segment
        
        Args:
            segment: Target segment (e.g., 'Premium', 'Standard', 'Enterprise')
            
        Returns:
            DataFrame containing matching plans
        """
        df = self.load_catalog()
        if df.empty or 'Target_Segment' not in df.columns:
            return pd.DataFrame()
        
        return df[df['Target_Segment'] == segment]
    
    def search_plans(self, **criteria) -> pd.DataFrame:
        """Search plans by multiple criteria
        
        Args:
            **criteria: Key-value pairs for filtering (e.g., Plan_Type='Postpaid')
            
        Returns:
            DataFrame containing matching plans
        """
        df = self.load_catalog()
        if df.empty:
            return pd.DataFrame()
        
        # Apply each filter criterion
        for column, value in criteria.items():
            if column in df.columns:
                df = df[df[column] == value]
        
        return df
    
    def get_catalog_stats(self) -> Dict[str, Any]:
        """Get statistics about the current catalog
        
        Returns:
            Dictionary containing catalog statistics
        """
        df = self.load_catalog()
        metadata = self.get_metadata()
        
        if df.empty:
            return {
                "total_plans": 0,
                "categories": [],
                "plan_types": [],
                "target_segments": [],
                "price_range": {"min": 0, "max": 0, "avg": 0},
                "last_updated": metadata.get("last_updated", "Unknown")
            }
        
        # Calculate statistics
        stats = {
            "total_plans": len(df),
            "categories": df['Category'].unique().tolist() if 'Category' in df.columns else [],
            "plan_types": df['Plan_Type'].unique().tolist() if 'Plan_Type' in df.columns else [],
            "target_segments": df['Target_Segment'].unique().tolist() if 'Target_Segment' in df.columns else [],
            "last_updated": metadata.get("last_updated", "Unknown")
        }
        
        # Price statistics
        if 'Base_Price' in df.columns:
            numeric_prices = pd.to_numeric(df['Base_Price'], errors='coerce').dropna()
            if not numeric_prices.empty:
                stats["price_range"] = {
                    "min": float(numeric_prices.min()),
                    "max": float(numeric_prices.max()),
                    "avg": float(numeric_prices.mean())
                }
            else:
                stats["price_range"] = {"min": 0, "max": 0, "avg": 0}
        else:
            stats["price_range"] = {"min": 0, "max": 0, "avg": 0}
        
        return stats
    
    def is_catalog_available(self) -> bool:
        """Check if a product catalog is available
        
        Returns:
            True if catalog has plans, False otherwise
        """
        df = self.load_catalog()
        return not df.empty
    
    def clear_catalog(self) -> bool:
        """Clear all plans from the catalog
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self._create_empty_db()
            return True
        except Exception as e:
            print(f"Error clearing catalog: {e}")
            return False


# Global instance for easy access
catalog_db = ProductCatalogDB()


def get_product_catalog() -> pd.DataFrame:
    """Get the current product catalog
    
    Returns:
        DataFrame containing all plans
    """
    return catalog_db.load_catalog()


def save_product_catalog(df: pd.DataFrame, description: str = None) -> bool:
    """Save a new product catalog
    
    Args:
        df: DataFrame containing product catalog data
        description: Optional description
        
    Returns:
        True if successful, False otherwise
    """
    return catalog_db.save_catalog_from_dataframe(df, description)


def get_catalog_stats() -> Dict[str, Any]:
    """Get catalog statistics
    
    Returns:
        Dictionary containing catalog statistics
    """
    return catalog_db.get_catalog_stats()


def is_catalog_available() -> bool:
    """Check if product catalog is available
    
    Returns:
        True if catalog is available, False otherwise
    """
    return catalog_db.is_catalog_available() 