# Product Requirements Document (PRD)  
## Agentic AI Revenue Assistant �V Minimal Viable Demo

### 1. Elevator Pitch

Agentic AI Revenue Assistant is a privacy-first, autonomous lead prioritization and sales suggestion tool for Hong Kong telecom companies. It enables business teams to securely upload customer and purchase data, automatically pseudonymizes sensitive information, analyzes purchase and engagement patterns, and outputs actionable, prioritized sales recommendations�Xall within an intuitive Streamlit dashboard styled in the Three HK color scheme. This demo showcases agentic AI autonomy, actionable business value, and strict data privacy, serving as a foundation for future multi-agent expansion.

### 2. Who is this app for

- CTOs, IT Department Heads, and Technical Teams at telecom companies
- Sales and Marketing Managers seeking data-driven lead prioritization
- Business Analysts and Product Owners evaluating AI-driven revenue tools
- Demo audiences (internal/external) interested in practical Agentic AI applications

### 3. Functional Requirements

#### 3.1 Highest Priority (Mandatory for Demo)

| ID   | Requirement Description                                                                 | Priority   |
|------|----------------------------------------------------------------------------------------|------------|
| FR1  | System shall allow user to upload/select both customer profile and purchase history CSV files. | Highest    |
| FR2  | System shall validate and parse both CSV files, providing feedback for errors.          | Highest    |
| FR3  | System shall pseudonymize all sensitive data (names, emails, HKID, etc.) immediately after upload and before any further processing. | Highest    |
| FR4  | System shall merge and align customer and purchase data by Account ID.                  | Highest    |
| FR5  | System shall load transformed data into a local JSON file/database for analysis.        | Highest    |
| FR6  | System shall analyze customer purchase history and engagement data using the agent.      | Highest    |
| FR7  | System shall use an open-source LLM (DeepSeek via OpenRouter) for agent reasoning.       | Highest    |
| FR8  | System shall output a prioritized list of leads with suggested actions (referencing Three HK offers and industry best practices). | Highest    |
| FR9  | System shall display anonymized results in a clear, interactive Streamlit dashboard.     | Highest    |
| FR10 | System shall allow user to review and export anonymized results after agent analysis.    | Highest    |
| FR11 | Data encryption at rest and in transit.                                                  | Highest    |
| FR12 | Intuitive UI for non-technical users.                                                    | Highest    |
| FR13 | Compliance with GDPR and Hong Kong PDPO.                                                 | Highest    |

#### 3.2 LLM Handling Requirements

- Use OpenRouter with DeepSeek (or Llama-2) as the language model backend.
- All LLM prompts and responses must be logged for audit and compliance.
- No raw PII (names, emails, HKID, etc.) is ever sent to the LLM; only pseudonymized or masked data is processed.
- LLM must be invoked only after privacy layer completes transformation.
- API keys and credentials for LLM access must be securely managed and never exposed in logs or UI.
- LLM requests should be rate-limited and monitored for abnormal activity.
- LLM outputs are to be reviewed before being shown to users or exported.

#### 3.3 Medium and Low Priority (For Future Phases)

| ID   | Requirement Description                                                     | Priority   |
|------|----------------------------------------------------------------------------|------------|
| FR14 | System shall log all agent actions and outputs for review.                  | Medium     |
| FR15 | Lead analysis response time < 30 seconds.                                   | High       |
| FR16 | Support up to 10,000 customer records in demo.                              | Medium     |
| FR17 | System shall support extension to multi-agent workflows.                    | Low        |
| FR18 | System shall allow for manual override or approval of agent recommendations.| Low        |
| FR19 | System shall integrate with external APIs (CRM, email, etc.).               | Low        |
| FR20 | System shall implement learning mechanisms for continuous improvement.       | Medium     |
| FR21 | System shall track offer acceptance rates and customer engagement outcomes.  | Medium     |
| FR22 | System shall adapt recommendations based on historical success patterns.     | Medium     |
| FR23 | System shall build knowledge base of effective customer patterns.           | Low        |

### 4. User Stories

| ID  | User Role         | Description                                                                                 | Acceptance Criteria                                               |
|-----|-------------------|--------------------------------------------------------------------------------------------|-------------------------------------------------------------------|
| US1 | Sales Manager     | As a sales manager, I want to upload a customer list and get prioritized leads with suggestions so I can focus my outreach. | Can upload CSVs, view anonymized prioritized leads, see clear suggestions, and export results. |
| US2 | Developer         | As a developer, I want clear demo requirements and priorities so I can focus on critical features. | Highest priority requirements are implemented and stable.         |
| US3 | Security Officer  | As a security officer, I want all sensitive data pseudonymized before analysis.             | No raw PII is transmitted or displayed in the UI.                 |
| US4 | Business Analyst  | As a business analyst, I want the system to learn from campaign outcomes to improve future recommendations. | System tracks offer acceptance rates and adapts strategies based on feedback. |
| US5 | Executive         | As an executive, I want to see continuous improvement in AI recommendations over time.      | System demonstrates measurable improvement in recommendation accuracy and business outcomes. |

### 5. User Interface

- **Home Screen:**  
  - Brief description of the demo and data privacy commitment.
  - File upload components for customer and purchase/engagement CSVs.
  - Option to use sample data.

- **Processing Screen:**  
  - Progress indicator while pseudonymization and analysis occur.

- **Results Dashboard:**  
  - Table with columns: Anonymized ID, Last Purchase, Engagement Summary, Suggested Action, Lead Priority Score.
  - Export button to download anonymized results (CSV).
  - Simple explanations/tooltips for each column.
  - Visuals and color palette consistent with Three HK��s branding (white, black, green, and accent colors).

- **Privacy Notice:**  
  - Banner or modal explaining how data is protected and pseudonymized.

### 6. Suggested Actions Reference

**Telecom Offer Templates (from Three HK & Industry Standards):**
- Device Upgrade Offer (latest smartphones)
- 5G SIM Only Plan Upsell
- Data Add-on Promotion (e.g., extra 10GB)
- Family Plan Proposal
- Streaming Service Bundle
- Mobile Phone Insurance Offer
- International Roaming Pack
- Smartwatch Plan
- Prepaid SIM Switch
- Loyalty Discount or Early Renewal Incentive
- Limited-Time Promotion (e.g., ��Upgrade in 7 days for 20% off��)
- Referral Reward Program
- Retention Campaign (bonus data, bill waiver, free add-on)
- Personalized Re-engagement Offer

### 7. Technical Architecture Overview

- **Data Input Layer:**  
  - Accepts two CSVs; validates and parses both.
- **Privacy Layer:**  
  - Pseudonymizes all sensitive fields before any further processing.
- **Data Storage Layer:**  
  - Loads merged, anonymized data into a JSON structure (in-memory or local file).
- **Agentic AI Layer:**  
  - Operates strictly on the unified, pseudonymized JSON data, using DeepSeek via OpenRouter.
- **Learning & Adaptation Layer (Future):**  
  - Tracks recommendation outcomes and customer feedback for continuous improvement.
  - Builds knowledge base of successful patterns and market trends.
  - Adapts AI model selection based on performance history and use case optimization.
- **Presentation Layer:**  
  - Streamlit dashboard for visualization and interaction.
- **Security Layer:**  
  - Data encryption in transit and at rest.
- **LLM Handling:**  
  - Secure API integration, privacy-first prompt construction, logging, and output review.

### 8. Technology Stack

| Component         | Technology/Framework           | Notes                                 |
|-------------------|-------------------------------|---------------------------------------|
| LLM API           | OpenRouter (DeepSeek, Llama-2)| Open-source, privacy-compliant        |
| Agent Framework   | Custom Python logic           | Single-agent for demo                 |
| Data Privacy      | Custom pseudonymization utils | Masking of names, emails, HKID        |
| Web Interface     | Streamlit                     | Lightweight, interactive UI           |
| Storage           | Local, encrypted JSON         | For demo data and logs                |

### 9. Development Plan (Demo-Focused)

| Day | Task                                       |
|-----|--------------------------------------------|
| 1   | Set up Streamlit UI, load sample data      |
| 2   | Implement privacy (pseudonymization) layer |
| 3   | Integrate OpenRouter/DeepSeek API          |
| 4   | Write agent logic for lead prioritization  |
| 5   | Display results in dashboard               |
| 6   | Polish UI, add comments, test flows        |
| 7   | Buffer for fixes, prep for presentation    |

### 10. Risks and Mitigations

| Risk                         | Mitigation Strategy                               |
|------------------------------|--------------------------------------------------|
| Data leakage of sensitive info | Implement strong pseudonymization and audit logging |
| LLM performance limitations   | Use open-source LLMs optimized for business context |
| Demo scope creep              | Strictly focus on ��Highest�� priority features      |

### 11. Future Enhancements

- Add multi-agent orchestration (lead, sales, retention, market insights)
- **Implement Learning & Adaptation Engine for continuous business intelligence improvement**
  - Outcome tracking system for offer acceptance rates and customer engagement metrics
  - Feedback integration to learn from successful vs. failed strategies
  - Business intelligence memory for building knowledge base of effective patterns
  - Adaptive model selection based on performance history and use case optimization
  - Agent performance learning to improve multi-agent collaboration over time
- Role-based access and advanced dashboard features
- Integration with real CRM, email, and marketing APIs
- Real-time social media sentiment analysis
- Advanced cryptographic privacy methods

**Note:**  
All requirements marked **��Highest��** are mandatory for the demo. Other requirements should be deferred unless time permits.  
LLM handling, privacy, and result export are explicitly detailed and prioritized as per the product owner��s idea document and the latest attachments.  
This PRD is ready for use by developers, architects, and project managers to deliver a focused, high-impact demo aligned with product owner goals and telecom industry best practices.

[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/9841353/1137b99b-7467-4f78-aee4-3b582892cecb/product-owner-ideas-document-v0.2.docx
[2] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/9841353/46336be9-b60e-476e-a0a4-ce7e50f6402d/sample_purchase_history.csv
[3] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/9841353/ab5b9a2e-247f-4c7c-9944-51a1bf93e3ca/sample-customer-data-20250714.csv