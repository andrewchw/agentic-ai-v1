# Software Requirements Specification  
## Agentic AI Revenue Assistant ¡V Minimal Viable Demo (Revised)

### System Design

- **Privacy-first agentic AI system** for telecom lead generation and sales suggestion.
- Users upload customer and purchase CSVs; data is pseudonymized, merged, and analyzed.
- Results are presented in an interactive Streamlit dashboard, with export capability.
- All logic and data processing occur locally or in a secure, encrypted environment.
- Incorporates an open-source agentic AI framework (CrewAI or LangChain) for agent orchestration, context management, and LLM integration.

### Architecture Pattern

- **Layered Architecture**:
  - **Presentation Layer:** Streamlit UI for workflow and results.
  - **Application Layer:** Workflow orchestration, validation, and state management.
  - **Agentic AI Framework Layer:** CrewAI/LangChain for agent orchestration, context engineering, and LLM workflow.
  - **Service Layer:** Data transformation, pseudonymization, agentic analysis (LLM).
  - **Data Layer:** CSV ingestion, JSON-based storage, export.

### State Management

- Stateless between sessions; all state held in memory during workflow.
- State transitions:
  1. Initial (no data)
  2. Data Uploaded (raw)
  3. Data Pseudonymized (privacy layer)
  4. Data Merged (customer + purchase)
  5. Analysis Complete (results ready)
- State held in Python objects; optionally serialized as JSON for persistence.
- Agentic AI framework manages agent state, workflow context, and LLM interaction context[1][2][3].
- **Agent Context Memory:** Agents maintain context of prior actions, recommendations, and user feedback for traceability and explainability.

### Data Flow

1. User uploads customer and purchase history CSVs.
2. System validates and parses files.
3. Privacy layer pseudonymizes all sensitive fields.
4. Data merged by Account ID; stored as unified JSON structure.
5. Agentic AI framework manages:
   - Context assembly (profile, purchase, engagement)
   - LLM prompt construction and memory
   - Agent workflow execution
6. LLM (DeepSeek via OpenRouter) analyzes merged data for lead scoring and suggestions.
7. Results displayed in dashboard and available for export.

### Technical Stack

| Component         | Technology/Framework           | Notes                                 |
|-------------------|-------------------------------|---------------------------------------|
| Frontend/UI       | Streamlit                     | Guided workflow dashboard             |
| Backend           | Python 3.x                    | Core logic and data processing        |
| Agentic Framework | CrewAI or LangChain           | Agent orchestration, context mgmt     |
| LLM API           | OpenRouter (DeepSeek, Llama-2)| Privacy-compliant, open-source LLM    |
| Data Privacy      | Custom Python utilities       | Pseudonymization, masking             |
| Storage           | Local JSON (encrypted)        | Prototype DB, in-memory or file-based |
| Export            | CSV/JSON                      | Download anonymized results           |

### Agentic AI Framework Integration

- **Framework Role:**
  - Orchestrates agent workflow, context assembly, and LLM interactions.
  - Provides modular agent definitions, tool integration, and memory/context management.
  - Supports context engineering: dynamically assembles relevant customer, purchase, and engagement data for each LLM call[1][2][3].
  - Ensures no raw PII is ever included in LLM context.
- **Implementation:**
  - Define a single lead generation agent within CrewAI/LangChain.
  - Use context engineering best practices: curate, compress, and deliver only relevant, pseudonymized data to the LLM.
  - Integrate with privacy layer: agent receives only masked data objects.
  - LLM outputs are reviewed and formatted by the agent before dashboard display/export.

### Context Engineering

- **Key Responsibilities:**
  - Design and manage the full context window for each LLM call (profile, purchase, engagement, prior agent outputs).
  - Implement context assembly logic in the agentic AI framework layer.
  - Ensure context is always privacy-compliant, relevant, and optimized for LLM reasoning.
  - Monitor and log context construction for audit and debugging[2][4][3][5].
- **Best Practices:**
  - Use modular context builders for each workflow step.
  - Separate prompt templates from context data for maintainability.
  - Limit context size to avoid LLM truncation and ensure performance.

### Authentication Process

- No user authentication required for demo.
- All data handled locally for security.
- API keys for LLM access are securely stored in environment variables; never exposed in UI or logs.

### Route Design

- Single-page workflow in Streamlit; steps managed via UI state.
- Main routes (logical, not URL-based):
  1. `/upload` ¡V Data upload step
  2. `/review` ¡V Data preview and pseudonymization confirmation
  3. `/analyze` ¡V Run agentic analysis
  4. `/results` ¡V View and export results

### API Design

- **Internal APIs (Python functions):**
  - `parse_csv(file)`: Validate and parse uploaded CSVs.
  - `pseudonymize(data)`: Mask all PII fields.
  - `merge_data(customers, purchases)`: Join datasets by Account ID.
  - `assemble_context(record)`: Build context for each lead.
  - `run_agentic_analysis(context)`: Call LLM for lead scoring and suggestions.
  - `export_results(data, format)`: Prepare anonymized results for download.
- **External APIs:**
  - OpenRouter LLM API for DeepSeek/Llama-2 (secured, only pseudonymized data sent).

### Database Design ERD

- **Prototype uses a JSON-based data store; ERD conceptualized as:**

```
Customer
---------
AccountID (PK)
Pseudonymized Name
Other Profile Fields
...

PurchaseHistory
---------------
AccountID (FK)
[Purchase 1]
[Purchase 2]
...
Engagement Data

UnifiedCustomer
---------------
AccountID (PK)
Pseudonymized Profile Fields
[PurchaseHistory List]
[Engagement Data]
Lead Score
Suggested Action
```

- All joins and lookups are performed on `AccountID`.
- No raw PII is stored beyond the privacy layer.

### Additional Notes

- **Agentic AI framework (CrewAI or LangChain) is a core architectural layer, not just a library.** It manages agent workflow, context engineering, and LLM orchestration.
- **Context engineering is a first-class responsibility:** assign a context engineer to the project to design, implement, and maintain context assembly and privacy compliance.
- **All context and agentic logic must be auditable and modular** to ensure future extensibility and regulatory compliance.
- **Delays and rework are minimized** by explicitly modeling agentic framework integration and context engineering in the architecture from the outset[1][2][3][5].

**

[1] https://www.moveworks.com/us/en/resources/blog/what-is-agentic-framework
[2] https://www.youtube.com/watch?v=FIXaMEBUFac
[3] https://dev.to/rakshith2605/context-engineering-the-game-changing-discipline-powering-modern-ai-4nle
[4] https://datasciencedojo.com/blog/what-is-context-engineering/
[5] https://momen.app/blogs/understanding-role-context-engineer-ai-systems/
[6] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/9841353/1137b99b-7467-4f78-aee4-3b582892cecb/product-owner-ideas-document-v0.2.docx
[7] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/9841353/f8d487cb-b78d-4a4c-a67f-dd4fba1d2c91/Agentic-AI-Revenue-Assistant-Lead-Generation-Agent-PRD.md
[8] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/9841353/3c6e1a02-7f67-41ac-956c-f8badcaeddbc/Agentic-AI-Revenue-Assistant-Lead-Generation-Agent-UI-Deisgn-Document.md
[9] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/9841353/34606b97-bfc8-45e1-8727-18c424a5b60d/sample_purchase_history.csv
[10] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/9841353/ca75fdaf-30f8-4252-868f-9db7832f61d2/sample-customer-data-20250714.csv
[11] https://eluminoustechnologies.com/blog/agentic-ai-frameworks/
[12] https://www.reply.com/en/ai-powered-software-engineering/integrating-ai-powered-agentic-systems
[13] https://addepto.com/blog/agentic-ai-api-how-to-make-your-ai-agent-talk-to-other-software-integration-patterns-that-work/
[14] https://www.xenonstack.com/blog/agentic-ai-software-development
[15] https://superagi.com/how-to-build-a-robust-agentic-ai-framework-step-by-step-implementation-strategies/
[16] https://www.infoq.com/articles/agentic-ai-architecture-framework/
[17] https://www.dataiq.global/articles/best-practices-implementing-agentic-ai/
[18] https://www.nexastack.ai/blog/agentic-ai-agent-framework
[19] https://statusneo.com/why-context-engineering-is-the-next-big-thing-in-ai-development/
[20] https://www.teksystems.com/en-hk/insights/article/agentic-ai-governance
[21] https://www.ibm.com/think/insights/top-ai-agent-frameworks
[22] https://www.digitalocean.com/community/tutorials/agentic-ai-frameworks-guide
[23] https://about.gitlab.com/topics/agentic-ai/ai-augmented-software-development/
[24] https://www.sierraventures.com/content/best-practices-building-agentic-ai
[25] https://www.askeygeek.com/agentic-ai-frameworks/