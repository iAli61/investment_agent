"""
Unit tests for the Orchestrator class
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from typing import Dict, Any, List

from src.ai_agents.orchestrator import Orchestrator
from src.ai_agents.base_agent import BaseAgent
from src.ai_agents.market_data_agent import MarketDataSearchAgent
from src.ai_agents.rent_estimation_agent import RentEstimationAgent


class TestOrchestrator:
    """Test cases for the Orchestrator class"""
    
    @pytest.fixture
    def mock_market_agent(self):
        """Create a mock market data agent"""
        mock = MagicMock(spec=BaseAgent)
        mock.name = "market_data_search_agent"
        mock._get_agent_name.return_value = "market_data_search_agent"
        mock.execute = AsyncMock(return_value={"success": True, "data": {"avg_price_sqm": 5000.0}})
        mock.get_agent_info.return_value = {
            "name": "market_data_search_agent",
            "description": "Market data search agent",
            "version": "1.0.0",
            "execution_count": 0
        }
        return mock
    
    @pytest.fixture
    def mock_rent_agent(self):
        """Create a mock rent estimation agent"""
        mock = MagicMock(spec=BaseAgent)
        mock.name = "rent_estimation_agent"
        mock._get_agent_name.return_value = "rent_estimation_agent"
        mock.execute = AsyncMock(return_value={"success": True, "data": {"estimated_rent": 1500.0}})
        mock.get_agent_info.return_value = {
            "name": "rent_estimation_agent",
            "description": "Rent estimation agent",
            "version": "1.0.0",
            "execution_count": 0
        }
        return mock
    
    @pytest.fixture
    def orchestrator_with_mocks(self, mock_market_agent, mock_rent_agent):
        """Create an orchestrator with mock agents"""
        with patch('src.ai_agents.orchestrator.create_market_data_agent', return_value=mock_market_agent), \
             patch('src.ai_agents.orchestrator.create_rent_estimation_agent', return_value=mock_rent_agent):
            orchestrator = Orchestrator(use_langchain=False)
            return orchestrator
    
    def test_init(self, orchestrator_with_mocks):
        """Test Orchestrator initialization"""
        orchestrator = orchestrator_with_mocks
        
        assert orchestrator.use_langchain is False
        assert isinstance(orchestrator.agents, dict)
        assert len(orchestrator.agents) == 2
        assert "market_data_search_agent" in orchestrator.agents
        assert "rent_estimation_agent" in orchestrator.agents
        assert isinstance(orchestrator.session_id, str)
        assert isinstance(orchestrator.context, dict)
        assert "session_id" in orchestrator.context
        assert "created_at" in orchestrator.context
        assert "agent_results" in orchestrator.context
    
    def test_init_with_langchain(self):
        """Test Orchestrator initialization with LangChain"""
        with patch('src.ai_agents.orchestrator.create_market_data_agent') as mock_market_factory, \
             patch('src.ai_agents.orchestrator.create_rent_estimation_agent') as mock_rent_factory:
            
            mock_market = MagicMock()
            mock_market._get_agent_name.return_value = "langchain_market_data_agent"
            mock_market_factory.return_value = mock_market
            
            mock_rent = MagicMock()
            mock_rent._get_agent_name.return_value = "langchain_rent_estimation_agent"
            mock_rent_factory.return_value = mock_rent
            
            orchestrator = Orchestrator(use_langchain=True, api_key="test-key")
            
            assert orchestrator.use_langchain is True
            assert "langchain_market_data_agent" in orchestrator.agents
            assert "langchain_rent_estimation_agent" in orchestrator.agents
            assert len(orchestrator.agents) == 2
    
    def test_get_available_agents(self, orchestrator_with_mocks):
        """Test getting available agents"""
        orchestrator = orchestrator_with_mocks
        
        agents = orchestrator.get_available_agents()
        
        assert isinstance(agents, list)
        assert len(agents) == 2
        
        # Check the first agent
        agent_info = agents[0]
        assert "name" in agent_info
        assert "description" in agent_info
        assert "version" in agent_info
        assert "execution_count" in agent_info
    
    def test_reset_context(self, orchestrator_with_mocks):
        """Test resetting the context"""
        orchestrator = orchestrator_with_mocks
        
        # Add some data to the context
        old_session_id = orchestrator.session_id
        orchestrator.context["test_key"] = "test_value"
        orchestrator.context["agent_results"]["test_agent"] = {"result": "test"}
        
        # Reset the context
        orchestrator.reset_context()
        
        # Check that the context has been reset
        assert orchestrator.session_id != old_session_id
        assert "test_key" not in orchestrator.context
        assert "agent_results" in orchestrator.context
        assert orchestrator.context["agent_results"] == {}
    
    def test_get_context(self, orchestrator_with_mocks):
        """Test getting the context"""
        orchestrator = orchestrator_with_mocks
        
        context = orchestrator.get_context()
        
        assert isinstance(context, dict)
        assert "session_id" in context
        assert context["session_id"] == orchestrator.session_id
    
    def test_toggle_langchain(self, orchestrator_with_mocks):
        """Test toggling between LangChain and basic agents"""
        orchestrator = orchestrator_with_mocks
        
        with patch('src.ai_agents.orchestrator.create_market_data_agent') as mock_market_factory, \
             patch('src.ai_agents.orchestrator.create_rent_estimation_agent') as mock_rent_factory:
            
            # Mock returning different agents for LangChain
            mock_market = MagicMock()
            mock_market._get_agent_name.return_value = "langchain_market_data_agent"
            mock_market_factory.return_value = mock_market
            
            mock_rent = MagicMock()
            mock_rent._get_agent_name.return_value = "langchain_rent_estimation_agent"
            mock_rent_factory.return_value = mock_rent
            
            # Toggle to LangChain
            result = orchestrator.toggle_langchain(True)
            
            assert result is True
            assert orchestrator.use_langchain is True
            assert "langchain_market_data_agent" in orchestrator.agents
            assert "langchain_rent_estimation_agent" in orchestrator.agents
            
            # Toggle back to basic
            mock_market_basic = MagicMock()
            mock_market_basic._get_agent_name.return_value = "market_data_search_agent"
            mock_market_factory.return_value = mock_market_basic
            
            mock_rent_basic = MagicMock()
            mock_rent_basic._get_agent_name.return_value = "rent_estimation_agent"
            mock_rent_factory.return_value = mock_rent_basic
            
            result = orchestrator.toggle_langchain(False)
            
            assert result is True
            assert orchestrator.use_langchain is False
            assert "market_data_search_agent" in orchestrator.agents
            assert "rent_estimation_agent" in orchestrator.agents
    
    @pytest.mark.asyncio
    async def test_execute_agent(self, orchestrator_with_mocks, mock_market_agent):
        """Test executing a single agent"""
        orchestrator = orchestrator_with_mocks
        
        parameters = {
            "location": "Berlin",
            "property_type": "apartment"
        }
        
        result = await orchestrator.execute_agent("market_data_search_agent", parameters)
        
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["avg_price_sqm"] == 5000.0
        
        # Check that the agent was called with the right parameters
        mock_market_agent.execute.assert_called_once()
        args, kwargs = mock_market_agent.execute.call_args
        assert args[0] == parameters
        assert args[1] == orchestrator.context
        
        # Check that the result was added to the context
        assert "market_data_search_agent" in orchestrator.context
        assert orchestrator.context["market_data_search_agent"] == result["data"]
        assert "market_data_search_agent" in orchestrator.context["agent_results"]
    
    @pytest.mark.asyncio
    async def test_execute_agent_not_found(self, orchestrator_with_mocks):
        """Test executing an agent that doesn't exist"""
        orchestrator = orchestrator_with_mocks
        
        result = await orchestrator.execute_agent("nonexistent_agent", {})
        
        assert result["success"] is False
        assert "error" in result
        assert "Agent not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_execute_agent_exception(self, orchestrator_with_mocks, mock_rent_agent):
        """Test executing an agent that raises an exception"""
        orchestrator = orchestrator_with_mocks
        
        # Set the agent to raise an exception
        mock_rent_agent.execute = AsyncMock(side_effect=ValueError("Test error"))
        
        result = await orchestrator.execute_agent("rent_estimation_agent", {})
        
        assert result["success"] is False
        assert "error" in result
        assert "Test error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_execute_workflow_simple(self, orchestrator_with_mocks):
        """Test executing a simple workflow"""
        orchestrator = orchestrator_with_mocks
        
        workflow_config = {
            "workflow_name": "test_workflow",
            "steps": [
                {
                    "id": "step1",
                    "agent": "market_data_search_agent",
                    "parameters": {
                        "location": "Berlin",
                        "property_type": "apartment"
                    }
                },
                {
                    "id": "step2",
                    "agent": "rent_estimation_agent",
                    "parameters": {
                        "location": "Berlin",
                        "property_type": "apartment",
                        "size_sqm": 75
                    }
                }
            ]
        }
        
        result = await orchestrator.execute_workflow(workflow_config)
        
        assert result["success"] is True
        assert result["workflow_name"] == "test_workflow"
        assert "workflow_id" in result
        assert "start_time" in result
        assert "end_time" in result
        assert "steps" in result
        assert len(result["steps"]) == 2
        
        # Check the first step result
        step1 = result["steps"][0]
        assert step1["step_id"] == 0
        assert step1["agent"] == "market_data_search_agent"
        assert step1["success"] is True
        
        # Check the second step result
        step2 = result["steps"][1]
        assert step2["step_id"] == 1
        assert step2["agent"] == "rent_estimation_agent"
        assert step2["success"] is True
    
    @pytest.mark.asyncio
    async def test_execute_workflow_with_dependencies(self, orchestrator_with_mocks):
        """Test executing a workflow with dependencies between steps"""
        orchestrator = orchestrator_with_mocks
        
        workflow_config = {
            "workflow_name": "dependency_workflow",
            "steps": [
                {
                    "id": "market_data",
                    "agent": "market_data_search_agent",
                    "parameters": {
                        "location": "Berlin",
                        "property_type": "apartment"
                    }
                },
                {
                    "id": "rent_estimation",
                    "agent": "rent_estimation_agent",
                    "parameters": {
                        "location": "Berlin",
                        "property_type": "apartment",
                        "size_sqm": 75
                    },
                    "depends_on": ["market_data"],
                    "enrich_context": {
                        "market_data": "step_0.data"
                    }
                }
            ]
        }
        
        result = await orchestrator.execute_workflow(workflow_config)
        
        assert result["success"] is True
        assert len(result["steps"]) == 2
        
        # The second step should have been executed after the first
        assert result["steps"][0]["step_id"] == 0
        assert result["steps"][1]["step_id"] == 1
    
    @pytest.mark.asyncio
    async def test_execute_workflow_invalid_agent(self, orchestrator_with_mocks):
        """Test workflow with an invalid agent"""
        orchestrator = orchestrator_with_mocks
        
        workflow_config = {
            "workflow_name": "invalid_agent_workflow",
            "steps": [
                {
                    "id": "step1",
                    "agent": "nonexistent_agent",
                    "parameters": {}
                }
            ]
        }
        
        result = await orchestrator.execute_workflow(workflow_config)
        
        assert result["success"] is False
        assert result["steps"][0]["success"] is False
        assert "Agent not found" in result["steps"][0]["result"]["error"]
    
    @pytest.mark.asyncio
    async def test_execute_workflow_circular_dependency(self, orchestrator_with_mocks):
        """Test workflow with a circular dependency"""
        orchestrator = orchestrator_with_mocks
        
        workflow_config = {
            "workflow_name": "circular_workflow",
            "steps": [
                {
                    "id": "step1",
                    "agent": "market_data_search_agent",
                    "parameters": {},
                    "depends_on": ["step2"]
                },
                {
                    "id": "step2",
                    "agent": "rent_estimation_agent",
                    "parameters": {},
                    "depends_on": ["step1"]
                }
            ]
        }
        
        result = await orchestrator.execute_workflow(workflow_config)
        
        assert result["success"] is False
        assert "error" in result
        assert "Circular dependency" in result["error"]
    
    @pytest.mark.asyncio
    async def test_execute_workflow_no_steps(self, orchestrator_with_mocks):
        """Test workflow with no steps"""
        orchestrator = orchestrator_with_mocks
        
        workflow_config = {
            "workflow_name": "empty_workflow"
            # No steps key
        }
        
        result = await orchestrator.execute_workflow(workflow_config)
        
        assert result["success"] is False
        assert "error" in result
        assert "No workflow steps provided" in result["error"]