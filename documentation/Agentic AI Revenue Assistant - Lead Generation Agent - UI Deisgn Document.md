# User Interface Design Document  
## Agentic AI Revenue Assistant ¡V Guided Workflow Dashboard

### Layout Structure

- **Vertical, Multi-Step Workflow:**  
  The interface is organized into clear, consecutive steps, displayed in a sidebar or top-stepper navigation. Each step is presented in the main content area, ensuring users always know their current position in the workflow.

- **Main Steps:**  
  1. **Upload Data:** Upload customer and purchase history CSV files.
  2. **Review Data:** Preview and confirm pseudonymized data.
  3. **Run Analysis:** Launch the lead generation agent.
  4. **View Results:** Review prioritized leads and suggested actions, with export option.

### Core Components

- **Sidebar Navigation:**  
  Displays each workflow step with progress indication. Steps are clickable but sequentially enabled.

- **File Upload Panels:**  
  Two upload fields for customer and purchase history CSVs, with drag-and-drop and file picker support.

- **Data Preview Modal:**  
  Shows a sample of the anonymized data after upload and pseudonymization, allowing user confirmation before proceeding.

- **Processing Indicator:**  
  Progress bar or spinner during data transformation and agent analysis.

- **Results Table:**  
  Displays anonymized leads with columns for Anonymized ID, Last Purchase, Engagement Summary, Suggested Action, and Lead Priority Score.

- **Export Button:**  
  Allows users to download the results table as a CSV.

- **Privacy Notice Banner:**  
  Persistent banner or modal summarizing privacy measures and data protection.

### Interaction Patterns

- **Step-by-Step Progression:**  
  Users must complete each step before moving to the next. Navigation is linear to ensure process clarity and data integrity.

- **Inline Validation:**  
  Immediate feedback for file structure, missing fields, or upload errors.

- **Hover Tooltips:**  
  Explanations for table columns, agent logic, and privacy features.

- **Confirmation Modals:**  
  Before running analysis and before exporting results.

- **Error Handling:**  
  Clear, actionable error messages for upload, processing, or export issues.

### Visual Design Elements & Color Scheme

- **Color Palette:**  
  - White backgrounds for clarity and cleanliness.
  - Three HK¡¦s signature green for buttons, progress bars, and highlights.
  - Black for text and navigation elements.
  - Subtle gradients or accent colors for visual interest, aligned with Three HK branding.

- **Modern, Flat Icons:**  
  Used for navigation steps, upload fields, and actions.

- **Consistent Spacing and Sizing:**  
  Generous padding and margins for a clean, professional look.

### Mobile, Web App, Desktop Considerations

- **Responsive Design:**  
  - Sidebar collapses to a top-stepper or hamburger menu on mobile.
  - Tables are horizontally scrollable on small screens.
  - Touch-friendly buttons and larger tap targets for mobile usability.

- **Web and Desktop Optimization:**  
  - Designed primarily for web browsers and desktop screens.
  - Ensures consistent experience across Chrome, Edge, and Safari.

### Typography

- **Font Family:**  
  - Modern, sans-serif fonts (e.g., Noto Sans, Arial, Roboto).

- **Hierarchy:**  
  - Bold, larger headings for step titles.
  - Medium-weight subheadings for data sections.
  - High-contrast body text for readability.

- **Consistent Sizing:**  
  - Headings, table headers, and body text sized for clarity and accessibility.

### Accessibility

- **Keyboard Navigation:**  
  - All steps, buttons, and tables accessible via keyboard.

- **ARIA Labels:**  
  - Proper labeling for upload fields, buttons, and navigation elements.

- **Color Contrast:**  
  - Meets WCAG standards for text and UI elements.

- **Scalable Text:**  
  - Supports browser zoom and user font size preferences.

- **Alt Text:**  
  - Descriptive alt text for icons and key visuals.

**Summary:**  
The Guided Workflow Dashboard offers a clear, stepwise experience tailored to technical and business users in telecom. It emphasizes data privacy, process transparency, and actionable output, ensuring a confident and professional demo for all stakeholders.

[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/9841353/1137b99b-7467-4f78-aee4-3b582892cecb/product-owner-ideas-document-v0.2.docx
[2] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/9841353/46336be9-b60e-476e-a0a4-ce7e50f6402d/sample_purchase_history.csv
[3] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/9841353/ab5b9a2e-247f-4c7c-9944-51a1bf93e3ca/sample-customer-data-20250714.csv
[4] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/9841353/f8d487cb-b78d-4a4c-a67f-dd4fba1d2c91/Agentic-AI-Revenue-Assistant-Lead-Generation-Agent-PRD.md