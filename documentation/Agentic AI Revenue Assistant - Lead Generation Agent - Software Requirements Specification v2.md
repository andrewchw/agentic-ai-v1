# Software Requirements Specification  
## Agentic AI Revenue Assistant ¡V Minimal Viable Demo (Revised & Expanded)

### System Design

- **Privacy-first agentic AI system** for telecom lead generation and sales suggestion.
- Incorporates an open-source agentic AI framework (CrewAI or LangChain) for agent orchestration, context management, and LLM integration.
- Modular design for future multi-agent expansion, robust error handling, and compliance.
- Users upload customer and purchase CSVs; data is pseudonymized, merged, and analyzed.
- Results are presented in an interactive Streamlit dashboard, with export capability.
- All logic and data processing occur locally or in a secure, encrypted environment.

### Architecture Pattern

- **Layered Architecture:**
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
- Agentic AI framework manages agent state, workflow context, and LLM interaction context.
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
8. **Agent logs all reasoning steps, context, and outputs for audit and review.**

### Technical Stack

| Component           | Technology/Framework          | Notes                                           |
|---------------------|------------------------------|-------------------------------------------------|
| Frontend/UI         | Streamlit                    | Guided workflow dashboard                       |
| Backend             | Python 3.x                   | Core logic and data processing                  |
| Agentic Framework   | CrewAI or LangChain          | Agent orchestration, context engineering, LLM integration |
| LLM API             | OpenRouter (DeepSeek, Llama-2)| Privacy-compliant, open-source LLM              |
| Data Privacy        | Custom Python utilities      | Pseudonymization, masking                       |
| Storage             | Local JSON (encrypted)       | Prototype DB, in-memory or file-based           |
| Export              | CSV/JSON                     | Download anonymized results                     |

### Agentic AI Framework Integration

- **Framework Role:**
  - Orchestrates agent workflow, context assembly, and LLM interactions.
  - Provides modular agent definitions, tool integration, and memory/context management.
  - Manages agent boundaries, permissions, and responsibilities.
  - Supports context engineering: dynamically assembles relevant, pseudonymized data for each LLM call.
  - Handles agent communication, workflow sequencing, and error recovery.
  - All agent logic, context engineering, and LLM integration are implemented within this framework for modularity and auditability.
  - Ensures no raw PII is ever included in LLM context.
- **Implementation:**
  - Define a single lead generation agent within CrewAI/LangChain.
  - Use context engineering best practices: curate, compress, and deliver only relevant, pseudonymized data to the LLM.
  - Integrate with privacy layer: agent receives only masked data objects.
  - LLM outputs are reviewed and formatted by the agent before dashboard display/export.

### Agentic Autonomy

- **Explicit Agent Boundaries:**  
  Each agent¡¦s scope, permissions, and responsibilities are defined in the agentic framework configuration. Agents only access data and perform actions within their assigned domain (e.g., lead generation, not retention).
- **Autonomous Decision Triggers:**  
  Agents initiate actions on specific events: new data upload, scheduled intervals, or when certain thresholds are crossed (e.g., low engagement detected).
- **Self-Monitoring and Recovery:**  
  Agents log errors, incomplete tasks, and unexpected states. Automatic retries or escalation to human-in-the-loop checkpoints are triggered as per configuration.
- **Autonomy Guardrails:**  
  Constraints and escalation paths are defined (e.g., actions requiring approval, limits on automated communications). Human-in-the-loop checkpoints are configurable for sensitive actions.

### Reasoning

- **Transparent Reasoning Chains:**  
  Agents log their reasoning process for each recommendation (e.g., "Lead prioritized due to high engagement and recent device purchase").
- **Explainability:**  
  Each agent decision includes a human-readable explanation, visible in the results dashboard and export.
- **Contextual Awareness:**  
  Agents maintain a memory of past actions, recommendations, and user feedback, enabling context-aware suggestions and avoiding redundant actions.
- **Reasoning Validation:**  
  Regular validation routines check the quality and consistency of agent outputs, with logs available for audit and review.

### Multi-Agent Orchestration (For Future Expansion)

- **Agent Role Definitions:**  
  Clear taxonomy of agent roles (e.g., Lead Generation Agent, Sales Suggestion Agent, Retention Agent) with documented responsibilities and interactions.
- **Communication Protocols:**  
  Agents communicate via shared memory, event-driven triggers, or message passing as supported by CrewAI/LangChain.
- **Workflow Coordination:**  
  Orchestration logic defines sequencing, parallelization, and synchronization of agent actions.
- **Conflict Resolution:**  
  Mechanisms for resolving conflicting recommendations (e.g., priority rules, human review).
- **Extensibility for New Agents:**  
  Plug-in architecture allows for adding, removing, or updating agents without disrupting the system.
- **Monitoring and Logging:**  
  All agent interactions, performance metrics, and outcomes are tracked for audit and optimization.

### Integration-Specific Considerations

- **Standardized Agent Interfaces:**  
  Input/output schemas and APIs are defined for agent communication and orchestration.
- **Context Sharing:**  
  Shared context is managed and updated between agents via the agentic framework¡¦s memory/context management features.
- **Privacy Compliance Across Agents:**  
  All agents uniformly respect pseudonymization and privacy rules; privacy checks are enforced at the framework level.
- **Orchestration Engine Selection:**  
  CrewAI or LangChain workflows are configured as the orchestration engine, with documentation on setup and extension.
- **Testing and Simulation:**  
  Requirements include simulation of multi-agent workflows and validation of integration before production use.

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

### Summary Table: Agentic Integration Requirements

| Area        | Key Requirements Added                                                                                 |
|-------------|-------------------------------------------------------------------------------------------------------|
| Autonomy    | Agent boundaries, triggers, self-monitoring, guardrails                                               |
| Reasoning   | Reasoning logs, explainability, context memory, validation                                            |
| Multi-Agent | Role taxonomy, communication, workflow, conflict resolution, extensibility, monitoring                |
| Integration | Standard interfaces, context sharing, privacy compliance, orchestration engine, simulation/testing     |

**Note:**  
All requirements marked **¡§Highest¡¨** are mandatory for the demo. Other requirements should be deferred unless time permits.  
Agentic AI framework integration, agent autonomy, explainability, and orchestration are now explicitly addressed to ensure robust, scalable, and trustworthy agentic AI development and integration.