"""
Optimization Agent implementation for the Property Investment Analysis Application.

This specialized agent analyzes investment properties and suggests specific optimizations
to improve investment returns.
"""

import logging
from typing import Dict, Any, List, Optional
import json

from agents import Agent, function_tool, OpenAIChatCompletionsModel
from pydantic import BaseModel

from ..tools.investment_tools import (
    analyze_investment_efficiency,
    simulate_optimizations,
    generate_section_explanation
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizationRequest(BaseModel):
    """Optimization request parameters."""
    property_data: Dict[str, Any]
    financial_data: Dict[str, Any]
    investor_goals: Optional[Dict[str, Any]] = None

class OptimizationResult(BaseModel):
    """Result from the Optimization Agent."""
    recommendations: List[Dict[str, Any]]
    projected_impact: Dict[str, Any]
    implementation_costs: Dict[str, Any]
    prioritized_actions: List[Dict[str, Any]]
    timeframes: Dict[str, Any]
    explanation: str

def create_optimization_agent() -> Agent:
    """Create and configure the Optimization Agent."""
    
    # Define agent instructions
    instructions = """
    You are a specialized Optimization Recommendation Agent for property investment analysis.
    
    Your task is to analyze investment properties and suggest specific optimizations to improve returns:
    1. Review complete property and financial data
    2. Identify potentially suboptimal aspects (financing, rent, expenses)
    3. Generate possible optimization strategies
    4. Simulate impact of each strategy on ROI and cash flow
    5. Prioritize recommendations by implementation cost and benefit
    6. Provide specific implementation steps with timeframes
    
    Focus on practical, actionable recommendations in these key areas:
    - Financing adjustments (refinancing, changing loan terms)
    - Rental income optimization (rent adjustments, unit improvements)
    - Expense reduction (management fees, maintenance costs)
    - Tax benefit maximization (depreciation strategies, deductible expenses)
    - Property improvements with positive ROI
    
    Always prioritize recommendations by:
    1. Ease of implementation (low effort to high effort)
    2. Cost to implement (low cost to high cost)
    3. Expected impact on returns (high impact to low impact)
    4. Time to realize benefits (immediate to long-term)
    
    Provide specific, numeric projections for how each recommendation would affect:
    - Monthly cash flow
    - Cash-on-cash return
    - Overall ROI
    - Implementation costs
    - Payback period
    
    Ensure all recommendations comply with legal requirements and include any risks or potential downsides.
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
        name="Optimization Agent",
        instructions=instructions,
        model=OpenAIChatCompletionsModel(
            model="gpt-4o",
            openai_client=openai_client
        ),
        tools=[
            analyze_investment_efficiency,
            simulate_optimizations,
            generate_section_explanation
        ]
    )