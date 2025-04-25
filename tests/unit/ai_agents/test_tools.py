"""
Unit tests for the agent tools
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from src.ai_agents.tools import (
    RealEstateSearchTool,
    MarketTrendTool,
    RentEstimationTool,
    create_real_estate_tools
)


class TestRealEstateSearchTool:
    """Test cases for the RealEstateSearchTool"""
    
    def test_init(self):
        """Test initialization of tool"""
        tool = RealEstateSearchTool()
        
        assert tool.name == "real_estate_search"
        assert "Searches for real estate" in tool.description
        assert callable(tool.func)
    
    def test_run(self):
        """Test the run method of the tool"""
        tool = RealEstateSearchTool()
        
        # Test with valid input
        input_str = json.dumps({
            "location": "Berlin",
            "property_type": "apartment",
            "price_range": {"min": 200000, "max": 500000},
            "size_range": {"min": 50, "max": 100}
        })
        
        result = tool.func(input_str)
        
        assert isinstance(result, str)
        result_json = json.loads(result)
        assert "properties" in result_json
        assert isinstance(result_json["properties"], list)
        assert len(result_json["properties"]) > 0
        
        # Check the first property
        property = result_json["properties"][0]
        assert "id" in property
        assert "title" in property
        assert "price" in property
        assert "size_sqm" in property
        assert "location" in property
        assert "url" in property
        
        # Test with invalid JSON
        with pytest.raises(json.JSONDecodeError):
            tool.func("invalid json")
        
        # Test with missing location
        invalid_input = json.dumps({
            "property_type": "apartment"
        })
        
        result = tool.func(invalid_input)
        result_json = json.loads(result)
        assert "error" in result_json
        assert "location is required" in result_json["error"]
        
        # Test with invalid property type
        invalid_input = json.dumps({
            "location": "Berlin",
            "property_type": "invalid_type"
        })
        
        result = tool.func(invalid_input)
        result_json = json.loads(result)
        assert "error" in result_json
        assert "Invalid property type" in result_json["error"]


class TestMarketTrendTool:
    """Test cases for the MarketTrendTool"""
    
    def test_init(self):
        """Test initialization of tool"""
        tool = MarketTrendTool()
        
        assert tool.name == "market_trend_analysis"
        assert "Analyzes real estate market trends" in tool.description
        assert callable(tool.func)
    
    def test_run(self):
        """Test the run method of the tool"""
        tool = MarketTrendTool()
        
        # Test with valid input
        input_str = json.dumps({
            "location": "Berlin",
            "property_type": "apartment",
            "timeframe": "5_years"
        })
        
        result = tool.func(input_str)
        
        assert isinstance(result, str)
        result_json = json.loads(result)
        assert "trends" in result_json
        assert "price_trends" in result_json["trends"]
        assert "rental_trends" in result_json["trends"]
        assert "supply_demand" in result_json["trends"]
        assert "forecast" in result_json
        assert "analysis" in result_json
        
        # Verify price trends structure
        price_trends = result_json["trends"]["price_trends"]
        assert "current_avg_sqm" in price_trends
        assert "yoy_change" in price_trends
        assert "five_year_change" in price_trends
        
        # Test with invalid JSON
        with pytest.raises(json.JSONDecodeError):
            tool.func("invalid json")
        
        # Test with missing location
        invalid_input = json.dumps({
            "property_type": "apartment",
            "timeframe": "5_years"
        })
        
        result = tool.func(invalid_input)
        result_json = json.loads(result)
        assert "error" in result_json
        assert "location is required" in result_json["error"]
        
        # Test with invalid timeframe
        invalid_input = json.dumps({
            "location": "Berlin",
            "property_type": "apartment",
            "timeframe": "invalid_timeframe"
        })
        
        result = tool.func(invalid_input)
        result_json = json.loads(result)
        assert "error" in result_json
        assert "Invalid timeframe" in result_json["error"]


class TestRentEstimationTool:
    """Test cases for the RentEstimationTool"""
    
    def test_init(self):
        """Test initialization of tool"""
        tool = RentEstimationTool()
        
        assert tool.name == "rent_estimation"
        assert "Estimates the potential rental income" in tool.description
        assert callable(tool.func)
    
    def test_run(self):
        """Test the run method of the tool"""
        tool = RentEstimationTool()
        
        # Test with valid input
        input_str = json.dumps({
            "location": "Berlin",
            "property_type": "apartment",
            "size_sqm": 75,
            "bedrooms": 2,
            "bathrooms": 1,
            "features": ["balcony", "parking"],
            "condition": "good"
        })
        
        result = tool.func(input_str)
        
        assert isinstance(result, str)
        result_json = json.loads(result)
        assert "estimated_rent" in result_json
        assert "rent_per_sqm" in result_json
        assert "confidence" in result_json
        assert "comparable_properties" in result_json
        assert "explanation" in result_json
        
        # Verify rent values
        assert isinstance(result_json["estimated_rent"], (int, float))
        assert isinstance(result_json["rent_per_sqm"], (int, float))
        assert 0 <= result_json["confidence"] <= 1
        
        # Verify comparable properties
        assert isinstance(result_json["comparable_properties"], list)
        assert len(result_json["comparable_properties"]) > 0
        comp = result_json["comparable_properties"][0]
        assert "address" in comp
        assert "size_sqm" in comp
        assert "rent" in comp
        assert "bedrooms" in comp
        
        # Test with invalid JSON
        with pytest.raises(json.JSONDecodeError):
            tool.func("invalid json")
        
        # Test with missing required fields
        invalid_input = json.dumps({
            "location": "Berlin",
            "property_type": "apartment"
            # Missing size_sqm which is required
        })
        
        result = tool.func(invalid_input)
        result_json = json.loads(result)
        assert "error" in result_json
        assert "size_sqm is required" in result_json["error"]
        
        # Test with invalid condition
        invalid_input = json.dumps({
            "location": "Berlin",
            "property_type": "apartment",
            "size_sqm": 75,
            "condition": "invalid_condition"
        })
        
        result = tool.func(invalid_input)
        result_json = json.loads(result)
        assert "error" in result_json
        assert "Invalid condition" in result_json["error"]


def test_create_real_estate_tools():
    """Test creation of real estate tools"""
    tools = create_real_estate_tools()
    
    assert isinstance(tools, list)
    assert len(tools) >= 3
    
    # Check that each tool is of the correct type
    tool_names = [tool.name for tool in tools]
    assert "real_estate_search" in tool_names
    assert "market_trend_analysis" in tool_names
    assert "rent_estimation" in tool_names
    
    # Verify all tools have required attributes
    for tool in tools:
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert hasattr(tool, "func")
        assert callable(tool.func)