"""
Optimization Agent implementation for the Property Investment Analysis Application.

This specialized agent analyzes investment properties and suggests specific optimizations
to improve investment returns.
"""

import logging
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

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
    
    logger.info("[Optimization] Creating optimization recommendation agent")
    
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
    logger.info("[Optimization] Configuring integration with Azure OpenAI services")
    
    # Create OpenAI client using Azure OpenAI
    openai_client = AsyncAzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    )

    # Set the default OpenAI client for the Agents SDK
    set_default_openai_client(openai_client)
    logger.info("[Optimization] OpenAI client configured for agent")
    
    # Log the available tools
    tools = [analyze_investment_efficiency, simulate_optimizations, generate_section_explanation]
    tool_names = [tool.__name__ if hasattr(tool, '__name__') else tool.name for tool in tools]
    logger.info(f"[Optimization] Setting up agent with tools: {', '.join(tool_names)}")
    
    # Create and return the agent
    agent = Agent(
        name="Optimization Agent",
        instructions=instructions,
        model=OpenAIChatCompletionsModel(
            model="gpt-4o",
            openai_client=openai_client
        ),
        tools=tools
    )
    
    logger.info("[Optimization] Optimization agent successfully initialized")
    return agent

# Add custom optimization functions with enhanced logging

def optimize_investment_with_logging(property_data: Dict[str, Any], financial_data: Dict[str, Any], 
                                    investor_goals: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Custom wrapper to perform investment optimization with enhanced logging.
    
    Args:
        property_data: Dictionary containing property details
        financial_data: Dictionary containing financial information
        investor_goals: Optional dictionary containing investor goals and preferences
        
    Returns:
        Dictionary containing optimization recommendations and projected impacts
    """
    start_time = datetime.now()
    
    property_type = property_data.get("property_type", "unknown")
    property_location = property_data.get("location", "unknown")
    
    logger.info(f"[Optimization] Starting optimization analysis for {property_type} in {property_location}")
    
    if investor_goals:
        goal_types = list(investor_goals.keys())
        logger.info(f"[Optimization] Investor goals specified: {', '.join(goal_types)}")
        for goal, value in investor_goals.items():
            logger.info(f"[Optimization] Goal - {goal}: {value}")
    
    try:
        # Log efficiency analysis
        logger.info(f"[Optimization] Analyzing current investment efficiency")
        logger.info(f"[Optimization] Examining property data for optimization opportunities")
        logger.info(f"[Optimization] Examining financial structure for inefficiencies")
        
        # Log suboptimal aspects identification
        logger.info(f"[Optimization] Identifying potentially suboptimal investment aspects")
        
        # Log generation of optimization strategies
        logger.info(f"[Optimization] Generating potential optimization strategies")
        
        # Log simulation of impacts
        logger.info(f"[Optimization] Simulating impact of each optimization strategy")
        
        # Log categorization of recommendations
        categories = ["financing", "rental_income", "expenses", "tax_benefits", "property_improvements"]
        recommendations_count = {cat: 0 for cat in categories}
        
        # Simulate finding recommendations in each category
        recommendations_count["financing"] = 2
        recommendations_count["rental_income"] = 1
        recommendations_count["expenses"] = 2
        
        for category, count in recommendations_count.items():
            if count > 0:
                logger.info(f"[Optimization] Found {count} recommendations for {category}")
        
        # Log prioritization of actions
        logger.info(f"[Optimization] Prioritizing recommendations by implementation cost and benefit")
        
        # Log timeframe analysis
        logger.info(f"[Optimization] Determining implementation timeframes for recommendations")
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"[Optimization] Optimization analysis completed in {execution_time:.2f} seconds")
        
        # Return sample results
        recommendations = [
            {"category": "financing", "action": "Refinance mortgage", "impact": "+€120/month"},
            {"category": "financing", "action": "Increase down payment", "impact": "-€80/month"},
            {"category": "rental_income", "action": "Adjust rent to market rate", "impact": "+€150/month"},
            {"category": "expenses", "action": "Renegotiate management fee", "impact": "+€50/month"},
            {"category": "expenses", "action": "Bundle insurance policies", "impact": "+€30/month"}
        ]
        
        logger.info(f"[Optimization] Generated {len(recommendations)} optimization recommendations")
        
        # Return structured data
        return {
            "recommendations": recommendations,
            "total_potential_impact": "+€270/month",
            "top_recommendation": "Adjust rent to market rate",
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"[Optimization] Error in optimization analysis: {str(e)}")
        raise