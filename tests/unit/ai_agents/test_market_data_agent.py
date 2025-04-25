"""
Unit tests for the MarketDataSearchAgent and LangChainMarketDataAgent classes
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from typing import Dict, Any, List

from src.ai_agents.market_data_agent import MarketDataSearchAgent, LangChainMarketDataAgent
from src.ai_agents.tools import RealEstateSearchTool, MarketTrendTool


class TestMarketDataSearchAgent:
    """Test cases for the MarketDataSearchAgent class"""
    
    def test_init(self):
        """Test MarketDataSearchAgent initialization"""
        agent = MarketDataSearchAgent()
        
        assert agent.name == "market_data_search_agent"
        assert "market data" in agent.description.lower()
        assert agent.version.startswith("1.")
        assert hasattr(agent, 'data_sources')
        assert len(agent.data_sources) > 0
        assert agent.default_data_source == "primary_db"
    
    @pytest.mark.asyncio
    async def test_execute_logic_success(self):
        """Test successful execution of agent logic"""
        agent = MarketDataSearchAgent()
        parameters = {
            "location": "Berlin",
            "property_type": "apartment",
            "operation": "buy"
        }
        context = {}
        
        # Patch validate_input to return True
        with patch.object(agent, 'validate_input', return_value=asyncio.Future()) as mock_validate:
            mock_validate.return_value.set_result(True)
            
            result = await agent._execute_logic(parameters, context)
            
            assert result["success"] is True
            assert "location" in result
            assert result["location"] == "Berlin"
            assert "property_type" in result
            assert result["property_type"] == "apartment"
            assert "market_data" in result
            
            # Check market data structure
            market_data = result["market_data"]
            assert "current_listings" in market_data
            assert "price_trends" in market_data
            assert "avg_price_sqm" in market_data
            assert "rental_yield" in market_data
            assert "time_on_market" in market_data
            
            # Check price trends
            price_trends = market_data["price_trends"]
            assert "year_over_year" in price_trends
            assert "month_over_month" in price_trends
            assert "five_year" in price_trends
            
            # Check current listings
            listings = market_data["current_listings"]
            assert isinstance(listings, list)
            assert len(listings) > 0
            
            # Check first listing
            listing = listings[0]
            assert "id" in listing
            assert "price" in listing
            assert "size_sqm" in listing
            assert "price_per_sqm" in listing
            assert "address" in listing
            assert "features" in listing
            
            # Check confidence scores
            assert "confidence_scores" in result
            confidence = result["confidence_scores"]
            assert "overall" in confidence
            assert "price_data" in confidence
            assert "trend_data" in confidence
            assert "location_specificity" in confidence
            assert 0 <= confidence["overall"] <= 1
    
    @pytest.mark.asyncio
    async def test_execute_logic_with_search_params(self):
        """Test execution with search parameters"""
        agent = MarketDataSearchAgent()
        parameters = {
            "location": "Berlin",
            "property_type": "apartment",
            "operation": "buy",
            "search_params": {
                "price_range": {"min": 200000, "max": 500000},
                "size_range": {"min": 50, "max": 100},
                "features": ["balcony", "parking"]
            }
        }
        context = {}
        
        # Patch validate_input to return True
        with patch.object(agent, 'validate_input', return_value=asyncio.Future()) as mock_validate:
            mock_validate.return_value.set_result(True)
            
            result = await agent._execute_logic(parameters, context)
            
            assert result["success"] is True
            assert "search_params" in result
            assert result["search_params"] == parameters["search_params"]
            
            # Check that listings match search criteria
            listings = result["market_data"]["current_listings"]
            for listing in listings:
                assert 200000 <= listing["price"] <= 500000
                assert 50 <= listing["size_sqm"] <= 100
                features = listing["features"]
                assert any(f in features for f in ["balcony", "parking"])
    
    @pytest.mark.asyncio
    async def test_execute_logic_with_data_source(self):
        """Test execution with specific data source"""
        agent = MarketDataSearchAgent()
        parameters = {
            "location": "Berlin",
            "property_type": "apartment",
            "operation": "buy",
            "data_source": "real_estate_portal"
        }
        context = {}
        
        # Patch validate_input to return True
        with patch.object(agent, 'validate_input', return_value=asyncio.Future()) as mock_validate:
            mock_validate.return_value.set_result(True)
            
            result = await agent._execute_logic(parameters, context)
            
            assert result["success"] is True
            assert "data_source" in result
            assert result["data_source"] == "real_estate_portal"
    
    @pytest.mark.asyncio
    async def test_execute_logic_rent_operation(self):
        """Test execution with rent operation"""
        agent = MarketDataSearchAgent()
        parameters = {
            "location": "Berlin",
            "property_type": "apartment",
            "operation": "rent"
        }
        context = {}
        
        # Patch validate_input to return True
        with patch.object(agent, 'validate_input', return_value=asyncio.Future()) as mock_validate:
            mock_validate.return_value.set_result(True)
            
            result = await agent._execute_logic(parameters, context)
            
            assert result["success"] is True
            assert "operation" in result
            assert result["operation"] == "rent"
            
            # Check rent-specific data
            market_data = result["market_data"]
            assert "avg_rent_sqm" in market_data
            assert "rental_demand" in market_data
    
    @pytest.mark.asyncio
    async def test_execute_logic_invalid_input(self):
        """Test agent logic with invalid input"""
        agent = MarketDataSearchAgent()
        parameters = {
            "location": "Berlin"
            # Missing property_type
        }
        context = {}
        
        # Patch validate_input to return False
        with patch.object(agent, 'validate_input', return_value=asyncio.Future()) as mock_validate:
            mock_validate.return_value.set_result(False)
            
            result = await agent._execute_logic(parameters, context)
            
            assert result["success"] is False
            assert "error" in result
            assert "Invalid input parameters" in result["error"]
    
    @pytest.mark.asyncio
    async def test_validate_input_valid(self):
        """Test input validation with valid parameters"""
        agent = MarketDataSearchAgent()
        parameters = {
            "location": "Berlin",
            "property_type": "apartment"
            # operation is optional, defaults to "buy"
        }
        
        result = await agent.validate_input(parameters)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_input_missing_location(self):
        """Test input validation with missing location"""
        agent = MarketDataSearchAgent()
        parameters = {
            "property_type": "apartment"
            # Missing location
        }
        
        result = await agent.validate_input(parameters)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_input_missing_property_type(self):
        """Test input validation with missing property type"""
        agent = MarketDataSearchAgent()
        parameters = {
            "location": "Berlin"
            # Missing property_type
        }
        
        result = await agent.validate_input(parameters)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_input_invalid_property_type(self):
        """Test input validation with invalid property type"""
        agent = MarketDataSearchAgent()
        parameters = {
            "location": "Berlin",
            "property_type": "invalid_type"  # Not a valid property type
        }
        
        result = await agent.validate_input(parameters)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_input_invalid_operation(self):
        """Test input validation with invalid operation"""
        agent = MarketDataSearchAgent()
        parameters = {
            "location": "Berlin",
            "property_type": "apartment",
            "operation": "invalid_operation"  # Not a valid operation
        }
        
        result = await agent.validate_input(parameters)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_input_with_search_params(self):
        """Test input validation with search parameters"""
        agent = MarketDataSearchAgent()
        parameters = {
            "location": "Berlin",
            "property_type": "apartment",
            "operation": "buy",
            "search_params": {
                "price_range": {"min": 200000, "max": 500000},
                "size_range": {"min": 50, "max": 100}
            }
        }
        
        result = await agent.validate_input(parameters)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_input_invalid_search_params(self):
        """Test input validation with invalid search parameters"""
        agent = MarketDataSearchAgent()
        parameters = {
            "location": "Berlin",
            "property_type": "apartment",
            "search_params": {
                "price_range": {"min": 500000, "max": 200000}  # max < min
            }
        }
        
        result = await agent.validate_input(parameters)
        
        assert result is False
    
    def test_get_market_data(self):
        """Test getting market data from data source"""
        agent = MarketDataSearchAgent()
        location = "Berlin"
        property_type = "apartment"
        operation = "buy"
        data_source = "primary_db"
        search_params = None
        
        market_data = agent._get_market_data(location, property_type, operation, data_source, search_params)
        
        assert isinstance(market_data, dict)
        assert "current_listings" in market_data
        assert "price_trends" in market_data
        assert "avg_price_sqm" in market_data
        assert isinstance(market_data["avg_price_sqm"], (int, float))
        assert isinstance(market_data["current_listings"], list)
    
    def test_generate_listings(self):
        """Test generation of property listings"""
        agent = MarketDataSearchAgent()
        location = "Berlin"
        property_type = "apartment"
        operation = "buy"
        search_params = {
            "price_range": {"min": 200000, "max": 500000},
            "size_range": {"min": 50, "max": 100}
        }
        
        listings = agent._generate_listings(location, property_type, operation, search_params)
        
        assert isinstance(listings, list)
        assert len(listings) >= 5  # Should generate at least 5 listings
        
        # Check that first listing has proper structure
        listing = listings[0]
        assert "id" in listing
        assert "price" in listing
        assert "size_sqm" in listing
        assert "price_per_sqm" in listing
        assert "address" in listing
        assert "features" in listing
        assert "year_built" in listing
        assert "bedrooms" in listing
        assert "bathrooms" in listing
        
        # Verify listings match search criteria if provided
        for listing in listings:
            assert 200000 <= listing["price"] <= 500000
            assert 50 <= listing["size_sqm"] <= 100
    
    def test_get_price_trends(self):
        """Test getting price trends"""
        agent = MarketDataSearchAgent()
        location = "Berlin"
        property_type = "apartment"
        operation = "buy"
        
        trends = agent._get_price_trends(location, property_type, operation)
        
        assert isinstance(trends, dict)
        assert "year_over_year" in trends
        assert "month_over_month" in trends
        assert "five_year" in trends
        assert isinstance(trends["year_over_year"], (int, float))
        assert isinstance(trends["month_over_month"], (int, float))
        assert isinstance(trends["five_year"], (int, float))
    
    def test_get_confidence_scores(self):
        """Test calculation of confidence scores"""
        agent = MarketDataSearchAgent()
        location = "Berlin"
        property_type = "apartment"
        data_source = "primary_db"
        sample_size = 20
        
        scores = agent._get_confidence_scores(location, property_type, data_source, sample_size)
        
        assert isinstance(scores, dict)
        assert "overall" in scores
        assert "price_data" in scores
        assert "trend_data" in scores
        assert "location_specificity" in scores
        assert "sample_size_score" in scores
        
        # Verify score ranges
        for key, score in scores.items():
            assert 0 <= score <= 1
        
        # High sample size should lead to better sample_size_score
        high_sample_scores = agent._get_confidence_scores(location, property_type, data_source, 100)
        assert high_sample_scores["sample_size_score"] > scores["sample_size_score"]
        
        # Specific location should have better location_specificity
        specific_loc_scores = agent._get_confidence_scores("Berlin Mitte", property_type, data_source, sample_size)
        assert specific_loc_scores["location_specificity"] > scores["location_specificity"]
    
    def test_get_agent_name(self):
        """Test getting the agent name"""
        agent = MarketDataSearchAgent()
        assert agent._get_agent_name() == "market_data_search_agent"
    
    def test_get_agent_description(self):
        """Test getting the agent description"""
        agent = MarketDataSearchAgent()
        description = agent._get_agent_description()
        assert "market data" in description.lower()
        assert "real estate" in description.lower()


@pytest.mark.asyncio
class TestLangChainMarketDataAgent:
    """Test cases for the LangChainMarketDataAgent class"""
    
    @pytest.fixture
    def mock_api_key(self):
        """Mock API key for testing"""
        return "test-api-key-12345"
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM"""
        mock = MagicMock()
        mock._call = AsyncMock(return_value="Market data result")
        return mock
    
    @pytest.fixture
    def agent(self, mock_api_key):
        """Create a patched LangChainMarketDataAgent"""
        with patch('langchain.chat_models.ChatOpenAI') as mock_chat_openai, \
             patch('src.ai_agents.market_data_agent.RealEstateSearchTool') as mock_search_tool, \
             patch('src.ai_agents.market_data_agent.MarketTrendTool') as mock_trend_tool:
            
            # Mock the LLM
            mock_llm = MagicMock()
            mock_chat_openai.return_value = mock_llm
            
            # Mock the tools
            mock_search = MagicMock(spec=RealEstateSearchTool)
            mock_search_tool.return_value = mock_search
            
            mock_trend = MagicMock(spec=MarketTrendTool)
            mock_trend_tool.return_value = mock_trend
            
            # Create the agent
            agent = LangChainMarketDataAgent(api_key=mock_api_key)
            
            # Replace agent_executor.arun with a mock to avoid actual execution
            mock_executor = MagicMock()
            mock_executor.arun = AsyncMock(return_value="""
            Based on my research, here are the key market data findings for Berlin apartments:
            
            1. Average Price per Square Meter: €5,000
            2. Year-over-Year Price Change: +4.2%
            3. Current Number of Listings: 342
            4. Average Time on Market: 45 days
            5. Rental Yield: 3.8%
            
            The market shows moderate growth with stable demand. Most apartments in this area sell within 1-2 months.
            """)
            agent.create_agent_executor = MagicMock(return_value=mock_executor)
            
            yield agent
    
    def test_init(self, agent, mock_api_key):
        """Test initialization of the agent"""
        assert agent.api_key == mock_api_key
        assert agent.name == "langchain_market_data_agent"
        assert "LangChain agent" in agent.description
        assert agent.tools is not None
    
    async def test_execute_logic_success(self, agent):
        """Test successful execution of agent logic"""
        parameters = {
            "location": "Berlin",
            "property_type": "apartment",
            "operation": "buy"
        }
        context = {}
        
        result = await agent._execute_logic(parameters, context)
        
        assert result["success"] is True
        assert result["location"] == "Berlin"
        assert result["property_type"] == "apartment"
        assert result["operation"] == "buy"
        assert "analysis" in result
        assert "€5,000" in result["analysis"]
        assert "+4.2%" in result["analysis"]
        assert "timestamp" in result
        
        # Verify extracted data
        assert "extracted_data" in result
        data = result["extracted_data"]
        assert "avg_price_sqm" in data
        assert data["avg_price_sqm"] == 5000.0
        assert "year_over_year_change" in data
        assert data["year_over_year_change"] == 4.2
        assert "rental_yield" in data
        assert data["rental_yield"] == 3.8
    
    async def test_execute_logic_exception(self, agent):
        """Test agent logic when an exception occurs"""
        parameters = {
            "location": "Berlin",
            "property_type": "apartment",
            "operation": "buy"
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
        assert result["operation"] == "buy"
    
    def test_get_agent_name(self, agent):
        """Test getting the agent name"""
        assert agent._get_agent_name() == "langchain_market_data_agent"
    
    def test_get_agent_description(self, agent):
        """Test getting the agent description"""
        description = agent._get_agent_description()
        assert "LangChain agent" in description
        assert "market data" in description