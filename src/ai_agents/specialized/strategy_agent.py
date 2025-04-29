"""
Strategy Agent implementation for the Property Investment Analysis Application.

This specialized agent creates comprehensive investment strategies for property investments
based on financial data, risk analysis, and investor goals.
"""

import logging
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from agents import Agent, function_tool, OpenAIChatCompletionsModel
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StrategyRequest(BaseModel):
    """Strategy request parameters."""
    property_data: Dict[str, Any] = Field(..., description="Property data including location, type, and financial details")
    financial_data: Dict[str, Any] = Field(..., description="Financial data including purchase price, income, expenses, etc.")
    investment_goals: Dict[str, Any] = Field(..., description="Investor's goals, risk tolerance, and timeframe")
    risk_analysis: Optional[Dict[str, Any]] = Field(None, description="Results from risk analysis if available")
    market_data: Optional[Dict[str, Any]] = Field(None, description="Market data for the location if available")

class StrategyResult(BaseModel):
    """Result from the Strategy Agent."""
    strategy_name: str = Field(..., description="Name of the recommended investment strategy")
    strategy_type: str = Field(..., description="Type of strategy (e.g., Cash Flow, Appreciation, Balanced)")
    recommended_actions: List[Dict[str, Any]] = Field(..., description="Specific actions to implement the strategy")
    expected_outcomes: Dict[str, Any] = Field(..., description="Expected financial outcomes and performance metrics")
    timeline: Dict[str, Any] = Field(..., description="Timeline for strategy implementation and key milestones")
    alternatives: List[Dict[str, Any]] = Field(..., description="Alternative strategies considered")
    confidence_score: float = Field(..., description="Confidence level in the strategy (0-1)")
    summary: str = Field(..., description="Executive summary of the recommended strategy")
    timestamp: str = Field(..., description="Timestamp of the strategy development")

# Define strategy development tools
@function_tool
def analyze_investment_goals(goals_data: str) -> str:
    """
    Analyze investment goals to determine strategy priorities.
    
    Args:
        goals_data: JSON string with investor goals, preferences, and constraints
        
    Returns:
        JSON string with analysis of investment priorities
    """
    logger.info("[Strategy] Analyzing investment goals and priorities")
    
    try:
        # Parse goals data
        goals = json.loads(goals_data)
        
        # Extract key priorities and constraints
        priority_keys = goals.get("priorities", [])
        risk_tolerance = goals.get("risk_tolerance", "moderate").lower()
        time_horizon = goals.get("time_horizon", "medium").lower()
        
        # Analyze priorities
        if not priority_keys and "primary_goal" in goals:
            primary_goal = goals["primary_goal"].lower()
            if "cash flow" in primary_goal or "income" in primary_goal:
                priority_keys = ["cash_flow", "stability"]
            elif "appreciation" in primary_goal or "growth" in primary_goal:
                priority_keys = ["appreciation", "equity_growth"]
            elif "tax" in primary_goal or "benefits" in primary_goal:
                priority_keys = ["tax_benefits", "wealth_preservation"]
        
        # Default priorities if none found
        if not priority_keys:
            priority_keys = ["balanced"]
        
        # Map risk tolerance to numerical value
        risk_tolerance_values = {
            "very low": 1,
            "low": 2,
            "moderate": 3,
            "high": 4,
            "very high": 5
        }
        
        risk_value = risk_tolerance_values.get(risk_tolerance, 3)
        
        # Map time horizon to years
        time_horizon_years = {
            "short": 1,
            "medium": 5,
            "long": 10,
            "very long": 20
        }
        
        if isinstance(time_horizon, int):
            years = time_horizon
        else:
            # Try extracting years from string
            import re
            year_match = re.search(r'(\d+)', str(time_horizon))
            if year_match:
                years = int(year_match.group(1))
            else:
                # Use mapped value or default
                years = time_horizon_years.get(time_horizon.lower(), 5)
        
        # Determine strategy direction based on priorities and risk
        strategy_direction = "balanced"
        if "cash_flow" in priority_keys and risk_value <= 3:
            strategy_direction = "income_focused"
        elif "appreciation" in priority_keys and risk_value >= 3:
            strategy_direction = "growth_focused"
        elif "tax_benefits" in priority_keys:
            strategy_direction = "tax_optimized"
        
        # Determine suitable investment types
        suitable_investments = []
        if years < 3:
            suitable_investments = ["turnkey_properties", "reit_investments"]
        elif years < 7:
            suitable_investments = ["value_add_properties", "stable_multifamily"]
        else:
            suitable_investments = ["development_opportunities", "long_term_holds"]
        
        if risk_value <= 2:
            # Reduce risky options
            if "development_opportunities" in suitable_investments:
                suitable_investments.remove("development_opportunities")
        
        logger.info(f"[Strategy] Identified strategy direction: {strategy_direction}")
        logger.info(f"[Strategy] Time horizon: {years} years")
        logger.info(f"[Strategy] Risk tolerance level: {risk_value}/5")
        
        return json.dumps({
            "strategy_direction": strategy_direction,
            "risk_tolerance": risk_value,
            "time_horizon_years": years,
            "investment_priorities": priority_keys,
            "suitable_investments": suitable_investments,
            "confidence": 0.85
        })
        
    except Exception as e:
        logger.error(f"[Strategy] Error analyzing investment goals: {str(e)}")
        return json.dumps({
            "error": f"Failed to analyze investment goals: {str(e)}",
            "strategy_direction": "balanced",
            "risk_tolerance": 3,
            "time_horizon_years": 5,
            "confidence": 0.5
        })

@function_tool
def develop_investment_strategy(property_data: str, financial_data: str, goals_analysis: str, risk_data: str = None) -> str:
    """
    Develop a comprehensive investment strategy based on property, financial, and risk data.
    
    Args:
        property_data: JSON string with property details
        financial_data: JSON string with financial information
        goals_analysis: JSON string with analyzed goals and priorities
        risk_data: Optional JSON string with risk analysis results
        
    Returns:
        JSON string with recommended investment strategy
    """
    logger.info("[Strategy] Developing comprehensive investment strategy")
    
    try:
        # Parse input data
        property_info = json.loads(property_data)
        financials = json.loads(financial_data)
        goals = json.loads(goals_analysis)
        
        # Parse risk data if provided
        risk_analysis = None
        if risk_data:
            risk_analysis = json.loads(risk_data)
        
        # Extract key strategy parameters
        strategy_direction = goals.get("strategy_direction", "balanced")
        risk_tolerance = goals.get("risk_tolerance", 3)
        time_horizon = goals.get("time_horizon_years", 5)
        
        # Determine strategy name and type
        strategy_name = "Balanced Growth Strategy"
        strategy_type = "Balanced"
        
        if strategy_direction == "income_focused":
            strategy_name = "Stable Income Strategy"
            strategy_type = "Cash Flow"
        elif strategy_direction == "growth_focused":
            strategy_name = "Equity Growth Strategy"
            strategy_type = "Appreciation"
        elif strategy_direction == "tax_optimized":
            strategy_name = "Tax-Advantaged Strategy"
            strategy_type = "Tax Optimization"
        
        # Develop specific actions based on strategy type
        actions = []
        
        # Cash flow strategy actions
        if strategy_type == "Cash Flow":
            actions.append({
                "action": "optimize_rents",
                "description": "Optimize rental rates to market levels",
                "priority": "high",
                "timeline": "immediate",
                "expected_impact": "Increase monthly cash flow by 5-10%"
            })
            actions.append({
                "action": "refinance",
                "description": "Refinance at lower interest rate or better terms",
                "priority": "medium",
                "timeline": "3-6 months",
                "expected_impact": "Reduce monthly payment by 8-12%"
            })
            actions.append({
                "action": "expense_reduction",
                "description": "Audit and reduce property operating expenses",
                "priority": "high",
                "timeline": "1-3 months",
                "expected_impact": "Reduce expenses by 5-15%"
            })
        
        # Appreciation strategy actions
        elif strategy_type == "Appreciation":
            actions.append({
                "action": "value_add_improvements",
                "description": "Implement value-adding property improvements",
                "priority": "high",
                "timeline": "6-12 months",
                "expected_impact": "Increase property value by 10-20%"
            })
            actions.append({
                "action": "market_positioning",
                "description": "Reposition property in market for higher-end tenants",
                "priority": "medium",
                "timeline": "6-18 months",
                "expected_impact": "Increase long-term appreciation potential"
            })
            actions.append({
                "action": "leverage_optimization",
                "description": "Structure optimal leverage for maximum ROI",
                "priority": "high",
                "timeline": "3-6 months",
                "expected_impact": "Maximize return on invested capital"
            })
        
        # Tax optimization strategy actions
        elif strategy_type == "Tax Optimization":
            actions.append({
                "action": "cost_segregation",
                "description": "Perform cost segregation study to accelerate depreciation",
                "priority": "high",
                "timeline": "immediate",
                "expected_impact": "Increase first-year tax benefits by 20-40%"
            })
            actions.append({
                "action": "tax_efficient_entity",
                "description": "Establish optimal tax entity structure",
                "priority": "high",
                "timeline": "1-3 months",
                "expected_impact": "Optimize tax treatment of income and expenses"
            })
            actions.append({
                "action": "1031_planning",
                "description": "Plan for future 1031 exchange to defer capital gains",
                "priority": "medium",
                "timeline": "ongoing",
                "expected_impact": "Defer capital gains taxes on future sale"
            })
        
        # Balanced strategy (default) actions
        else:
            actions.append({
                "action": "strategic_improvements",
                "description": "Implement high-ROI property improvements",
                "priority": "high",
                "timeline": "6-12 months",
                "expected_impact": "Balance of cash flow increase and value appreciation"
            })
            actions.append({
                "action": "optimize_financing",
                "description": "Optimize financing terms for balance of safety and returns",
                "priority": "medium",
                "timeline": "3-9 months",
                "expected_impact": "Improve cash flow while maintaining equity growth"
            })
            actions.append({
                "action": "staged_value_creation",
                "description": "Implement phased value creation plan",
                "priority": "medium",
                "timeline": "ongoing",
                "expected_impact": "Balanced improvements in both income and value"
            })
        
        # Add risk mitigation actions if risk analysis was provided
        if risk_analysis:
            risk_level = risk_analysis.get("risk_level", "Medium")
            
            if risk_level in ["Medium-High", "High", "Very High"]:
                actions.append({
                    "action": "risk_mitigation",
                    "description": "Implement specific risk mitigation measures",
                    "priority": "high",
                    "timeline": "immediate",
                    "expected_impact": "Reduce exposure to identified risks"
                })
        
        # Expected outcomes calculation
        current_monthly_income = financials.get("monthly_income", 0)
        current_monthly_expenses = financials.get("monthly_expenses", 0)
        current_cash_flow = current_monthly_income - current_monthly_expenses
        purchase_price = financials.get("purchase_price", 0)
        
        # Calculate expected performance based on strategy type
        if strategy_type == "Cash Flow":
            projected_cash_flow_increase = 0.15  # 15% improvement
            projected_appreciation = 0.03  # 3% annual
        elif strategy_type == "Appreciation":
            projected_cash_flow_increase = 0.05  # 5% improvement
            projected_appreciation = 0.07  # 7% annual
        elif strategy_type == "Tax Optimization":
            projected_cash_flow_increase = 0.10  # 10% improvement (tax savings)
            projected_appreciation = 0.04  # 4% annual
        else:  # Balanced
            projected_cash_flow_increase = 0.10  # 10% improvement
            projected_appreciation = 0.05  # 5% annual
        
        projected_monthly_cash_flow = current_cash_flow * (1 + projected_cash_flow_increase)
        projected_annual_cash_flow = projected_monthly_cash_flow * 12
        projected_value_5yr = purchase_price * (1 + projected_appreciation) ** 5
        
        # Rough estimate of Cash on Cash ROI
        down_payment_percent = financials.get("down_payment_percent", 20)
        down_payment = purchase_price * (down_payment_percent / 100)
        cash_on_cash_roi = (projected_annual_cash_flow / down_payment) * 100
        
        # Establish timeline
        timeline = {
            "immediate_actions": [a["action"] for a in actions if a["timeline"] == "immediate"],
            "short_term_actions": [a["action"] for a in actions if "months" in a["timeline"] and int(a["timeline"].split("-")[0]) <= 3],
            "medium_term_actions": [a["action"] for a in actions if "months" in a["timeline"] and int(a["timeline"].split("-")[0]) > 3],
            "long_term_actions": [a["action"] for a in actions if "ongoing" in a["timeline"]],
            "review_points": [
                {"milestone": "Initial Implementation", "timing": "90 days"},
                {"milestone": "First Performance Review", "timing": "6 months"},
                {"milestone": "Strategy Adjustment", "timing": "12 months"},
                {"milestone": "Comprehensive Evaluation", "timing": "24 months"}
            ]
        }
        
        # Alternative strategies
        alternatives = []
        if strategy_type != "Cash Flow":
            alternatives.append({
                "name": "Stable Income Strategy",
                "type": "Cash Flow",
                "key_difference": "Prioritizes immediate income over long-term growth",
                "when_to_consider": "If income needs become more important than growth"
            })
        if strategy_type != "Appreciation":
            alternatives.append({
                "name": "Equity Growth Strategy",
                "type": "Appreciation",
                "key_difference": "Prioritizes property value growth over immediate income",
                "when_to_consider": "If market conditions favor stronger appreciation"
            })
        if strategy_type != "Tax Optimization":
            alternatives.append({
                "name": "Tax-Advantaged Strategy",
                "type": "Tax Optimization",
                "key_difference": "Prioritizes tax benefits over other investment considerations",
                "when_to_consider": "If tax situation changes or benefits become more valuable"
            })
        
        logger.info(f"[Strategy] Developed {strategy_name} ({strategy_type})")
        logger.info(f"[Strategy] Strategy includes {len(actions)} recommended actions")
        logger.info(f"[Strategy] Projected cash flow: ${projected_monthly_cash_flow:.2f}/month")
        logger.info(f"[Strategy] Projected 5-year value: ${projected_value_5yr:.2f}")
        
        return json.dumps({
            "strategy_name": strategy_name,
            "strategy_type": strategy_type,
            "actions": actions,
            "expected_outcomes": {
                "projected_monthly_cash_flow": round(projected_monthly_cash_flow, 2),
                "projected_annual_cash_flow": round(projected_annual_cash_flow, 2),
                "cash_on_cash_roi": round(cash_on_cash_roi, 2),
                "projected_5yr_value": round(projected_value_5yr, 2),
                "projected_annual_appreciation": projected_appreciation * 100
            },
            "timeline": timeline,
            "alternatives": alternatives,
            "confidence": 0.8
        })
        
    except Exception as e:
        logger.error(f"[Strategy] Error developing investment strategy: {str(e)}")
        return json.dumps({
            "error": f"Failed to develop investment strategy: {str(e)}",
            "strategy_name": "Basic Balanced Strategy",
            "strategy_type": "Balanced",
            "actions": [
                {
                    "action": "standard_improvements",
                    "description": "Implement standard property improvements",
                    "priority": "medium",
                    "timeline": "6-12 months",
                    "expected_impact": "Moderate improvements in property value and rental income"
                }
            ],
            "confidence": 0.5
        })

@function_tool
def analyze_financing_options(property_data: str, financial_data: str, investor_profile: str) -> str:
    """
    Analyze and recommend optimal financing options for the investment.
    
    Args:
        property_data: JSON string with property details
        financial_data: JSON string with current financial information
        investor_profile: JSON string with investor information and preferences
        
    Returns:
        JSON string with financing recommendations
    """
    logger.info("[Strategy] Analyzing financing options")
    
    try:
        # Parse input data
        property_info = json.loads(property_data)
        financials = json.loads(financial_data)
        investor = json.loads(investor_profile)
        
        # Extract key financial parameters
        purchase_price = financials.get("purchase_price", 0)
        current_down_payment = financials.get("down_payment_percent", 20)
        current_interest_rate = financials.get("interest_rate", 5.0)
        current_loan_term = financials.get("loan_term_years", 30)
        property_type = property_info.get("property_type", "residential")
        
        # Determine available financing options
        options = []
        
        # Conventional financing
        options.append({
            "type": "conventional",
            "down_payment_options": [20, 25, 30],
            "interest_rates": [current_interest_rate, current_interest_rate - 0.25],
            "terms": [15, 30],
            "pros": ["Widely available", "Predictable terms", "No PMI with 20%+ down"],
            "cons": ["May have higher rates than specialized programs"]
        })
        
        # FHA loan if eligible (primary residence)
        if property_type == "residential" and investor.get("owner_occupied", False):
            options.append({
                "type": "fha",
                "down_payment_options": [3.5],
                "interest_rates": [current_interest_rate - 0.1],
                "terms": [30],
                "pros": ["Low down payment", "More flexible credit requirements"],
                "cons": ["Requires mortgage insurance", "Owner-occupied requirement"]
            })
        
        # VA loan if eligible
        if investor.get("veteran_status", False):
            options.append({
                "type": "va",
                "down_payment_options": [0],
                "interest_rates": [current_interest_rate - 0.3],
                "terms": [15, 30],
                "pros": ["No down payment required", "No PMI", "Competitive rates"],
                "cons": ["Funding fee applies", "Limited to eligible veterans"]
            })
        
        # Commercial options for larger properties
        if property_type in ["multi-family", "commercial"] or property_info.get("units", 1) > 4:
            options.append({
                "type": "commercial",
                "down_payment_options": [25, 30],
                "interest_rates": [current_interest_rate + 0.5],
                "terms": [5, 10, 15],
                "pros": ["Designed for investment properties", "Based on property performance"],
                "cons": ["Higher down payment", "Higher rates", "Shorter terms"]
            })
        
        # Portfolio loan options
        options.append({
            "type": "portfolio",
            "down_payment_options": [20, 25, 30],
            "interest_rates": [current_interest_rate + 0.25],
            "terms": [30],
            "pros": ["More flexible qualifying", "Good for multiple properties"],
            "cons": ["Typically higher rates", "May have prepayment penalties"]
        })
        
        # Private/hard money options
        options.append({
            "type": "private_money",
            "down_payment_options": [30, 40],
            "interest_rates": [8.0, 10.0],
            "terms": [1, 2, 3],
            "pros": ["Fast funding", "Flexible terms", "Asset-based approval"],
            "cons": ["High interest rates", "Short terms", "Higher fees"]
        })
        
        # Analyze optimal loan structures
        loan_scenarios = []
        
        # Calculate scenarios for different down payments and loan types
        for option in options:
            option_type = option["type"]
            
            for dp_percent in option["down_payment_options"]:
                for rate in option["interest_rates"]:
                    for term in option["terms"]:
                        down_payment = purchase_price * (dp_percent / 100)
                        loan_amount = purchase_price - down_payment
                        
                        # Calculate monthly P&I payment
                        monthly_rate = rate / 100 / 12
                        num_payments = term * 12
                        
                        if monthly_rate == 0:
                            monthly_payment = loan_amount / num_payments
                        else:
                            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
                        
                        # Monthly PMI (if applicable)
                        monthly_pmi = 0
                        if option_type == "conventional" and dp_percent < 20:
                            monthly_pmi = loan_amount * 0.0005  # Rough estimate
                        elif option_type == "fha":
                            monthly_pmi = loan_amount * 0.0055 / 12  # Rough FHA MIP
                        
                        total_monthly_payment = monthly_payment + monthly_pmi
                        
                        # Calculate key metrics
                        cash_required = down_payment + (purchase_price * 0.03)  # Down payment + closing costs
                        monthly_income = financials.get("monthly_income", 0)
                        other_expenses = financials.get("monthly_expenses", 0) - financials.get("monthly_mortgage", 0)
                        monthly_cash_flow = monthly_income - total_monthly_payment - other_expenses
                        cash_on_cash_return = (monthly_cash_flow * 12) / cash_required * 100
                        
                        loan_scenarios.append({
                            "loan_type": option_type,
                            "down_payment_percent": dp_percent,
                            "down_payment_amount": down_payment,
                            "loan_amount": loan_amount,
                            "interest_rate": rate,
                            "term_years": term,
                            "monthly_payment": round(monthly_payment, 2),
                            "monthly_pmi": round(monthly_pmi, 2),
                            "total_monthly_payment": round(total_monthly_payment, 2),
                            "cash_required": round(cash_required, 2),
                            "monthly_cash_flow": round(monthly_cash_flow, 2),
                            "cash_on_cash_return": round(cash_on_cash_return, 2)
                        })
        
        # Sort scenarios by cash-on-cash return
        loan_scenarios.sort(key=lambda x: x["cash_on_cash_return"], reverse=True)
        
        # Get top recommendations
        top_recommendations = loan_scenarios[:3]
        
        # Determine the best overall option
        best_option = loan_scenarios[0] if loan_scenarios else None
        
        # Get the option with lowest cash required
        min_cash_option = min(loan_scenarios, key=lambda x: x["cash_required"]) if loan_scenarios else None
        
        # Get the option with highest cash flow
        max_cash_flow_option = max(loan_scenarios, key=lambda x: x["monthly_cash_flow"]) if loan_scenarios else None
        
        logger.info(f"[Strategy] Analyzed {len(loan_scenarios)} financing scenarios")
        if best_option:
            logger.info(f"[Strategy] Best option: {best_option['loan_type']} with {best_option['down_payment_percent']}% down, {best_option['interest_rate']}% rate, {best_option['term_years']}yr term")
            logger.info(f"[Strategy] Best option cash-on-cash return: {best_option['cash_on_cash_return']}%")
        
        return json.dumps({
            "financing_options": options,
            "analyzed_scenarios": loan_scenarios[:10],  # Only include top 10 for brevity
            "top_recommendations": top_recommendations,
            "best_overall_option": best_option,
            "lowest_cash_option": min_cash_option,
            "highest_cash_flow_option": max_cash_flow_option,
            "confidence": 0.85
        })
        
    except Exception as e:
        logger.error(f"[Strategy] Error analyzing financing options: {str(e)}")
        return json.dumps({
            "error": f"Failed to analyze financing options: {str(e)}",
            "financing_options": [
                {
                    "type": "conventional",
                    "down_payment_options": [20],
                    "interest_rates": [5.0],
                    "terms": [30]
                }
            ],
            "confidence": 0.5
        })

@function_tool
def develop_exit_strategy(property_data: str, strategy_data: str, market_data: str = None) -> str:
    """
    Develop exit strategy options based on property, strategy, and market data.
    
    Args:
        property_data: JSON string with property details
        strategy_data: JSON string with investment strategy information
        market_data: Optional JSON string with market trend data
        
    Returns:
        JSON string with exit strategy recommendations
    """
    logger.info("[Strategy] Developing exit strategy options")
    
    try:
        # Parse input data
        property_info = json.loads(property_data)
        strategy = json.loads(strategy_data)
        
        # Parse market data if provided
        market_trends = None
        if market_data:
            market_trends = json.loads(market_data)
        
        # Extract key parameters
        strategy_type = strategy.get("strategy_type", "Balanced")
        time_horizon = 0
        if "time_horizon_years" in strategy:
            time_horizon = strategy["time_horizon_years"]
        elif "timeline" in strategy and "review_points" in strategy["timeline"]:
            # Try to extract from timeline
            review_points = strategy["timeline"]["review_points"]
            if review_points and len(review_points) > 0:
                last_point = review_points[-1]
                # Try to extract years from timing
                import re
                year_match = re.search(r'(\d+).*?year', str(last_point.get("timing", "")))
                if year_match:
                    time_horizon = int(year_match.group(1))
                else:
                    time_horizon = 5  # Default
        else:
            time_horizon = 5  # Default
        
        # Develop appropriate exit strategies
        exit_options = []
        
        # Traditional sale
        exit_options.append({
            "exit_type": "traditional_sale",
            "timing": f"{time_horizon} years",
            "description": "Sell property on the open market through a real estate agent",
            "pros": ["Maximizes sale price", "Standard process", "Buyer pool includes owner-occupants"],
            "cons": ["Agent commissions", "Longer time on market", "Staging and preparation costs"],
            "typical_costs": "5-6% of sale price",
            "suitable_for": ["All property types", "All strategy types"],
            "optimal_market_conditions": "Seller's market with low inventory"
        })
        
        # 1031 Exchange
        exit_options.append({
            "exit_type": "1031_exchange",
            "timing": f"{time_horizon} years",
            "description": "Sell and reinvest in like-kind property to defer capital gains taxes",
            "pros": ["Tax deferral", "Property upgrade potential", "Wealth preservation"],
            "cons": ["Strict timeline requirements", "Complex rules", "Qualified intermediary required"],
            "typical_costs": "Exchange fees plus standard sale costs",
            "suitable_for": ["Investors continuing in real estate", "Properties with significant appreciation"],
            "optimal_market_conditions": "Strong market with available replacement properties"
        })
        
        # Refinance and hold
        exit_options.append({
            "exit_type": "refinance_and_hold",
            "timing": f"{time_horizon - 2} years then continue holding",
            "description": "Refinance to extract equity while maintaining ownership",
            "pros": ["No capital gains tax", "Maintains cash-flowing asset", "Extracts equity tax-free"],
            "cons": ["Increases debt", "Reduces cash flow", "Property management continues"],
            "typical_costs": "2-3% of loan amount",
            "suitable_for": ["Cash flow focused strategies", "Properties in appreciating markets"],
            "optimal_market_conditions": "Low interest rate environment"
        })
        
        # Owner financing
        if property_info.get("property_type", "") != "commercial":
            exit_options.append({
                "exit_type": "seller_financing",
                "timing": f"{time_horizon} years",
                "description": "Sell property with owner-provided financing to buyer",
                "pros": ["Higher sale price", "Monthly income stream", "Potential tax advantages"],
                "cons": ["Buyer default risk", "Longer to fully exit", "Complicated transaction"],
                "typical_costs": "1-2% of sale price for legal setup",
                "suitable_for": ["Income-focused investors", "Properties difficult to finance conventionally"],
                "optimal_market_conditions": "Tight credit markets or high interest rate environment"
            })
        
        # BRRRR (if relevant)
        if strategy_type in ["Appreciation", "Value-Add"] or "value_add" in strategy.get("strategy_name", "").lower():
            exit_options.append({
                "exit_type": "brrrr_strategy",
                "timing": f"{min(time_horizon, 2)} years",
                "description": "Buy, Rehab, Rent, Refinance, Repeat - cash-out refinance after forced appreciation",
                "pros": ["Recovers initial investment", "Maintains cash-flowing asset", "Can reinvest capital"],
                "cons": ["Refinancing risk", "Market timing critical", "Dependent on successful value-add"],
                "typical_costs": "2-3% of refinance amount",
                "suitable_for": ["Value-add strategies", "Investors seeking portfolio growth"],
                "optimal_market_conditions": "Appreciating market with stable rental demand"
            })
        
        # Determine recommended exit strategy based on strategy type
        recommended_exit = None
        if strategy_type == "Cash Flow":
            recommended_exit = next((opt for opt in exit_options if opt["exit_type"] == "refinance_and_hold"), exit_options[0])
        elif strategy_type == "Appreciation":
            recommended_exit = next((opt for opt in exit_options if opt["exit_type"] == "1031_exchange"), exit_options[0])
        elif strategy_type == "Tax Optimization":
            recommended_exit = next((opt for opt in exit_options if opt["exit_type"] == "1031_exchange"), exit_options[0])
        else:  # Balanced
            recommended_exit = next((opt for opt in exit_options if opt["exit_type"] == "traditional_sale"), exit_options[0])
        
        # If market data is available, refine recommendation
        if market_trends:
            # Implementation would analyze market trends to adjust recommendations
            # This is a placeholder for more sophisticated market analysis
            pass
        
        logger.info(f"[Strategy] Developed {len(exit_options)} exit strategy options")
        logger.info(f"[Strategy] Recommended exit strategy: {recommended_exit['exit_type']}")
        
        return json.dumps({
            "exit_options": exit_options,
            "recommended_exit": recommended_exit,
            "timing_considerations": {
                "optimal_holding_period": f"{time_horizon} years",
                "market_timing_factors": [
                    "Interest rate trends",
                    "Local market cycle position",
                    "Comparable inventory levels",
                    "Seasonal sale timing"
                ]
            },
            "preparation_steps": [
                "Begin exit preparation 6-12 months before planned exit",
                "Evaluate refinance options 1-2 years before potential sale",
                "Consult tax professional about timing implications",
                "Implement strategic improvements 1 year before sale"
            ],
            "confidence": 0.8
        })
        
    except Exception as e:
        logger.error(f"[Strategy] Error developing exit strategy: {str(e)}")
        return json.dumps({
            "error": f"Failed to develop exit strategy: {str(e)}",
            "exit_options": [
                {
                    "exit_type": "traditional_sale",
                    "timing": "5 years",
                    "description": "Standard sale of property"
                }
            ],
            "confidence": 0.5
        })

@function_tool
def create_implementation_plan(strategy_data: str, financing_data: str = None, exit_data: str = None) -> str:
    """
    Create a detailed implementation plan for the recommended strategy.
    
    Args:
        strategy_data: JSON string with investment strategy
        financing_data: Optional JSON string with financing recommendations
        exit_data: Optional JSON string with exit strategy
        
    Returns:
        JSON string with implementation plan
    """
    logger.info("[Strategy] Creating detailed implementation plan")
    
    try:
        # Parse input data
        strategy = json.loads(strategy_data)
        
        # Parse optional data if provided
        financing = None
        exit_strategy = None
        
        if financing_data:
            financing = json.loads(financing_data)
        
        if exit_data:
            exit_strategy = json.loads(exit_data)
        
        # Extract strategy actions
        actions = strategy.get("actions", [])
        
        # Create phase-based implementation plan
        implementation_phases = [
            {
                "phase": "initial_setup",
                "timeline": "0-30 days",
                "description": "Complete initial property acquisition and setup",
                "steps": [
                    {
                        "step": "finalize_financing",
                        "description": "Secure optimal financing based on analysis",
                        "resources_needed": ["Lender", "Credit documentation", "Down payment funds"],
                        "success_criteria": "Loan closed with terms matching or better than recommendation"
                    },
                    {
                        "step": "entity_setup",
                        "description": "Establish proper legal entity for ownership",
                        "resources_needed": ["Attorney", "Accountant"],
                        "success_criteria": "Entity formed and property titled correctly"
                    },
                    {
                        "step": "insurance_setup",
                        "description": "Obtain comprehensive property insurance",
                        "resources_needed": ["Insurance broker", "Property details"],
                        "success_criteria": "Coverage in place with appropriate limits"
                    }
                ]
            },
            {
                "phase": "operational_setup",
                "timeline": "30-60 days",
                "description": "Establish property management systems",
                "steps": [
                    {
                        "step": "management_selection",
                        "description": "Select property management approach (self or professional)",
                        "resources_needed": ["Management proposals", "Contractor list"],
                        "success_criteria": "Management solution implemented with clear responsibilities"
                    },
                    {
                        "step": "tenant_systems",
                        "description": "Establish tenant screening and management systems",
                        "resources_needed": ["Screening service", "Lease templates"],
                        "success_criteria": "Documented tenant processes and standards"
                    },
                    {
                        "step": "maintenance_plan",
                        "description": "Create proactive maintenance schedule",
                        "resources_needed": ["Property inspection", "Contractor relationships"],
                        "success_criteria": "Written maintenance plan with schedule and budget"
                    }
                ]
            },
            {
                "phase": "strategy_execution",
                "timeline": "60-180 days",
                "description": "Implement core strategy actions",
                "steps": []
            },
            {
                "phase": "monitoring_adjustment",
                "timeline": "Ongoing",
                "description": "Monitor performance and adjust strategy",
                "steps": [
                    {
                        "step": "performance_tracking",
                        "description": "Track key financial and property metrics",
                        "resources_needed": ["Accounting system", "Property records"],
                        "success_criteria": "Monthly financial reporting established"
                    },
                    {
                        "step": "market_monitoring",
                        "description": "Monitor local market conditions and trends",
                        "resources_needed": ["Market data sources", "Realtor relationship"],
                        "success_criteria": "Quarterly market analysis completed"
                    },
                    {
                        "step": "strategy_reviews",
                        "description": "Conduct regular strategy review sessions",
                        "resources_needed": ["Investment data", "Strategy documentation"],
                        "success_criteria": "Documented reviews with action items"
                    }
                ]
            }
        ]
        
        # Add strategy-specific steps
        strategy_steps = []
        for action in actions:
            step = {
                "step": action["action"].lower(),
                "description": action["description"],
                "priority": action["priority"],
                "resources_needed": [],
                "success_criteria": f"Achieved {action['expected_impact']}"
            }
            
            # Add appropriate resources based on action type
            if "improve" in action["action"] or "renovation" in action["action"]:
                step["resources_needed"] = ["Contractors", "Construction budget", "Project timeline"]
            elif "refinance" in action["action"]:
                step["resources_needed"] = ["Lender", "Property appraisal", "Financial documentation"]
            elif "rent" in action["action"]:
                step["resources_needed"] = ["Market rent analysis", "Tenant communication plan"]
            elif "tax" in action["action"]:
                step["resources_needed"] = ["Tax professional", "Financial records"]
            else:
                step["resources_needed"] = ["Investment analysis", "Strategy documentation"]
            
            strategy_steps.append(step)
        
        # Add strategy steps to the strategy execution phase
        for i, phase in enumerate(implementation_phases):
            if phase["phase"] == "strategy_execution":
                implementation_phases[i]["steps"] = strategy_steps
        
        # Add financing-specific steps if available
        if financing and "best_overall_option" in financing:
            best_option = financing["best_overall_option"]
            financing_step = {
                "step": "optimal_financing",
                "description": f"Secure {best_option['loan_type']} financing with {best_option['down_payment_percent']}% down at {best_option['interest_rate']}% for {best_option['term_years']} years",
                "priority": "high",
                "resources_needed": ["Lender relationships", "Financial documentation", "Credit history"],
                "success_criteria": f"Loan secured at or below {best_option['interest_rate']}% with {best_option['down_payment_percent']}% down payment"
            }
            
            # Add to initial setup phase
            for i, phase in enumerate(implementation_phases):
                if phase["phase"] == "initial_setup":
                    implementation_phases[i]["steps"].insert(0, financing_step)
        
        # Add exit strategy preparation if available
        if exit_strategy and "recommended_exit" in exit_strategy:
            recommended = exit_strategy["recommended_exit"]
            exit_step = {
                "step": "exit_preparation",
                "description": f"Prepare for {recommended['exit_type']} exit strategy",
                "priority": "medium",
                "resources_needed": ["Exit strategy document", "Tax advisor consultation"],
                "success_criteria": "Exit plan documented with timing milestones"
            }
            
            # Add to monitoring phase
            for i, phase in enumerate(implementation_phases):
                if phase["phase"] == "monitoring_adjustment":
                    implementation_phases[i]["steps"].append(exit_step)
        
        # Create key milestones
        key_milestones = [
            {
                "milestone": "Strategy Initiation",
                "timing": "Day 1",
                "description": "Official start of strategy implementation",
                "success_criteria": "All stakeholders aligned on plan"
            },
            {
                "milestone": "Operational Readiness",
                "timing": "Day 60",
                "description": "Basic operational systems in place",
                "success_criteria": "Management and tenant systems operational"
            },
            {
                "milestone": "Strategy Implementation Complete",
                "timing": "Day 180",
                "description": "All initial strategy actions implemented",
                "success_criteria": "All strategy execution steps completed"
            },
            {
                "milestone": "First Performance Review",
                "timing": "6 months",
                "description": "First comprehensive review of strategy performance",
                "success_criteria": "Performance metrics meet or exceed projections"
            },
            {
                "milestone": "Strategy Refinement",
                "timing": "12 months",
                "description": "Adjust strategy based on first year performance",
                "success_criteria": "Updated strategy document with adjustments"
            }
        ]
        
        # Add exit-related milestone if applicable
        if exit_strategy and "recommended_exit" in exit_strategy:
            recommended = exit_strategy["recommended_exit"]
            timing = recommended.get("timing", "5 years")
            
            exit_milestone = {
                "milestone": "Exit Strategy Execution",
                "timing": timing,
                "description": f"Implement {recommended['exit_type']} exit strategy",
                "success_criteria": "Successful exit with financial targets achieved"
            }
            
            key_milestones.append(exit_milestone)
        
        logger.info(f"[Strategy] Created implementation plan with {len(implementation_phases)} phases")
        logger.info(f"[Strategy] Implementation plan includes {len(key_milestones)} key milestones")
        
        return json.dumps({
            "implementation_phases": implementation_phases,
            "key_milestones": key_milestones,
            "resource_requirements": {
                "financial": [
                    "Down payment and closing costs",
                    "Renovation/improvement budget",
                    "Operating reserves",
                    "Professional service fees"
                ],
                "expertise": [
                    "Property management",
                    "Contractor relationships",
                    "Legal and tax advisors",
                    "Real estate market analysts"
                ],
                "tools": [
                    "Property management software",
                    "Financial tracking system",
                    "Market monitoring tools",
                    "Document management system"
                ]
            },
            "potential_challenges": [
                {
                    "challenge": "Market changes",
                    "contingency": "Regular strategy reviews with adjustment flexibility"
                },
                {
                    "challenge": "Financing changes",
                    "contingency": "Multiple financing relationships and backup options"
                },
                {
                    "challenge": "Property condition issues",
                    "contingency": "Thorough inspection and maintenance reserves"
                },
                {
                    "challenge": "Tenant problems",
                    "contingency": "Robust screening and clear management policies"
                }
            ],
            "confidence": 0.85
        })
        
    except Exception as e:
        logger.error(f"[Strategy] Error creating implementation plan: {str(e)}")
        return json.dumps({
            "error": f"Failed to create implementation plan: {str(e)}",
            "implementation_phases": [
                {
                    "phase": "basic_setup",
                    "timeline": "0-30 days",
                    "steps": [
                        {
                            "step": "property_setup",
                            "description": "Set up basic property operations"
                        }
                    ]
                }
            ],
            "confidence": 0.5
        })

def create_strategy_agent() -> Agent:
    """Create and configure the Strategy Agent."""
    
    logger.info("[Strategy] Creating investment strategy agent")
    
    # Define agent instructions
    instructions = """
    You are a specialized Strategy Agent for property investment analysis.
    
    Your task is to develop comprehensive investment strategies based on:
    1. Property characteristics and financial data
    2. Investor goals and preferences
    3. Risk analysis results
    4. Market conditions and trends
    
    Follow these steps when developing investment strategies:
    1. Analyze investor goals and risk tolerance
    2. Consider property characteristics and financial metrics
    3. Evaluate market conditions and trends
    4. Develop strategy options (Cash Flow, Appreciation, Balanced, Tax-Optimized)
    5. Recommend specific implementation actions
    6. Create detailed timelines and milestones
    7. Outline exit strategy options
    
    Your strategies should be:
    - Tailored to the specific property and investor
    - Data-driven with clear financial projections
    - Practical with specific, actionable steps
    - Comprehensive, covering acquisition through exit
    - Risk-aware with contingency options
    
    Provide clear metrics for strategy success and specific implementation steps.
    Explain the reasoning behind your recommendations and include alternative approaches.
    Balance optimizing financial returns with the investor's risk tolerance and time horizon.
    """
    
    from openai import AsyncAzureOpenAI
    from agents import set_default_openai_client
    from dotenv import load_dotenv
    import os

    # Load environment variables
    load_dotenv()
    logger.info("[Strategy] Configuring integration with Azure OpenAI services")
    
    # Create OpenAI client using Azure OpenAI
    openai_client = AsyncAzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    )

    # Set the default OpenAI client for the Agents SDK
    set_default_openai_client(openai_client)
    logger.info("[Strategy] OpenAI client configured for agent")

    # Log the available tools
    tools = [
        analyze_investment_goals,
        develop_investment_strategy,
        analyze_financing_options,
        develop_exit_strategy,
        create_implementation_plan
    ]
    
    tool_names = [tool.__name__ if hasattr(tool, '__name__') else tool.name for tool in tools]
    logger.info(f"[Strategy] Setting up agent with tools: {', '.join(tool_names)}")

    # Create and return the agent
    agent = Agent(
        name="Strategy Agent",
        instructions=instructions,
        model=OpenAIChatCompletionsModel(
            model="gpt-4o",
            openai_client=openai_client
        ),
        tools=tools
    )
    
    logger.info("[Strategy] Strategy agent successfully initialized")
    return agent

# Advanced strategy functions with enhanced logging

def create_strategy_with_logging(property_data: Dict[str, Any], financial_data: Dict[str, Any], 
                              investor_goals: Dict[str, Any], risk_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a comprehensive investment strategy with detailed logging.
    
    Args:
        property_data: Property details
        financial_data: Financial information
        investor_goals: Investor goals and preferences
        risk_analysis: Optional risk analysis results
        
    Returns:
        Strategy recommendation
    """
    logger.info("[Strategy] Starting comprehensive strategy development")
    
    # This is a placeholder for a more complex implementation
    # In a real implementation, this would call the various strategy tools
    # and aggregate their results
    
    logger.info("[Strategy] Analyzing investor goals and risk tolerance")
    logger.info("[Strategy] Evaluating property characteristics and financial metrics")
    logger.info("[Strategy] Considering market conditions and trends")
    
    strategy_type = "Balanced"
    if investor_goals.get("cash_flow_focus", False):
        strategy_type = "Cash Flow"
        logger.info("[Strategy] Selected Cash Flow strategy based on investor preferences")
    elif investor_goals.get("appreciation_focus", False):
        strategy_type = "Appreciation"
        logger.info("[Strategy] Selected Appreciation strategy based on investor preferences")
    
    if risk_analysis:
        risk_level = risk_analysis.get("risk_level", "Medium")
        logger.info(f"[Strategy] Incorporating risk analysis (Risk Level: {risk_level})")
    
    logger.info("[Strategy] Developing detailed implementation actions")
    logger.info("[Strategy] Creating timeline and milestones")
    logger.info("[Strategy] Outlining exit strategy options")
    
    logger.info(f"[Strategy] Completed strategy development: {strategy_type} Strategy")
    
    # Return simulated results
    return {
        "strategy_complete": True,
        "strategy_type": strategy_type,
        "timestamp": datetime.now().isoformat()
    }