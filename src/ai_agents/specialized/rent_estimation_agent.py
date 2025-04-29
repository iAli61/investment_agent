"""
Rent Estimation Agent implementation for the Property Investment Analysis Application.

This specialized agent generates rental estimates based on property specifics and market data.
"""

import logging
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from agents import Agent, function_tool, OpenAIChatCompletionsModel
from pydantic import BaseModel

from ..tools.investment_tools import (
    query_market_data,
    analyze_comparables,
    parse_property_text
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RentEstimateRequest(BaseModel):
    """Rent estimation request parameters."""
    location: str
    property_type: str
    size_sqm: float
    year_built: Optional[int] = None
    condition: Optional[str] = None
    features: Optional[List[str]] = None
    check_rent_control: Optional[bool] = True

class RentEstimateResult(BaseModel):
    """Result from the Rent Estimation Agent."""
    property_address: str
    estimated_rent: float
    low_range: float
    high_range: float
    rent_per_sqm: float
    comparable_properties: List[Dict[str, Any]]
    key_factors: List[str]
    rent_control_flag: Optional[bool] = False
    confidence_score: float
    explanation: str

# Check for LangChain dependencies
try:
    from langchain_community.utilities import GoogleSerperAPIWrapper
    from langchain_community.document_loaders import WebBaseLoader
    has_langchain = True
    logger.info("[Rent Estimation] LangChain dependencies loaded")
except ImportError:
    has_langchain = False
    logger.warning("[Rent Estimation] LangChain dependencies not available")

# Define LangChain-enhanced rent search tool
if has_langchain:
    @function_tool
    def search_rental_data_with_langchain(location: str, property_type: str) -> str:
        """
        Search for comparable rental listings using LangChain-enhanced search.
        """
        logger.info(f"[Rent Estimation] LangChain searching rentals in {location} for {property_type}")
        try:
            search = GoogleSerperAPIWrapper()
            results = search.results(f"{location} {property_type} rental listings average rent")
            items = results.get("organic", [])[:5]
            entries = []
            for it in items:
                title = it.get("title") or it.get("link")
                snippet = it.get("snippet", "")
                entries.append({"title": title, "snippet": snippet, "link": it.get("link")})
            return json.dumps({"results": entries, "langchain_enhanced": True})
        except Exception as e:
            logger.error(f"[Rent Estimation] LangChain search error: {e}")
            return json.dumps({"results": [], "error": str(e), "langchain_enhanced": False})

    @function_tool
    def analyze_rent_trends_with_langchain(historical_data: str) -> str:
        """
        Analyze rental trends from historical data using LangChain.
        """
        logger.info("[Rent Estimation] Analyzing rent trends with LangChain")
        try:
            data = json.loads(historical_data)
            loader = WebBaseLoader(data.get("source_url"))
            docs = loader.load()
            text = docs[0].page_content if docs else ""
            # simple placeholder analysis
            trend = "increasing" if "increase" in text else "stable"
            return json.dumps({"trend": trend, "langchain_enhanced": True})
        except Exception as e:
            logger.error(f"[Rent Estimation] Trend analysis error: {e}")
            return json.dumps({"trend": "unknown", "error": str(e), "langchain_enhanced": False})

def create_rent_estimation_agent() -> Agent:
    """Create and configure the Rent Estimation Agent."""
    
    logger.info("[Rent Estimation] Creating rent estimation agent")
    
    # Define agent instructions
    instructions = """
    You are a specialized Rent Estimation Agent for property investment analysis.
    
    Your task is to generate accurate rental estimates for properties based on:
    1. Property specifics (size, features, condition)
    2. Current market data and comparable properties
    3. Location-specific factors
    4. Legal limitations (like rent control)
    
    Follow these steps when processing requests:
    1. Retrieve property specifics (size, features, condition)
    2. Query database for comparable properties in location
    3. Analyze key factors affecting rent (renovations, amenities, etc.)
    4. Generate estimate with low/medium/high ranges
    5. Check against rent control limits (Mietpreisbremse) and flag if exceeded
    
    Your estimates should be well-reasoned and include confidence levels. 
    When legal rent control limitations apply, explicitly flag this in your response.
    Provide clear explanations for which property characteristics have the most significant 
    impact on your estimate.
    """
    
    from openai import AsyncAzureOpenAI
    from agents import set_default_openai_client
    from dotenv import load_dotenv
    import os

    # Load environment variables
    load_dotenv()
    logger.info("[Rent Estimation] Configuring integration with Azure OpenAI services")
    
    # Create OpenAI client using Azure OpenAI
    openai_client = AsyncAzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    )

    # Set the default OpenAI client for the Agents SDK
    set_default_openai_client(openai_client)
    logger.info("[Rent Estimation] OpenAI client configured for agent")

    # Define tools list
    tools = [query_market_data, analyze_comparables, parse_property_text]
    if has_langchain:
        tools.extend([search_rental_data_with_langchain, analyze_rent_trends_with_langchain])
    # Log the available tools
    tool_names = [tool.__name__ if hasattr(tool, '__name__') else tool.name for tool in tools]
    logger.info(f"[Rent Estimation] Setting up agent with tools: {', '.join(tool_names)}")

    # Create and return the agent
    agent = Agent(
        name="Rent Estimation Agent",
        instructions=instructions,
        model=OpenAIChatCompletionsModel(
            model="gpt-4o",
            openai_client=openai_client
        ),
        tools=tools
    )
    
    logger.info("[Rent Estimation] Rent estimation agent successfully initialized")
    return agent

# Add custom tool wrappers with enhanced logging for rent estimation
def estimate_rent_with_logging(location: str, property_details: Dict[str, Any]) -> RentEstimateResult:
    """
    Custom wrapper to perform rent estimation with enhanced logging.
    
    Args:
        location: Property location
        property_details: Dictionary containing property details
        
    Returns:
        RentEstimateResult containing the rent estimation
    """
    start_time = datetime.now()
    
    try:
        size_sqm = property_details.get("size_sqm", 0)
        property_type = property_details.get("property_type", "unknown")
        features = property_details.get("features", [])
        condition = property_details.get("condition", "average")
        
        logger.info(f"[Rent Estimation] Starting rent estimation for {size_sqm}sqm {property_type} in {location}")
        logger.info(f"[Rent Estimation] Property features: {', '.join(features)}")
        logger.info(f"[Rent Estimation] Property condition: {condition}")
        
        # Log that we're querying market data
        logger.info(f"[Rent Estimation] Querying comparable properties data for {location}")
        
        # Log analysis of key factors
        logger.info(f"[Rent Estimation] Analyzing factors affecting rental value")
        
        # Log rent control check if enabled
        check_rent_control = property_details.get("check_rent_control", True)
        if check_rent_control:
            logger.info(f"[Rent Estimation] Checking rent control regulations for {location}")
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"[Rent Estimation] Estimation completed in {execution_time:.2f} seconds")
        
        # Return dummy result for demonstration
        # In production, this would call the actual estimation logic
        return RentEstimateResult(
            property_address=f"{location}, Example St.",
            estimated_rent=1500,
            low_range=1400,
            high_range=1600,
            rent_per_sqm=15.0,
            comparable_properties=[],
            key_factors=["size", "location", "condition"],
            rent_control_flag=False,
            confidence_score=0.85,
            explanation="Example rent estimation."
        )
    except Exception as e:
        logger.error(f"[Rent Estimation] Error in rent estimation: {str(e)}")
        raise