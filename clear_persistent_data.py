#!/usr/bin/env python3
"""
Clear All Persistent Data Script
================================

This script clears all persistent session data and file backups to reset the system
to a clean state for testing purposes.
"""

import os
import shutil
import json
from datetime import datetime

def clear_session_backups():
    """Clear all session backup files"""
    backup_dir = "data/session_backups"
    if os.path.exists(backup_dir):
        print(f"🗑️ Clearing session backups from {backup_dir}...")
        try:
            # List files before deletion
            files = os.listdir(backup_dir)
            print(f"   Found {len(files)} backup files to delete")
            for file in files:
                print(f"   - {file}")
            
            # Clear the directory
            shutil.rmtree(backup_dir)
            os.makedirs(backup_dir, exist_ok=True)
            print("✅ Session backups cleared successfully!")
            return True
        except Exception as e:
            print(f"❌ Error clearing session backups: {e}")
            return False
    else:
        print("ℹ️ No session backup directory found")
        return True

def clear_product_catalog():
    """Clear persistent product catalog"""
    catalog_file = "data/product_catalog/persistent_catalog.json"
    if os.path.exists(catalog_file):
        print(f"🗑️ Clearing product catalog: {catalog_file}")
        try:
            os.remove(catalog_file)
            print("✅ Product catalog cleared successfully!")
            return True
        except Exception as e:
            print(f"❌ Error clearing product catalog: {e}")
            return False
    else:
        print("ℹ️ No persistent product catalog found")
        return True

def show_cleanup_summary():
    """Show summary of what was cleaned"""
    print("\n" + "="*50)
    print("🧹 CLEANUP SUMMARY")
    print("="*50)
    print("✅ Session backup files: Cleared")
    print("✅ Product catalog: Cleared") 
    print("✅ Analysis results: Will be cleared on next app start")
    print("✅ Customer data: Will be cleared on next app start")
    print("✅ Collaboration results: Will be cleared on next app start")
    print("\n💡 Next Steps:")
    print("1. Restart your Streamlit application")
    print("2. Go to Upload Data page")
    print("3. Upload fresh customer and purchase data")
    print("4. Run new analysis")

def main():
    print("🚀 Clear All Persistent Data")
    print("="*50)
    print("This script will clear all persistent session data and file backups.")
    print("Use this to reset the system to a clean state for testing.\n")
    
    print("🧹 Starting cleanup process...")
    
    # Clear session backups
    backup_success = clear_session_backups()
    
    # Clear product catalog
    catalog_success = clear_product_catalog()
    
    # Show summary
    if backup_success and catalog_success:
        show_cleanup_summary()
        print("\n🎉 All persistent data cleared successfully!")
    else:
        print("\n⚠️ Some cleanup operations failed. Check the errors above.")

if __name__ == "__main__":
    main()
