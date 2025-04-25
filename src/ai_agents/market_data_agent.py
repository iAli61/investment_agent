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
from .tools import create_real_estate_tools

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
                - additional_filters: Dict[str, Any] - Additional search filters
            context: Shared context from the orchestrator
            
        Returns:
            Dictionary containing market data results
        """
        if not await self.validate_input(parameters):
            logger.error("Invalid input parameters for market data search")
            return {"error": "Invalid input parameters", "success": False}
        
        try:
            # Get parameters
            location = parameters.get("location", "")
            property_type = parameters.get("property_type", "")
            additional_filters = parameters.get("additional_filters", {})
            
            # In a real implementation, this would make API calls to real estate data sources
            # or use web scraping to gather market data
            
            # For this demo, we'll simulate the process with realistic mock data
            await asyncio.sleep(2)  # Simulate API call delay
            
            # Get market data
            market_data, sources_used = self._generate_market_data(location, property_type, additional_filters)
            
            # Calculate confidence level
            confidence_level = self.get_confidence_level({
                "num_sources": len(sources_used),
                "data_completeness": 0.85,  # Simulated completeness score
                "property_type_match": True,
                "location_specificity": 0.9  # Simulated location match score
            })
            
            return {
                "success": True,
                "data": market_data,
                "sources": sources_used,
                "confidence_level": confidence_level,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in market data search: {str(e)}")
            return {"error": str(e), "success": False}
    
    def _generate_market_data(self, location: str, property_type: str, 
                             filters: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Generate market data for the given parameters
        
        Args:
            location: Location to search for
            property_type: Type of property
            filters: Additional filters
            
        Returns:
            Tuple of (market_data_dict, sources_used_list)
        """
        # Select random data sources to simulate varied data availability
        num_sources = random.randint(3, len(self.data_sources))
        sources_used = random.sample(self.data_sources, num_sources)
        
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
        
        # Apply additional filters if they affect the data
        if "min_size_sqm" in filters and "max_size_sqm" in filters:
            # Size range might affect average prices slightly
            size_factor = (filters["min_size_sqm"] + filters["max_size_sqm"]) / 200
            avg_price_sqm *= max(0.9, min(1.1, size_factor))
            avg_rent_sqm *= max(0.9, min(1.1, size_factor))
        
        # Formulate trend predictions
        price_trend = random.choice(["increasing", "stable", "slightly increasing", "rapidly increasing"])
        rent_trend = random.choice(["increasing", "stable", "slightly increasing", "rapidly increasing"])
        
        # Create listing samples
        listings = self._generate_sample_listings(location, property_type, avg_price_sqm, avg_rent_sqm)
        
        # Compile market data
        market_data = {
            "location": location,
            "property_type": property_type,
            "avg_price_sqm": round(avg_price_sqm, 2),
            "avg_rent_sqm": round(avg_rent_sqm, 2),
            "vacancy_rate": round(vacancy_rate, 4),
            "price_trend": price_trend,
            "rent_trend": rent_trend,
            "price_to_rent_ratio": round(avg_price_sqm / avg_rent_sqm, 2) if avg_rent_sqm > 0 else 0,
            "sample_listings": listings,
            "last_updated": datetime.datetime.now().isoformat(),
            "sources": sources_used
        }
        
        return market_data, sources_used
    
    def _generate_sample_listings(self, location: str, property_type: str, 
                                 avg_price_sqm: float, avg_rent_sqm: float) -> List[Dict[str, Any]]:
        """
        Generate sample property listings to support market data
        
        Args:
            location: Location of properties
            property_type: Type of property
            avg_price_sqm: Average price per square meter
            avg_rent_sqm: Average rent per square meter
            
        Returns:
            List of sample property listings
        """
        listings = []
        
        # Generate 3-5 sample listings
        for i in range(random.randint(3, 5)):
            # Random size between 30-120 sqm for apartments, 80-200 for houses
            size_min = 30 if property_type == "apartment" else 80
            size_max = 120 if property_type == "apartment" else 200
            size = random.randint(size_min, size_max)
            
            # Price and rent with some variance
            price_variance = random.uniform(0.85, 1.15)
            rent_variance = random.uniform(0.85, 1.15)
            
            price = round(size * avg_price_sqm * price_variance, 2)
            rent = round(size * avg_rent_sqm * rent_variance, 2)
            
            # Create listing
            listing = {
                "id": f"listing-{uuid.uuid4().hex[:8]}",
                "title": f"{size} sqm {property_type} in {location}",
                "size_sqm": size,
                "price": price,
                "price_sqm": round(price / size, 2),
                "monthly_rent": rent,
                "rent_sqm": round(rent / size, 2),
                "bedrooms": random.randint(1, 4),
                "bathrooms": random.choice([1, 1, 1.5, 2, 2.5]),
                "year_built": random.randint(1950, 2020),
                "features": random.sample(["balcony", "garden", "parking", "elevator", "storage", "fitted kitchen"], k=random.randint(1, 4))
            }
            
            listings.append(listing)
        
        return listings
    
    async def validate_input(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate the input parameters
        
        Args:
            parameters: Dictionary of parameters to validate
            
        Returns:
            True if parameters are valid, False otherwise
        """
        required_params = ["location", "property_type"]
        for param in required_params:
            if param not in parameters:
                logger.error(f"Missing required parameter: {param}")
                return False
        
        valid_property_types = ["apartment", "house", "multi-family", "commercial"]
        if parameters.get("property_type") not in valid_property_types:
            logger.error(f"Invalid property type: {parameters.get('property_type')}")
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
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required either as parameter or OPENAI_API_KEY environment variable")
        
        # Create LLM
        llm = ChatOpenAI(
            temperature=0.2,
            model_name="gpt-3.5-turbo",
            api_key=self.api_key
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
                "property_type": property_type
            }


# Factory function to create the appropriate market data agent
def create_market_data_agent(use_langchain: bool = True, api_key: Optional[str] = None) -> BaseAgent:
    """
    Create a market data agent
    
    Args:
        use_langchain: Whether to use the LangChain implementation
        api_key: OpenAI API key if using LangChain
        
    Returns:
        A market data agent
    """
    if use_langchain:
        try:
            return LangChainMarketDataAgent(api_key=api_key)
        except Exception as e:
            logger.error(f"Failed to create LangChain market data agent: {str(e)}")
            logger.info("Falling back to basic market data agent")
            return MarketDataSearchAgent()
    else:
        return MarketDataSearchAgent()