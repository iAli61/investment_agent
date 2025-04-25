"""
Orchestrator for coordinating different AI agents
"""
import logging
import asyncio
import datetime
import uuid
import os
from typing import Dict, Any, List, Optional, Type

from .base_agent import BaseAgent
from .market_data_agent import MarketDataSearchAgent, create_market_data_agent
from .rent_estimation_agent import RentEstimationAgent, create_rent_estimation_agent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Orchestrator class that coordinates the execution of specialized AI agents
    
    This class manages the workflow of different agents, passing context between
    them and aggregating their results.
    """
    
    def __init__(self, use_langchain: bool = True, api_key: Optional[str] = None):
        """
        Initialize the orchestrator with available agents
        
        Args:
            use_langchain: Whether to use LangChain-based agents (if available)
            api_key: API key for language models (if using LangChain)
        """
        self.agents: Dict[str, BaseAgent] = {}
        self.session_id = str(uuid.uuid4())
        self.context: Dict[str, Any] = {
            "session_id": self.session_id,
            "created_at": datetime.datetime.now().isoformat(),
            "agent_results": {}
        }
        
        # Use LangChain if specified and API key is available
        self.use_langchain = use_langchain
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        
        # Register agents
        self._register_agents()
        logger.info(f"Orchestrator initialized with session ID: {self.session_id}")
        logger.info(f"Using LangChain: {self.use_langchain}")
    
    def _register_agents(self) -> None:
        """Register all available agents"""
        try:
            # Register the market data agent using factory
            market_data_agent = create_market_data_agent(
                use_langchain=self.use_langchain,
                api_key=self.api_key
            )
            self.agents[market_data_agent._get_agent_name()] = market_data_agent
            
            # Register the rent estimation agent using factory
            rent_estimation_agent = create_rent_estimation_agent(
                use_langchain=self.use_langchain,
                api_key=self.api_key
            )
            self.agents[rent_estimation_agent._get_agent_name()] = rent_estimation_agent
            
            # Additional agents would be registered here
            
            logger.info(f"Registered {len(self.agents)} agents: {', '.join(self.agents.keys())}")
        except Exception as e:
            logger.error(f"Error registering agents: {str(e)}")
            logger.info("Falling back to basic agents")
            
            # Fall back to basic agents if LangChain initialization fails
            market_data_agent = MarketDataSearchAgent()
            self.agents[market_data_agent._get_agent_name()] = market_data_agent
            
            rent_estimation_agent = RentEstimationAgent()
            self.agents[rent_estimation_agent._get_agent_name()] = rent_estimation_agent
            
            logger.info(f"Registered {len(self.agents)} fallback agents: {', '.join(self.agents.keys())}")
    
    async def execute_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow of agent calls based on configuration
        
        Args:
            workflow_config: Dictionary containing:
                - workflow_name: Name of the workflow
                - steps: List of workflow steps, each containing:
                    - agent: Name of the agent to call
                    - parameters: Parameters to pass to the agent
                    - depends_on: Optional list of step IDs this step depends on
                
        Returns:
            Dictionary with workflow results
        """
        if "steps" not in workflow_config:
            return {"success": False, "error": "No workflow steps provided"}
        
        workflow_name = workflow_config.get("workflow_name", "unnamed_workflow")
        logger.info(f"Starting workflow: {workflow_name}")
        
        # Initialize workflow context
        workflow_context = self.context.copy()
        workflow_context["workflow_name"] = workflow_name
        workflow_context["workflow_id"] = str(uuid.uuid4())
        workflow_context["start_time"] = datetime.datetime.now().isoformat()
        
        # Track step results
        step_results: Dict[str, Any] = {}
        
        # Build dependency graph
        dependency_graph = self._build_dependency_graph(workflow_config["steps"])
        
        # Execute workflow steps in order of dependencies
        completed_steps = set()
        remaining_steps = set(range(len(workflow_config["steps"])))
        
        while remaining_steps:
            # Find steps that can be executed (all dependencies satisfied)
            executable_steps = []
            for step_idx in remaining_steps:
                depends_on = dependency_graph.get(step_idx, set())
                if depends_on.issubset(completed_steps):
                    executable_steps.append(step_idx)
            
            if not executable_steps:
                return {"success": False, "error": "Circular dependency detected in workflow"}
            
            # Execute steps in parallel
            tasks = []
            for step_idx in executable_steps:
                step_config = workflow_config["steps"][step_idx]
                tasks.append(self._execute_step(step_idx, step_config, workflow_context, step_results))
            
            # Wait for all tasks to complete
            step_outputs = await asyncio.gather(*tasks)
            
            # Update step results
            for i, step_idx in enumerate(executable_steps):
                step_results[step_idx] = step_outputs[i]
                completed_steps.add(step_idx)
                remaining_steps.remove(step_idx)
                
                # Update workflow context with step results
                workflow_context["agent_results"][f"step_{step_idx}"] = step_outputs[i]
                
                # Also add direct access to the most recent agent results by agent name
                agent_name = workflow_config["steps"][step_idx].get("agent")
                if agent_name:
                    workflow_context[agent_name] = step_outputs[i].get("data", {})
        
        # Assemble final workflow result
        workflow_result = {
            "success": all(result.get("success", False) for result in step_results.values()),
            "workflow_name": workflow_name,
            "workflow_id": workflow_context["workflow_id"],
            "start_time": workflow_context["start_time"],
            "end_time": datetime.datetime.now().isoformat(),
            "steps": [
                {
                    "step_id": step_idx,
                    "agent": workflow_config["steps"][step_idx].get("agent"),
                    "success": step_results[step_idx].get("success", False),
                    "result": step_results[step_idx]
                }
                for step_idx in sorted(step_results.keys())
            ]
        }
        
        logger.info(f"Workflow {workflow_name} completed with success: {workflow_result['success']}")
        return workflow_result
    
    def _build_dependency_graph(self, steps: List[Dict[str, Any]]) -> Dict[int, set]:
        """
        Build a dependency graph from workflow steps
        
        Args:
            steps: List of workflow step configurations
            
        Returns:
            Dictionary mapping step index to set of dependency step indices
        """
        dependency_graph = {}
        
        for step_idx, step in enumerate(steps):
            depends_on = step.get("depends_on", [])
            
            # Convert dependency IDs to indices
            dependency_indices = set()
            for dep_id in depends_on:
                for i, s in enumerate(steps):
                    if s.get("id") == dep_id:
                        dependency_indices.add(i)
                        break
            
            dependency_graph[step_idx] = dependency_indices
        
        return dependency_graph
    
    async def _execute_step(
        self, 
        step_idx: int, 
        step_config: Dict[str, Any], 
        workflow_context: Dict[str, Any],
        step_results: Dict[int, Any]
    ) -> Dict[str, Any]:
        """
        Execute a single workflow step
        
        Args:
            step_idx: Index of the step
            step_config: Configuration for the step
            workflow_context: Current workflow context
            step_results: Dictionary of completed step results
            
        Returns:
            Result of the step execution
        """
        agent_name = step_config.get("agent")
        if not agent_name or agent_name not in self.agents:
            return {
                "success": False, 
                "error": f"Agent not found: {agent_name}",
                "step_idx": step_idx
            }
        
        # Get parameters
        parameters = step_config.get("parameters", {})
        
        # Get context enrichment from previous step results
        context_enrichment = {}
        if "enrich_context" in step_config:
            enrichment_mappings = step_config["enrich_context"]
            for dest_key, source_path in enrichment_mappings.items():
                parts = source_path.split(".")
                if len(parts) < 2:
                    continue
                
                step_id = int(parts[0].replace("step_", ""))
                if step_id not in step_results:
                    continue
                
                source = step_results[step_id]
                for part in parts[1:]:
                    if isinstance(source, dict) and part in source:
                        source = source[part]
                    else:
                        source = None
                        break
                
                if source is not None:
                    context_enrichment[dest_key] = source
        
        # Create step-specific context
        step_context = workflow_context.copy()
        step_context.update(context_enrichment)
        
        # Execute agent
        agent = self.agents[agent_name]
        logger.info(f"Executing step {step_idx} with agent {agent_name}")
        
        try:
            result = await agent.execute(parameters, step_context)
            agent.log_execution(parameters, result)
            
            # Add step metadata
            result["step_idx"] = step_idx
            result["agent"] = agent_name
            result["timestamp"] = datetime.datetime.now().isoformat()
            
            return result
        except Exception as e:
            logger.exception(f"Error executing step {step_idx} with agent {agent_name}")
            return {
                "success": False,
                "error": str(e),
                "step_idx": step_idx,
                "agent": agent_name,
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    async def execute_agent(self, agent_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single agent directly
        
        Args:
            agent_name: Name of the agent to execute
            parameters: Parameters to pass to the agent
            
        Returns:
            Result of the agent execution
        """
        if agent_name not in self.agents:
            return {"success": False, "error": f"Agent not found: {agent_name}"}
        
        agent = self.agents[agent_name]
        logger.info(f"Executing agent {agent_name} directly")
        
        try:
            result = await agent.execute(parameters, self.context)
            agent.log_execution(parameters, result)
            
            # Update context with agent result
            self.context["agent_results"][agent_name] = result
            self.context[agent_name] = result.get("data", {})
            
            return result
        except Exception as e:
            logger.exception(f"Error executing agent {agent_name}")
            return {"success": False, "error": str(e)}
    
    def get_available_agents(self) -> List[Dict[str, Any]]:
        """
        Get information about all available agents
        
        Returns:
            List of agent info dictionaries
        """
        return [agent.get_agent_info() for agent in self.agents.values()]
    
    def reset_context(self) -> None:
        """Reset the orchestrator context"""
        self.session_id = str(uuid.uuid4())
        self.context = {
            "session_id": self.session_id,
            "created_at": datetime.datetime.now().isoformat(),
            "agent_results": {}
        }
        logger.info(f"Orchestrator context reset with new session ID: {self.session_id}")
    
    def get_context(self) -> Dict[str, Any]:
        """Get the current orchestrator context"""
        return self.context
    
    def toggle_langchain(self, use_langchain: bool) -> bool:
        """
        Toggle between LangChain and basic agent implementations
        
        Args:
            use_langchain: Whether to use LangChain agents
            
        Returns:
            Success status of the operation
        """
        if use_langchain == self.use_langchain:
            return True  # Already in the requested state
        
        # Update setting
        self.use_langchain = use_langchain
        
        try:
            # Re-register agents with new setting
            self.agents = {}  # Clear existing agents
            self._register_agents()
            logger.info(f"Switched to {'LangChain' if use_langchain else 'basic'} agents")
            return True
        except Exception as e:
            logger.error(f"Error switching agent implementation: {str(e)}")
            return False