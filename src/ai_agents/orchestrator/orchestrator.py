"""
Agent Orchestrator module implementing the Manager Pattern.

This orchestrator coordinates specialized agents and maintains context across interactions.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from uuid import uuid4
from pydantic import BaseModel, Field
import queue
import time

from agents import Agent, Runner, function_tool

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
    timestamp: float = Field(default_factory=time.time)

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
        self.task_queue = queue.Queue()
        self.task_status = {}  # Track status of tasks even after they've been processed
        logger.info("[Orchestrator] Initialized new Agent Orchestrator instance")
        
    def register_manager_agent(self, agent: Agent):
        """Register the manager agent that will coordinate specialized agents."""
        self.manager_agent = agent
        logger.info(f"[Orchestrator] Registered manager agent: {agent.name}")
        logger.info(f"[Orchestrator] Manager agent has {len(agent.tools or [])} tools available")
        
    def register_specialized_agent(self, agent_type: str, agent: Agent):
        """Register a specialized agent with the orchestrator."""
        self.specialized_agents[agent_type] = agent
        tool_count = len(agent.tools or [])
        logger.info(f"[Orchestrator] Registered specialized agent: {agent_type} - {agent.name}")
        logger.info(f"[Orchestrator] Agent {agent_type} has {tool_count} tools available")
    
    def get_specialized_agent(self, agent_type: str) -> Optional[Agent]:
        """Get a specialized agent by type."""
        agent = self.specialized_agents.get(agent_type)
        if not agent:
            logger.warning(f"[Orchestrator] No agent found for requested type: {agent_type}")
        return agent
    
    def add_task(self, task):
        """Add a task to the queue for processing."""
        self.task_queue.put(task)
        queue_size = self.task_queue.qsize() if hasattr(self.task_queue, 'qsize') else 'unknown'
        logger.info(f"[Orchestrator] Added task {task.task_id} to queue: {task.description}")
        logger.info(f"[Orchestrator] Current queue size: {queue_size}")
        
        # Track the task status
        self.task_status[task.task_id] = "pending"
        logger.info(f"[Orchestrator] Task {task.task_id} status set to: pending")
        
    def get_task_status(self, task_id: str) -> str:
        """Get the current status of a task."""
        # First check if we have a result already
        if task_id in self.results_cache:
            status = self.results_cache[task_id].status
            logger.info(f"[Orchestrator] Retrieved status for task {task_id} from results cache: {status}")
            return status
            
        # Then check the task_status dictionary
        if task_id in self.task_status:
            status = self.task_status[task_id]
            logger.info(f"[Orchestrator] Retrieved status for task {task_id} from status tracker: {status}")
            return status
            
        # If not found anywhere, it's unknown
        logger.warning(f"[Orchestrator] No status information found for task {task_id}")
        return "unknown"
        
    def get_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the result of a completed task."""
        if task_id in self.results_cache:
            task_result = self.results_cache[task_id]
            if task_result.status == "success":
                logger.info(f"[Orchestrator] Retrieved successful result for task {task_id}")
                # Update the task status
                self.task_status[task_id] = "completed"
                logger.info(f"[Orchestrator] Task {task_id} status updated to: completed")
                return task_result.content
            else:
                logger.info(f"[Orchestrator] Task {task_id} status: {task_result.status}")
                # Update the task status
                self.task_status[task_id] = task_result.status
                logger.info(f"[Orchestrator] Task {task_id} status updated to: {task_result.status}")
        else:
            logger.info(f"[Orchestrator] Result for task {task_id} not yet available")
            
        return None
        
    async def process_queue(self):
        """Process the task queue."""
        if self.task_queue.empty():
            logger.info("[Orchestrator] Task queue is empty, nothing to process")
            return
            
        queue_size = self.task_queue.qsize() if hasattr(self.task_queue, 'qsize') else 'unknown'
        logger.info(f"[Orchestrator] Processing task queue with {queue_size} tasks")
        
        while not self.task_queue.empty():
            task = self.task_queue.get()
            logger.info(f"[Orchestrator] Processing task {task.task_id}: {task.description}")
            logger.info(f"[Orchestrator] Delegating to agent type: {task.agent_type}")
            
            # Update task status to processing
            task.status = "processing"
            self.task_status[task.task_id] = "processing"
            logger.info(f"[Orchestrator] Task {task.task_id} status updated to: processing")
            
            agent_type = task.agent_type
            
            try:
                logger.info(f"[Orchestrator] Executing task parameters: {list(task.parameters.keys())}")
                task_result = await self.execute_task(
                    agent_type=agent_type,
                    input_text=task.description,
                    **task.parameters
                )
                
                # Update task status based on the result
                task.status = task_result.status
                self.task_status[task.task_id] = task_result.status
                logger.info(f"[Orchestrator] Task {task.task_id} completed with status: {task_result.status}")
                logger.info(f"[Orchestrator] Task {task.task_id} status updated to: {task_result.status}")
                
                # Add result to results cache
                if task_result.status == "success":
                    self.results_cache[task.task_id] = task_result
                    self.task_status[task.task_id] = "completed"
                    logger.info(f"[Orchestrator] Task {task.task_id} status updated to: completed")
                
            except Exception as e:
                logger.error(f"[Orchestrator] Error processing task {task.task_id}: {str(e)}")
                task.status = "failure"
                self.task_status[task.task_id] = "failure"
                logger.info(f"[Orchestrator] Task {task.task_id} status updated to: failure")
                
                self.results_cache[task.task_id] = TaskResult(
                    task_id=task.task_id,
                    agent_name="orchestrator",
                    status="failure",
                    error=str(e)
                )
            
            self.task_queue.task_done()
            remaining = self.task_queue.qsize() if hasattr(self.task_queue, 'qsize') else 'unknown'
            logger.info(f"[Orchestrator] Tasks remaining in queue: {remaining}")
    
    async def execute_task(self, agent_type: str, input_text: str, **kwargs) -> TaskResult:
        """Execute a task with a specialized agent."""
        task_id = str(uuid4())
        logger.info(f"[Orchestrator] Creating new task with ID: {task_id}")
        agent = self.get_specialized_agent(agent_type)
        
        if not agent:
            error_msg = f"No agent found for type: {agent_type}"
            logger.error(f"[Orchestrator] {error_msg}")
            return TaskResult(
                task_id=task_id,
                agent_name="unknown",
                status="failure",
                error=error_msg
            )
        
        try:
            logger.info(f"[Orchestrator] Executing task {task_id} with agent {agent.name}")
            
            # Store parameters in context for tool access instead of passing directly to Runner.run
            context = {"parameters": kwargs}
            param_names = list(kwargs.keys())
            logger.info(f"[Orchestrator] Task parameters: {param_names}")
            
            # Only pass the model parameter to Runner.run if it exists
            runner_kwargs = {}
            if "model" in kwargs:
                model_name = kwargs["model"]
                runner_kwargs["model"] = model_name
                logger.info(f"[Orchestrator] Using model: {model_name}")
                
            logger.info(f"[Orchestrator] Sending input to {agent.name}: '{input_text[:50]}...' ({len(input_text)} chars)")
            result = await Runner.run(agent, input_text, context=context, **runner_kwargs)
            
            logger.info(f"[Orchestrator] Task {task_id} successfully completed by {agent.name}")
            task_result = TaskResult(
                task_id=task_id,
                agent_name=agent.name,
                status="success",
                content={"final_output": result.final_output}
            )
            
            # Cache the result
            self.results_cache[task_id] = task_result
            result_size = len(str(result.final_output))
            logger.info(f"[Orchestrator] Cached result for task {task_id} ({result_size} chars)")
            return task_result
            
        except Exception as e:
            error_msg = f"Error executing task with agent {agent.name}: {str(e)}"
            logger.error(f"[Orchestrator] {error_msg}")
            return TaskResult(
                task_id=task_id,
                agent_name=agent.name,
                status="failure",
                error=error_msg
            )
    
    async def execute_with_manager(self, input_text: str, **kwargs) -> Any:
        """Execute a task using the manager agent to coordinate specialized agents."""
        if not self.manager_agent:
            error_msg = "No manager agent registered"
            logger.error(f"[Orchestrator] {error_msg}")
            raise ValueError(error_msg)
        
        try:
            logger.info(f"[Orchestrator] Delegating user input to manager agent: '{input_text[:50]}...'")
            
            # Log available specialized agents
            agent_types = list(self.specialized_agents.keys())
            logger.info(f"[Orchestrator] Available specialized agents: {agent_types}")
            
            # Log model information if provided
            if "model" in kwargs:
                logger.info(f"[Orchestrator] Using model for manager agent: {kwargs['model']}")
            
            result = await Runner.run(self.manager_agent, input_text, **kwargs)
            
            logger.info("[Orchestrator] Manager agent execution completed successfully")
            tool_calls = getattr(result, 'tool_calls', [])
            if tool_calls:
                logger.info(f"[Orchestrator] Manager made {len(tool_calls)} tool calls during execution")
                
            return result.final_output
        except Exception as e:
            error_msg = f"Error executing with manager agent: {str(e)}"
            logger.error(f"[Orchestrator] {error_msg}")
            raise