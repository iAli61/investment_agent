"""
Agent Orchestrator module implementing the Manager Pattern.

This orchestrator coordinates specialized agents and maintains context across interactions.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from uuid import uuid4

from agents import Agent, Runner, function_tool
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskResult(BaseModel):
    """Result of a task executed by an agent."""
    task_id: str
    agent_name: str
    status: str  # "success", "failure", "in_progress"
    content: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class AgentOrchestrator:
    """
    Orchestrator implementing the Manager Pattern to coordinate specialized agents.
    
    This orchestrator:
    - Manages a task queue
    - Routes tasks to appropriate specialized agents
    - Maintains context across agent interactions
    - Aggregates results from multiple agents
    - Implements human escalation when needed
    """
    
    def __init__(self):
        """Initialize the orchestrator with specialized agents."""
        self.context = {}
        self.manager_agent = None
        self.specialized_agents = {}
        self.results_cache = {}
        
    def register_manager_agent(self, agent: Agent):
        """Register the manager agent that will coordinate specialized agents."""
        self.manager_agent = agent
        logger.info(f"Registered manager agent: {agent.name}")
        
    def register_specialized_agent(self, agent_type: str, agent: Agent):
        """Register a specialized agent with the orchestrator."""
        self.specialized_agents[agent_type] = agent
        logger.info(f"Registered specialized agent: {agent_type} - {agent.name}")
    
    def get_specialized_agent(self, agent_type: str) -> Optional[Agent]:
        """Get a specialized agent by type."""
        return self.specialized_agents.get(agent_type)
    
    async def execute_task(self, agent_type: str, input_text: str, **kwargs) -> TaskResult:
        """Execute a task with a specialized agent."""
        task_id = str(uuid4())
        agent = self.get_specialized_agent(agent_type)
        
        if not agent:
            error_msg = f"No agent found for type: {agent_type}"
            logger.error(error_msg)
            return TaskResult(
                task_id=task_id,
                agent_name="unknown",
                status="failure",
                error=error_msg
            )
        
        try:
            logger.info(f"Executing task {task_id} with agent {agent.name}")
            result = await Runner.run(agent, input_text, **kwargs)
            
            task_result = TaskResult(
                task_id=task_id,
                agent_name=agent.name,
                status="success",
                content={"final_output": result.final_output}
            )
            
            # Cache the result
            self.results_cache[task_id] = task_result
            return task_result
            
        except Exception as e:
            error_msg = f"Error executing task with agent {agent.name}: {str(e)}"
            logger.error(error_msg)
            return TaskResult(
                task_id=task_id,
                agent_name=agent.name,
                status="failure",
                error=error_msg
            )
    
    async def execute_with_manager(self, input_text: str, **kwargs) -> Any:
        """Execute a task using the manager agent to coordinate specialized agents."""
        if not self.manager_agent:
            raise ValueError("No manager agent registered")
        
        try:
            result = await Runner.run(self.manager_agent, input_text, **kwargs)
            return result.final_output
        except Exception as e:
            error_msg = f"Error executing with manager agent: {str(e)}"
            logger.error(error_msg)
            raise