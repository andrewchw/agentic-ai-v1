"""
Email Template Generation Functions
Generates HTML and plain text email templates from CrewAI deliverables
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import html


class EmailTemplateGenerator:
    """Generate personalized email templates from CrewAI collaboration results"""
    
    def __init__(self):
        self.three_hk_primary = "#00FF00"
        self.three_hk_secondary = "#000000"
        self.three_hk_accent = "#FFFFFF"
        
    def generate_html_email_template(
        self, 
        customer_data: Dict, 
        recommendations: Dict, 
        offers: List[Dict],
        agent_deliverables: Dict = None
    ) -> str:
        """Generate HTML email template for a customer"""
        
        # Extract customer information
        customer_name = self._get_customer_reference(customer_data)
        usage_pattern = self._extract_usage_pattern(customer_data, agent_deliverables)
        primary_offer = self._get_primary_offer(offers, recommendations)
        
        # Generate template content
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exclusive Offer from Three HK</title>
    {self._get_email_styles()}
</head>
<body>
    <div class="email-container">
        {self._generate_header()}
        
        <main class="email-content">
            <div class="greeting-section">
                <h1>Hi {customer_name},</h1>
                <p class="personalized-intro">
                    {self._generate_personalized_intro(usage_pattern, agent_deliverables)}
                </p>
            </div>
            
            <div class="offer-section">
                {self._generate_offer_content(primary_offer, recommendations, agent_deliverables)}
            </div>
            
            <div class="additional-offers">
                {self._generate_secondary_offers(offers[1:3], agent_deliverables)}
            </div>
            
            <div class="cta-section">
                {self._generate_call_to_action(primary_offer)}
            </div>
            
            <div class="ai-attribution">
                {self._generate_ai_attribution(agent_deliverables)}
            </div>
        </main>
        
        {self._generate_footer()}
    </div>
</body>
</html>"""
        
        return html_template
    
    def generate_plain_text_email_template(
        self, 
        customer_data: Dict, 
        recommendations: Dict, 
        offers: List[Dict],
        agent_deliverables: Dict = None
    ) -> str:
        """Generate plain text email template for a customer"""
        
        customer_name = self._get_customer_reference(customer_data)
        usage_pattern = self._extract_usage_pattern(customer_data, agent_deliverables)
        primary_offer = self._get_primary_offer(offers, recommendations)
        
        # Generate plain text content
        text_template = f"""THREE HK - EXCLUSIVE OFFER FOR YOU
===============================================

Hi {customer_name},

{self._generate_personalized_intro_text(usage_pattern, agent_deliverables)}

YOUR EXCLUSIVE OFFER:
{self._generate_offer_content_text(primary_offer, recommendations, agent_deliverables)}

{self._generate_secondary_offers_text(offers[1:3], agent_deliverables)}

NEXT STEPS:
{self._generate_call_to_action_text(primary_offer)}

{self._generate_ai_attribution_text(agent_deliverables)}

---
Three HK | Building Hong Kong's Digital Future
Website: three.com.hk | Customer Service: 3166 3333

This email was generated using AI analysis of your usage patterns.
To unsubscribe: [Unsubscribe Link]
Privacy Policy: three.com.hk/privacy
"""
        
        return text_template
    
    def create_subject_lines(
        self, 
        customer_profile: Dict, 
        primary_offer: Dict,
        agent_deliverables: Dict = None
    ) -> List[str]:
        """Generate multiple subject line variants for A/B testing"""
        
        # Extract key information
        savings_amount = self._extract_savings_amount(primary_offer)
        offer_type = self._extract_offer_type(primary_offer)
        urgency_level = self._assess_urgency(customer_profile, agent_deliverables)
        
        subject_lines = []
        
        # Savings-focused subject lines
        if savings_amount:
            subject_lines.extend([
                f"Save HK${savings_amount} with your exclusive Three HK offer",
                f"HK${savings_amount} savings waiting for you",
                f"Your personal HK${savings_amount} discount is ready"
            ])
        
        # Offer-focused subject lines
        subject_lines.extend([
            f"Exclusive {offer_type} offer just for you",
            f"Three HK: Your personalized {offer_type} upgrade",
            f"Special {offer_type} offer based on your usage"
        ])
        
        # Urgency-based subject lines (if applicable)
        if urgency_level == "high":
            subject_lines.extend([
                "Limited time: Your exclusive Three HK offer expires soon",
                "48 hours left: Your personalized savings offer",
                "Don't miss out: Your special Three HK discount"
            ])
        
        # AI-powered subject lines from Campaign Manager
        if agent_deliverables and "campaign_manager" in agent_deliverables:
            ai_subjects = self._extract_ai_subject_lines(agent_deliverables["campaign_manager"])
            subject_lines.extend(ai_subjects[:3])
        
        # Generic backup subject lines
        subject_lines.extend([
            "Your personalized Three HK offer is ready",
            "Exclusive savings from Three HK",
            "A special offer based on your usage"
        ])
        
        return subject_lines[:8]  # Return top 8 variants
    
    def format_three_hk_branding(self, template_content: str) -> str:
        """Apply Three HK branding and compliance to template content"""
        
        # Apply brand colors and styling
        branded_content = template_content.replace(
            "{{THREE_HK_PRIMARY}}", self.three_hk_primary
        ).replace(
            "{{THREE_HK_SECONDARY}}", self.three_hk_secondary
        ).replace(
            "{{THREE_HK_ACCENT}}", self.three_hk_accent
        )
        
        # Add compliance elements
        branded_content = self._add_compliance_elements(branded_content)
        
        # Ensure Hong Kong localization
        branded_content = self._apply_hk_localization(branded_content)
        
        return branded_content
    
    # Helper methods
    
    def _get_customer_reference(self, customer_data: Dict) -> str:
        """Get privacy-compliant customer reference"""
        if not customer_data:
            return "Valued Customer"
        
        # Use pseudonymized customer ID or generic reference
        customer_id = customer_data.get("customer_id", "")
        if customer_id:
            return f"Customer {customer_id[:8]}"  # First 8 chars of pseudonym
        
        return "Valued Customer"
    
    def _extract_usage_pattern(self, customer_data: Dict, agent_deliverables: Dict = None) -> str:
        """Extract usage pattern description"""
        if agent_deliverables and "customer_intelligence" in agent_deliverables:
            usage_analysis = agent_deliverables["customer_intelligence"].get("usage_analysis", "")
            if usage_analysis:
                return self._summarize_usage_pattern(usage_analysis)
        
        # Fallback to customer data analysis
        if customer_data:
            monthly_spend = customer_data.get("monthly_spend", 0)
            data_usage = customer_data.get("data_usage_gb", 0)
            
            if monthly_spend > 500:
                return "high-value usage pattern"
            elif data_usage > 20:
                return "heavy data usage"
            else:
                return "regular usage pattern"
        
        return "usage pattern"
    
    def _get_primary_offer(self, offers: List[Dict], recommendations: Dict) -> Dict:
        """Get the primary recommended offer"""
        if not offers:
            return {}
        
        # If recommendations specify a primary offer, use it
        if recommendations and "primary_offer" in recommendations:
            return recommendations["primary_offer"]
        
        # Otherwise, use the first offer
        return offers[0] if offers else {}
    
    def _get_email_styles(self) -> str:
        """Generate CSS styles for HTML email"""
        return f"""
<style>
    .email-container {{
        max-width: 600px;
        margin: 0 auto;
        font-family: Arial, sans-serif;
        background-color: {self.three_hk_accent};
        color: {self.three_hk_secondary};
    }}
    .email-header {{
        background-color: {self.three_hk_secondary};
        color: {self.three_hk_accent};
        padding: 20px;
        text-align: center;
    }}
    .three-hk-logo {{
        font-size: 24px;
        font-weight: bold;
        color: {self.three_hk_primary};
    }}
    .email-content {{
        padding: 30px 20px;
    }}
    .greeting-section h1 {{
        color: {self.three_hk_secondary};
        font-size: 28px;
        margin-bottom: 15px;
    }}
    .personalized-intro {{
        font-size: 16px;
        line-height: 1.6;
        margin-bottom: 25px;
    }}
    .offer-section {{
        background-color: #f8f9fa;
        padding: 25px;
        border-radius: 8px;
        border-left: 4px solid {self.three_hk_primary};
        margin: 25px 0;
    }}
    .offer-title {{
        font-size: 22px;
        font-weight: bold;
        color: {self.three_hk_secondary};
        margin-bottom: 15px;
    }}
    .savings-highlight {{
        font-size: 20px;
        font-weight: bold;
        color: {self.three_hk_primary};
        margin: 10px 0;
    }}
    .cta-button {{
        display: inline-block;
        background-color: {self.three_hk_primary};
        color: {self.three_hk_secondary};
        padding: 15px 30px;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
        margin: 20px 0;
    }}
    .ai-attribution {{
        font-size: 12px;
        color: #666;
        font-style: italic;
        margin-top: 25px;
        padding-top: 15px;
        border-top: 1px solid #eee;
    }}
    .email-footer {{
        background-color: #f8f9fa;
        padding: 20px;
        text-align: center;
        font-size: 12px;
        color: #666;
    }}
</style>"""
    
    def _generate_header(self) -> str:
        """Generate email header with Three HK branding"""
        return f"""
<header class="email-header">
    <div class="three-hk-logo">3 THREE HK</div>
    <div style="font-size: 14px; margin-top: 5px;">Building Hong Kong's Digital Future</div>
</header>"""
    
    def _generate_personalized_intro(self, usage_pattern: str, agent_deliverables: Dict = None) -> str:
        """Generate personalized introduction text"""
        base_intro = f"Based on your {usage_pattern}, our AI analysis has identified an exclusive offer that could significantly enhance your mobile experience."
        
        # Add AI-generated personalization if available
        if agent_deliverables and "customer_intelligence" in agent_deliverables:
            insights = agent_deliverables["customer_intelligence"].get("key_insights", [])
            if insights:
                key_insight = insights[0] if isinstance(insights, list) else str(insights)
                base_intro += f" Our analysis shows that {key_insight.lower()}"
        
        return base_intro
    
    def _generate_offer_content(self, primary_offer: Dict, recommendations: Dict, agent_deliverables: Dict = None) -> str:
        """Generate the main offer content section"""
        if not primary_offer:
            return "<p>We have identified several opportunities to optimize your mobile plan.</p>"
        
        offer_title = primary_offer.get("title", "Exclusive Offer")
        offer_description = primary_offer.get("description", "A special offer tailored to your needs")
        monthly_cost = primary_offer.get("monthly_cost", "")
        savings = primary_offer.get("potential_savings", "")
        
        content = f"""
<h2 class="offer-title">{html.escape(offer_title)}</h2>
<p>{html.escape(offer_description)}</p>"""
        
        if monthly_cost:
            content += f'<p><strong>Monthly Cost:</strong> HK${monthly_cost}</p>'
        
        if savings:
            content += f'<p class="savings-highlight">Potential Annual Savings: HK${savings}</p>'
        
        # Add AI-generated content if available
        if agent_deliverables and "campaign_manager" in agent_deliverables:
            campaign_content = agent_deliverables["campaign_manager"].get("email_content", "")
            if campaign_content:
                content += f'<div class="ai-content">{html.escape(campaign_content[:200])}...</div>'
        
        return content
    
    def _generate_secondary_offers(self, secondary_offers: List[Dict], agent_deliverables: Dict = None) -> str:
        """Generate secondary offers section"""
        if not secondary_offers:
            return ""
        
        content = '<div class="secondary-offers"><h3>Additional Opportunities:</h3><ul>'
        
        for offer in secondary_offers[:2]:  # Limit to 2 secondary offers
            title = offer.get("title", "Additional Offer")
            content += f'<li>{html.escape(title)}</li>'
        
        content += '</ul></div>'
        return content
    
    def _generate_call_to_action(self, primary_offer: Dict) -> str:
        """Generate call-to-action section"""
        return f"""
<div style="text-align: center; margin: 30px 0;">
    <a href="tel:31663333" class="cta-button">Call 3166 3333 to Activate</a>
    <p style="margin-top: 15px; font-size: 14px;">
        Or visit any Three HK store | Available online at three.com.hk
    </p>
    <p style="font-size: 12px; color: #666; margin-top: 10px;">
        Quote reference: AIREV{datetime.now().strftime('%Y%m%d')}
    </p>
</div>"""
    
    def _generate_ai_attribution(self, agent_deliverables: Dict = None) -> str:
        """Generate AI attribution section"""
        base_attribution = "This personalized offer was generated using advanced AI analysis of anonymized usage patterns."
        
        if agent_deliverables:
            agents_involved = []
            if "customer_intelligence" in agent_deliverables:
                agents_involved.append("Customer Intelligence")
            if "revenue_optimization" in agent_deliverables:
                agents_involved.append("Revenue Optimization")
            if "campaign_manager" in agent_deliverables:
                agents_involved.append("Campaign Manager")
            
            if agents_involved:
                base_attribution += f" Analysis provided by our {', '.join(agents_involved)} AI agents."
        
        return f'<div class="ai-attribution">{base_attribution}</div>'
    
    def _generate_footer(self) -> str:
        """Generate email footer with compliance information"""
        return f"""
<footer class="email-footer">
    <p><strong>Three HK</strong> | Building Hong Kong's Digital Future</p>
    <p>Website: three.com.hk | Customer Service: 3166 3333</p>
    <p style="margin-top: 15px;">
        <a href="#unsubscribe">Unsubscribe</a> | 
        <a href="https://three.com.hk/privacy">Privacy Policy</a> | 
        <a href="https://three.com.hk/terms">Terms of Service</a>
    </p>
    <p style="margin-top: 10px; font-size: 10px;">
        This email contains personalized offers based on AI analysis of anonymized data.<br>
        Three HK respects your privacy and complies with Hong Kong PDPO regulations.
    </p>
</footer>"""
    
    # Plain text helper methods
    
    def _generate_personalized_intro_text(self, usage_pattern: str, agent_deliverables: Dict = None) -> str:
        """Generate personalized introduction for plain text"""
        return f"Based on your {usage_pattern}, our AI analysis has identified an exclusive offer that could significantly enhance your mobile experience and save you money."
    
    def _generate_offer_content_text(self, primary_offer: Dict, recommendations: Dict, agent_deliverables: Dict = None) -> str:
        """Generate main offer content for plain text"""
        if not primary_offer:
            return "We have identified several opportunities to optimize your mobile plan."
        
        offer_title = primary_offer.get("title", "Exclusive Offer")
        offer_description = primary_offer.get("description", "A special offer tailored to your needs")
        monthly_cost = primary_offer.get("monthly_cost", "")
        savings = primary_offer.get("potential_savings", "")
        
        content = f"{offer_title}\n{'-' * len(offer_title)}\n{offer_description}\n"
        
        if monthly_cost:
            content += f"Monthly Cost: HK${monthly_cost}\n"
        
        if savings:
            content += f"Potential Annual Savings: HK${savings}\n"
        
        return content
    
    def _generate_secondary_offers_text(self, secondary_offers: List[Dict], agent_deliverables: Dict = None) -> str:
        """Generate secondary offers for plain text"""
        if not secondary_offers:
            return ""
        
        content = "ADDITIONAL OPPORTUNITIES:\n"
        for i, offer in enumerate(secondary_offers[:2], 1):
            title = offer.get("title", "Additional Offer")
            content += f"{i}. {title}\n"
        
        return content
    
    def _generate_call_to_action_text(self, primary_offer: Dict) -> str:
        """Generate call-to-action for plain text"""
        return f"""Ready to activate this offer?

📞 Call: 3166 3333 (24/7 Customer Service)
🌐 Online: three.com.hk
🏪 Visit: Any Three HK store

Quote reference: AIREV{datetime.now().strftime('%Y%m%d')}"""
    
    def _generate_ai_attribution_text(self, agent_deliverables: Dict = None) -> str:
        """Generate AI attribution for plain text"""
        return "This personalized offer was generated using advanced AI analysis of anonymized usage patterns, ensuring your privacy while delivering relevant recommendations."
    
    # Utility helper methods
    
    def _summarize_usage_pattern(self, usage_analysis: str) -> str:
        """Summarize usage pattern from AI analysis"""
        # Extract key patterns from analysis text
        if "high usage" in usage_analysis.lower():
            return "high-usage pattern"
        elif "data heavy" in usage_analysis.lower():
            return "data-intensive usage"
        elif "business" in usage_analysis.lower():
            return "business usage pattern"
        else:
            return "unique usage pattern"
    
    def _extract_savings_amount(self, offer: Dict) -> Optional[str]:
        """Extract savings amount from offer"""
        savings = offer.get("potential_savings", "")
        if savings:
            # Extract numeric value
            import re
            match = re.search(r'(\d+)', str(savings))
            return match.group(1) if match else None
        return None
    
    def _extract_offer_type(self, offer: Dict) -> str:
        """Extract offer type for subject line"""
        title = offer.get("title", "").lower()
        if "data" in title:
            return "data plan"
        elif "unlimited" in title:
            return "unlimited plan"
        elif "upgrade" in title:
            return "upgrade"
        else:
            return "mobile plan"
    
    def _assess_urgency(self, customer_profile: Dict, agent_deliverables: Dict = None) -> str:
        """Assess urgency level for messaging"""
        # Check if customer is at risk (from retention specialist)
        if agent_deliverables and "retention_specialist" in agent_deliverables:
            churn_risk = agent_deliverables["retention_specialist"].get("churn_risk", "low")
            if churn_risk == "high":
                return "high"
        
        return "normal"
    
    def _extract_ai_subject_lines(self, campaign_manager_data: Dict) -> List[str]:
        """Extract AI-generated subject lines from Campaign Manager"""
        subject_lines = campaign_manager_data.get("subject_lines", [])
        if isinstance(subject_lines, str):
            # If it's a string, try to parse multiple lines
            return [line.strip() for line in subject_lines.split('\n') if line.strip()]
        elif isinstance(subject_lines, list):
            return subject_lines
        else:
            return []
    
    def _add_compliance_elements(self, content: str) -> str:
        """Add compliance elements to template"""
        # Ensure unsubscribe link is present
        if "unsubscribe" not in content.lower():
            content = content.replace(
                "</footer>", 
                '<p><a href="#unsubscribe">Unsubscribe</a></p></footer>'
            )
        
        # Add PDPO compliance notice
        if "pdpo" not in content.lower():
            content = content.replace(
                "</footer>",
                '<p style="font-size: 10px;">Complies with Hong Kong PDPO regulations</p></footer>'
            )
        
        return content
    
    def _apply_hk_localization(self, content: str) -> str:
        """Apply Hong Kong localization"""
        # Ensure HK$ currency format
        content = re.sub(r'\$(\d+)', r'HK$\1', content)
        
        # Ensure Hong Kong phone format
        content = re.sub(r'(\d{4})\s*(\d{4})', r'\1 \2', content)
        
        return content
