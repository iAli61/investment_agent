# Enhanced Design for Property Investment Analysis App (AI-Driven)

## 1. Overview
This design leverages advanced AI agent orchestration, RAG (Retrieval-Augmented Generation), and memory management to deliver a highly interactive, explainable, and autonomous investment analysis experience. The interface and backend are restructured to maximize the value of enhanced AI capabilities.

---

## 2. Interface (Frontend)

### 2.1 Conversational & Guided UI
- **AI Chat Assistant**: Persistent chat panel for natural language queries, explanations, and step-by-step guidance (powered by the Manager Agent).
- **Step-by-Step Wizard**: Data input wizard with contextual help, validation, and progress tracking. Each step can be explained by the AI.
- **Interactive Dashboard**: Real-time, streaming updates of key metrics (cash flow, ROI, risk, etc.) as user changes inputs.
- **Scenario Comparison**: Side-by-side comparison of multiple investment scenarios, with AI-generated insights on differences.
- **Human-in-the-Loop**: UI for reviewing, approving, or modifying AI recommendations for high-impact decisions.
- **Document Upload & Analysis**: Drag-and-drop for leases, reports, etc. with AI extraction and discrepancy highlighting.
- **Personalization**: User preferences and expertise level remembered and reflected in explanations and terminology.

### 2.2 Visual Enhancements
- **Responsive Design**: Mobile-first, adaptive layouts.
- **Data Visualizations**: Enhanced charts for cash flow, amortization, risk, and optimization impact.
- **Confidence Indicators**: Visual cues for AI confidence in estimates and recommendations.
- **Feedback Mechanisms**: Users can rate, correct, or comment on AI outputs for continuous improvement.

---

## 3. Backend (API & Agent System)

### 3.1 Conversational Guidance (Manager Agent)
- **Endpoint**: POST /ai/conversation/
  - Accepts: `{ message: string, context?: object }`
  - Returns: `{ response: string, suggestions: string[], context: object }`
- **Manager Agent `converse` method**:
  - Registered by orchestrator at startup:
    ```python
    orchestrator.register_manager_agent(manager_agent)
    # attaches manager_agent.converse = orchestrator._manager_converse
    ```
  - Internally calls `execute_with_manager(message, context)` to:
    1. Append user message to conversation memory
    2. Retrieve relevant knowledge (RAG)
    3. Fetch conversation history and preferences from memory
    4. Invoke the Manager Agent via Runner.run()
    5. Store agent response in memory
    6. Return structured output
- **Suggestions**:
  - Initially an empty list, to be populated by Manager Agent logic
  - In future: analyze `intent` or `response` to suggest next steps (e.g., “Enter property details”, “Upload lease document”)

### 3.2 API Enhancements
- **Async Endpoints**: All AI/agent endpoints remain asynchronous for real-time UX
- **Context Management**: Frontend passes and preserves `context` between calls
- **Error Handling**: Consistent HTTP errors for missing manager agent or failures

### 3.3 Data & Security
- **Vector DB**: Chroma/FAISS for knowledge, with Azure Cognitive Search as an option.
- **Relational DB**: PostgreSQL for core data (properties, users, scenarios, feedback).
- **Azure Integration**: Azure OpenAI, Key Vault, Managed Identities, and VNET for security and compliance.

---

## 4. Key User Flows
- **Conversational Analysis**: User asks, "Is this a good investment?" → Manager agent orchestrates data gathering, analysis, and explanation, streaming results and visualizations.
- **Document Upload**: User uploads a lease → Document agent extracts terms, highlights issues, and compares to user-entered data.
- **Optimization**: User requests "How can I improve returns?" → Optimization agent simulates strategies, shows impact, and provides actionable steps.
- **Scenario Comparison**: User compares two properties → AI highlights key differences, risks, and opportunities.

---

## 5. Implementation Phases
1. **Core Infrastructure**: Vector DB, memory, agent orchestrator, async API.
2. **Agent Enhancement**: Specialized agents, tool standardization, prompt engineering.
3. **UI/UX Upgrade**: Conversational UI, streaming, scenario comparison, document upload.
4. **Feedback & Learning**: Feedback loop, agent learning, human-in-the-loop.

---

## 6. References
- See `doc/system_architecture.md` for detailed diagrams and technical rationale.
- Requirements and user stories: `RDP-Agents.md` section 7.
