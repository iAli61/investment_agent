# System Architecture Diagram

This document contains the system architecture diagrams for the Property Investment Analysis App using Mermaid syntax.

## System Architecture

```mermaid
flowchart TD
    subgraph "Presentation Layer"
        UI[Streamlit Frontend]
        API[FastAPI Endpoints]
        CLI[CLI Tools]
    end
    
    subgraph "Application Layer"
        Controllers[API Controllers]
        BackgroundTasks[Background Tasks]
        Validation[Request Validation]
    end
    
    subgraph "Domain Layer"
        AgentSystem[AI Agent System]
        BusinessLogic[Investment Analysis Logic]
        FinancialEngine[Financial Calculation Engine]
    end
    
    subgraph "Data Access Layer"
        Repositories[Database Repositories]
        ExternalAPI[External API Integration]
        Cache[Caching Mechanisms]
    end
    
    subgraph "Infrastructure Layer"
        Database[(Database Storage)]
        Auth[Authentication Services]
        Logging[Logging and Monitoring]
    end
    
    UI --> Controllers
    API --> Controllers
    CLI --> Controllers
    
    Controllers --> BusinessLogic
    Controllers --> AgentSystem
    BackgroundTasks --> AgentSystem
    
    BusinessLogic --> Repositories
    AgentSystem --> ExternalAPI
    AgentSystem --> Repositories
    FinancialEngine --> Cache
    
    Repositories --> Database
    ExternalAPI --> Auth
    Cache --> Database
    
    Logging -.- UI
    Logging -.- Controllers
    Logging -.- AgentSystem
    Logging -.- Repositories
```

## AI Agent Architecture

```mermaid
flowchart TD
    User[User] --> FrontendUI[Frontend UI]
    FrontendUI --> API[FastAPI Backend]
    API --> Orchestrator
    
    subgraph "AI Agent System"
        Orchestrator[Task Orchestrator]
        TaskQueue[Task Queue & Status]
        ResultCache[Result Cache]
        
        subgraph "Manager Agent"
            Manager[Manager LLM]
            ContextManager[Context Manager]
            PlanningEngine[Planning Engine]
        end
        
        subgraph "Specialized Agents"
            MarketAgent[Market Data Agent]
            RentAgent[Rent Estimation Agent]
            DocAgent[Document Analysis Agent]
            OptAgent[Optimization Agent]
        end
        
        subgraph "Tool Framework"
            WebSearch[Web Search Tools]
            DataProcessing[Data Processing Tools]
            FinancialTools[Financial Calculation Tools]
            DocumentTools[Document Processing Tools]
        end
        
        subgraph "Guardrails"
            SafetyCheckers[Safety Checkers]
            RelevanceFilters[Relevance Filters]
            ToolRisk[Tool Risk Assessment]
        end
    end
    
    ExternalSources[External Data Sources]
    Database[(Investment Database)]
    
    API --> TaskQueue
    Orchestrator --> Manager
    Manager --> MarketAgent
    Manager --> RentAgent
    Manager --> DocAgent
    Manager --> OptAgent
    
    MarketAgent --> WebSearch
    RentAgent --> DataProcessing
    DocAgent --> DocumentTools
    OptAgent --> FinancialTools
    
    WebSearch <--> ExternalSources
    DataProcessing --> Database
    FinancialTools --> Database
    
    SafetyCheckers -.- Manager
    SafetyCheckers -.- MarketAgent
    SafetyCheckers -.- RentAgent
    SafetyCheckers -.- DocAgent
    SafetyCheckers -.- OptAgent
    
    Orchestrator --> TaskQueue
    Orchestrator --> ResultCache
    Manager <--> ContextManager
    Manager <--> PlanningEngine
```

## Azure Deployment Architecture

```mermaid
flowchart TD
    Users[Web Users] --> AFD[Azure Front Door]
    AFD --> ACA[Azure Container Apps<br>Streamlit Frontend]
    AFD --> AppService[Azure App Service<br>FastAPI Backend]
    
    AppService <--> AzureOpenAI[Azure OpenAI Service]
    AppService <--> Redis[Azure Cache for Redis]
    AppService <--> PSQL[Azure DB for PostgreSQL<br>Flexible Server]
    
    ACA --> AppService
    
    PSQL --> PSQL_Backup[Automated Backups]
    
    subgraph "Security & Monitoring"
        KeyVault[Azure Key Vault]
        AAD[Azure Active Directory]
        AppInsights[Application Insights]
        Monitor[Azure Monitor]
    end
    
    AppService --> KeyVault
    AppService --> AAD
    ACA --> AAD
    AppService -.-> AppInsights
    ACA -.-> AppInsights
    AppInsights --> Monitor
    
    subgraph "Storage & Data"
        BlobStorage[Azure Blob Storage]
        CosmosDB[Azure Cosmos DB<br>Vector Store]
    end
    
    AppService <--> BlobStorage
    AppService <--> CosmosDB
    
    subgraph "Networking"
        VNET[Azure Virtual Network]
        PrivateEndpoints[Private Endpoints]
        NSG[Network Security Groups]
    end
    
    AppService -.-> VNET
    PSQL -.-> PrivateEndpoints
    KeyVault -.-> PrivateEndpoints
    PrivateEndpoints -.-> VNET
    VNET -.-> NSG
```