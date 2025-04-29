"""
Market Data Search Agent implementation for the Property Investment Analysis Application.

This specialized agent collects current rental rates, property values, vacancy rates, 
and market trends for target locations using LangChain tools for enhanced search capabilities.
"""

import logging
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from agents import Agent, function_tool, OpenAIChatCompletionsModel
from pydantic import BaseModel, Field

# Import original investment tools
from ..tools.investment_tools import (
    web_search,
    parse_market_data,
    query_market_data,
    gather_historical_data,
    search_development_news
)

# Import LangChain prompt templates
from langchain_core.prompts import (
    ChatPromptTemplate, 
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if LangChain dependencies are available
try:
    from langchain_community.utilities import GoogleSerperAPIWrapper, WikipediaAPIWrapper
    from langchain_core.tools import Tool
    from langchain_community.document_loaders import WebBaseLoader
    from langchain_community.tools.tavily_search import TavilySearchResults
    from langchain_community.tools.pubmed.tool import PubmedQueryRun
    has_langchain = True
    logger.info("[Market Data] LangChain dependencies successfully loaded")
except ImportError:
    has_langchain = False
    logger.warning("[Market Data] LangChain dependencies not found, will use basic search tools only")

class MarketDataRequest(BaseModel):
    """Market data request parameters."""
    location: str = Field(..., description="The target location for market data (city, neighborhood, postal code)")
    property_type: str = Field(..., description="Type of property (residential, commercial, multi-family, etc.)")
    data_types: List[str] = Field(..., description="Types of data to collect (prices, rents, trends, vacancy, development)")
    timeframe: Optional[str] = Field("5 years", description="Historical timeframe for trend data")
    
    model_config = {
        "extra": "forbid"
    }

class MarketDataResult(BaseModel):
    """Result from the Market Data Search Agent."""
    location: str = Field(..., description="Location for which data was collected")
    property_type: str = Field(..., description="Type of property for which data was collected")
    price_data: Dict[str, Any] = Field(..., description="Property price data and trends")
    rental_data: Dict[str, Any] = Field(..., description="Rental rate data and trends")
    historical_data: Optional[Dict[str, Any]] = Field(None, description="Historical market data if requested")
    development_news: Optional[List[Dict[str, Any]]] = Field(None, description="Development projects and news")
    confidence_scores: Dict[str, float] = Field(..., description="Confidence scores for various data points")
    sources: List[str] = Field(..., description="Sources of market data")
    timestamp: str = Field(..., description="Timestamp of data collection")
    
    model_config = {
        "extra": "forbid"
    }

# Define LangChain-enhanced market data tools
if has_langchain:
    @function_tool
    def search_market_data_with_langchain(location: str, property_type: str, data_type: str) -> str:
        """
        Search for real estate market data using LangChain's enhanced search capabilities.
        
        Args:
            location: The location to search for (city, neighborhood, postal code)
            property_type: Type of property (residential, commercial, multi-family, etc.)
            data_type: Type of data to search for (prices, rents, trends, vacancy, development)
            
        Returns:
            JSON string containing market data search results
        """
        logger.info(f"[Market Data] Searching for {data_type} data in {location} for {property_type} properties using LangChain")
        
        try:
            # Create a search query based on parameters
            search_query = f"{location} {property_type} real estate {data_type} {datetime.now().year}"
            
            # Initialize search tool - use Google Serper if API key is available, otherwise fallback
            import os
            serper_api_key = os.getenv("SERPER_API_KEY")
            tavily_api_key = os.getenv("TAVILY_API_KEY")
            
            search_results = []
            
            if serper_api_key:
                logger.info(f"[Market Data] Using Serper API for enhanced search")
                search = GoogleSerperAPIWrapper()
                results = search.results(search_query)
                search_results = results.get("organic", [])
            elif tavily_api_key:
                logger.info(f"[Market Data] Using Tavily Search API")
                search_tool = TavilySearchResults()
                results = search_tool.invoke({"query": search_query})
                search_results = results
            else:
                logger.warning(f"[Market Data] No search API keys found, using basic web search")
                # Fall back to basic web search
                basic_results = json.loads(web_search(location, data_type))
                return json.dumps({
                    "results": [basic_results],
                    "source": "basic_web_search",
                    "langchain_enhanced": False
                })
            
            # Process search results
            processed_results = []
            for result in search_results[:5]:  # Limit to top 5 results
                title = result.get("title", "")
                link = result.get("link", "")
                snippet = result.get("snippet", "")
                
                if not title or not link:
                    continue
                
                # Try to extract data from the webpage if it's accessible
                try:
                    loader = WebBaseLoader(link)
                    docs = loader.load()
                    content = docs[0].page_content if docs else ""
                    logger.info(f"[Market Data] Successfully loaded content from {link}")
                except Exception as e:
                    logger.warning(f"[Market Data] Could not load content from {link}: {str(e)}")
                    content = snippet
                
                # Extract relevant data points based on data_type
                data_points = {}
                
                if "price" in data_type:
                    import re
                    # Look for price patterns (e.g., $X,XXX per square foot or €X,XXX per square meter)
                    price_patterns = [
                        r'\$(\d{1,3}(?:,\d{3})*(?:\.\d+)?)(?:\s+(?:per|\/)\s+(?:sq\.?(?:\s+ft\.?|\')?|square\s+foot|sqft))',
                        r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s+(?:USD|EUR|€|\$)(?:\s+(?:per|\/)\s+(?:sq\.?(?:\s+ft\.?|\')?|square\s+foot|sqft|m²|square\s+meter))',
                        r'average(?:\s+price|\s+value|\s+cost)(?:\s+of)?\s+\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
                        r'median(?:\s+price|\s+value|\s+cost)(?:\s+of)?\s+\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)'
                    ]
                    
                    for pattern in price_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            # Extract the first match and convert to float
                            try:
                                data_points["price_value"] = float(matches[0].replace(',', ''))
                                break
                            except (ValueError, IndexError):
                                continue
                
                if "rent" in data_type:
                    import re
                    # Look for rental rate patterns
                    rent_patterns = [
                        r'average(?:\s+monthly)?\s+rent(?:\s+of)?\s+\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
                        r'median(?:\s+monthly)?\s+rent(?:\s+of)?\s+\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
                        r'rent(?:al)?\s+rates?(?:\s+of)?\s+\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
                        r'rent(?:s)?\s+for\s+\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)'
                    ]
                    
                    for pattern in rent_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            try:
                                data_points["rent_value"] = float(matches[0].replace(',', ''))
                                break
                            except (ValueError, IndexError):
                                continue
                
                if "vacancy" in data_type:
                    import re
                    # Look for vacancy rate patterns
                    vacancy_patterns = [
                        r'vacancy\s+rate(?:\s+of)?\s+(\d{1,2}(?:\.\d+)?)%',
                        r'(\d{1,2}(?:\.\d+)?)%\s+vacancy\s+rate',
                        r'vacancy(?:\s+is)?(?:\s+at)?\s+(\d{1,2}(?:\.\d+)?)%'
                    ]
                    
                    for pattern in vacancy_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            try:
                                data_points["vacancy_rate"] = float(matches[0])
                                break
                            except (ValueError, IndexError):
                                continue
                
                if "trend" in data_type:
                    import re
                    # Look for trend patterns
                    trend_patterns = [
                        r'(increas|decreas|appreciation|depreciation|grew|declined)(?:ed|ing)?\s+(?:by)?\s+(\d{1,2}(?:\.\d+)?)%',
                        r'(\d{1,2}(?:\.\d+)?)%\s+(increas|decreas|appreciation|depreciation|growth|decline)',
                        r'(upward|downward)\s+trend'
                    ]
                    
                    # Try to identify trends
                    trend_matches = []
                    for pattern in trend_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            trend_matches.extend(matches)
                    
                    if trend_matches:
                        data_points["trends"] = trend_matches
                
                processed_results.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet,
                    "data_points": data_points
                })
            
            # Calculate confidence score based on number of sources and consistency
            confidence_score = min(len(processed_results) / 5, 1.0)  # 0.0-1.0 based on number of sources
            
            logger.info(f"[Market Data] Found {len(processed_results)} relevant results with confidence {confidence_score:.2f}")
            
            return json.dumps({
                "results": processed_results,
                "source": "langchain_search",
                "confidence_score": confidence_score,
                "langchain_enhanced": True
            })
            
        except Exception as e:
            logger.error(f"[Market Data] Error using LangChain search: {str(e)}")
            # Fallback to basic web search
            basic_results = json.loads(web_search(location, data_type))
            return json.dumps({
                "results": [basic_results],
                "source": "basic_web_search_fallback",
                "langchain_enhanced": False,
                "error": str(e)
            })
    
    @function_tool
    def analyze_market_trends_with_langchain(historical_data: str, location: str, property_type: str) -> str:
        """
        Analyze market trends using LangChain tools and historical data.
        
        Args:
            historical_data: JSON string with historical market data
            location: The location to analyze
            property_type: Type of property
            
        Returns:
            JSON string containing trend analysis
        """
        logger.info(f"[Market Data] Analyzing market trends for {property_type} in {location} using LangChain")
        
        try:
            # Parse historical data
            data = json.loads(historical_data)
            
            # Search for relevant academic and economic research
            import os
            if os.getenv("PUBMED_API_KEY"):
                logger.info(f"[Market Data] Using PubMed API for research on real estate trends")
                pubmed_tool = PubmedQueryRun()
                research_query = f"real estate market trends {property_type} economic factors"
                research_results = pubmed_tool.invoke({"query": research_query})
            else:
                research_results = "No academic research API available"
            
            # Use Wikipedia for additional context
            wiki_tool = WikipediaAPIWrapper()
            wiki_query = f"{location} real estate market"
            try:
                wiki_results = wiki_tool.run(wiki_query)
                logger.info(f"[Market Data] Found Wikipedia information about {location} real estate")
            except Exception as e:
                logger.warning(f"[Market Data] Error retrieving Wikipedia data: {str(e)}")
                wiki_results = "No Wikipedia data available"
            
            # Process historical data to identify trends
            # This is a placeholder for actual trend analysis
            processed_trends = {
                "price_trends": {
                    "direction": "increasing" if "increasing" in str(data) else "stable",
                    "rate": "5.2% annually",  # Placeholder
                    "confidence": 0.85
                },
                "rental_trends": {
                    "direction": "increasing" if "increasing" in str(data) else "stable",
                    "rate": "3.8% annually",  # Placeholder
                    "confidence": 0.8
                },
                "vacancy_trends": {
                    "direction": "decreasing" if "decreasing" in str(data) else "stable",
                    "rate": "0.5% annually",  # Placeholder
                    "confidence": 0.75
                },
                "forecast": {
                    "short_term": "Continued growth expected",
                    "medium_term": "Stabilization likely as interest rates adjust",
                    "confidence": 0.65
                }
            }
            
            # Enrich with research insights
            research_insights = []
            if "research" in str(research_results):
                research_insights.append("Academic research suggests correlation between economic indicators and real estate performance")
            if "market cycle" in str(research_results):
                research_insights.append("Research indicates current position in market cycle may be approaching peak")
            
            # Add wiki insights if available
            wiki_insights = []
            if len(wiki_results) > 100:
                wiki_insights.append("Local market factors identified from regional data")
                if "development" in wiki_results:
                    wiki_insights.append("Urban development projects may influence future property values")
            
            logger.info(f"[Market Data] Completed trend analysis with {len(research_insights)} research insights")
            
            return json.dumps({
                "trend_analysis": processed_trends,
                "research_insights": research_insights,
                "wiki_insights": wiki_insights,
                "analysis_timestamp": datetime.now().isoformat(),
                "langchain_enhanced": True
            })
            
        except Exception as e:
            logger.error(f"[Market Data] Error analyzing market trends with LangChain: {str(e)}")
            # Fallback to basic analysis
            return json.dumps({
                "trend_analysis": {
                    "price_trends": {"direction": "unknown", "confidence": 0.5},
                    "rental_trends": {"direction": "unknown", "confidence": 0.5},
                    "vacancy_trends": {"direction": "unknown", "confidence": 0.5}
                },
                "langchain_enhanced": False,
                "error": str(e)
            })

def create_market_data_search_agent() -> Agent:
    """Create and configure the Market Data Search Agent with LangChain enhancements if available."""
    
    logger.info("[Market Data] Creating Market Data Search Agent with prompt templates")
    # Define system and human prompt templates
    system_prompt = SystemMessagePromptTemplate.from_template(
        """
You are a specialized Market Data Search Agent for property investment analysis.
Gather market data for {location} focusing on: {data_types} for {property_type} properties.
Include current rental rates, property values, vacancy rates, trends, historical data, and development news.
Always provide confidence scores and cite sources.
Use LangChain-enhanced tools when available to extract precise data points from authoritative sources.
"""
    )
    human_prompt = HumanMessagePromptTemplate.from_template(
        "Process request with parameters: location={location}, property_type={property_type}, data_types={data_types}, timeframe={timeframe}"
    )
    prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])

    from openai import AsyncAzureOpenAI
    from agents import set_default_openai_client
    from dotenv import load_dotenv
    import os

    # Load environment variables
    load_dotenv()
    logger.info("[Market Data] Loading environment variables")
    
    # Create OpenAI client using Azure OpenAI
    openai_client = AsyncAzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
    )

    # Set the default OpenAI client for the Agents SDK
    set_default_openai_client(openai_client)
    logger.info("[Market Data] Configured Azure OpenAI client")
    
    # Define tools based on available dependencies
    tools = [
        web_search,
        parse_market_data,
        query_market_data,
        gather_historical_data,
        search_development_news
    ]
    
    # Add LangChain-enhanced tools if available
    if has_langchain:
        tools.extend([
            search_market_data_with_langchain,
            analyze_market_trends_with_langchain
        ])
        logger.info("[Market Data] Added LangChain-enhanced tools")
    
    # Log the available tools
    tool_names = [tool.__name__ if hasattr(tool, '__name__') else tool.name for tool in tools]
    logger.info(f"[Market Data] Setting up agent with tools: {', '.join(tool_names)}")
    
    # Create and return the agent using the prompt template
    agent = Agent(
        name="Market Data Search Agent",
        instructions=prompt,
        model=OpenAIChatCompletionsModel(
            model="gpt-4o",
            openai_client=openai_client
        ),
        tools=tools
    )
    
    logger.info("[Market Data] Market Data Search Agent successfully initialized")
    return agent

# Utility functions for the Market Data Agent

def extract_market_data_from_results(results: List[Dict[str, Any]], data_type: str) -> Dict[str, Any]:
    """
    Extract specific market data from search results.
    
    Args:
        results: List of search result objects
        data_type: Type of data to extract (prices, rents, etc.)
        
    Returns:
        Dictionary with extracted data points
    """
    logger.info(f"[Market Data] Extracting {data_type} data from {len(results)} results")
    
    # This would be expanded in a production implementation
    extracted_data = {
        "values": [],
        "sources": [],
        "average": None,
        "confidence": 0.0
    }
    
    if not results:
        return extracted_data
    
    # Process each result
    for result in results:
        # The actual processing would depend on the structure of the results
        # This is a placeholder implementation
        if isinstance(result, dict):
            if "data_points" in result and data_type in result.get("data_points", {}):
                value = result["data_points"][data_type]
                extracted_data["values"].append(value)
                extracted_data["sources"].append(result.get("link", "unknown"))
    
    # Calculate average if values are available
    if extracted_data["values"]:
        try:
            extracted_data["average"] = sum(extracted_data["values"]) / len(extracted_data["values"])
            # Confidence based on number of sources and variance
            extracted_data["confidence"] = min(len(extracted_data["values"]) / 5, 1.0)
        except (TypeError, ValueError):
            # Handle case where values might not be numeric
            extracted_data["average"] = None
            extracted_data["confidence"] = 0.0
    
    return extracted_data

def calculate_data_confidence(data_points: List[Any], variance_threshold: float = 0.2) -> float:
    """
    Calculate confidence score based on number of data points and their variance.
    
    Args:
        data_points: List of numeric data points
        variance_threshold: Threshold for acceptable variance
        
    Returns:
        Confidence score between 0.0 and 1.0
    """
    if not data_points:
        return 0.0
    
    try:
        # Convert all data points to float
        numeric_points = [float(p) for p in data_points if p is not None]
        if not numeric_points:
            return 0.0
        
        # Calculate mean and variance
        mean = sum(numeric_points) / len(numeric_points)
        if mean == 0:
            return 0.0
        
        # Calculate normalized variance
        variances = [(p - mean) ** 2 for p in numeric_points]
        variance = sum(variances) / len(numeric_points)
        normalized_variance = variance / (mean ** 2)
        
        # Calculate source factor (more sources = higher confidence)
        source_factor = min(len(numeric_points) / 5, 1.0)
        
        # Calculate variance factor (lower variance = higher confidence)
        variance_factor = max(0, 1.0 - (normalized_variance / variance_threshold))
        
        # Combine factors (equal weighting)
        confidence = (source_factor + variance_factor) / 2
        
        return min(1.0, max(0.0, confidence))
    except (TypeError, ValueError, ZeroDivisionError):
        return 0.0