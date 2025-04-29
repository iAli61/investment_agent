# User Stories for Enhanced AI-Driven Investment App

## Core User Stories

### 1. Conversational Guidance
- **As an investor, I want to ask questions in natural language and receive step-by-step guidance from the AI assistant, so I can understand and complete the investment analysis process easily.**
#### Task Plan: Conversational Guidance
- Conversational UI Design
    - Add a persistent chat panel to the frontend (Streamlit).
    - Allow users to ask questions in natural language at any step.
    - Display AI responses, explanations, and step-by-step guidance.

- Backend API for Conversation
    - Create /ai/conversation/ endpoint to handle chat messages.
    - Route user messages to the Manager Agent for orchestration.
    - Maintain conversation history (session or persistent).

- AI Agent Orchestration
    - Manager Agent interprets user intent and delegates to specialized agents.
    - Use memory/context to provide relevant, stepwise guidance.
    - Return both direct answers and next-step suggestions.

- Frontend Integration
    - Show chat history and allow follow-up questions.
    - Highlight actionable suggestions (e.g., “Would you like to enter property details now?”).
    - Allow users to click suggestions to trigger UI navigation or actions.

- Session/Context Management
    Store conversation state per user/session.
    Use vector memory for context-aware responses.

- Feedback Loop
    - Allow users to rate or correct AI responses for continuous improvement.

#### Conversational Guidance Design

Frontend (Streamlit):
    - Add a chat sidebar or floating panel.
    - Input box for user questions.
    - Display AI responses with markdown formatting.
    - Show “suggested actions” as clickable buttons.

Backend:
    - /ai/conversation/ POST endpoint:
        - Input: { message: str, context: dict }
        - Output: { response: str, suggestions: [str], context: dict }

    - Manager Agent:
        - Receives message and context.
        - Uses memory to maintain conversation flow.
        - Delegates to specialized agents as needed.
        - Returns answer and next-step suggestions.

Example Flow:

 - User: “How do I start an investment analysis?”
 - AI: “Let’s begin by entering your property details. Would you like to proceed?”
 - [Button: “Enter Property Details”] (navigates to input form)

### 2. Real-Time Analysis
- **As a user, I want to see investment metrics update in real time as I change inputs, so I can instantly understand the impact of my decisions.**

### 3. Scenario Comparison
- **As an investor, I want to compare multiple investment scenarios side-by-side, with AI-generated insights on key differences and risks.**

### 4. Document Upload & Analysis
- **As a user, I want to upload property documents (leases, reports) and have the AI extract key information, highlight issues, and compare with my data.**

### 5. Human-in-the-Loop Review
- **As a user, I want to review, approve, or modify AI recommendations for high-impact decisions, so I retain control over important actions.**

### 6. Personalized Explanations
- **As a user, I want the AI to remember my preferences and expertise level, so explanations and terminology are tailored to me.**

### 7. Feedback and Learning
- **As a user, I want to provide feedback or corrections on AI outputs, so the system can learn and improve over time.**

---

## Technical/Developer Stories

### 8. Agent Orchestration
- **As a developer, I want a LangChain-based manager agent to coordinate specialized agents (market, rent, risk, optimization, document), so the system is modular and scalable.**

### 9. RAG & Memory Integration
- **As a developer, I want all agents to use a shared vector database and persistent memory, so knowledge and context are consistent across the system.**

### 10. Tool Standardization
- **As a developer, I want all agent tools to use standardized schemas and validation, so outputs are reliable and easy to integrate.**

### 11. Guardrails & Human Escalation
- **As a developer, I want multi-layered guardrails and human escalation for high-risk actions, so the system is safe and trustworthy.**

### 12. Streaming & Async API
- **As a developer, I want all agent endpoints to be async and support streaming, so the UI remains responsive and users see progress in real time.**

---

## Next Steps
- Prioritize implementation of the conversational UI and streaming agent responses.
- Design feedback collection and learning loop for continuous improvement.
- Plan integration of document upload and analysis workflows.
- Define API contracts for scenario management and feedback endpoints.
