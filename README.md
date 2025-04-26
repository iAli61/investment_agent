# Property Investment Analysis App with AI Agents

A comprehensive application for real estate investors to analyze potential property investments with the help of AI-powered market data and intelligent analysis.

## Overview

This application helps real estate investors make informed decisions by:

- Collecting real-time market data for target locations
- Estimating potential rental income based on property specifics
- Calculating acquisition costs including closing fees
- Analyzing financing options and mortgage payments
- Projecting detailed cash flow and investment returns
- Assessing tax benefits and regulatory considerations
- Providing AI-powered investment risk and opportunity analysis

The system integrates multiple AI agents to automate complex analytical tasks and deliver accurate, up-to-date information about potential property investments.

## Features

### Property Data Management
- Input detailed property information (address, price, type, age, condition)
- Multi-unit property support with independent unit management
- AI-powered market data collection for the property's location

### Financial Analysis
- Closing cost calculator with regional tax considerations
- Mortgage payment calculator with amortization schedules
- Operating expenses estimation with customizable parameters
- Tax benefit calculator including building depreciation
- Comprehensive cash flow analysis (before and after tax)

### AI-Powered Insights
- Market Data Search Agent: Collects up-to-date market information
- Rent Estimation Agent: Provides accurate rent estimates for vacant units
- Tax Regulation Monitoring: Ensures tax calculations reflect current regulations
- Risk Assessment: Identifies specific investment risks and opportunities
- Optimization Recommendations: Suggests ways to improve investment returns

### Visualization and Reporting
- Interactive dashboard with key metrics
- Visual cash flow breakdowns
- Amortization charts
- Investment metrics visualization
- Downloadable investment reports

## System Architecture

The application follows a modular architecture with several key components:

### User Interface
- Streamlit-based web interface with interactive components
- Responsive design with clear data visualization
- Interactive forms for property data input
- Real-time calculation updates

### Core Application
- API Layer: FastAPI backend service
- Calculation Engine: Complex financial calculations
- Agent Orchestrator: Coordinates multiple AI agents
- Asynchronous task processing for long-running operations

### AI Agents
- Multiple specialized agents for different tasks
- Agent Orchestration Framework for coordination
- Context management for shared information
- LLM integration for natural language processing

### Data Storage
- Property Database: Stores property details
- Market Data Database: Stores collected market information
- Vector Knowledge Base: Stores domain knowledge for agents
- Secure credential management for API access

## Getting Started

### Prerequisites
- Python 3.9+
- uv package manager (recommended) or pip
- Node.js 18+ (for frontend development only)
- pytest-asyncio for running asynchronous tests

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/investment_agent.git
cd investment_agent
```

2. Install the required packages:

Using uv (recommended):
```bash
# Install uv if you don't have it
# On Linux/macOS
curl -sSf https://astral.sh/uv/install.sh | bash
# Or on Windows
curl.exe -sSf https://astral.sh/uv/install.ps1 | powershell

# Set up a virtual environment and install dependencies with uv
uv venv
source .venv/bin/activate  # On Linux/macOS
# Or on Windows: .venv\Scripts\activate

# Install dependencies with uv
uv pip install -e .
# Or with development dependencies
uv pip install -e ".[dev]"
```

Using pip (alternative):
```bash
python -m venv .venv
source .venv/bin/activate  # On Linux/macOS
# Or on Windows: .venv\Scripts\activate

pip install -e .
# Or with development dependencies
pip install -e ".[dev]"

# Make sure to install pytest-asyncio for async tests
pip install pytest-asyncio
```

3. Set up environment variables:
```bash
# For development
export DATABASE_URL=sqlite:///./investment_analysis.db
export API_URL=http://localhost:8000
export OPENAI_API_KEY=your_openai_api_key  # Required for AI agents
```

### Running the Application

Using uv (recommended):
1. Start the backend API:
```bash
cd investment_agent
source .venv/bin/activate  # If not already activated
uv run -m uvicorn src.backend.api:app --reload
```

2. In a separate terminal, start the frontend:
```bash
cd investment_agent
source .venv/bin/activate  # If not already activated
uv run -m streamlit run src/frontend/app.py
```

Alternative method:
1. Start the backend API:
```bash
cd src
uvicorn backend.api:app --reload
```

2. In a separate terminal, start the frontend:
```bash
cd src
streamlit run frontend/app.py
```

3. Open your browser and navigate to http://localhost:8501

### Troubleshooting Common Issues

- **Backend API connection errors**: Ensure the DATABASE_URL environment variable is correctly set and the database file is accessible.
- **OpenAI API key issues**: Verify your OPENAI_API_KEY is valid and has sufficient credits.
- **Module import errors**: Make sure you've installed the package in development mode with `uv pip install -e .` or `pip install -e .`.
- **Port conflicts**: If ports 8000 or 8501 are already in use, specify alternative ports:
  ```bash
  uv run -m uvicorn src.backend.api:app --reload --port 8080
  uv run -m streamlit run src/frontend/app.py -- --server.port 8081
  ```

## Deployment Options

### Local Deployment
Follow the instructions above for running the application locally.

### Docker Deployment
1. Build the Docker image:
```bash
docker build -t investment-agent .
```

2. Run the container:
```bash
docker run -p 8501:8501 -p 8000:8000 -e DATABASE_URL=sqlite:///./investment_analysis.db -e OPENAI_API_KEY=your_openai_api_key investment-agent
```

### Azure Deployment
The application can be deployed to Azure using the following services:

1. **Azure App Service**: For hosting the FastAPI backend
2. **Azure Container Apps**: For hosting the Streamlit frontend
3. **Azure Database for PostgreSQL Flexible Server**: For the application database
4. **Azure Key Vault**: For secure storage of API keys and secrets
5. **Azure OpenAI Service**: For LLM functionality

#### Azure Deployment Best Practices

- **Infrastructure as Code**: Use Azure Bicep or Terraform to define and deploy your infrastructure
- **CI/CD Pipelines**: Set up GitHub Actions or Azure DevOps Pipelines for automated deployment
- **Zero-Trust Security**: Implement Managed Identities for Azure resources instead of service principals when possible
- **Private Endpoints**: Use private endpoints for Key Vault and Database connectivity
- **VNET Integration**: Place App Service and Container Apps in a virtual network for enhanced security
- **Scalability**: Configure autoscaling rules based on CPU, memory usage, and request count
- **Monitoring**: Set up Azure Monitor and Application Insights for comprehensive observability
- **Backup and Recovery**: Configure automated backups for your PostgreSQL database

Deployment steps:
1. Create the Azure resources using Azure CLI or Azure Portal
2. Configure the application settings with Azure-specific connection strings
3. Deploy the backend and frontend as separate services
4. Set up networking and security rules

See the [Azure Deployment Guide](docs/azure-deployment.md) for detailed instructions.

## Project Structure

```
investment_agent/
├── src/
│   ├── ai_agents/                 # AI agent implementations
│   │   ├── agent_system.py        # Main integration module for AI agents
│   │   ├── guardrails/            # Safety mechanisms for agent behavior
│   │   │   ├── agent_guardrails.py # Implementation of multi-layered guardrails
│   │   ├── orchestrator/          # Agent orchestration framework
│   │   │   ├── orchestrator.py    # Manager Pattern implementation
│   │   │   ├── manager_agent.py   # Manager agent for coordinating specialized agents
│   │   ├── specialized/           # Specialized agent implementations
│   │   │   ├── market_data_agent.py  # Market data collection agent
│   │   │   ├── rent_estimation_agent.py # Rent estimation agent
│   │   │   ├── document_analysis_agent.py # Document processing agent
│   │   │   ├── optimization_agent.py # Investment optimization agent
│   │   ├── tools/                 # Tool implementations for agents
│   │       ├── investment_tools.py # Shared tools for property investment analysis
│   ├── backend/                   # Backend API
│   │   ├── api.py                 # FastAPI implementation
│   ├── database/                  # Database models and connections
│   │   ├── database.py            # Database connection handling
│   │   ├── models.py              # SQLAlchemy models
│   ├── frontend/                  # Frontend application
│   │   ├── app.py                 # Streamlit application
│   └── utils/                     # Utility functions
│       ├── financial_utils.py     # Financial calculation utilities
├── tests/                         # Test suites
│   ├── unit/                      # Unit tests for individual components
│   │   ├── ai_agents/             # Tests for AI agent functionality
│   ├── integration/               # Integration tests
│   └── e2e/                       # End-to-end tests
├── doc/                           # Documentation
│   ├── a-practical-guide-to-building-agents/ # Guide for building AI agents
├── example_usage.py               # Example script demonstrating the AI agent system
├── requirements.txt               # Package dependencies
├── setup.py                       # Package setup
├── pyproject.toml                 # Python project configuration
└── README.md                      # Project documentation
```

### Key Components

#### AI Agent System
- **Agent Orchestrator**: Implements the Manager Pattern to coordinate specialized agents
- **Manager Agent**: Central agent that delegates to specialized agents through tool calls
- **Specialized Agents**: Purpose-built agents for different investment analysis tasks
- **Reusable Tools**: Shared functionality for web search, data analysis, and document processing
- **Guardrails**: Multi-layered safety mechanisms to ensure appropriate agent behavior

#### Backend
- **FastAPI Server**: RESTful API for the application
- **SQLAlchemy Models**: ORM models for database interaction
- **Database Connection**: Handlers for database connections

#### Frontend
- **Streamlit Application**: Interactive web interface
- **Data Visualization**: Components for displaying investment metrics

#### Infrastructure
- **Azure OpenAI Integration**: Support for Azure OpenAI services
- **Database Storage**: Models for storing property and market data
- **Authentication**: User authentication and authorization

## AI Agent Architecture

The application implements a Manager Pattern AI architecture with specialized AI agents for different property investment analysis tasks. The system is designed with the following components:

### Agent Architecture Components

1. **Orchestrator**: Coordinates specialized agents and maintains context across interactions.
   - Manages a task queue
   - Routes tasks to appropriate agents
   - Aggregates results from multiple agents
   - Implements human escalation when needed

2. **Manager Agent**: Central agent that delegates to specialized agents through tool calls.
   - Understands user intents
   - Plans sequences of agent calls
   - Synthesizes results into cohesive responses
   - Manages context between agent interactions

3. **Specialized Agents**:
   - **Market Data Search Agent**: Gathers current market data for target locations.
   - **Rent Estimation Agent**: Estimates rental income based on property characteristics.
   - **Document Analysis Agent**: Extracts key information from property documents.
   - **Optimization Agent**: Suggests ways to optimize investment returns.

4. **Reusable Tools**: Shared functionality that multiple agents can use:
   - Web search tools for gathering market data
   - Database query tools for retrieving property information
   - Document parsing tools for extracting information
   - Analysis tools for financial calculations

5. **Guardrails**: Safety mechanisms that ensure agent behavior stays within defined boundaries:
   - Relevance checkers to ensure on-topic interactions
   - Safety checkers to prevent prompt manipulation
   - PII filters to protect sensitive information
   - Tool risk assessment for high-impact operations

### Using the AI Agent System

The system can be used in two ways:

1. **Using the Manager Agent** (recommended): The manager agent coordinates specialized agents to complete complex tasks.

```python
from src.ai_agents import AIAgentSystem

# Initialize the system
agent_system = AIAgentSystem(model_name="gpt-4o")
agent_system.initialize()

# Process a user request using the manager agent
async def process_request():
    result = await agent_system.process_user_request(
        "I'm considering buying a 2-bedroom apartment in Berlin. Can you analyze..."
    )
    return result
```

2. **Using Specialized Agents Directly**: For specific, focused tasks.

```python
# Execute a task with a specific agent
async def get_market_data():
    market_request = {
        "location": "Berlin Mitte",
        "property_type": "apartment",
        "data_types": ["prices", "rents", "trends"]
    }
    result = await agent_system.execute_direct_task(
        "market_data", 
        json.dumps(market_request)
    )
    return result
```

### Key Benefits

- **Modularity**: Each agent focuses on a specific capability, making the system easier to extend and maintain.
- **Reusable Tools**: Common functionality is implemented once and shared across agents.
- **Comprehensive Guardrails**: Multi-layered protection ensures safe and appropriate agent behavior.
- **Flexible Integration**: Can be used with different LLM providers and models.
- **Context Management**: Maintains information between agent interactions.

See `example_usage.py` for a complete demonstration of the AI agent system.

## Testing the Application

### Unit Tests
Run unit tests with:
```bash
# Install pytest-asyncio first if you haven't
uv pip install pytest-asyncio

# Run all unit tests
python -m pytest tests/unit

# Run specific agent tests
python -m pytest tests/unit/ai_agents
```

Note: The test suite is currently being expanded and updated to match the latest implementation. Some tests may fail due to API changes in progress.

### Integration Tests
Run integration tests with:
```bash
python -m pytest tests/integration
```

### End-to-End Tests
Run end-to-end tests with:
```bash
python -m pytest tests/e2e
```

## Development Status

This project is currently in active development with the following components in progress:

- AI Agent System: Core functionality implemented, refinements ongoing
- Backend API: Basic endpoints implemented
- Frontend: Initial Streamlit interface in development
- Database: Schema defined, integration in progress

Next development priorities:
1. Complete and stabilize AI agent implementation
2. Expand API functionality
3. Enhance frontend user experience
4. Implement comprehensive testing

## Contributing

We welcome contributions to the Property Investment Analysis App!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Submit a pull request

Please follow these guidelines:
- Use uv for dependency management
- Run tests before submitting a PR
- Follow PEP 8 style guide
- Add appropriate documentation
- Include tests for new features

## License

[MIT License](LICENSE)

## Acknowledgments

- OpenAI for providing advanced language models
- LangChain for the agent framework
- Streamlit for the interactive web interface
- FastAPI for the high-performance backend
- The real estate investment community for domain expertise

## Azure OpenAI Integration

### Overview

The Property Investment Analysis Application can be deployed using Azure OpenAI services for enhanced enterprise features, including:

- Regional data residency compliance with data stored in your selected Azure region
- Azure Active Directory integration for seamless enterprise authentication
- Advanced security and compliance certifications (ISO 27001, SOC 1/2/3, HIPAA)
- Centralized billing and resource management through Azure portal
- Integration with other Azure services like Azure Cognitive Search and Azure Machine Learning
- Private networking capabilities with Virtual Network (VNET) integration

### Azure OpenAI Setup

To use Azure OpenAI with this application:

1. **Create an Azure OpenAI resource**:
   ```bash
   # Install Azure CLI if not already available
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   
   # Login to Azure
   az login
   
   # Create a resource group if needed
   az group create --name property-investment-rg --location westeurope
   
   # Create Azure OpenAI resource
   az cognitiveservices account create \
     --name property-investment-openai \
     --resource-group property-investment-rg \
     --kind OpenAI \
     --sku s0 \
     --location westeurope
   ```

2. **Deploy required models**:
   - Deploy `gpt-4o` or `gpt-35-turbo` for the manager agent
   - Deploy smaller models for specialized tasks as needed

3. **Configure environment variables**:
   ```bash
   # For Azure OpenAI
   export AZURE_OPENAI_API_KEY=your_azure_openai_api_key
   export AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   export AZURE_OPENAI_DEPLOYMENT_NAME=your_model_deployment_name
   
   # Or use Azure Managed Identity (preferred for production)
   export AZURE_OPENAI_USE_MANAGED_IDENTITY=true
   ```

### Using the Agent System with Azure OpenAI

The AI agent system supports both OpenAI's standard API and Azure OpenAI. Here's how to initialize the agent system with Azure OpenAI:

```python
from src.ai_agents import AIAgentSystem
import os

# Initialize the system with Azure OpenAI
agent_system = AIAgentSystem(
    use_azure=True,
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
agent_system.initialize()

# Process a user request using the manager agent
async def process_request():
    result = await agent_system.process_user_request(
        "I'm considering buying a 2-bedroom apartment in Berlin. Can you analyze..."
    )
    return result
```

### Azure Architecture for Production Deployment

For production deployments, we recommend:

1. **Azure App Service**: For hosting the FastAPI backend
   - Enable VNET integration
   - Configure autoscaling rules
   - Use deployment slots for zero-downtime deployments

2. **Azure Container Apps**: For hosting the Streamlit frontend
   - Enable scale-to-zero for cost optimization
   - Configure horizontal scaling based on traffic patterns
   - Use GitHub Actions for CI/CD automation

3. **Azure Database for PostgreSQL Flexible Server**: For the application database
   - Enable high availability with zone redundancy
   - Configure automated backups
   - Use Private Link for secure connectivity

4. **Azure Cache for Redis**: For caching search requests and agent context
   - Premium tier for persistence and high availability
   - Configure memory policies based on usage patterns

5. **Azure Key Vault**: For secure storage of API keys and secrets
   - Use Managed Identities for access
   - Enable soft-delete and purge protection
   - Configure access policies with least privilege

6. **Azure OpenAI Service**: For the LLM functionality
   - Deploy models in the same region as your application
   - Configure content filtering settings
   - Set appropriate capacity limits

7. **Azure Monitor & Application Insights**: For monitoring agent performance
   - Set up custom dashboards
   - Configure alerts for key metrics
   - Enable distributed tracing

8. **Azure Front Door**: For global CDN and load balancing
   - Enable WAF protection
   - Configure caching rules
   - Set up health probes for backend services

Here's a deployment architecture diagram:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Web Clients   │────▶│  Azure Front    │────▶│  Container Apps │
│                 │     │  Door (CDN)     │     │  (Frontend)     │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Azure OpenAI  │◀───▶│   App Service   │◀───▶│  Azure Cache    │
│   Service       │     │   (Backend)     │     │  for Redis      │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Azure Key     │◀───▶│  Azure DB for   │     │  Application    │
│   Vault         │     │  PostgreSQL     │     │  Insights       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Version History

- **v0.1.0** (April 2025): Initial release with core functionality
  - Basic property analysis capabilities
  - Integration with AI agents for market research
  - Streamlit frontend and FastAPI backend

## Roadmap

- **Q2 2025**: 
  - Advanced financial modeling
  - Multiple property comparison
  - Portfolio analysis dashboard

- **Q3 2025**:
  - Mobile app support
  - Real-time market alerts
  - Advanced tax optimization

- **Q4 2025**:
  - Multi-user collaboration
  - Integration with popular real estate listing platforms
  - Custom reporting templates