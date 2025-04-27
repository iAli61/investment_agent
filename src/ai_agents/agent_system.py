"""
AI Agent System for the Property Investment Analysis Application.

This module integrates all AI agent components: orchestrator, specialized agents, tools, and guardrails.
"""

import logging
import asyncio
import os
from typing import Dict, Any, Optional, List

from agents import Agent, Runner

from .orchestrator import AgentOrchestrator, create_manager_agent, TaskResult
from .specialized import (
    create_market_data_search_agent,
    create_rent_estimation_agent,
    create_document_analysis_agent,
    create_optimization_agent
)
from .guardrails import create_guardrails
from openai import AsyncAzureOpenAI
from agents import set_default_openai_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Monkey patch Agent class to add guardrails attribute if it doesn't exist
if not hasattr(Agent, 'guardrails'):
    # Add guardrails attribute to Agent class
    setattr(Agent, 'guardrails', property(
        lambda self: getattr(self, '_guardrails', []),
        lambda self, value: setattr(self, '_guardrails', value)
    ))
    # Initialize _guardrails for each new Agent instance
    original_init = Agent.__init__
    def patched_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self._guardrails = []
    Agent.__init__ = patched_init
    logger.info("Added guardrails support to Agent class")

class AIAgentSystem:
    """
    Integrated AI agent system for property investment analysis.
    
    This class brings together all components of the AI agent system:
    - Orchestrator for coordinating agent tasks
    - Specialized agents for different investment analysis tasks
    - Manager agent that delegates to specialized agents
    - Guardrails for ensuring safe and relevant agent behavior
    """
    
    def __init__(
        self, 
        model_name: str = "gpt-4o",
        use_azure: bool = False,
        azure_deployment: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        azure_api_version: Optional[str] = None,
        use_managed_identity: bool = False
    ):
        """
        Initialize the AI agent system.
        
        Args:
            model_name: Name of the LLM model to use for agents
            use_azure: Whether to use Azure OpenAI instead of regular OpenAI
            azure_deployment: Azure OpenAI deployment name (required if use_azure is True)
            azure_endpoint: Azure OpenAI endpoint URL (required if use_azure is True)
            azure_api_version: Azure OpenAI API version (optional)
            use_managed_identity: Whether to use Azure Managed Identity for authentication (optional)
        """
        self.model_name = model_name
        self.use_azure = use_azure
        self.azure_deployment = azure_deployment
        self.azure_endpoint = azure_endpoint
        self.azure_api_version = azure_api_version or "2023-07-01-preview"
        self.use_managed_identity = use_managed_identity
        
        self.orchestrator = None
        self.manager_agent = None
        self.specialized_agents = {}
        self.guardrails = create_guardrails()
        
        if self.use_azure:
            self._configure_azure_openai()
        
        logger.info(f"Initializing AI Agent System with model: {model_name}")
        if self.use_azure:
            logger.info(f"Using Azure OpenAI with deployment: {azure_deployment}")
        
    def _configure_azure_openai(self):
        """Configure the system to use Azure OpenAI instead of regular OpenAI."""
        if not self.azure_deployment or not self.azure_endpoint:
            raise ValueError(
                "Azure OpenAI deployment name and endpoint URL are required when use_azure is True. "
                "Set azure_deployment and azure_endpoint or configure via environment variables."
            )
        
        # Set environment variables for Azure OpenAI
        os.environ["OPENAI_API_TYPE"] = "azure"
        os.environ["OPENAI_API_VERSION"] = self.azure_api_version
        os.environ["OPENAI_API_BASE"] = self.azure_endpoint
        
        if self.use_managed_identity:
            logger.info("Using Azure Managed Identity for authentication")
            os.environ["OPENAI_USE_MANAGED_IDENTITY"] = "true"
        else:
            # Ensure API key is set in the environment
            if not os.environ.get("AZURE_OPENAI_API_KEY"):
                raise ValueError(
                    "AZURE_OPENAI_API_KEY environment variable must be set when using Azure OpenAI "
                    "without managed identity"
                )
            os.environ["OPENAI_API_KEY"] = os.environ.get("AZURE_OPENAI_API_KEY")

        # Create OpenAI client using Azure OpenAI
        openai_client = AsyncAzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        )

        # Set the default OpenAI client for the Agents SDK
        set_default_openai_client(openai_client)
        
        # When using Azure, the model_name should be the deployment name
        self.model_name = self.azure_deployment
        
    def initialize(self):
        """Initialize the complete agent system."""
        logger.info("Initializing AI agent system components")
        
        # Initialize orchestrator
        self.orchestrator = AgentOrchestrator()
        
        # Initialize specialized agents
        self._initialize_specialized_agents()
        
        # Initialize manager agent
        self._initialize_manager_agent()
        
        logger.info("AI agent system initialization complete")
        
    def _initialize_specialized_agents(self):
        """Initialize all specialized agents."""
        logger.info("Initializing specialized agents")
        
        # Create specialized agents with guardrails
        self.specialized_agents = {
            "market_data": create_market_data_search_agent(),
            "rent_estimation": create_rent_estimation_agent(),
            "document_analysis": create_document_analysis_agent(),
            "optimization": create_optimization_agent()
        }
        
        # Apply guardrails to all agents
        for agent_type, agent in self.specialized_agents.items():
            try:
                # Safely add guardrails to agent
                if not hasattr(agent, 'guardrails'):
                    # If no guardrails attribute exists, create it
                    setattr(agent, '_guardrails', [])
                    
                # Add each guardrail safely
                guardrails_list = getattr(agent, '_guardrails', [])
                for guardrail in self.guardrails:
                    if guardrail not in guardrails_list:
                        guardrails_list.append(guardrail)
                
                # Register with orchestrator
                self.orchestrator.register_specialized_agent(agent_type, agent)
                
                logger.info(f"Initialized {agent_type} agent with guardrails")
            except Exception as e:
                logger.error(f"Error initializing {agent_type} agent: {str(e)}")
                raise
    
    def _initialize_manager_agent(self):
        """Initialize the manager agent."""
        logger.info("Initializing manager agent")
        
        try:
            # Create manager agent with specialized agents as tools
            self.manager_agent = create_manager_agent(self.specialized_agents, model=self.model_name)
            
            # Apply guardrails to manager agent safely
            if not hasattr(self.manager_agent, 'guardrails'):
                # If no guardrails attribute exists, create it
                setattr(self.manager_agent, '_guardrails', [])
                
            # Add each guardrail safely
            guardrails_list = getattr(self.manager_agent, '_guardrails', [])
            for guardrail in self.guardrails:
                if guardrail not in guardrails_list:
                    guardrails_list.append(guardrail)
            
            # Register with orchestrator
            self.orchestrator.register_manager_agent(self.manager_agent)
            
            logger.info("Manager agent initialized with guardrails")
        except Exception as e:
            logger.error(f"Error initializing manager agent: {str(e)}")
            raise
    
    async def process_user_request(self, user_input: str) -> Dict[str, Any]:
        """
        Process a user request using the manager agent to coordinate specialized agents.
        
        Args:
            user_input: User's request text
            
        Returns:
            Dictionary with processed results
        """
        if not self.orchestrator or not self.manager_agent:
            raise ValueError("AI agent system not initialized. Call initialize() first.")
        
        logger.info(f"Processing user request: {user_input}")
        
        try:
            # Use manager agent to process the request
            result = await self.orchestrator.execute_with_manager(
                user_input,
                model=self.model_name
            )
            
            return {
                "status": "success",
                "result": result
            }
        except Exception as e:
            logger.error(f"Error processing user request: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def execute_direct_task(self, agent_type: str, input_text: str) -> TaskResult:
        """
        Execute a task directly with a specific specialized agent.
        
        Args:
            agent_type: Type of specialized agent to use
            input_text: Input text for the agent
            
        Returns:
            Task result from the agent
        """
        if not self.orchestrator:
            raise ValueError("AI agent system not initialized. Call initialize() first.")
        
        logger.info(f"Executing direct task with {agent_type} agent")
        
        return await self.orchestrator.execute_task(
            agent_type,
            input_text,
            model=self.model_name
        )