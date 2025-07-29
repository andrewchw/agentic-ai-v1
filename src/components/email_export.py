"""
Email Export UI Components
Streamlit components for email template export functionality
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Tuple
import zipfile
import io
import json
from datetime import datetime

# Import the email template generator
from src.utils.email_templates import EmailTemplateGenerator


def render_email_export_section():
    """Render the complete email export section in the results page"""
    
    st.markdown("### 📧 Email Template Export")
    st.markdown("Generate personalized email templates for marketing campaigns")
    
    # Check if we have collaboration data
    if not _has_email_export_data():
        st.info("📊 Complete a CrewAI collaboration analysis to generate email templates")
        return
    
    # Get collaboration data
    collaboration_data = _get_collaboration_data()
    deliverables = st.session_state.get("crewai_deliverables", {})
    customer_data = st.session_state.get("customer_data", {})
    
    if not collaboration_data or not deliverables:
        st.warning("No collaboration results found. Please run CrewAI analysis first.")
        return
    
    # Email export configuration
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Export Configuration")
        
        # Format selection
        export_formats = st.multiselect(
            "Email Formats",
            ["HTML", "Plain Text"],
            default=["HTML", "Plain Text"],
            help="Select which email formats to generate"
        )
        
        # Template options
        include_subject_variants = st.checkbox(
            "Include Subject Line Variants",
            value=True,
            help="Generate multiple subject line options for A/B testing"
        )
        
        include_preview = st.checkbox(
            "Include Preview Files",
            value=True,
            help="Generate preview HTML files for easy review"
        )
        
        # Bulk actions
        st.markdown("#### Bulk Actions")
        select_all = st.checkbox("Select All Customers", value=True)
        
    with col2:
        st.markdown("#### Export Preview")
        
        # Get customer list for preview
        customers = _extract_customer_list(collaboration_data, customer_data)
        
        if customers:
            st.metric("Total Customers", len(customers))
            st.metric("Email Templates", len(customers) * len(export_formats))
            
            # Show sample customer for preview
            preview_customer = st.selectbox(
                "Preview Customer",
                options=range(len(customers)),
                format_func=lambda x: f"Customer {customers[x].get('customer_id', x+1)}"
            )
            
            if st.button("🔍 Preview Email Template", key="preview_email"):
                _show_email_preview(customers[preview_customer], deliverables, export_formats)
    
    # Customer selection
    if not select_all and customers:
        st.markdown("#### Customer Selection")
        selected_customers = st.multiselect(
            "Select customers for email export",
            options=range(len(customers)),
            format_func=lambda x: f"Customer {customers[x].get('customer_id', x+1)} - {customers[x].get('usage_pattern', 'Standard')}"
        )
        customers_to_export = [customers[i] for i in selected_customers]
    else:
        customers_to_export = customers
    
    # Export buttons
    if customers_to_export and export_formats:
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📧 Generate Email Templates", type="primary"):
                _generate_email_templates(
                    customers_to_export, 
                    deliverables, 
                    export_formats,
                    include_subject_variants,
                    include_preview
                )
        
        with col2:
            if st.button("📦 Export ZIP Package"):
                _export_email_zip_package(
                    customers_to_export, 
                    deliverables, 
                    export_formats,
                    include_subject_variants,
                    include_preview
                )
        
        with col3:
            if st.button("📊 Export Campaign Metadata"):
                _export_campaign_metadata(customers_to_export, deliverables)


def _has_email_export_data() -> bool:
    """Check if we have the necessary data for email export"""
    required_keys = ["crewai_collaboration_results", "crewai_deliverables"]
    
    for key in required_keys:
        if key not in st.session_state or not st.session_state[key]:
            return False
    
    return True


def _get_collaboration_data() -> Dict:
    """Get collaboration data from session state"""
    return st.session_state.get("crewai_collaboration_results", {})


def _extract_customer_list(collaboration_data: Dict, customer_data: Dict) -> List[Dict]:
    """Extract customer list from collaboration and customer data"""
    customers = []
    
    # Try to get customer data from various sources
    if "customers_analyzed" in collaboration_data:
        # From collaboration results
        for customer in collaboration_data["customers_analyzed"]:
            customers.append(customer)
    
    elif customer_data and "original_data" in customer_data:
        # From uploaded customer data
        df = customer_data["original_data"]
        if isinstance(df, pd.DataFrame):
            for idx, row in df.iterrows():
                customer = {
                    "customer_id": f"CUST_{idx+1:03d}",
                    "monthly_spend": row.get("monthly_spend", 0),
                    "data_usage_gb": row.get("data_usage_gb", 0),
                    "usage_pattern": "Standard",
                    "row_data": row.to_dict()
                }
                customers.append(customer)
                
                # Limit to reasonable number for email generation
                if len(customers) >= 50:
                    break
    
    return customers


def _show_email_preview(customer: Dict, deliverables: Dict, formats: List[str]):
    """Show email template preview for a customer"""
    
    generator = EmailTemplateGenerator()
    
    # Generate recommendations and offers from deliverables
    recommendations = _extract_recommendations_for_customer(customer, deliverables)
    offers = _extract_offers_for_customer(customer, deliverables)
    
    st.markdown("#### 📧 Email Template Preview")
    
    if "HTML" in formats:
        st.markdown("##### HTML Version")
        html_template = generator.generate_html_email_template(
            customer, recommendations, offers, deliverables
        )
        
        # Show HTML preview in expandable section
        with st.expander("View HTML Email", expanded=True):
            st.components.v1.html(html_template, height=600, scrolling=True)
        
        # Show HTML source in code block
        with st.expander("HTML Source Code"):
            st.code(html_template, language="html")
    
    if "Plain Text" in formats:
        st.markdown("##### Plain Text Version")
        text_template = generator.generate_plain_text_email_template(
            customer, recommendations, offers, deliverables
        )
        
        with st.expander("Plain Text Email", expanded=True):
            st.text(text_template)
    
    # Show subject line variants
    st.markdown("##### Subject Line Variants")
    subject_lines = generator.create_subject_lines(customer, offers[0] if offers else {}, deliverables)
    
    for i, subject in enumerate(subject_lines[:5], 1):
        st.text(f"{i}. {subject}")


def _generate_email_templates(
    customers: List[Dict], 
    deliverables: Dict, 
    formats: List[str],
    include_subjects: bool,
    include_preview: bool
):
    """Generate and display email templates"""
    
    generator = EmailTemplateGenerator()
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    all_templates = []
    
    for i, customer in enumerate(customers):
        status_text.text(f"Generating templates for Customer {i+1}/{len(customers)}")
        
        # Extract customer-specific data
        recommendations = _extract_recommendations_for_customer(customer, deliverables)
        offers = _extract_offers_for_customer(customer, deliverables)
        
        customer_templates = {
            "customer_id": customer.get("customer_id", f"CUST_{i+1:03d}"),
            "templates": {}
        }
        
        # Generate HTML template
        if "HTML" in formats:
            html_template = generator.generate_html_email_template(
                customer, recommendations, offers, deliverables
            )
            customer_templates["templates"]["html"] = html_template
        
        # Generate plain text template
        if "Plain Text" in formats:
            text_template = generator.generate_plain_text_email_template(
                customer, recommendations, offers, deliverables
            )
            customer_templates["templates"]["text"] = text_template
        
        # Generate subject lines
        if include_subjects:
            primary_offer = offers[0] if offers else {}
            subject_lines = generator.create_subject_lines(customer, primary_offer, deliverables)
            customer_templates["subject_lines"] = subject_lines
        
        all_templates.append(customer_templates)
        
        # Update progress
        progress_bar.progress((i + 1) / len(customers))
    
    status_text.text("✅ Email templates generated successfully!")
    
    # Store templates in session state for download
    st.session_state["generated_email_templates"] = all_templates
    
    # Show summary
    st.success(f"Generated {len(all_templates)} email templates in {len(formats)} format(s)")
    
    # Provide download options
    _show_template_download_options(all_templates, formats)


def _export_email_zip_package(
    customers: List[Dict], 
    deliverables: Dict, 
    formats: List[str],
    include_subjects: bool,
    include_preview: bool
):
    """Export email templates as ZIP package"""
    
    generator = EmailTemplateGenerator()
    
    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        
        # Add campaign metadata
        campaign_metadata = {
            "campaign_name": f"AI_Generated_Campaign_{datetime.now().strftime('%Y%m%d_%H%M')}",
            "generated_date": datetime.now().isoformat(),
            "total_customers": len(customers),
            "formats": formats,
            "ai_agents_used": list(deliverables.keys()) if deliverables else [],
            "generation_settings": {
                "include_subject_variants": include_subjects,
                "include_preview": include_preview
            }
        }
        
        zip_file.writestr("campaign_metadata.json", json.dumps(campaign_metadata, indent=2))
        
        # Generate templates for each customer
        for i, customer in enumerate(customers):
            customer_id = customer.get("customer_id", f"CUST_{i+1:03d}")
            
            # Extract customer-specific data
            recommendations = _extract_recommendations_for_customer(customer, deliverables)
            offers = _extract_offers_for_customer(customer, deliverables)
            
            # Create customer folder
            customer_folder = f"customers/{customer_id}/"
            
            # Generate HTML template
            if "HTML" in formats:
                html_template = generator.generate_html_email_template(
                    customer, recommendations, offers, deliverables
                )
                zip_file.writestr(f"{customer_folder}email_template.html", html_template)
            
            # Generate plain text template
            if "Plain Text" in formats:
                text_template = generator.generate_plain_text_email_template(
                    customer, recommendations, offers, deliverables
                )
                zip_file.writestr(f"{customer_folder}email_template.txt", text_template)
            
            # Generate subject lines
            if include_subjects:
                primary_offer = offers[0] if offers else {}
                subject_lines = generator.create_subject_lines(customer, primary_offer, deliverables)
                subject_content = "\n".join([f"{i+1}. {subject}" for i, subject in enumerate(subject_lines)])
                zip_file.writestr(f"{customer_folder}subject_lines.txt", subject_content)
            
            # Add customer metadata
            customer_metadata = {
                "customer_id": customer_id,
                "usage_pattern": customer.get("usage_pattern", "Standard"),
                "monthly_spend": customer.get("monthly_spend", 0),
                "primary_offer": offers[0].get("title", "") if offers else "",
                "total_offers": len(offers)
            }
            zip_file.writestr(f"{customer_folder}customer_metadata.json", json.dumps(customer_metadata, indent=2))
        
        # Add campaign summary
        campaign_summary = _generate_campaign_summary(customers, deliverables, formats)
        zip_file.writestr("campaign_summary.txt", campaign_summary)
        
        # Add import instructions
        import_instructions = _generate_import_instructions(formats)
        zip_file.writestr("IMPORT_INSTRUCTIONS.md", import_instructions)
    
    zip_buffer.seek(0)
    
    # Provide download button
    filename = f"email_campaign_{datetime.now().strftime('%Y%m%d_%H%M')}.zip"
    
    st.download_button(
        label="📦 Download Email Campaign ZIP",
        data=zip_buffer.getvalue(),
        file_name=filename,
        mime="application/zip",
        help="Download complete email campaign package with all templates and metadata"
    )
    
    st.success(f"✅ Email campaign package ready for download: {filename}")


def _export_campaign_metadata(customers: List[Dict], deliverables: Dict):
    """Export campaign metadata CSV for CRM integration"""
    
    metadata_rows = []
    
    for i, customer in enumerate(customers):
        customer_id = customer.get("customer_id", f"CUST_{i+1:03d}")
        offers = _extract_offers_for_customer(customer, deliverables)
        recommendations = _extract_recommendations_for_customer(customer, deliverables)
        
        # Primary offer details
        primary_offer = offers[0] if offers else {}
        
        metadata_row = {
            "customer_id": customer_id,
            "usage_pattern": customer.get("usage_pattern", "Standard"),
            "monthly_spend": customer.get("monthly_spend", 0),
            "data_usage_gb": customer.get("data_usage_gb", 0),
            "primary_offer_title": primary_offer.get("title", ""),
            "primary_offer_cost": primary_offer.get("monthly_cost", ""),
            "potential_savings": primary_offer.get("potential_savings", ""),
            "total_offers": len(offers),
            "ai_confidence": recommendations.get("confidence_score", "High"),
            "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "email_html_file": f"customers/{customer_id}/email_template.html",
            "email_text_file": f"customers/{customer_id}/email_template.txt",
            "subject_lines_file": f"customers/{customer_id}/subject_lines.txt"
        }
        
        metadata_rows.append(metadata_row)
    
    # Create DataFrame
    metadata_df = pd.DataFrame(metadata_rows)
    
    # Convert to CSV
    csv_buffer = io.StringIO()
    metadata_df.to_csv(csv_buffer, index=False)
    csv_content = csv_buffer.getvalue()
    
    # Provide download
    filename = f"email_campaign_metadata_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    
    st.download_button(
        label="📊 Download Campaign Metadata CSV",
        data=csv_content,
        file_name=filename,
        mime="text/csv",
        help="Download metadata CSV for CRM integration and tracking"
    )
    
    st.success(f"✅ Campaign metadata ready for download: {filename}")


def _show_template_download_options(templates: List[Dict], formats: List[str]):
    """Show individual template download options"""
    
    st.markdown("#### 📥 Individual Template Downloads")
    
    # Create tabs for different formats
    if len(formats) > 1:
        format_tabs = st.tabs(formats)
        
        for format_idx, format_name in enumerate(formats):
            with format_tabs[format_idx]:
                _show_format_download_options(templates, format_name)
    else:
        _show_format_download_options(templates, formats[0])


def _show_format_download_options(templates: List[Dict], format_name: str):
    """Show download options for a specific format"""
    
    st.markdown(f"##### {format_name} Templates")
    
    for template in templates[:5]:  # Show first 5 for demo
        customer_id = template["customer_id"]
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.text(f"Customer: {customer_id}")
        
        with col2:
            if format_name == "HTML" and "html" in template["templates"]:
                st.download_button(
                    "📄 HTML",
                    data=template["templates"]["html"],
                    file_name=f"{customer_id}_email.html",
                    mime="text/html",
                    key=f"html_{customer_id}"
                )
            elif format_name == "Plain Text" and "text" in template["templates"]:
                st.download_button(
                    "📄 TXT",
                    data=template["templates"]["text"],
                    file_name=f"{customer_id}_email.txt",
                    mime="text/plain",
                    key=f"text_{customer_id}"
                )
        
        with col3:
            if "subject_lines" in template:
                subject_content = "\n".join([f"{i+1}. {subject}" for i, subject in enumerate(template["subject_lines"])])
                st.download_button(
                    "📝 Subjects",
                    data=subject_content,
                    file_name=f"{customer_id}_subjects.txt",
                    mime="text/plain",
                    key=f"subjects_{customer_id}"
                )
    
    if len(templates) > 5:
        st.info(f"Showing first 5 of {len(templates)} templates. Use ZIP download for all templates.")


# Helper functions for data extraction

def _extract_recommendations_for_customer(customer: Dict, deliverables: Dict) -> Dict:
    """Extract AI recommendations for a specific customer"""
    
    recommendations = {
        "confidence_score": "High",
        "primary_offer": None,
        "reasoning": "AI-generated recommendation based on usage analysis"
    }
    
    # Extract from Revenue Optimization Agent
    if "revenue_optimization" in deliverables:
        revenue_data = deliverables["revenue_optimization"]
        
        if isinstance(revenue_data, dict):
            recommendations["reasoning"] = revenue_data.get("analysis", recommendations["reasoning"])
            
            # Try to extract offers
            if "recommended_offers" in revenue_data:
                offers = revenue_data["recommended_offers"]
                if isinstance(offers, list) and offers:
                    recommendations["primary_offer"] = offers[0]
                elif isinstance(offers, dict):
                    recommendations["primary_offer"] = offers
    
    return recommendations


def _extract_offers_for_customer(customer: Dict, deliverables: Dict) -> List[Dict]:
    """Extract offer details for a specific customer"""
    
    default_offers = [
        {
            "title": "Premium Data Upgrade",
            "description": "Enhanced data allowance with 5G speeds",
            "monthly_cost": "298",
            "potential_savings": "1200"
        },
        {
            "title": "Unlimited Voice & Data",
            "description": "Unlimited local calls and data with roaming benefits",
            "monthly_cost": "398",
            "potential_savings": "2400"
        }
    ]
    
    offers = []
    
    # Extract from Revenue Optimization Agent
    if "revenue_optimization" in deliverables:
        revenue_data = deliverables["revenue_optimization"]
        
        if isinstance(revenue_data, dict) and "recommended_offers" in revenue_data:
            ai_offers = revenue_data["recommended_offers"]
            
            if isinstance(ai_offers, list):
                for offer in ai_offers:
                    if isinstance(offer, dict):
                        offers.append(offer)
                    elif isinstance(offer, str):
                        # Parse string offers
                        offers.append({
                            "title": offer[:50] + "..." if len(offer) > 50 else offer,
                            "description": offer,
                            "monthly_cost": "298",
                            "potential_savings": "1200"
                        })
            elif isinstance(ai_offers, dict):
                offers.append(ai_offers)
    
    # Use default offers if no AI offers found
    if not offers:
        offers = default_offers
    
    return offers[:3]  # Limit to 3 offers per customer


def _generate_campaign_summary(customers: List[Dict], deliverables: Dict, formats: List[str]) -> str:
    """Generate campaign summary text"""
    
    summary = f"""THREE HK AI-GENERATED EMAIL CAMPAIGN SUMMARY
============================================

Campaign Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Total Customers: {len(customers)}
Email Formats: {', '.join(formats)}

AI AGENTS INVOLVED:
"""
    
    if deliverables:
        for agent_name in deliverables.keys():
            summary += f"- {agent_name.replace('_', ' ').title()}\n"
    
    summary += f"""
CAMPAIGN STRUCTURE:
- Individual email templates for {len(customers)} customers
- Personalized content based on usage analysis
- Three HK branding and compliance
- Multiple subject line variants for A/B testing

USAGE INSTRUCTIONS:
1. Import templates into your email marketing platform
2. Map customer IDs to your contact database
3. Test subject line variants for optimal performance
4. Monitor campaign performance and engagement

TECHNICAL DETAILS:
- Templates are mobile-responsive
- Compliant with Hong Kong PDPO regulations
- Include unsubscribe and privacy links
- Generated using advanced AI analysis

For support, contact the Three HK marketing team.
"""
    
    return summary


def _generate_import_instructions(formats: List[str]) -> str:
    """Generate import instructions markdown"""
    
    instructions = """# Email Campaign Import Instructions

This package contains AI-generated email templates for Three HK marketing campaigns.

## 📁 Package Structure

```
email_campaign_YYYYMMDD_HHMM.zip
├── campaign_metadata.json          # Campaign configuration and settings
├── campaign_summary.txt            # Human-readable campaign overview
├── IMPORT_INSTRUCTIONS.md          # This file
├── customers/                      # Individual customer templates
│   ├── CUST_001/
│   │   ├── email_template.html     # HTML email template
│   │   ├── email_template.txt      # Plain text email template
│   │   ├── subject_lines.txt       # Subject line variants
│   │   └── customer_metadata.json  # Customer-specific data
│   └── [additional customers...]
```

## 🚀 Platform-Specific Import Instructions

### MailChimp
1. Create new campaign in MailChimp
2. Import customer list using campaign metadata CSV
3. Use HTML templates as campaign content
4. Map customer_id field for personalization
5. Test with subject line variants

### Constant Contact
1. Upload contact list from metadata CSV
2. Create email campaign using HTML templates
3. Use merge tags for personalization
4. Test subject line performance

### HubSpot
1. Import contacts using metadata CSV
2. Create email templates from HTML files
3. Set up automated sequences
4. A/B test subject line variants

### Generic Email Platforms
1. Import contact database
2. Copy HTML template content
3. Map personalization fields
4. Configure tracking and analytics

## 📊 Tracking and Analytics

- Monitor open rates by subject line variant
- Track click-through rates on offers
- Measure conversion rates by customer segment
- Use customer_id for attribution analysis

## 🔒 Privacy and Compliance

- All customer data is pseudonymized
- Templates include required unsubscribe links
- Compliant with Hong Kong PDPO regulations
- Remove any test data before production use

## 🆘 Support

For technical support or questions about this campaign package:
- Contact: Three HK Marketing Team
- Reference: AI Campaign Generation Tool
- Generated: """
    
    instructions += datetime.now().strftime('%Y-%m-%d %H:%M')
    
    return instructions
