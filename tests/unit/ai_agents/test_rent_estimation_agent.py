"""
Unit tests for the RentEstimationAgent and LangChainRentEstimationAgent classes
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from typing import Dict, Any, List

from src.ai_agents.rent_estimation_agent import RentEstimationAgent, LangChainRentEstimationAgent
from src.ai_agents.tools import RentEstimationTool


class TestRentEstimationAgent:
    """Test cases for the RentEstimationAgent class"""
    
    def test_init(self):
        """Test RentEstimationAgent initialization"""
        agent = RentEstimationAgent()
        
        assert agent.name == "rent_estimation_agent"
        assert agent.feature_multipliers["balcony"] == 1.05
        assert agent.feature_multipliers["garden"] == 1.08
        assert agent.condition_multipliers["excellent"] == 1.15
        assert agent.condition_multipliers["poor"] == 0.8
        assert agent.location_categories["central"] == 1.2
    
    @pytest.mark.asyncio
    async def test_execute_logic_success(self):
        """Test successful execution of agent logic"""
        agent = RentEstimationAgent()
        parameters = {
            "location": "Berlin",
            "property_type": "apartment",
            "size_sqm": 75,
            "num_bedrooms": 2,
            "num_bathrooms": 1,
            "features": ["balcony", "elevator"],
            "condition": "good"
        }
        context = {}
        
        # Patch validate_input to return True
        with patch.object(agent, 'validate_input', return_value=asyncio.Future()) as mock_validate:
            mock_validate.return_value.set_result(True)
            
            result = await agent._execute_logic(parameters, context)
            
            assert result["success"] is True
            assert "estimated_rent" in result
            assert "rent_per_sqm" in result
            assert "rent_range" in result
            assert "comparable_properties" in result
            assert "confidence_level" in result
            assert "legal_limit_warning" in result
            assert "explanation" in result
            
            # Verify calculated values
            assert isinstance(result["estimated_rent"], float)
            assert isinstance(result["rent_per_sqm"], float)
            assert result["rent_per_sqm"] == result["estimated_rent"] / parameters["size_sqm"]
            assert isinstance(result["rent_range"], dict)
            assert "low" in result["rent_range"]
            assert "medium" in result["rent_range"]
            assert "high" in result["rent_range"]
            assert len(result["comparable_properties"]) >= 3
            assert 0.0 <= result["confidence_level"] <= 1.0
            assert isinstance(result["legal_limit_warning"], bool)
    
    @pytest.mark.asyncio
    async def test_execute_logic_with_market_data(self):
        """Test execution with market data from context"""
        agent = RentEstimationAgent()
        parameters = {
            "location": "Berlin",
            "property_type": "apartment",
            "size_sqm": 75,
            "condition": "good"
        }
        context = {
            "market_data": {
                "avg_rent_sqm": 18.5,
                "price_trend": "increasing"
            }
        }
        
        # Patch validate_input to return True
        with patch.object(agent, 'validate_input', return_value=asyncio.Future()) as mock_validate:
            mock_validate.return_value.set_result(True)
            
            # Spy on _get_default_rent_sqm to ensure it's not called
            with patch.object(agent, '_get_default_rent_sqm') as mock_default_rent:
                result = await agent._execute_logic(parameters, context)
                
                assert result["success"] is True
                assert not mock_default_rent.called  # Should use market data instead
                
                # Base rent should be derived from market data
                expected_base_rent = 75 * 18.5
                assert abs(result["estimated_rent"] / expected_base_rent - 1) < 0.3  # Within 30% of base (after adjustments)
    
    @pytest.mark.asyncio
    async def test_execute_logic_invalid_input(self):
        """Test agent logic with invalid input"""
        agent = RentEstimationAgent()
        parameters = {
            "location": "Berlin",
            # Missing required parameters
        }
        context = {}
        
        # Patch validate_input to return False
        with patch.object(agent, 'validate_input', return_value=asyncio.Future()) as mock_validate:
            mock_validate.return_value.set_result(False)
            
            result = await agent._execute_logic(parameters, context)
            
            assert result["success"] is False
            assert "error" in result
            assert "Invalid input parameters" in result["error"]
    
    def test_get_default_rent_sqm(self):
        """Test default rent per square meter calculation"""
        agent = RentEstimationAgent()
        
        # Test for different cities and property types
        berlin_apt = agent._get_default_rent_sqm("Berlin", "apartment")
        munich_apt = agent._get_default_rent_sqm("Munich", "apartment")
        berlin_house = agent._get_default_rent_sqm("Berlin", "house")
        
        assert munich_apt > berlin_apt  # Munich should be more expensive
        assert berlin_apt > berlin_house  # Apartments typically cost more per sqm than houses
        
        # Test with unknown city (should default to a base value)
        unknown_city = agent._get_default_rent_sqm("Unknown City", "apartment")
        assert unknown_city > 0  # Should still return a positive value
    
    def test_apply_adjustments(self):
        """Test rent adjustments based on property features"""
        agent = RentEstimationAgent()
        base_rent = 1000.0
        
        # Test size adjustments
        small_apt = agent._apply_adjustments(base_rent, 35, 1, 1, [], "average", "Berlin")
        large_apt = agent._apply_adjustments(base_rent, 150, 3, 2, [], "average", "Berlin")
        assert small_apt > base_rent  # Small apartments get premium
        assert large_apt < base_rent  # Large apartments get discount
        
        # Test feature adjustments
        no_features = agent._apply_adjustments(base_rent, 75, 2, 1, [], "average", "Berlin")
        with_features = agent._apply_adjustments(base_rent, 75, 2, 1, ["balcony", "garden"], "average", "Berlin")
        assert with_features > no_features  # Features should increase rent
        
        # Test condition adjustments
        poor_condition = agent._apply_adjustments(base_rent, 75, 2, 1, [], "poor", "Berlin")
        excellent_condition = agent._apply_adjustments(base_rent, 75, 2, 1, [], "excellent", "Berlin")
        assert excellent_condition > base_rent
        assert poor_condition < base_rent
        
        # Test location adjustments
        central = agent._apply_adjustments(base_rent, 75, 2, 1, [], "average", "Berlin Center")
        suburban = agent._apply_adjustments(base_rent, 75, 2, 1, [], "average", "Berlin Suburb")
        assert central > suburban
    
    def test_calculate_details_completeness(self):
        """Test calculation of property details completeness"""
        agent = RentEstimationAgent()
        
        # Test with all details
        complete_params = {
            "size_sqm": 75,
            "num_bedrooms": 2,
            "num_bathrooms": 1,
            "features": ["balcony", "garden", "parking"],
            "condition": "good"
        }
        complete_score = agent._calculate_details_completeness(complete_params)
        
        # Test with minimal details
        minimal_params = {
            "size_sqm": 75,
        }
        minimal_score = agent._calculate_details_completeness(minimal_params)
        
        # Test with some details
        partial_params = {
            "size_sqm": 75,
            "num_bedrooms": 2,
            "features": ["balcony"]
        }
        partial_score = agent._calculate_details_completeness(partial_params)
        
        assert complete_score > partial_score > minimal_score
        assert 0.0 <= minimal_score <= 1.0
        assert 0.0 <= partial_score <= 1.0
        assert 0.0 <= complete_score <= 1.0
    
    def test_calculate_rent_range(self):
        """Test calculation of rent ranges based on confidence"""
        agent = RentEstimationAgent()
        estimated_rent = 1000.0
        
        # Test with high confidence
        high_conf_range = agent._calculate_rent_range(estimated_rent, 0.9)
        assert high_conf_range["low"] < high_conf_range["medium"] < high_conf_range["high"]
        assert high_conf_range["medium"] == estimated_rent
        
        # Test with low confidence
        low_conf_range = agent._calculate_rent_range(estimated_rent, 0.3)
        assert low_conf_range["low"] < low_conf_range["medium"] < low_conf_range["high"]
        assert low_conf_range["medium"] == estimated_rent
        
        # Low confidence should have wider range
        high_conf_diff = high_conf_range["high"] - high_conf_range["low"]
        low_conf_diff = low_conf_range["high"] - low_conf_range["low"]
        assert low_conf_diff > high_conf_diff
    
    def test_check_legal_limits(self):
        """Test legal limit checks for regulated markets"""
        agent = RentEstimationAgent()
        
        # Test Berlin (regulated)
        berlin_result, berlin_limit = agent._check_legal_limits(
            2000.0, "Berlin", 75, "apartment", "good"
        )
        
        # Test Munich (not explicitly regulated in the agent)
        munich_result, munich_limit = agent._check_legal_limits(
            2000.0, "Munich", 75, "apartment", "good"
        )
        
        assert isinstance(berlin_result, bool)
        assert isinstance(berlin_limit, float)
        assert munich_result is False
        assert munich_limit == 0.0
        
        # Test with different property conditions
        poor_result, poor_limit = agent._check_legal_limits(
            2000.0, "Berlin", 75, "apartment", "poor"
        )
        excellent_result, excellent_limit = agent._check_legal_limits(
            2000.0, "Berlin", 75, "apartment", "excellent"
        )
        
        assert excellent_limit > poor_limit  # Better condition allows higher legal rent
    
    def test_generate_comparable_properties(self):
        """Test generation of comparable properties"""
        agent = RentEstimationAgent()
        location = "Berlin"
        property_type = "apartment"
        size_sqm = 75
        estimated_rent = 1200.0
        bedrooms = 2
        features = ["balcony", "elevator"]
        
        comparables = agent._generate_comparable_properties(
            location, property_type, size_sqm, estimated_rent, bedrooms, features
        )
        
        assert isinstance(comparables, list)
        assert len(comparables) >= 3
        
        # Check structure of first comparable
        comp = comparables[0]
        assert "id" in comp
        assert "address" in comp
        assert "size_sqm" in comp
        assert "bedrooms" in comp
        assert "rent" in comp
        assert "rent_per_sqm" in comp
        assert "features" in comp
        assert "distance_km" in comp
        
        # Verify rentals are roughly in the ballpark of the estimate
        for comp in comparables:
            assert 0.7 * estimated_rent <= comp["rent"] <= 1.3 * estimated_rent
            assert comp["rent_per_sqm"] == round(comp["rent"] / comp["size_sqm"], 2)
    
    def test_generate_explanation(self):
        """Test generation of rent explanation"""
        agent = RentEstimationAgent()
        base_rent = 900.0
        adjusted_rent = 1200.0
        features = ["balcony", "elevator"]
        condition = "good"
        location = "Berlin Center"
        bedrooms = 2
        size_sqm = 75
        legal_warning = False
        
        explanation = agent._generate_explanation(
            base_rent, adjusted_rent, features, condition, location, bedrooms, size_sqm, legal_warning
        )
        
        assert isinstance(explanation, str)
        assert f"{size_sqm} sqm" in explanation
        assert "Berlin Center" in explanation
        assert "€1200.00" in explanation
        assert "2 bedroom" in explanation
        assert "balcony" in explanation
        assert "elevator" in explanation
        assert "good" in explanation
        
        # Test with legal warning
        warning_explanation = agent._generate_explanation(
            base_rent, adjusted_rent, features, condition, location, bedrooms, size_sqm, True
        )
        
        assert "regulated market" in warning_explanation
    
    @pytest.mark.asyncio
    async def test_validate_input_valid(self):
        """Test input validation with valid parameters"""
        agent = RentEstimationAgent()
        parameters = {
            "location": "Berlin",
            "property_type": "apartment",
            "size_sqm": 75
        }
        
        result = await agent.validate_input(parameters)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_input_missing_param(self):
        """Test input validation with missing parameter"""
        agent = RentEstimationAgent()
        parameters = {
            "location": "Berlin",
            "property_type": "apartment"
            # Missing size_sqm
        }
        
        result = await agent.validate_input(parameters)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_input_invalid_property_type(self):
        """Test input validation with invalid property type"""
        agent = RentEstimationAgent()
        parameters = {
            "location": "Berlin",
            "property_type": "invalid_type",  # Not a valid property type
            "size_sqm": 75
        }
        
        result = await agent.validate_input(parameters)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_input_invalid_size(self):
        """Test input validation with invalid size"""
        agent = RentEstimationAgent()
        parameters = {
            "location": "Berlin",
            "property_type": "apartment",
            "size_sqm": -10  # Negative size
        }
        
        result = await agent.validate_input(parameters)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_input_invalid_condition(self):
        """Test input validation with invalid condition"""
        agent = RentEstimationAgent()
        parameters = {
            "location": "Berlin",
            "property_type": "apartment",
            "size_sqm": 75,
            "condition": "invalid_condition"  # Not a valid condition
        }
        
        result = await agent.validate_input(parameters)
        
        assert result is False
    
    def test_get_confidence_level(self):
        """Test confidence level calculation"""
        agent = RentEstimationAgent()
        
        # Test high confidence case
        high_conf_data = {
            "has_market_data": True,
            "property_details_completeness": 0.9,
            "location_specificity": 0.95,
            "property_type_match": True
        }
        high_conf = agent.get_confidence_level(high_conf_data)
        
        # Test low confidence case
        low_conf_data = {
            "has_market_data": False,
            "property_details_completeness": 0.3,
            "location_specificity": 0.4,
            "property_type_match": False
        }
        low_conf = agent.get_confidence_level(low_conf_data)
        
        assert high_conf > 0.7  # Should be high confidence
        assert low_conf < 0.5  # Should be low confidence
        assert 0.0 <= low_conf <= 1.0
        assert 0.0 <= high_conf <= 1.0


@pytest.mark.asyncio
class TestLangChainRentEstimationAgent:
    """Test cases for the LangChainRentEstimationAgent class"""
    
    @pytest.fixture
    def mock_api_key(self):
        """Mock API key for testing"""
        return "test-api-key-12345"
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM"""
        mock = MagicMock()
        mock._call = AsyncMock(return_value="Rent estimation result")
        return mock
    
    @pytest.fixture
    def agent(self, mock_api_key):
        """Create a patched LangChainRentEstimationAgent"""
        with patch('langchain.chat_models.ChatOpenAI') as mock_chat_openai, \
             patch('src.ai_agents.rent_estimation_agent.RentEstimationTool') as mock_rent_tool:
            
            # Mock the LLM
            mock_llm = MagicMock()
            mock_chat_openai.return_value = mock_llm
            
            # Mock the tool
            mock_tool = MagicMock(spec=RentEstimationTool)
            mock_rent_tool.return_value = mock_tool
            
            # Create the agent
            agent = LangChainRentEstimationAgent(api_key=mock_api_key)
            
            # Replace agent_executor.arun with a mock to avoid actual execution
            mock_executor = MagicMock()
            mock_executor.arun = AsyncMock(return_value="The estimated monthly rent for the apartment is €1,200.")
            agent.create_agent_executor = MagicMock(return_value=mock_executor)
            
            yield agent
    
    def test_init(self, agent, mock_api_key):
        """Test initialization of the agent"""
        assert agent.api_key == mock_api_key
        assert agent.name == "langchain_rent_estimation_agent"
        assert "LangChain agent for estimating" in agent.description
    
    async def test_execute_logic_success(self, agent):
        """Test successful execution of agent logic"""
        parameters = {
            "location": "Berlin",
            "property_type": "apartment",
            "size_sqm": 75,
            "num_bedrooms": 2,
            "features": ["balcony", "elevator"],
            "condition": "good"
        }
        context = {}
        
        result = await agent._execute_logic(parameters, context)
        
        assert result["success"] is True
        assert result["location"] == "Berlin"
        assert result["property_type"] == "apartment"
        assert result["size_sqm"] == 75
        assert "analysis" in result
        assert "€1,200" in result["analysis"]
        assert result["estimated_rent"] == 1200.0  # Extracted from the analysis text
        assert "timestamp" in result
    
    async def test_execute_logic_exception(self, agent):
        """Test agent logic when an exception occurs"""
        parameters = {
            "location": "Berlin",
            "property_type": "apartment",
            "size_sqm": 75
        }
        context = {}
        
        # Set up the executor to raise an exception
        mock_executor = MagicMock()
        mock_executor.arun = AsyncMock(side_effect=ValueError("Test error"))
        agent.create_agent_executor = MagicMock(return_value=mock_executor)
        
        result = await agent._execute_logic(parameters, context)
        
        assert result["success"] is False
        assert "error" in result
        assert "Test error" in result["error"]
        assert result["location"] == "Berlin"
        assert result["property_type"] == "apartment"
        assert result["size_sqm"] == 75
    
    def test_get_agent_name(self, agent):
        """Test getting the agent name"""
        assert agent._get_agent_name() == "langchain_rent_estimation_agent"
    
    def test_get_agent_description(self, agent):
        """Test getting the agent description"""
        description = agent._get_agent_description()
        assert "LangChain agent" in description
        assert "rental income" in description