"""
Unit tests for the BaseAgent class
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from typing import Dict, Any

from src.ai_agents.base_agent import BaseAgent


class TestBaseAgent:
    """Test cases for the BaseAgent class"""
    
    class ConcreteAgent(BaseAgent):
        """Concrete implementation of the abstract BaseAgent class for testing"""
        
        def __init__(self):
            super().__init__()
            self.name = "test_agent"
            self.description = "Test agent implementation"
            self.version = "1.0.0"
        
        async def _execute_logic(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
            """Implement the abstract method for testing"""
            # Simply echo back the parameters
            return {
                "success": True,
                "result": "Success",
                "parameters": parameters
            }
        
        async def validate_input(self, parameters: Dict[str, Any]) -> bool:
            """Implement input validation for testing"""
            # Example validation: require "test_param" parameter
            return "test_param" in parameters
        
        def _get_agent_name(self) -> str:
            """Return the agent name"""
            return "test_agent"
        
        def _get_agent_description(self) -> str:
            """Return the agent description"""
            return "Test agent implementation"
    
    @pytest.fixture
    def agent(self):
        """Create a ConcreteAgent instance for testing"""
        return self.ConcreteAgent()
    
    def test_init(self, agent):
        """Test initialization of the agent"""
        assert agent.name == "test_agent"
        assert agent.description == "Test agent implementation"
        assert agent.version == "1.0.0"
        assert agent.execution_count == 0
        assert isinstance(agent.creation_time, datetime)
    
    @pytest.mark.asyncio
    async def test_execute_success(self, agent):
        """Test successful execution of agent"""
        parameters = {"test_param": "test_value"}
        context = {"context_key": "context_value"}
        
        result = await agent.execute(parameters, context)
        
        assert result["success"] is True
        assert result["result"] == "Success"
        assert result["parameters"] == parameters
        assert "execution_time" in result
        assert "timestamp" in result
        assert agent.execution_count == 1
    
    @pytest.mark.asyncio
    async def test_execute_with_validation_failure(self, agent):
        """Test execution with validation failure"""
        parameters = {}  # Missing required test_param
        context = {}
        
        result = await agent.execute(parameters, context)
        
        assert result["success"] is False
        assert "error" in result
        assert "validation failed" in result["error"]
        assert "execution_time" in result
        assert "timestamp" in result
        assert agent.execution_count == 1  # Still increments on validation failure
    
    @pytest.mark.asyncio
    async def test_execute_with_exception(self, agent):
        """Test execution when an exception occurs"""
        parameters = {"test_param": "test_value"}
        context = {}
        
        # Patch _execute_logic to raise an exception
        with patch.object(agent, '_execute_logic', side_effect=ValueError("Test error")):
            result = await agent.execute(parameters, context)
            
            assert result["success"] is False
            assert "error" in result
            assert "Test error" in result["error"]
            assert "execution_time" in result
            assert "timestamp" in result
            assert agent.execution_count == 1  # Still increments on exception
    
    def test_get_agent_info(self, agent):
        """Test getting agent information"""
        # Execute once to increment execution count
        asyncio.run(agent.execute({"test_param": "value"}, {}))
        
        info = agent.get_agent_info()
        
        assert info["name"] == agent.name
        assert info["description"] == agent.description
        assert info["version"] == agent.version
        assert info["execution_count"] == 1
        assert "creation_time" in info
        assert "type" in info
        assert info["type"] == "BaseAgent"
    
    @pytest.mark.asyncio
    async def test_validate_input_method(self, agent):
        """Test the validate_input method"""
        valid_params = {"test_param": "value"}
        invalid_params = {}
        
        valid_result = await agent.validate_input(valid_params)
        invalid_result = await agent.validate_input(invalid_params)
        
        assert valid_result is True
        assert invalid_result is False