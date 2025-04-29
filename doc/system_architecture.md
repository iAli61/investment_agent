# Property Investment Analysis Application - System Architecture

## Enhanced AI Agent Architecture with LangChain

The AI Agent component of the Property Investment Analysis Application has been enhanced with a LangChain-based implementation that creates a more autonomous system while maintaining calculation accuracy. This section details the revised architecture.

### RAG-Enhanced Knowledge System

```
┌─────────────────────┐    ┌─────────────────────┐
│   Property Data     │    │   Market Knowledge  │
│   Vector Store      │◄───┤   Embedding Pipeline│
└─────────┬───────────┘    └─────────────────────┘
          │                           ▲
          ▼                           │
┌─────────────────────┐    ┌─────────────────────┐
│   Retrieval         │    │   Knowledge Sources │
│   Augmentation      │◄───┤   - Documents       │
│   Component         │    │   - Regulations     │
└─────────┬───────────┘    │   - Market Data     │
          │                └─────────────────────┘
          ▼
┌─────────────────────┐
│   Agent Context     │
│   Enhancement       │
└─────────────────────┘
```

The Retrieval-Augmented Generation (RAG) system provides investment-specific knowledge to LLM agents:

1. **Vector Database Integration**
   - Implemented using LangChain's vector store abstractions (Chroma or FAISS)
   - Stores embedded property investment knowledge, market data, and financial principles
   - Enables semantic search over investment terminology and concepts

2. **Embedding Pipeline**
   - Uses HuggingFace embeddings through LangChain integration
   - Processes investment documents, regulations, and market data into vector representations
   - Automatic chunking with RecursiveCharacterTextSplitter for optimal retrieval

3. **Retrieval Component**
   - Implements similarity search with optional metadata filtering
   - Enhances agent prompts with contextually relevant investment knowledge
   - Improves accuracy of financial advice and market analysis

### Advanced Agent Framework

```
┌───────────────────────────────────────────────────────────┐
│                    Agent Orchestrator                     │
└───────────────┬─────────────────────────┬─────────────────┘
                │                         │
    ┌───────────▼──────────┐   ┌─────────▼───────────┐
    │   Manager Agent      │   │   Context Manager   │
    └───────────┬──────────┘   └─────────────────────┘
                │
┌───────────────┼───────────────┬───────────────────┬─────────────────┐
│               │               │                   │                 │
▼               ▼               ▼                   ▼                 ▼
┌───────────┐ ┌───────────┐ ┌───────────┐     ┌───────────┐     ┌───────────┐
│ Market    │ │ Rent      │ │ Document  │     │ Risk      │     │ Strategy  │
│ Data      │ │ Estimation│ │ Analysis  │     │ Analysis  │     │ Agent     │
│ Agent     │ │ Agent     │ │ Agent     │     │ Agent     │     │           │
└─────┬─────┘ └─────┬─────┘ └─────┬─────┘     └─────┬─────┘     └─────┬─────┘
      │             │             │                 │                 │
      ▼             ▼             ▼                 ▼                 ▼
┌───────────┐ ┌───────────┐ ┌───────────┐     ┌───────────┐     ┌───────────┐
│ Search    │ │ Calculation│ │ Document  │     │ Risk      │     │ Strategy  │
│ Tools     │ │ Tools     │ │ Tools     │     │ Tools     │     │ Tools     │
└───────────┘ └───────────┘ └───────────┘     └───────────┘     └───────────┘
```

The enhanced agent framework is built using LangChain components:

1. **Agent Orchestrator**
   - Implemented with LangChain's Expression Language (LCEL) for component chaining
   - Coordinates task delegation to specialized agents
   - Manages conversation flow and task distribution

2. **Manager Agent**
   - Built with a LangChain ChatModel with tool calling capabilities
   - Uses SystemMessagePromptTemplate with carefully crafted instructions
   - Delegates to specialized agents through standardized tool interfaces

3. **Specialized Agents**
   - Implemented as LangChain agents with domain-specific capabilities
   - Added Risk Analysis and Strategy agents to the existing specialized agents
   - Each agent has its own context window and prompt templates

4. **Tool Framework**
   - Created using LangChain's @tool decorator pattern
   - Standardized interfaces with Pydantic models for validation
   - Clear separation between agent reasoning and calculation tools

### Memory Management System

```
┌────────────────────────┐
│   Agent Memory System  │
└───────────┬────────────┘
            │
┌───────────┴────────────┐
│                        │
▼                        ▼
┌────────────────┐  ┌────────────────┐
│ Conversation   │  │ Knowledge Base │
│ Memory         │  │ Memory         │
└────────┬───────┘  └────────┬───────┘
         │                   │
         ▼                   ▼
┌────────────────┐  ┌────────────────┐
│ Short-term     │  │ User           │
│ Memory         │  │ Preferences    │
└────────────────┘  └────────────────┘
```

The memory system provides context maintenance across interactions:

1. **Conversation Memory**
   - Implements LangChain's ConversationBufferMemory for dialogue history
   - Maintains a seamless conversation context for the user
   - Tracks messages with their source (user, agent, function)

2. **Knowledge Base Memory**
   - Persists investment facts and principles for later retrieval
   - Stores regulatory information with source attribution
   - Maintains a database of past decisions and their outcomes

3. **User Preferences**
   - Remembers user-specific investment criteria and risk tolerance
   - Adapts responses based on user expertise level
   - Persists preferences across sessions

### Real-Time Update System

```
┌────────────────────────┐
│   Real-Time Updates    │
└───────────┬────────────┘
            │
┌───────────┴────────────┐
│                        │
▼                        ▼
┌────────────────┐  ┌────────────────┐
│ Metric         │  │ Server-Sent    │
│ Calculation    │  │ Events Channel │
└────────┬───────┘  └────────┬───────┘
         │                   │
         ▼                   ▼
┌────────────────┐  ┌────────────────┐
│ Calculation    │  │ Client-Side    │
│ Engine API     │  │ UI Updates     │
└────────────────┘  └────────────────┘
```

The real-time update system provides immediate feedback on input changes:

1. **Metric Calculation Engine**
   - Performs fast, incremental calculations when inputs change
   - Caches intermediate results for efficiency
   - Prioritizes high-impact metrics for immediate updates

2. **Server-Sent Events (SSE) Channel**
   - Implements SSE for streaming updates to the frontend
   - Maintains persistent connection for real-time data flow
   - Handles reconnection and backpressure

3. **Client-Side Update Logic**
   - Updates UI components as new data arrives
   - Animates transitions for metric changes
   - Provides visual indicators of calculation status

### Scenario Management System

```
┌────────────────────────┐
│   Scenario Management  │
└───────────┬────────────┘
            │
┌───────────┴────────────┐
│                        │
▼                        ▼
┌────────────────┐  ┌────────────────┐
│ Scenario       │  │ Comparison     │
│ Service        │  │ Engine         │
└────────┬───────┘  └────────┬───────┘
         │                   │
         ▼                   ▼
┌────────────────┐  ┌────────────────┐
│ Scenario       │  │ Diff           │
│ Repository     │  │ Visualization  │
└────────────────┘  └────────────────┘
```

The scenario management system supports comparison and storage of investment scenarios:

1. **Scenario Service**
   - Provides CRUD operations for investment scenarios
   - Supports cloning and modification of existing scenarios
   - Manages scenario metadata and status

2. **Comparison Engine**
   - Calculates differences between scenarios
   - Identifies key metric variations
   - Generates natural language explanations of differences

3. **Scenario Repository**
   - Persists scenarios in the database with status tracking
   - Supports tagging and categorization
   - Implements version control for scenario iterations

### Cost Tracking System

```
┌────────────────────────┐
│   Cost Tracking        │
└───────────┬────────────┘
            │
┌───────────┴────────────┐
│                        │
▼                        ▼
┌────────────────┐  ┌────────────────┐
│ Token Usage    │  │ Compute        │
│ Middleware     │  │ Cost Tracker   │
└────────┬───────┘  └────────┬───────┘
         │                   │
         ▼                   ▼
┌────────────────┐  ┌────────────────┐
│ Usage          │  │ Cost           │
│ Analytics      │  │ Reporting      │
└────────────────┘  └────────────────┘
```

The cost tracking system monitors and reports on AI and infrastructure costs:

1. **Token Usage Middleware**
   - Intercepts API calls to LLM providers
   - Counts tokens used per request
   - Calculates associated costs based on current pricing

2. **Compute Cost Tracker**
   - Monitors CPU/GPU usage for local operations
   - Estimates infrastructure costs for hosted scenarios
   - Aggregates costs across the application

3. **Usage Analytics**
   - Provides dashboards for cost monitoring
   - Identifies optimization opportunities
   - Supports budgeting and forecasting

### Internationalization (i18n) System

```
┌────────────────────────┐
│   i18n System          │
└───────────┬────────────┘
            │
┌───────────┴────────────┐
│                        │
▼                        ▼
┌────────────────┐  ┌────────────────┐
│ UI             │  │ Prompt         │
│ Translation    │  │ Templates      │
└────────┬───────┘  └────────┬───────┘
         │                   │
         ▼                   ▼
┌────────────────┐  ┌────────────────┐
│ Locale         │  │ Language       │
│ Selection      │  │ Detection      │
└────────────────┘  └────────────────┘
```

The internationalization system provides multilingual support:

1. **UI Translation Layer**
   - Translates interface elements based on locale
   - Supports right-to-left languages when needed
   - Manages number and date formatting

2. **Prompt Templates**
   - Maintains separate prompt templates for each language
   - Adapts examples and instructions to cultural context
   - Preserves technical accuracy across translations

3. **Locale Selection**
   - Allows users to explicitly select language preference
   - Remembers preference across sessions
   - Supports language-specific settings

4. **Language Detection**
   - Automatically detects user language when possible
   - Falls back to browser/system settings
   - Respects explicit user preferences

## Implementation Details

### Technology Stack

The enhanced AI agent system is implemented with the following technologies:

1. **LangChain Dependencies**
   - langchain-core: Core abstractions and interfaces
   - langchain-community: Integration with vector stores and embedding models
   - langchain: Primary framework for agent implementation
   - langgraph: For complex agent workflows (when needed)
   - langsmith: For tracing, debugging, and evaluation (optional)

2. **Vector Database**
   - chromadb: Primary vector database for investment knowledge
   - HuggingFace sentence-transformers: For generating embeddings

3. **LLM Providers**
   - Primary: Azure OpenAI Service
   - Fallback: Direct OpenAI API access

4. **Real-Time Technologies**
   - Server-Sent Events (SSE) for streaming updates
   - WebSockets for bidirectional communication (optional)
   - React for reactive UI updates

5. **Internationalization**
   - i18next for UI translations
   - Language-specific prompt templates
   - Azure Translator API for dynamic translations (optional)

### Core Classes and Components

1. **VectorStore**
   - Manages the property investment knowledge base
   - Provides methods for storing and retrieving knowledge
   - Implements similarity search with metadata filtering

2. **AgentMemory**
   - Manages conversation history and user preferences
   - Provides methods for storing and retrieving facts
   - Implements caching for performance optimization

3. **AgentOrchestrator**
   - Coordinates the activities of all specialized agents
   - Manages task delegation and result aggregation
   - Implements the Manager Pattern for agent coordination

4. **PromptTemplateManager**
   - Manages system prompts for different agent roles
   - Provides standardized templates for agent interactions
   - Implements dynamic prompt construction with context

5. **ScenarioService**
   - Manages the creation and comparison of investment scenarios
   - Provides CRUD operations for scenarios
   - Implements diff algorithms for scenario comparison

6. **MetricCalculator**
   - Performs real-time calculations based on input changes
   - Streams updates to the frontend
   - Supports incremental recalculation for efficiency

7. **CostTracker**
   - Monitors and records LLM API usage
   - Calculates estimated costs per scenario
   - Provides analytics on usage patterns

8. **TranslationService**
   - Manages translations for UI elements and prompts
   - Supports dynamic language switching
   - Handles language-specific formatting

### Implementation Phases

The system will be implemented in the following phases:

1. **Phase 1: Core Infrastructure Enhancement** (Current)
   - Implement Vector Database integration
   - Create Memory Management System
   - Enhance Agent Orchestrator
   - Add Scenario Management capability
   - Implement i18n foundation
   - Add Cost Tracking middleware

2. **Phase 2: Agent Enhancement**
   - Upgrade specialized agents with LangChain tools
   - Implement improved system prompts
   - Create new Risk Analysis and Strategy agents
   - Add multi-language support for prompts

3. **Phase 3: Tool Enhancement**
   - Standardize calculation tools
   - Implement comprehensive guardrails
   - Create verification components for output validation
   - Implement real-time update system

4. **Phase 4: Integration and Testing**
   - Connect all components using LCEL
   - Implement comprehensive testing with LangSmith
   - Optimize performance and resource usage
   - Validate multi-language support

## Azure OpenAI Integration

The Property Investment Analysis Application now fully supports integration with Azure OpenAI Service, providing enterprise-grade AI capabilities with enhanced security, compliance, and regional deployment options.

### Azure OpenAI Architecture

```
┌─────────────────────┐    ┌─────────────────────┐
│   Application       │    │   Azure OpenAI      │
│   Backend           │───▶│   Service           │
└─────────┬───────────┘    └─────────────────────┘
          │                           ▲
          ▼                           │
┌─────────────────────┐    ┌─────────────────────┐
│   Agent System      │───▶│   Azure             │
│   Orchestrator      │    │   Identity Platform │
└─────────┬───────────┘    └─────────────────────┘
          │                           ▲
          ▼                           │
┌─────────────────────┐    ┌─────────────────────┐
│   Specialized       │───▶│   Azure Key         │
│   Agents            │    │   Vault             │
└─────────────────────┘    └─────────────────────┘
```

### Azure OpenAI Integration Components

1. **Azure OpenAI Client Configuration**
   - AsyncAzureOpenAI client initialization with proper authentication
   - Support for Azure API versions and regional endpoints
   - Deployment-specific model configurations

2. **Azure OpenAI Models Support**
   - Primary model: GPT-4o for sophisticated reasoning tasks
   - Alternative models: GPT-3.5 Turbo for more cost-efficient operations
   - Embedding models: text-embedding-ada-002 for vector operations

3. **OpenAI Agents SDK Integration**
   - Full compatibility with the OpenAI Agents SDK
   - Tool binding with Azure OpenAI models
   - Asynchronous processing support

### Azure Integration Features

1. **Authentication Methods**
   - API Key-based authentication
   - Support for Azure Managed Identities (optional)
   - Azure Active Directory integration capabilities

2. **Regional Deployment**
   - Support for model deployments in specific Azure regions
   - Data residency compliance through regional selection
   - Low-latency access through strategic regional deployment

3. **Security Enhancements**
   - Key vault integration for credential storage
   - Private endpoints capability for secure networking
   - Support for Azure Virtual Network integration

4. **Operational Monitoring**
   - Azure-compatible logging and telemetry
   - Application Insights integration
   - Comprehensive error handling and reporting

### Configuration Pattern

The system implements a flexible configuration pattern for Azure OpenAI:

```python
# Azure OpenAI Client Initialization
async def setup_azure_openai_client():
    """Set up Azure OpenAI client for use with Agents SDK."""
    
    # Create Azure OpenAI client
    openai_client = AsyncAzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
    )
    
    # Set as default client for Agents SDK
    set_default_openai_client(openai_client)
    
    return openai_client
```

### Environment Configuration

The system supports comprehensive environment-based configuration:

1. **Azure OpenAI Settings**
   - AZURE_OPENAI_API_KEY: Authentication key for Azure OpenAI
   - AZURE_OPENAI_ENDPOINT: Service endpoint URL
   - AZURE_OPENAI_DEPLOYMENT_NAME: Specific model deployment name
   - AZURE_OPENAI_API_VERSION: API version specification

2. **Feature Flags**
   - USE_AZURE_OPENAI: Toggle between Azure OpenAI and standard OpenAI
   - AZURE_OPENAI_USE_MANAGED_IDENTITY: Optional managed identity support

3. **Model Configuration**
   - DEFAULT_MODEL: Primary model selection
   - OPTIMIZED_MODEL: Alternative model for cost efficiency
   - AZURE_OPENAI_EMBEDDING_DEPLOYMENT: Vector embedding model

### Production Azure Deployment Recommendations

For optimal performance and security in production environments:

1. **Resource Configuration**
   - Deploy Azure OpenAI resources in the same region as application services
   - Implement proper capacity provisioning based on expected load
   - Configure appropriate quotas and rate limits

2. **Network Security**
   - Use Private Link and VNET integration for secure communication
   - Implement network security groups with appropriate inbound/outbound rules
   - Configure Application Gateway or Front Door for public-facing components

3. **Identity Management**
   - Use Managed Identities instead of API keys when possible
   - Store necessary secrets in Azure Key Vault
   - Implement least-privilege access controls

4. **Monitoring and Scaling**
   - Set up alerting for quota limits and error rates
   - Implement proper logging with diagnostic settings
   - Configure auto-scaling based on usage patterns