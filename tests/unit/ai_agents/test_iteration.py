"""
Unit tests for agent iteration functionality
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from src.ai_agents.base_agent import BaseAgent


class TestAgentIteration:
    """Test cases for the agent iteration functionality"""
    
    class IterativeAgent(BaseAgent):
        """Agent implementation that supports iteration"""
        
        def __init__(self):
            super().__init__()
            self.iterations = 0
            self.max_iterations = 3
            self.should_continue = True
        
        def _get_agent_name(self) -> str:
            """Return the agent name"""
            return "iterative_agent"
        
        def _get_agent_description(self) -> str:
            """Return the agent description"""
            return "Test agent supporting iteration"
        
        async def _execute_logic(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
            """Implement the abstract method with iteration support"""
            self.iterations += 1
            
            # Check if we should continue iterating
            continue_param = parameters.get("continue_iteration")
            if continue_param is not None:
                if continue_param.lower() in ["yes", "true", "y", "continue"]:
                    self.should_continue = True
                elif continue_param.lower() in ["no", "false", "n", "stop"]:
                    self.should_continue = False
            
            # If max iterations reached, don't continue regardless
            if self.iterations >= self.max_iterations:
                self.should_continue = False
            
            result = {
                "success": True,
                "iteration": self.iterations,
                "should_continue": self.should_continue,
                "parameters": parameters
            }
            
            # Include message asking if user wants to continue
            if self.should_continue:
                result["message"] = "Continue to iterate?"
            else:
                result["message"] = "Iteration complete."
            
            return result
    
    @pytest.fixture
    def agent(self):
        """Create an IterativeAgent instance for testing"""
        return self.IterativeAgent()
    
    @pytest.mark.asyncio
    async def test_continue_iteration(self, agent):
        """Test the agent correctly continues iteration when requested"""
        # First execution
        result1 = await agent.execute({"continue_iteration": "yes"}, {})
        assert result1["success"] is True
        assert result1["iteration"] == 1
        assert result1["should_continue"] is True
        assert "Continue to iterate?" in result1["message"]
        
        # Second execution with continue
        result2 = await agent.execute({"continue_iteration": "continue"}, {})
        assert result2["iteration"] == 2
        assert result2["should_continue"] is True
        assert "Continue to iterate?" in result2["message"]
        
        # Third execution with continue
        result3 = await agent.execute({"continue_iteration": "yes"}, {})
        assert result3["iteration"] == 3
        assert result3["should_continue"] is False  # Max iterations reached
        assert "Iteration complete" in result3["message"]
    
    @pytest.mark.asyncio
    async def test_stop_iteration(self, agent):
        """Test the agent correctly stops iteration when requested"""
        # First execution
        result1 = await agent.execute({}, {})
        assert result1["success"] is True
        assert result1["iteration"] == 1
        assert result1["should_continue"] is True
        
        # Second execution with stop
        result2 = await agent.execute({"continue_iteration": "no"}, {})
        assert result2["iteration"] == 2
        assert result2["should_continue"] is False
        assert "Iteration complete" in result2["message"]
        
        # Confirm it stays stopped even if continue is requested
        result3 = await agent.execute({"continue_iteration": "yes"}, {})
        assert result3["iteration"] == 3
        assert result3["should_continue"] is False
    
    @pytest.mark.asyncio
    async def test_max_iterations(self, agent):
        """Test the agent respects maximum iteration limit"""
        # Run for max iterations
        for i in range(agent.max_iterations):
            result = await agent.execute({"continue_iteration": "yes"}, {})
            assert result["iteration"] == i + 1
            
            # Last iteration should indicate no more iterations
            if i == agent.max_iterations - 1:
                assert result["should_continue"] is False
                assert "Iteration complete" in result["message"]
            else:
                assert result["should_continue"] is True
                assert "Continue to iterate?" in result["message"]
        
        # Additional execution should not increment iteration counter
        final_result = await agent.execute({"continue_iteration": "yes"}, {})
        assert final_result["iteration"] == agent.max_iterations  # Should not increase
        assert final_result["should_continue"] is False