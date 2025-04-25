"""
Market Data Search Agent for gathering real estate market data
"""
import logging
import random
import asyncio
import datetime
import os
import json
from typing import Dict, Any, List, Optional, Tuple, Union
import uuid

# LangChain imports
from langchain.agents import AgentExecutor
from langchain.schema import AgentAction, AgentFinish
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

# Local imports
from .base_agent import BaseAgent, LangChainAgent
from .tools import create_real_estate_tools, RealEstateSearchTool, MarketTrendTool, RentEstimationTool

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketDataSearchAgent(BaseAgent):
    """
    Agent responsible for searching and aggregating real estate market data
    
    Implementation of AI-001: Market Data Search Agent
    """
    
    def __init__(self):
        """Initialize the market data search agent"""
        super().__init__()
        # Initialize data sources
        self.data_sources = [
            "ImmoScout24",
            "ImmoWelt",
            "Immobilien.de",
            "Statista",
            "Federal Statistical Office",
            "Regional Housing Market Reports"
        ]
        self.default_data_source = "primary_db"
    
    def _get_agent_name(self) -> str:
        """Get the name of the agent"""
        return "market_data_search_agent"
    
    def _get_agent_description(self) -> str:
        """Get the description of the agent"""
        return "Agent responsible for searching and aggregating real estate market data"
    
    async def _execute_logic(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for and aggregate market data based on input parameters
        
        Args:
            parameters: Dictionary containing:
                - location: str - The location to search for (city/district)
                - property_type: str - The type of property (apartment, house, etc.)
                - operation: str - Operation type (buy, rent)
                - data_source: str - Data source to use (optional)
                - search_params: Dict[str, Any] - Additional search parameters
            context: Shared context from the orchestrator
            
        Returns:
            Dictionary containing market data results
        """
        try:
            # Validate the input parameters first
            validation_result = await self.validate_input(parameters)
            
            if not validation_result:
                logger.error("Invalid input parameters for market data search")
                return {
                    "success": False,
                    "error": "Invalid input parameters",
                    "timestamp": datetime.datetime.now().isoformat()
                }
            
            # Get parameters
            location = parameters.get("location", "")
            property_type = parameters.get("property_type", "")
            operation = parameters.get("operation", "buy")
            data_source = parameters.get("data_source", self.default_data_source)
            search_params = parameters.get("search_params", None)
            
            # In a real implementation, this would make API calls to real estate data sources
            # or use web scraping to gather market data
            
            # For this demo, we'll simulate the process with realistic mock data
            await asyncio.sleep(1)  # Simulate API call delay
            
            # Get market data
            market_data = self._get_market_data(location, property_type, operation, data_source, search_params)
            
            # Generate listings based on parameters
            listings = self._generate_listings(location, property_type, operation, search_params)
            
            # Get price trends
            price_trends = self._get_price_trends(location, property_type, operation)
            
            # Calculate confidence scores
            confidence_scores = self._get_confidence_scores(location, property_type, data_source, len(listings))
            
            # Put together the full result
            result = {
                "success": True,
                "location": location,
                "property_type": property_type,
                "operation": operation,
                "data_source": data_source,
                "search_params": search_params,
                "market_data": market_data,
                "listings": listings,
                "price_trends": price_trends,
                "confidence_scores": confidence_scores,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in market data search: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def _get_market_data(self, location: str, property_type: str, operation: str,
                        data_source: str, search_params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get market data from the specified data source
        
        Args:
            location: Location to search for
            property_type: Type of property
            operation: Operation type (buy, rent)
            data_source: Data source to use
            search_params: Additional search parameters
            
        Returns:
            Dictionary with market data
        """
        # Base values - would be retrieved from real data sources in production
        base_values = {
            "apartment": {
                "berlin": {"price": 5000, "rent": 15.0, "vacancy": 0.02},
                "hamburg": {"price": 5500, "rent": 14.5, "vacancy": 0.02},
                "munich": {"price": 9000, "rent": 20.0, "vacancy": 0.01},
                "frankfurt": {"price": 6000, "rent": 16.0, "vacancy": 0.03},
                "cologne": {"price": 5000, "rent": 13.0, "vacancy": 0.03}
            },
            "house": {
                "berlin": {"price": 4000, "rent": 12.0, "vacancy": 0.03},
                "hamburg": {"price": 4500, "rent": 13.0, "vacancy": 0.03},
                "munich": {"price": 8000, "rent": 17.0, "vacancy": 0.02},
                "frankfurt": {"price": 5000, "rent": 14.0, "vacancy": 0.04},
                "cologne": {"price": 4200, "rent": 12.0, "vacancy": 0.04}
            },
            "multi-family": {
                "berlin": {"price": 3800, "rent": 12.0, "vacancy": 0.04},
                "hamburg": {"price": 4200, "rent": 13.0, "vacancy": 0.04},
                "munich": {"price": 7500, "rent": 16.0, "vacancy": 0.03},
                "frankfurt": {"price": 4800, "rent": 13.5, "vacancy": 0.05},
                "cologne": {"price": 3900, "rent": 11.5, "vacancy": 0.05}
            },
            "commercial": {
                "berlin": {"price": 3500, "rent": 20.0, "vacancy": 0.06},
                "hamburg": {"price": 4000, "rent": 21.0, "vacancy": 0.05},
                "munich": {"price": 7000, "rent": 26.0, "vacancy": 0.04},
                "frankfurt": {"price": 5500, "rent": 24.0, "vacancy": 0.06},
                "cologne": {"price": 3600, "rent": 19.0, "vacancy": 0.07}
            }
        }
        
        # Extract city from location for basic data lookup
        city = location.lower().split()[0]
        if city not in ["berlin", "hamburg", "munich", "frankfurt", "cologne"]:
            city = "berlin"  # Default to Berlin if city not found
        
        # Get base data and apply randomness to simulate real-world variance
        base_data = base_values.get(property_type, base_values["apartment"]).get(city, base_values["apartment"]["berlin"])
        
        # Apply variance to create realistic data
        price_variance = random.uniform(0.9, 1.1)
        rent_variance = random.uniform(0.9, 1.1)
        vacancy_variance = random.uniform(0.8, 1.2)
        
        # Calculate final values
        avg_price_sqm = base_data["price"] * price_variance
        avg_rent_sqm = base_data["rent"] * rent_variance
        vacancy_rate = base_data["vacancy"] * vacancy_variance
        
        # Apply data source factor - some sources might have higher/lower estimates
        source_factors = {
            "primary_db": 1.0,
            "real_estate_portal": 1.05,
            "government_data": 0.95,
            "market_analysis": 1.02
        }
        
        source_factor = source_factors.get(data_source, 1.0)
        avg_price_sqm *= source_factor
        avg_rent_sqm *= source_factor
        
        # Apply search params if provided
        if search_params:
            # Size range might affect average prices slightly
            if "size_range" in search_params:
                size_range = search_params["size_range"]
                min_size = size_range.get("min", 0)
                max_size = size_range.get("max", 200)
                size_factor = (min_size + max_size) / 200
                avg_price_sqm *= max(0.9, min(1.1, size_factor))
                avg_rent_sqm *= max(0.9, min(1.1, size_factor))
            
            # Features might affect prices
            if "features" in search_params:
                features = search_params["features"]
                feature_premium = len(features) * 0.02  # 2% premium per feature
                avg_price_sqm *= (1 + feature_premium)
                avg_rent_sqm *= (1 + feature_premium)
        
        # Formulate trend predictions
        price_trend = random.choice(["increasing", "stable", "slightly increasing", "rapidly increasing"])
        rent_trend = random.choice(["increasing", "stable", "slightly increasing", "rapidly increasing"])
        
        # Select random data sources to simulate varied data availability
        num_sources = random.randint(3, len(self.data_sources))
        sources_used = random.sample(self.data_sources, num_sources)
        
        # Calculate rental yield
        rental_yield = (avg_rent_sqm * 12) / avg_price_sqm * 100 if avg_price_sqm > 0 else 0
        
        # Generate sample listings for current listings
        current_listings = self._generate_listings(location, property_type, operation, search_params)
        
        # Get price trends data
        price_trends = self._get_price_trends(location, property_type, operation)
        
        # Compile market data
        market_data = {
            "location": location,
            "property_type": property_type,
            "avg_price_sqm": round(avg_price_sqm, 2),
            "avg_rent_sqm": round(avg_rent_sqm, 2),
            "vacancy_rate": round(vacancy_rate, 4),
            "price_trend": price_trend,
            "rent_trend": rent_trend,
            "rental_yield": round(rental_yield, 2),
            "price_to_rent_ratio": round(avg_price_sqm / avg_rent_sqm, 2) if avg_rent_sqm > 0 else 0,
            "current_listings": current_listings,
            "price_trends": price_trends,
            "time_on_market": random.randint(30, 90),
            "last_updated": datetime.datetime.now().isoformat()
        }
        
        # Add operation-specific data
        if operation == "rent":
            market_data["rental_demand"] = random.choice(["high", "medium", "very high"])
            market_data["avg_days_on_market"] = random.randint(20, 60)
            
        elif operation == "buy":
            market_data["price_per_income"] = round(random.uniform(8, 15), 2)
            market_data["avg_days_on_market"] = random.randint(30, 90)
            
        return market_data
    
    def _generate_listings(self, location: str, property_type: str, operation: str, 
                         search_params: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate property listings based on the search parameters
        
        Args:
            location: Location of properties
            property_type: Type of property
            operation: Operation type (buy, rent)
            search_params: Additional search parameters
            
        Returns:
            List of property listings
        """
        listings = []
        
        # Get base price and rent values for the location and property type
        base_values = {
            "apartment": {
                "berlin": {"price": 5000, "rent": 15.0},
                "hamburg": {"price": 5500, "rent": 14.5},
                "munich": {"price": 9000, "rent": 20.0},
                "frankfurt": {"price": 6000, "rent": 16.0},
                "cologne": {"price": 5000, "rent": 13.0},
                "default": {"price": 5000, "rent": 15.0}
            },
            "house": {
                "berlin": {"price": 4000, "rent": 12.0},
                "hamburg": {"price": 4500, "rent": 13.0},
                "munich": {"price": 8000, "rent": 17.0},
                "frankfurt": {"price": 5000, "rent": 14.0},
                "cologne": {"price": 4200, "rent": 12.0},
                "default": {"price": 4000, "rent": 12.0}
            },
            "default": {
                "default": {"price": 5000, "rent": 15.0}
            }
        }
        
        city = location.lower().split()[0]
        prop_type = property_type.lower()
        
        type_data = base_values.get(prop_type, base_values["default"])
        base_data = type_data.get(city, type_data.get("default"))
        
        # Extract search parameters
        size_min = 30
        size_max = 120
        price_min = 0
        price_max = 1000000000
        required_features = []
        
        if search_params:
            if "size_range" in search_params:
                size_min = search_params["size_range"].get("min", size_min)
                size_max = search_params["size_range"].get("max", size_max)
            
            if "price_range" in search_params:
                price_min = search_params["price_range"].get("min", price_min)
                price_max = search_params["price_range"].get("max", price_max)
            
            if "features" in search_params:
                required_features = search_params["features"]
        
        # Generate 5-10 sample listings
        num_listings = random.randint(5, 10)
        
        for i in range(num_listings):
            # Generate size within the range
            size = random.randint(int(size_min), int(size_max))
            
            # Price and rent with some variance
            price_variance = random.uniform(0.85, 1.15)
            rent_variance = random.uniform(0.85, 1.15)
            
            # Calculate price or rent based on operation
            if operation == "buy":
                price = round(size * base_data["price"] * price_variance, 2)
                rent = round(size * base_data["rent"] * rent_variance, 2)  # Potential rent
            else:  # rent
                rent = round(size * base_data["rent"] * rent_variance, 2)
                price = round(size * base_data["price"] * price_variance, 2)  # Property value
            
            # Skip if price is outside the specified range
            if operation == "buy" and (price < price_min or price > price_max):
                continue
            if operation == "rent" and (rent < price_min or rent > price_max):
                continue
            
            # Select features
            all_features = ["balcony", "garden", "parking", "elevator", "storage", "fitted kitchen", "terrace"]
            # Make sure required features are included
            if required_features:
                features = required_features.copy()
                # Add some random additional features
                for feature in random.sample([f for f in all_features if f not in required_features], 
                                             k=random.randint(0, len(all_features) - len(required_features))):
                    features.append(feature)
            else:
                features = random.sample(all_features, k=random.randint(1, 4))
            
            # Create listing
            listing = {
                "id": f"listing-{uuid.uuid4().hex[:8]}",
                "title": f"{size} sqm {property_type} in {location}",
                "address": f"{random.randint(1, 100)} Example Street, {location}",
                "size_sqm": size,
                "features": features,
                "year_built": random.randint(1950, 2020),
                "bedrooms": random.randint(1, 4),
                "bathrooms": random.choice([1, 1, 1.5, 2, 2.5])
            }
            
            if operation == "buy":
                listing["price"] = price
                listing["price_per_sqm"] = round(price / size, 2)
                listing["estimated_rent"] = rent
                listing["rental_yield"] = round((rent * 12 / price) * 100, 2)
            else:  # rent
                listing["monthly_rent"] = rent
                listing["rent_per_sqm"] = round(rent / size, 2)
                listing["estimated_value"] = price
                listing["deposit"] = round(rent * 3, 2)
            
            listings.append(listing)
        
        return listings
    
    def _get_price_trends(self, location: str, property_type: str, operation: str) -> Dict[str, Any]:
        """
        Get price trend data for the given parameters
        
        Args:
            location: Location to get trends for
            property_type: Type of property
            operation: Operation type (buy, rent)
            
        Returns:
            Dictionary with price trend data
        """
        # City-specific trend factors
        city_trends = {
            "berlin": {"yoy": 0.042, "mom": 0.004, "five_year": 0.21},
            "hamburg": {"yoy": 0.038, "mom": 0.003, "five_year": 0.19},
            "munich": {"yoy": 0.056, "mom": 0.005, "five_year": 0.28},
            "frankfurt": {"yoy": 0.045, "mom": 0.004, "five_year": 0.23},
            "cologne": {"yoy": 0.037, "mom": 0.003, "five_year": 0.18},
            "default": {"yoy": 0.04, "mom": 0.003, "five_year": 0.2}
        }
        
        # Property type modifiers
        property_modifiers = {
            "apartment": {"price": 1.1, "rent": 1.05},
            "house": {"price": 1.0, "rent": 0.95},
            "multi-family": {"price": 0.95, "rent": 1.0},
            "commercial": {"price": 0.9, "rent": 1.1},
            "default": {"price": 1.0, "rent": 1.0}
        }
        
        # Get base trends for the city
        city = location.lower().split()[0]
        base_trends = city_trends.get(city, city_trends["default"])
        
        # Get property modifiers
        modifiers = property_modifiers.get(property_type.lower(), property_modifiers["default"])
        
        # Calculate adjusted trends based on operation
        if operation == "buy":
            modifier = modifiers["price"]
        else:  # rent
            modifier = modifiers["rent"]
        
        # Apply modifier and add some randomness
        yoy_change = base_trends["yoy"] * modifier * random.uniform(0.9, 1.1)
        mom_change = base_trends["mom"] * modifier * random.uniform(0.9, 1.1)
        five_year_change = base_trends["five_year"] * modifier * random.uniform(0.9, 1.1)
        
        # Format according to test expectations
        # Tests expect simple numeric values, not nested objects
        return {
            "year_over_year": round(yoy_change * 100, 2),
            "month_over_month": round(mom_change * 100, 2),
            "five_year": round(five_year_change * 100, 2)
        }
    
    def _get_confidence_scores(self, location: str, property_type: str, 
                            data_source: str, sample_size: int) -> Dict[str, float]:
        """
        Calculate confidence scores for the market data
        
        Args:
            location: Location being analyzed
            property_type: Type of property
            data_source: Data source being used
            sample_size: Number of sample listings
            
        Returns:
            Dictionary with confidence scores
        """
        # Base confidence score
        base_confidence = 0.7
        
        # Adjust for location specificity
        location_words = location.split()
        location_specificity = min(1.0, 0.5 + 0.1 * len(location_words))  # More specific with more words
        
        # Adjust for data source
        source_confidence = {
            "primary_db": 0.9,
            "real_estate_portal": 0.85,
            "government_data": 0.95,
            "market_analysis": 0.8
        }
        source_factor = source_confidence.get(data_source, 0.7)
        
        # Adjust for sample size - ensure it scales with sample size
        # Cap it at 0.99 for normal case and 1.0 for high sample case
        sample_size_score = min(0.99, 0.5 + (sample_size / 100))
        
        # Calculate trend data reliability
        trend_data_score = 0.75  # Base score for trend data
        
        # Calculate overall confidence, weighing different factors
        overall_confidence = (
            base_confidence * 0.2 +
            location_specificity * 0.2 +
            source_factor * 0.25 +
            sample_size_score * 0.2 +
            trend_data_score * 0.15
        )
        
        # Ensure all scores are between 0 and 1
        return {
            "overall": round(min(1.0, overall_confidence), 2),
            "location_specificity": round(location_specificity, 2),
            "data_source_reliability": round(source_factor, 2),
            "sample_size_score": round(sample_size_score, 2),
            "price_data": round(min(1.0, source_factor * sample_size_score), 2),
            "trend_data": round(trend_data_score, 2)
        }
    
    async def validate_input(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate the input parameters
        
        Args:
            parameters: Dictionary of parameters to validate
            
        Returns:
            True if parameters are valid, False otherwise
        """
        # Check required parameters
        required_params = ["location", "property_type"]
        for param in required_params:
            if param not in parameters:
                logger.error(f"Missing required parameter: {param}")
                return False
        
        # Validate property type
        valid_property_types = ["apartment", "house", "multi-family", "commercial"]
        if parameters.get("property_type") not in valid_property_types:
            logger.error(f"Invalid property type: {parameters.get('property_type')}")
            return False
        
        # Validate operation if provided
        if "operation" in parameters:
            valid_operations = ["buy", "rent"]
            if parameters.get("operation") not in valid_operations:
                logger.error(f"Invalid operation: {parameters.get('operation')}")
                return False
        
        # Validate search parameters if provided
        if "search_params" in parameters and parameters["search_params"]:
            search_params = parameters["search_params"]
            
            # Validate price range if provided
            if "price_range" in search_params:
                price_range = search_params["price_range"]
                if "min" in price_range and "max" in price_range:
                    if price_range["min"] > price_range["max"]:
                        logger.error(f"Invalid price range: min ({price_range['min']}) > max ({price_range['max']})")
                        return False
            
            # Validate size range if provided
            if "size_range" in search_params:
                size_range = search_params["size_range"]
                if "min" in size_range and "max" in size_range:
                    if size_range["min"] > size_range["max"]:
                        logger.error(f"Invalid size range: min ({size_range['min']}) > max ({size_range['max']})")
                        return False
        
        return True
    
    def get_confidence_level(self, data: Dict[str, Any]) -> float:
        """
        Calculate confidence level for the market data
        
        Args:
            data: Dictionary with factors affecting confidence:
                - num_sources: Number of data sources used
                - data_completeness: Completeness of data (0.0-1.0)
                - property_type_match: Whether the property type exactly matched the request
                - location_specificity: How specific the location match was (0.0-1.0)
            
        Returns:
            Confidence level as a float between 0.0 and 1.0
        """
        # Base confidence level
        confidence = 0.5
        
        # Adjust based on number of sources
        num_sources = data.get("num_sources", 0)
        if num_sources >= 5:
            confidence += 0.2
        elif num_sources >= 3:
            confidence += 0.1
        elif num_sources < 2:
            confidence -= 0.1
        
        # Adjust based on data completeness
        completeness = data.get("data_completeness", 0)
        confidence += completeness * 0.2
        
        # Adjust based on property type match
        if data.get("property_type_match", False):
            confidence += 0.1
        else:
            confidence -= 0.1
        
        # Adjust based on location specificity
        location_specificity = data.get("location_specificity", 0)
        confidence += location_specificity * 0.2
        
        # Ensure confidence is between 0.0 and 1.0
        return max(0.0, min(1.0, confidence))


class LangChainMarketDataAgent(LangChainAgent):
    """
    LangChain implementation of the market data search agent
    
    This agent leverages LangChain's agent framework to search for and analyze
    real estate market data using a combination of tools and LLM reasoning.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LangChain market data agent
        
        Args:
            api_key: OpenAI API key for the LLM. If not provided, will look for OPENAI_API_KEY env variable
        """
        # Set up OpenAI API key
        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required either as parameter or OPENAI_API_KEY environment variable")
        
        # Create LLM
        llm = ChatOpenAI(
            temperature=0.2,
            model_name="gpt-3.5-turbo",
            api_key=api_key
        )
        
        # Create tools
        tools = create_real_estate_tools()
        
        # Define the prompt template
        prompt_template = """
        You are a real estate market data analyst. Your job is to gather and analyze data about real estate markets
        to help investors make informed decisions. You have access to the following tools:
        
        {tools}
        
        Use these tools to provide comprehensive market data analysis.
        
        User Query: {input}
        
        Think step by step about how to approach this query:
        1. What specific location and property type are we researching?
        2. What kind of market data would be most valuable (prices, rents, trends)?
        3. How can you use your tools to gather this information?
        
        Previous steps: {intermediate_steps}
        
        Based on the information so far, what tool should you use next and why?
        
        Tool:
        """
        
        # Initialize LangChain Agent
        super().__init__(
            llm=llm,
            tools=tools,
            prompt_template=prompt_template,
            input_variables=["input", "intermediate_steps", "tools"]
        )
    
    def _get_agent_name(self) -> str:
        """Get the name of the agent"""
        return "langchain_market_data_agent"
    
    def _get_agent_description(self) -> str:
        """Get the description of the agent"""
        return "LangChain agent for searching and analyzing real estate market data"
    
    async def _execute_logic(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's core logic
        
        Args:
            parameters: Parameters specific to this agent execution
            context: Shared context from the orchestrator
            
        Returns:
            Dictionary with execution results
        """
        # Format the input query for the agent
        location = parameters.get("location", "")
        property_type = parameters.get("property_type", "")
        
        # Build a natural language query from the parameters
        query = f"Analyze the real estate market for {property_type} properties in {location}. "
        
        # Add details for filters if provided
        if "additional_filters" in parameters and parameters["additional_filters"]:
            filters = parameters["additional_filters"]
            if "min_size_sqm" in filters and "max_size_sqm" in filters:
                query += f"Size range: {filters['min_size_sqm']} to {filters['max_size_sqm']} square meters. "
            if "min_price" in filters and "max_price" in filters:
                query += f"Price range: {filters['min_price']} to {filters['max_price']}. "
        
        # Add specific data requests if provided
        if "data_requests" in parameters:
            query += f"Specifically focus on: {', '.join(parameters['data_requests'])}. "
        
        # Create an agent executor
        agent_executor = self.create_agent_executor(
            max_iterations=10,
            early_stopping_method="generate",
        )
        
        # Run the agent
        try:
            result = await agent_executor.arun(input=query)
            
            return {
                "success": True,
                "query": query,
                "analysis": result,
                "location": location,
                "property_type": property_type,
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error executing LangChain agent: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "location": location,
                "property_type": property_type,
                "timestamp": datetime.datetime.now().isoformat()
            }