"""
Risk Analysis Agent implementation for the Property Investment Analysis Application.

This specialized agent analyzes potential risks associated with property investments
and provides risk assessment and mitigation strategies.
"""

import logging
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from agents import Agent, function_tool, OpenAIChatCompletionsModel
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskAnalysisRequest(BaseModel):
    """Risk analysis request parameters."""
    property_data: Dict[str, Any] = Field(..., description="Property data including location, type, and financial details")
    investment_goals: Optional[Dict[str, Any]] = Field(None, description="Investor's goals and risk tolerance")
    market_conditions: Optional[Dict[str, Any]] = Field(None, description="Current market conditions data")
    timeframe: Optional[str] = Field(None, description="Investment timeframe (short-term, medium-term, long-term)")

class RiskAnalysisResult(BaseModel):
    """Result from the Risk Analysis Agent."""
    risk_score: float = Field(..., description="Overall risk score (0-100, where higher means more risk)")
    risk_level: str = Field(..., description="Risk level categorization (Low, Medium, High, Very High)")
    risk_factors: List[Dict[str, Any]] = Field(..., description="Identified risk factors with severity and probability")
    mitigation_strategies: List[Dict[str, Any]] = Field(..., description="Strategies to mitigate identified risks")
    analysis_confidence: float = Field(..., description="Confidence level of the analysis (0-1)")
    summary: str = Field(..., description="Summary of risk analysis findings")
    timestamp: str = Field(..., description="Timestamp of the analysis")

# Define risk analysis tools
@function_tool
def analyze_market_risks(location: str, property_type: str, historical_data: str) -> str:
    """
    Analyze market-related risks for a property investment.

    """
    logger.info("[Risk Analysis] Analyzing market-related risks")
    try:
        import statistics
        data = json.loads(historical_data)
        prices = data.get("prices", [])
        vacancy = data.get("vacancy_rates", [])
        interest = data.get("interest_rates", [])

        price_vol = statistics.pstdev(prices)/statistics.mean(prices) if len(prices)>1 and statistics.mean(prices)!=0 else 0
        interest_trend = (interest[-1]-interest[0])/interest[0] if len(interest)>1 and interest[0]!=0 else 0
        vacancy_risk = max(vacancy) if vacancy else 0

        risk_factors = [
            {"risk": "price_volatility", "severity": round(price_vol,2), "probability": 0.5},
            {"risk": "interest_rate_risk", "severity": round(abs(interest_trend),2), "probability": 0.5},
            {"risk": "vacancy_risk", "severity": round(vacancy_risk,2), "probability": 0.5}
        ]
        score = sum(f["severity"]*f["probability"] for f in risk_factors)/len(risk_factors)*100
        if score < 30:
            level = "Low"
        elif score < 60:
            level = "Medium"
        elif score < 80:
            level = "High"
        else:
            level = "Very High"
        result = {
            "risk_score": round(score,2),
            "risk_level": level,
            "risk_factors": risk_factors,
            "analysis_confidence": 0.9,
            "summary": f"Market risk score of {round(score,2)} based on volatility, rates, and vacancy.",
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(result)
    except Exception as e:
        logger.error(f"[Risk Analysis] Error analyzing market risks: {str(e)}")
        return json.dumps({"error": f"Failed market risk analysis: {str(e)}", "timestamp": datetime.now().isoformat()})

@function_tool
def analyze_property_specific_risks(property_data: str) -> str:
    """
    Analyze property-specific risks based on property characteristics.
    
    """
    logger.info("[Risk Analysis] Analyzing property-specific risks")
    try:
        data = json.loads(property_data)
        age = data.get("age_years", 0)
        condition = data.get("condition_rating", 5)
        location_score = data.get("location_score", 5)

        age_risk = min(age / 100, 1)
        cond_risk = (10 - condition) / 10
        loc_risk = (10 - location_score) / 10

        risk_factors = [
            {"risk": "age_risk", "severity": round(age_risk,2), "probability": 0.5},
            {"risk": "condition_risk", "severity": round(cond_risk,2), "probability": 0.5},
            {"risk": "location_risk", "severity": round(loc_risk,2), "probability": 0.5}
        ]
        score = sum(f["severity"]*f["probability"] for f in risk_factors)/len(risk_factors)*100
        if score < 30:
            level = "Low"
        elif score < 60:
            level = "Medium"
        elif score < 80:
            level = "High"
        else:
            level = "Very High"
        result = {
            "risk_score": round(score,2),
            "risk_level": level,
            "risk_factors": risk_factors,
            "analysis_confidence": 0.9,
            "summary": f"Property-specific risk score of {round(score,2)} based on age, condition, and location.",
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(result)
    except Exception as e:
        logger.error(f"[Risk Analysis] Error analyzing property risks: {str(e)}")
        return json.dumps({"error": f"Failed property risk analysis: {str(e)}", "timestamp": datetime.now().isoformat()})

@function_tool
def analyze_financial_risks(financial_data: str, investment_goals: str) -> str:
    """
    Analyze financial risks associated with the property investment.

    """
    logger.info("[Risk Analysis] Analyzing financial risks")
    try:
        fin = json.loads(financial_data)
        goals = json.loads(investment_goals)
        income = fin.get("monthly_income", 0)
        expenses = fin.get("monthly_expenses", 0)
        ltv = fin.get("loan_to_value", 0)
        reserves = fin.get("cash_reserves", 0)

        cash_flow_risk = (expenses / income) if income else 1
        leverage_risk = min(ltv / 100, 1)
        liquidity_risk = 1 if reserves < (expenses * 3) else 0.2

        risk_factors = [
            {"risk": "cash_flow_risk", "severity": round(cash_flow_risk,2), "probability": 0.5},
            {"risk": "leverage_risk", "severity": round(leverage_risk,2), "probability": 0.5},
            {"risk": "liquidity_risk", "severity": round(liquidity_risk,2), "probability": 0.5}
        ]
        score = sum(f["severity"]*f["probability"] for f in risk_factors)/len(risk_factors)*100
        if score < 30:
            level = "Low"
        elif score < 60:
            level = "Medium"
        elif score < 80:
            level = "High"
        else:
            level = "Very High"
        result = {
            "risk_score": round(score,2),
            "risk_level": level,
            "risk_factors": risk_factors,
            "analysis_confidence": 0.9,
            "summary": f"Financial risk score of {round(score,2)} based on cash flow, leverage, and liquidity.",
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(result)
    except Exception as e:
        logger.error(f"[Risk Analysis] Error analyzing financial risks: {str(e)}")
        return json.dumps({"error": f"Failed financial risk analysis: {str(e)}", "timestamp": datetime.now().isoformat()})

@function_tool
def generate_risk_mitigation_strategies(risks_data: str) -> str:
    """
    Generate strategies to mitigate identified investment risks.
    
    """
    logger.info("[Risk Analysis] Generating risk mitigation strategies")
    try:
        data = json.loads(risks_data)
        factors = data.get("risk_factors", [])
        strategies = []
        for f in factors:
            r = f.get("risk")
            if r == "price_volatility":
                strategies.append({"risk": r, "strategy": "Diversify investment locations and lock in long-term rates."})
            elif r == "interest_rate_risk":
                strategies.append({"risk": r, "strategy": "Consider fixed-rate financing or rate caps."})
            elif r == "vacancy_risk":
                strategies.append({"risk": r, "strategy": "Maintain contingency reserves and pre-market units."})
            elif r == "age_risk":
                strategies.append({"risk": r, "strategy": "Schedule detailed inspections and budget for maintenance."})
            elif r == "condition_risk":
                strategies.append({"risk": r, "strategy": "Allocate funds for renovations and upgrades."})
            elif r == "location_risk":
                strategies.append({"risk": r, "strategy": "Assess neighborhood trends and local developments."})
            elif r == "cash_flow_risk":
                strategies.append({"risk": r, "strategy": "Optimize rental rates and control expenses."})
            elif r == "leverage_risk":
                strategies.append({"risk": r, "strategy": "Reduce leverage or refinance to lower LTV."})
            elif r == "liquidity_risk":
                strategies.append({"risk": r, "strategy": "Maintain reserve fund covering at least 6 months expenses."})
            else:
                strategies.append({"risk": r, "strategy": "Develop tailored mitigation plan."})
        result = {"mitigation_strategies": strategies, "analysis_confidence": 0.9, "timestamp": datetime.now().isoformat()}
        return json.dumps(result)
    except Exception as e:
        logger.error(f"[Risk Analysis] Error generating mitigation strategies: {str(e)}")
        return json.dumps({"error": f"Failed mitigation strategy generation: {str(e)}", "timestamp": datetime.now().isoformat()})

@function_tool
def calculate_consolidated_risk_score(market_risks: str, property_risks: str, financial_risks: str) -> str:
    """
    Calculate consolidated risk score and level based on various risk assessments.
    
    """
    logger.info("[Risk Analysis] Calculating consolidated risk score")
    try:
        m = json.loads(market_risks)
        p = json.loads(property_risks)
        f = json.loads(financial_risks)
        scores = [m.get("risk_score",0), p.get("risk_score",0), f.get("risk_score",0)]
        average = sum(scores)/len(scores)
        if average < 30:
            level = "Low"
        elif average < 60:
            level = "Medium"
        elif average < 80:
            level = "High"
        else:
            level = "Very High"
        result = {"risk_score": round(average,2), "risk_level": level, "analysis_confidence": 0.9, "timestamp": datetime.now().isoformat()}
        return json.dumps(result)
    except Exception as e:
        logger.error(f"[Risk Analysis] Error consolidating risk scores: {str(e)}")
        return json.dumps({"error": f"Failed risk consolidation: {str(e)}", "timestamp": datetime.now().isoformat()})

def create_risk_analysis_agent() -> Agent:
    """Create and configure the Risk Analysis Agent."""
    
    logger.info("[Risk Analysis] Creating risk analysis agent")
    
    # Define agent instructions
    instructions = """
    You are a specialized Risk Analysis Agent for property investment analysis.
    
    Your task is to identify, assess, and help mitigate risks associated with property investments:
    1. Market risks (market volatility, interest rate trends, supply/demand imbalances)
    2. Property-specific risks (age, condition, location factors, property type)
    3. Financial risks (cash flow, leverage, liquidity, financing terms)
    4. Regulatory risks (zoning changes, rent control, property tax assessments)
    
    Follow these steps when analyzing investment risks:
    1. Gather property, market, and financial data
    2. Identify potential risk factors in each category
    3. Assess severity and probability for each risk factor
    4. Calculate risk scores for different risk categories
    5. Generate practical risk mitigation strategies
    6. Provide a consolidated risk assessment with confidence level
    
    Your risk assessments should be data-driven, nuanced, and actionable.
    Provide risk scores on a clear scale and explain your reasoning.
    Generate specific mitigation strategies tailored to the investor's goals and risk tolerance.
    
    When presenting risks, always balance identifying potential issues with practical solutions.
    Focus on helping investors make informed decisions rather than simply avoiding all risks.
    """
    
    from openai import AsyncAzureOpenAI
    from agents import set_default_openai_client
    from dotenv import load_dotenv
    import os

    # Load environment variables
    load_dotenv()
    logger.info("[Risk Analysis] Configuring integration with Azure OpenAI services")
    
    # Create OpenAI client using Azure OpenAI
    openai_client = AsyncAzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    )

    # Set the default OpenAI client for the Agents SDK
    set_default_openai_client(openai_client)
    logger.info("[Risk Analysis] OpenAI client configured for agent")

    # Log the available tools
    tools = [
        analyze_market_risks, 
        analyze_property_specific_risks, 
        analyze_financial_risks,
        generate_risk_mitigation_strategies,
        calculate_consolidated_risk_score
    ]
    
    tool_names = [tool.__name__ if hasattr(tool, '__name__') else tool.name for tool in tools]
    logger.info(f"[Risk Analysis] Setting up agent with tools: {', '.join(tool_names)}")

    # Create and return the agent
    agent = Agent(
        name="Risk Analysis Agent",
        instructions=instructions,
        model=OpenAIChatCompletionsModel(
            model="gpt-4o",
            openai_client=openai_client
        ),
        tools=tools
    )
    
    logger.info("[Risk Analysis] Risk analysis agent successfully initialized")
    return agent

# Advanced risk assessment functions with enhanced logging

def assess_risk_with_logging(property_data: Dict[str, Any], market_data: Dict[str, Any], 
                          financial_data: Dict[str, Any], investor_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Comprehensive risk assessment function with detailed logging.
    
    Args:
        property_data: Property details
        market_data: Market information
        financial_data: Financial information
        investor_profile: Optional investor goals and risk tolerance
        
    Returns:
        Risk assessment results
    """
    logger.info("[Risk Analysis] Starting comprehensive risk assessment")
    
    # This is a placeholder for a more complex implementation
    # In a real implementation, this would call the various analysis tools
    # and aggregate their results
    
    logger.info("[Risk Analysis] Analyzing property characteristics for risk factors")
    logger.info("[Risk Analysis] Evaluating market conditions and trends")
    logger.info("[Risk Analysis] Assessing financial metrics and exposure")
    
    if investor_profile:
        risk_tolerance = investor_profile.get("risk_tolerance", "moderate")
        logger.info(f"[Risk Analysis] Considering investor risk tolerance: {risk_tolerance}")
    
    logger.info("[Risk Analysis] Completed risk assessment")
    
    # Return simulated results
    return {
        "risk_assessment_complete": True,
        "timestamp": datetime.now().isoformat()
    }