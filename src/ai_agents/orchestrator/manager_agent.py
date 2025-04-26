"""
Manager Agent implementation for the Property Investment Analysis Application.

This agent is responsible for orchestrating the workflow and delegating tasks
to specialized agents based on user requests.
"""

import logging
from typing import Dict, Any, List, Optional
import json

from agents import Agent, function_tool
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ManagerAgentResult(BaseModel):
    """Result from the Manager Agent."""
    task_type: str
    status: str
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

def create_manager_agent(specialized_agents: Dict[str, Agent]) -> Agent:
    """
    Create and configure the Manager Agent that coordinates specialized agents.
    
    Args:
        specialized_agents: Dictionary of specialized agents to be used as tools
        
    Returns:
        Configured Manager Agent
    """
    
    # Convert specialized agents to tools
    agent_tools = []
    for agent_type, agent in specialized_agents.items():
        agent_tools.append(
            agent.as_tool(
                tool_name=f"use_{agent_type}",
                tool_description=f"Use the {agent.name} to {_get_agent_description(agent_type)}"
            )
        )
    
    # Define agent instructions
    instructions = """
    You are the Manager Agent for the Property Investment Analysis Application.
    
    Your role is to coordinate multiple specialized AI agents to help users analyze property investments.
    You must understand user requests, determine which specialized agent(s) to invoke, and synthesize
    their outputs into coherent responses.
    
    Available specialized agents:
    1. Market Data Search Agent - Gathers current market data for target locations
    2. Rent Estimation Agent - Estimates rental income based on property characteristics
    3. Document Analysis Agent - Extracts information from property documents
    4. Optimization Agent - Suggests ways to optimize investment returns
    
    When processing user requests:
    1. Identify the user's intent and required information
    2. Determine which specialized agent(s) can best handle the request
    3. Delegate tasks to appropriate specialized agents
    4. Synthesize results into a coherent, actionable response
    5. If information is missing, ask the user for clarification
    
    For complex analyses that require multiple agents:
    1. Plan the sequence of agent calls needed
    2. Execute them in a logical order, passing context between agents
    3. Combine their outputs into a comprehensive analysis
    
    Always maintain a helpful, professional tone and provide clear explanations.
    If a specialized agent fails or returns low-confidence results, acknowledge
    limitations and suggest alternative approaches.
    """
    
    # Create and return the agent
    return Agent(
        name="Investment Analysis Manager",
        instructions=instructions,
        tools=agent_tools
    )

def _get_agent_description(agent_type: str) -> str:
    """Get a description for a specific agent type."""
    descriptions = {
        "market_data": "gather current market data for a specific location including prices, rents, and trends",
        "rent_estimation": "estimate potential rental income based on property specifics and local market data",
        "document_analysis": "extract key information from property documents like leases and inspection reports",
        "optimization": "analyze an investment and suggest specific optimizations to improve returns"
    }
    return descriptions.get(agent_type, "perform a specialized task")