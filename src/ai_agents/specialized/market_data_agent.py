"""
Market Data Search Agent implementation for the Property Investment Analysis Application.

This specialized agent collects current rental rates, property values, vacancy rates, 
and market trends for target locations.
"""

import logging
from typing import Dict, Any, List, Optional
import json

from agents import Agent, function_tool, OpenAIChatCompletionsModel
from pydantic import BaseModel

from ..tools.investment_tools import (
    web_search,
    parse_market_data,
    query_market_data,
    gather_historical_data,
    search_development_news
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketDataRequest(BaseModel):
    """Market data request parameters."""
    location: str
    property_type: str
    data_types: List[str]
    timeframe: Optional[str] = "5 years"
    
    model_config = {
        "extra": "forbid"
    }

class MarketDataResult(BaseModel):
    """Result from the Market Data Search Agent."""
    location: str
    property_type: str
    price_data: Dict[str, Any]
    rental_data: Dict[str, Any]
    historical_data: Optional[Dict[str, Any]] = None
    development_news: Optional[List[Dict[str, Any]]] = None
    confidence_scores: Dict[str, float]
    sources: List[str]
    timestamp: str
    
    model_config = {
        "extra": "forbid"
    }

def create_market_data_search_agent() -> Agent:
    """Create and configure the Market Data Search Agent."""
    
    # Define agent instructions
    instructions = """
    You are a specialized Market Data Search Agent for property investment analysis.
    
    Your task is to gather up-to-date market data for target property locations, including:
    1. Current rental rates
    2. Property values
    3. Vacancy rates
    4. Market trends
    5. Historical price and rent data
    6. Development projects and news
    
    Follow these steps when processing requests:
    1. Accept location and data type parameters
    2. Determine appropriate sources based on data type
    3. Execute web search with appropriate queries
    4. Parse and validate results with confidence scores
    5. Store validated data with timestamps and source citations
    
    Always include confidence scores for all data points and cite sources for all information.
    Flag any inconsistent or contradictory data from different sources.
    """
    from openai import AsyncAzureOpenAI
    from agents import set_default_openai_client
    from dotenv import load_dotenv
    import os

    # Load environment variables
    load_dotenv()
    # Create OpenAI client using Azure OpenAI
    openai_client = AsyncAzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    )

    # Set the default OpenAI client for the Agents SDK
    set_default_openai_client(openai_client)
    # Create and return the agent
    return Agent(
        name="Market Data Search Agent",
        instructions=instructions,
        model=OpenAIChatCompletionsModel(
            model="gpt-4o",
            openai_client=openai_client
        ),
        tools=[
            web_search,
            parse_market_data,
            query_market_data,
            gather_historical_data,
            search_development_news
        ]
    )