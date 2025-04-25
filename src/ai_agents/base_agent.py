"""
Base agent class that all agents will inherit from
"""
import abc
import asyncio
import datetime
import logging
import uuid
from typing import Dict, Any, List, Optional, Union, Callable

# LangChain imports
from langchain.agents import AgentExecutor, BaseSingleActionAgent
from langchain.schema import AgentAction, AgentFinish
from langchain.tools import BaseTool
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms.base import BaseLLM

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAgent(abc.ABC):
    """
    Abstract base class for all AI agents in the system
    
    This class defines the interface that all agents must implement
    and provides common functionality for agent execution and logging.
    """
    
    def __init__(self):
        """Initialize the base agent with required properties"""
        self.name = self._get_agent_name()
        self.description = self._get_agent_description()
        self.version = "1.0.0"
        self.execution_history: List[Dict[str, Any]] = []
        self.iteration_count = 0
        self.max_iterations = 10  # Default maximum iterations
        self.should_continue = True  # Flag to track if iterations should continue
        logger.info(f"Initialized agent: {self.name}")
    
    @abc.abstractmethod
    def _get_agent_name(self) -> str:
        """
        Get the name of the agent
        
        This must be implemented by subclasses to provide a unique name
        """
        pass
    
    @abc.abstractmethod
    def _get_agent_description(self) -> str:
        """
        Get the description of the agent
        
        This must be implemented by subclasses to describe the agent's purpose
        """
        pass
    
    @abc.abstractmethod
    async def _execute_logic(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's core logic
        
        This must be implemented by subclasses to perform the agent's specific task
        
        Args:
            parameters: Parameters specific to this agent execution
            context: Shared context from the orchestrator
            
        Returns:
            Dictionary with execution results
        """
        pass
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent with parameters and context
        
        This is the main entry point for agent execution, which handles common
        operations like timing, error handling, and result formatting
        
        Args:
            parameters: Parameters specific to this agent execution
            context: Shared context from the orchestrator
            
        Returns:
            Dictionary with execution results
        """
        execution_id = str(uuid.uuid4())
        start_time = datetime.datetime.now()
        
        # Check if this is an iteration request
        continue_param = parameters.get("continue_iteration")
        if continue_param is not None:
            # Process continue_iteration parameter
            if continue_param.lower() in ["yes", "true", "y", "continue"]:
                self.should_continue = True
            elif continue_param.lower() in ["no", "false", "n", "stop"]:
                self.should_continue = False
                
            # If a prior iteration indicated to stop, don't reset it
            if not self.should_continue:
                logger.info(f"Agent {self.name} iteration stopped by user")
        
        # Increment iteration counter
        self.iteration_count += 1
        
        # Check if we've reached max iterations
        if self.iteration_count >= self.max_iterations:
            logger.info(f"Agent {self.name} reached maximum iterations ({self.max_iterations})")
            self.should_continue = False
        
        logger.info(f"Starting execution of agent {self.name} (iteration {self.iteration_count}) with ID {execution_id}")
        
        try:
            # Execute the agent's logic
            result = await self._execute_logic(parameters, context)
            
            # Add metadata
            end_time = datetime.datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Ensure result is a dictionary with required fields
            if not isinstance(result, dict):
                result = {"data": result, "success": True}
            if "success" not in result:
                result["success"] = True
                
            # Add execution metadata
            result.update({
                "execution_id": execution_id,
                "agent_name": self.name,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "execution_time_seconds": execution_time,
                "parameters": parameters,  # Include the original parameters
                "iteration": self.iteration_count,
                "should_continue": self.should_continue
            })
            
            # If agent should continue, add a prompt for the next iteration
            if self.should_continue:
                result["message"] = "Continue to iterate?"
            else:
                result["message"] = "Iteration complete."
            
            logger.info(f"Completed execution of agent {self.name} iteration {self.iteration_count} in {execution_time:.2f}s")
            
            # Log the execution
            self.log_execution(parameters, result)
            
            return result
            
        except Exception as e:
            # Handle exceptions and return error information
            end_time = datetime.datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            error_result = {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "execution_id": execution_id,
                "agent_name": self.name,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "execution_time_seconds": execution_time,
                "parameters": parameters,  # Include the original parameters
                "iteration": self.iteration_count,
                "should_continue": False  # Don't continue after an error
            }
            
            # Log the execution
            self.log_execution(parameters, error_result)
            
            logger.error(f"Error executing agent {self.name} iteration {self.iteration_count}: {str(e)}")
            return error_result
    
    def reset_iteration(self) -> None:
        """
        Reset the iteration counter and continue flag
        
        This allows an agent to start a fresh iteration sequence
        """
        self.iteration_count = 0
        self.should_continue = True
        logger.info(f"Reset iteration state for agent {self.name}")
    
    def set_max_iterations(self, max_iterations: int) -> None:
        """
        Set the maximum number of iterations for this agent
        
        Args:
            max_iterations: Maximum number of iterations
        """
        if max_iterations <= 0:
            raise ValueError("Maximum iterations must be greater than zero")
        
        self.max_iterations = max_iterations
        logger.info(f"Set max iterations for agent {self.name} to {max_iterations}")
    
    def log_execution(self, parameters: Dict[str, Any], result: Dict[str, Any]) -> None:
        """
        Log an execution to the agent's history
        
        Args:
            parameters: Parameters passed to the agent
            result: Result returned by the agent
        """
        # Store execution history (limited to last 100 executions)
        self.execution_history.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "parameters": parameters,
            "result_summary": {
                "success": result.get("success", False),
                "execution_id": result.get("execution_id", ""),
                "execution_time_seconds": result.get("execution_time_seconds", 0),
                "iteration": result.get("iteration", 0),
                "should_continue": result.get("should_continue", False),
                "error": result.get("error", None) if not result.get("success", False) else None
            }
        })
        
        # Keep only the last 100 executions
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about this agent
        
        Returns:
            Dictionary with agent information
        """
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "execution_count": len(self.execution_history),
            "iteration_count": self.iteration_count,
            "max_iterations": self.max_iterations,
            "should_continue": self.should_continue,
            "last_execution": self.execution_history[-1] if self.execution_history else None
        }
    
    def get_execution_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get the execution history for this agent
        
        Args:
            limit: Optional limit on the number of history items to return
            
        Returns:
            List of execution history entries
        """
        if limit is None or limit <= 0:
            return self.execution_history
        return self.execution_history[-limit:]


class LangChainAgent(BaseSingleActionAgent, BaseAgent):
    """
    Base class for agents implemented using LangChain
    
    This class extends both BaseSingleActionAgent from LangChain and our own BaseAgent,
    providing compatibility with the LangChain ecosystem while maintaining our existing
    agent infrastructure.
    """
    
    def __init__(
        self,
        llm: BaseLLM,
        tools: List[BaseTool],
        prompt_template: str,
        input_variables: List[str],
        output_parser: Optional[Callable] = None
    ):
        """
        Initialize a LangChain-based agent
        
        Args:
            llm: The language model to use
            tools: List of tools available to the agent
            prompt_template: Template string for the agent's prompt
            input_variables: List of input variables for the prompt template
            output_parser: Optional function to parse the LLM output
        """
        BaseAgent.__init__(self)
        
        self.tools = tools
        self.llm = llm
        
        # Create a prompt template for the agent
        self.prompt = PromptTemplate(
            template=prompt_template,
            input_variables=input_variables
        )
        
        # Create an LLM chain for the agent
        self.llm_chain = LLMChain(
            llm=llm,
            prompt=self.prompt
        )
        
        self.output_parser = output_parser
        logger.info(f"Initialized LangChain agent: {self.name} with {len(tools)} tools")
    
    @property
    def input_keys(self) -> List[str]:
        """Return the expected input keys."""
        return self.prompt.input_variables
    
    def plan(
        self, intermediate_steps: List[tuple], **kwargs: Any
    ) -> Union[AgentAction, AgentFinish]:
        """
        Given input, decided what to do.
        
        Args:
            intermediate_steps: Steps the LLM has taken to date, 
                along with observations
            **kwargs: User inputs

        Returns:
            Action specifying what tool to use.
        """
        inputs = {**kwargs}
        if intermediate_steps:
            # Add intermediate steps to input if they exist
            inputs["intermediate_steps"] = intermediate_steps

        # Call the LLM to get the next action
        output = self.llm_chain.run(**inputs)
        
        # Parse the output to get the next action
        if self.output_parser:
            parsed_output = self.output_parser(output)
        else:
            # Simple default parser that assumes the output is the tool name
            # followed by the tool input in the format "Tool: <tool>\nInput: <input>"
            try:
                tool_line, input_line = output.strip().split("\n", 1)
                tool = tool_line.split(":", 1)[1].strip()
                tool_input = input_line.split(":", 1)[1].strip()
                return AgentAction(tool=tool, tool_input=tool_input, log=output)
            except Exception:
                # If parsing fails, assume the LLM has finished
                return AgentFinish(return_values={"output": output}, log=output)
        
        return parsed_output
    
    async def aplan(
        self, intermediate_steps: List[tuple], **kwargs: Any
    ) -> Union[AgentAction, AgentFinish]:
        """Async version of plan method."""
        return self.plan(intermediate_steps, **kwargs)
    
    def create_agent_executor(self, **kwargs) -> AgentExecutor:
        """
        Create an AgentExecutor for this agent
        
        Args:
            **kwargs: Additional arguments to pass to AgentExecutor
            
        Returns:
            AgentExecutor instance
        """
        return AgentExecutor.from_agent_and_tools(
            agent=self,
            tools=self.tools,
            verbose=True,
            **kwargs
        )