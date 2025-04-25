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
- uv package manager (optional, recommended) or pip
- Node.js 18+ (for frontend development only)
- pytest-asyncio for running asynchronous tests

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/investment_agent.git
cd investment_agent
```

2. Install the required packages:

Using uv (recommended for faster installation):
```bash
# Install uv if you don't have it
curl -sSf https://astral.sh/uv/install.sh | bash
# Or on Windows
curl.exe -sSf https://astral.sh/uv/install.ps1 | powershell

# Install dependencies with uv
uv pip install -e .
# Or with development dependencies
uv pip install -e ".[dev]"
```

Using pip:
```bash
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

### Deployment Options

#### Local Deployment
Follow the instructions above for running the application locally.

#### Docker Deployment
1. Build the Docker image:
```bash
docker build -t investment-agent .
```

2. Run the container:
```bash
docker run -p 8501:8501 -p 8000:8000 -e DATABASE_URL=sqlite:///./investment_analysis.db -e OPENAI_API_KEY=your_openai_api_key investment-agent
```

#### Azure Deployment
The application can be deployed to Azure using the following services:

1. **Azure App Service**: For hosting the FastAPI backend
2. **Azure Container Apps**: For hosting the Streamlit frontend
3. **Azure Database for PostgreSQL**: For the application database
4. **Azure Key Vault**: For secure storage of API keys and secrets
5. **Azure OpenAI Service**: For LLM functionality

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
│   ├── ai_agents/            # AI agent implementations
│   │   ├── base_agent.py     # Base agent class with common functionality
│   │   ├── market_data_agent.py  # Market data collection agent
│   │   ├── orchestrator.py   # Agent orchestration framework
│   │   ├── rent_estimation_agent.py  # Rent estimation agent
│   │   └── tools.py          # Tool implementations for agents
│   ├── backend/              # Backend API
│   │   ├── api.py            # FastAPI implementation
│   ├── database/             # Database models and connections
│   │   ├── database.py       # Database connection handling
│   │   ├── models.py         # SQLAlchemy models
│   ├── frontend/             # Frontend application
│   │   ├── app.py            # Streamlit application
│   └── utils/                # Utility functions
│       ├── financial_utils.py  # Financial calculation utilities
├── tests/                    # Test suites
│   ├── unit/                 # Unit tests for individual components
│   │   ├── ai_agents/        # Tests for AI agent functionality
│   ├── integration/          # Integration tests
│   └── e2e/                  # End-to-end tests
├── docker/                   # Docker configuration
│   ├── Dockerfile            # Docker image definition
│   └── docker-compose.yml    # Multi-container setup
├── docs/                     # Documentation
│   ├── api/                  # API documentation
│   ├── user-guide/           # User guide
│   └── azure-deployment.md   # Azure deployment guide
├── requirements.txt          # Package dependencies
├── setup.py                  # Package setup
├── pyproject.toml            # Python project configuration
├── Dockerfile                # Main Dockerfile
└── README.md                 # This file
```

## AI Agent System

The application uses a modular AI agent system with the following components:

1. **Base Agent (BaseAgent)**: Provides core functionality including:
   - Execution tracking with iteration count
   - Input validation
   - Logging and monitoring
   - Error handling and recovery
   - Result formatting

2. **Market Data Agent (MarketDataSearchAgent)**:
   - Collects real estate market data for specific locations and property types
   - Generates sample listings for analysis
   - Calculates confidence levels for data reliability
   - Supports different operations (buy/rent)

3. **Rent Estimation Agent (RentEstimationAgent)**:
   - Estimates rental prices based on property characteristics
   - Uses market data to improve estimation accuracy
   - Factors in property features and condition
   - Calculates per square meter rental values

4. **Agent Tools**:
   - RealEstateSearchTool: Search for real estate listings
   - MarketTrendTool: Analyze market trends
   - RentEstimationTool: Estimate rental prices

The orchestrator coordinates these agents to complete complex analytical tasks.

## Testing the Application

### Unit Tests
Run unit tests with:
```bash
# Install pytest-asyncio first if you haven't
pip install pytest-asyncio

# Run all unit tests
pytest tests/unit

# Run specific agent tests
pytest tests/unit/ai_agents
```

Note: The test suite is currently being expanded and updated to match the latest implementation. Some tests may fail due to API changes in progress.

### Integration Tests
Run integration tests with:
```bash
pytest tests/integration
```

### End-to-End Tests
Run end-to-end tests with:
```bash
pytest tests/e2e
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

## License

[MIT License](LICENSE)

## Acknowledgments

- OpenAI for providing advanced language models
- LangChain for the agent framework
- Streamlit for the interactive web interface
- FastAPI for the high-performance backend
- The real estate investment community for domain expertise