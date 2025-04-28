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

### Prompt Engineering Framework

The system implements improved prompt engineering with LangChain's templating capabilities:

1. **System Prompts**: Carefully designed instructions for each agent role
   - Manager Agent: Expert investment advisor coordinating specialized agents
   - Market Data Agent: Specialist in gathering property market information
   - Rent Estimation Agent: Expert in rental property income analysis
   - Document Analysis Agent: Specialist in extracting information from property documents
   - Risk Analysis Agent: Expert in identifying and quantifying investment risks
   - Strategy Agent: Specialist in optimizing investment approach

2. **Prompt Templates**: Standardized formats for different agent roles
   - ChatPromptTemplates for conversational interactions
   - SystemMessagePromptTemplates for consistent base instructions
   - MessagesPlaceholder for maintaining conversation history

3. **Few-Shot Examples**: When appropriate, to guide specific agent behaviors
   - Examples of market data analysis for different property types
   - Examples of risk assessment at different confidence levels
   - Examples of document extraction for various document types

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

### Implementation Phases

The system will be implemented in the following phases:

1. **Phase 1: Core Infrastructure Enhancement** (Current)
   - Implement Vector Database integration
   - Create Memory Management System
   - Enhance Agent Orchestrator

2. **Phase 2: Agent Enhancement**
   - Upgrade specialized agents with LangChain tools
   - Implement improved system prompts
   - Create new Risk Analysis and Strategy agents

3. **Phase 3: Tool Enhancement**
   - Standardize calculation tools
   - Implement comprehensive guardrails
   - Create verification components for output validation

4. **Phase 4: Integration and Testing**
   - Connect all components using LCEL
   - Implement comprehensive testing with LangSmith
   - Optimize performance and resource usage

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