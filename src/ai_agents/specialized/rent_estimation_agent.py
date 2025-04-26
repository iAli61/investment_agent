"""
Rent Estimation Agent implementation for the Property Investment Analysis Application.

This specialized agent generates rental estimates based on property specifics and market data.
"""

import logging
from typing import Dict, Any, List, Optional
import json

from agents import Agent, function_tool
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

def create_rent_estimation_agent() -> Agent:
    """Create and configure the Rent Estimation Agent."""
    
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
    
    # Create and return the agent
    return Agent(
        name="Rent Estimation Agent",
        instructions=instructions,
        tools=[
            query_market_data,
            analyze_comparables,
            parse_property_text
        ]
    )