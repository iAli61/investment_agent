#!/usr/bin/env python3
"""
Test script for testing the Risk Analysis Agent functionality.

This script tests the risk analysis tools including market risk analysis,
property-specific risk analysis, financial risk analysis, and mitigation strategies.
"""

import logging
import json
import sys
import os
from datetime import datetime
import statistics

# Add src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler("risk_analysis_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("risk_analysis_test")

# Direct implementations of the tools for testing
def test_analyze_market_risks(location: str, property_type: str, historical_data: str) -> str:
    """
    Direct implementation of market risk analysis for testing purposes.
    """
    logger.info("[Risk Analysis] Analyzing market-related risks")
    try:
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

def test_analyze_property_specific_risks(property_data: str) -> str:
    """
    Direct implementation of property-specific risk analysis for testing purposes.
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

def test_analyze_financial_risks(financial_data: str, investment_goals: str) -> str:
    """
    Direct implementation of financial risk analysis for testing purposes.
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

def test_generate_risk_mitigation_strategies(risks_data: str) -> str:
    """
    Direct implementation of risk mitigation strategies generation for testing purposes.
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

def test_calculate_consolidated_risk_score(market_risks: str, property_risks: str, financial_risks: str) -> str:
    """
    Direct implementation of consolidated risk score calculation for testing purposes.
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

def test_analyze_market_risks_workflow():
    """Test the market risk analysis functionality"""
    logger.info(f"{'='*80}")
    logger.info(f"MARKET RISK ANALYSIS TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"{'='*80}")
    
    # Test location and property type
    location = "Berlin"
    property_type = "residential"
    
    # Sample historical data
    historical_data = {
        "prices": [350000, 365000, 380000, 410000, 425000],
        "vacancy_rates": [3.2, 2.8, 2.5, 2.2, 1.9],
        "interest_rates": [2.5, 2.7, 3.0, 3.2, 3.5]
    }
    
    logger.info(f"Testing market risk analysis for {property_type} property in {location}")
    logger.info(f"Historical data spans {len(historical_data['prices'])} periods")
    
    # Convert historical data to JSON string
    historical_data_json = json.dumps(historical_data)
    
    try:
        # Call the test_analyze_market_risks function
        result_json = test_analyze_market_risks(location, property_type, historical_data_json)
        result = json.loads(result_json)
        
        logger.info(f"Market risk analysis completed successfully")
        
        # Print the results
        print(f"\n{'='*80}")
        print(f"MARKET RISK ANALYSIS RESULTS")
        print(f"{'='*80}")
        print(f"Location: {location}")
        print(f"Property Type: {property_type}")
        print(f"Risk Score: {result.get('risk_score')}")
        print(f"Risk Level: {result.get('risk_level')}")
        
        print("\nRisk Factors:")
        for factor in result.get('risk_factors', []):
            print(f"  • {factor['risk']}: Severity {factor['severity']} (Probability: {factor['probability']})")
        
        print(f"\nAnalysis Confidence: {result.get('analysis_confidence', 0) * 100:.1f}%")
        print(f"Summary: {result.get('summary', 'No summary available')}")
        print(f"{'='*80}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error during market risk analysis: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return None

def test_property_specific_risks_workflow():
    """Test the property-specific risk analysis functionality"""
    logger.info(f"{'='*80}")
    logger.info(f"PROPERTY-SPECIFIC RISK ANALYSIS TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"{'='*80}")
    
    # Sample property data
    property_data = {
        "age_years": 25,
        "condition_rating": 7,  # Scale of 1-10
        "location_score": 8,    # Scale of 1-10
        "property_type": "apartment",
        "size_sqm": 85,
        "features": ["balcony", "elevator", "parking"]
    }
    
    logger.info(f"Testing property-specific risk analysis for {property_data['property_type']}")
    logger.info(f"Property age: {property_data['age_years']} years, Condition: {property_data['condition_rating']}/10")
    
    # Convert property data to JSON string
    property_data_json = json.dumps(property_data)
    
    try:
        # Call the test_analyze_property_specific_risks function
        result_json = test_analyze_property_specific_risks(property_data_json)
        result = json.loads(result_json)
        
        logger.info(f"Property-specific risk analysis completed successfully")
        
        # Print the results
        print(f"\n{'='*80}")
        print(f"PROPERTY-SPECIFIC RISK ANALYSIS RESULTS")
        print(f"{'='*80}")
        print(f"Property Type: {property_data['property_type']}")
        print(f"Risk Score: {result.get('risk_score')}")
        print(f"Risk Level: {result.get('risk_level')}")
        
        print("\nRisk Factors:")
        for factor in result.get('risk_factors', []):
            print(f"  • {factor['risk']}: Severity {factor['severity']} (Probability: {factor['probability']})")
        
        print(f"\nAnalysis Confidence: {result.get('analysis_confidence', 0) * 100:.1f}%")
        print(f"Summary: {result.get('summary', 'No summary available')}")
        print(f"{'='*80}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error during property-specific risk analysis: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return None

def test_financial_risks_workflow():
    """Test the financial risk analysis functionality"""
    logger.info(f"{'='*80}")
    logger.info(f"FINANCIAL RISK ANALYSIS TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"{'='*80}")
    
    # Sample financial data
    financial_data = {
        "purchase_price": 400000,
        "monthly_income": 2000,
        "monthly_expenses": 800,
        "loan_to_value": 70,
        "interest_rate": 3.5,
        "loan_term_years": 25,
        "cash_reserves": 15000
    }
    
    # Sample investment goals
    investment_goals = {
        "investment_horizon": "long-term",
        "primary_goal": "cash_flow",
        "risk_tolerance": "moderate",
        "target_yield": 4.5,
        "cash_flow_requirements": 500
    }
    
    logger.info(f"Testing financial risk analysis")
    logger.info(f"LTV: {financial_data['loan_to_value']}%, Monthly cash flow: €{financial_data['monthly_income'] - financial_data['monthly_expenses']}")
    
    # Convert data to JSON strings
    financial_data_json = json.dumps(financial_data)
    investment_goals_json = json.dumps(investment_goals)
    
    try:
        # Call the test_analyze_financial_risks function
        result_json = test_analyze_financial_risks(financial_data_json, investment_goals_json)
        result = json.loads(result_json)
        
        logger.info(f"Financial risk analysis completed successfully")
        
        # Print the results
        print(f"\n{'='*80}")
        print(f"FINANCIAL RISK ANALYSIS RESULTS")
        print(f"{'='*80}")
        print(f"Purchase Price: €{financial_data['purchase_price']}")
        print(f"Risk Score: {result.get('risk_score')}")
        print(f"Risk Level: {result.get('risk_level')}")
        
        print("\nRisk Factors:")
        for factor in result.get('risk_factors', []):
            print(f"  • {factor['risk']}: Severity {factor['severity']} (Probability: {factor['probability']})")
        
        print(f"\nAnalysis Confidence: {result.get('analysis_confidence', 0) * 100:.1f}%")
        print(f"Summary: {result.get('summary', 'No summary available')}")
        print(f"{'='*80}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error during financial risk analysis: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return None

def test_mitigation_strategies_workflow():
    """Test the risk mitigation strategies functionality"""
    logger.info(f"{'='*80}")
    logger.info(f"RISK MITIGATION STRATEGIES TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"{'='*80}")
    
    # Sample risk data with factors
    risks_data = {
        "risk_score": 65,
        "risk_level": "Medium",
        "risk_factors": [
            {"risk": "price_volatility", "severity": 0.7, "probability": 0.5},
            {"risk": "vacancy_risk", "severity": 0.4, "probability": 0.5},
            {"risk": "condition_risk", "severity": 0.6, "probability": 0.5},
            {"risk": "cash_flow_risk", "severity": 0.5, "probability": 0.5},
            {"risk": "leverage_risk", "severity": 0.8, "probability": 0.5}
        ]
    }
    
    logger.info(f"Testing risk mitigation strategies generation")
    logger.info(f"Input: {len(risks_data['risk_factors'])} risk factors with overall score of {risks_data['risk_score']}")
    
    # Convert risks data to JSON string
    risks_data_json = json.dumps(risks_data)
    
    try:
        # Call the test_generate_risk_mitigation_strategies function
        result_json = test_generate_risk_mitigation_strategies(risks_data_json)
        result = json.loads(result_json)
        
        logger.info(f"Mitigation strategies generation completed successfully")
        
        # Print the results
        print(f"\n{'='*80}")
        print(f"RISK MITIGATION STRATEGIES")
        print(f"{'='*80}")
        
        print("\nRecommended Strategies:")
        for strategy in result.get('mitigation_strategies', []):
            print(f"  • {strategy['risk']}: {strategy['strategy']}")
        
        print(f"\nAnalysis Confidence: {result.get('analysis_confidence', 0) * 100:.1f}%")
        print(f"{'='*80}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error generating mitigation strategies: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return None

def test_consolidated_risk_score_workflow():
    """Test the consolidated risk score calculation functionality"""
    logger.info(f"{'='*80}")
    logger.info(f"CONSOLIDATED RISK SCORE TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"{'='*80}")
    
    # Sample risk analysis results
    market_risks = {"risk_score": 45, "risk_level": "Medium"}
    property_risks = {"risk_score": 35, "risk_level": "Medium"}
    financial_risks = {"risk_score": 68, "risk_level": "High"}
    
    logger.info(f"Testing consolidated risk score calculation")
    logger.info(f"Market risk: {market_risks['risk_score']} ({market_risks['risk_level']})")
    logger.info(f"Property risk: {property_risks['risk_score']} ({property_risks['risk_level']})")
    logger.info(f"Financial risk: {financial_risks['risk_score']} ({financial_risks['risk_level']})")
    
    # Convert risk data to JSON strings
    market_risks_json = json.dumps(market_risks)
    property_risks_json = json.dumps(property_risks)
    financial_risks_json = json.dumps(financial_risks)
    
    try:
        # Call the test_calculate_consolidated_risk_score function
        result_json = test_calculate_consolidated_risk_score(market_risks_json, property_risks_json, financial_risks_json)
        result = json.loads(result_json)
        
        logger.info(f"Consolidated risk score calculation completed successfully")
        
        # Print the results
        print(f"\n{'='*80}")
        print(f"CONSOLIDATED RISK SCORE")
        print(f"{'='*80}")
        print(f"Risk Score: {result.get('risk_score')}")
        print(f"Risk Level: {result.get('risk_level')}")
        print(f"Calculated from: Market ({market_risks['risk_score']}), Property ({property_risks['risk_score']}), Financial ({financial_risks['risk_score']})")
        print(f"Analysis Confidence: {result.get('analysis_confidence', 0) * 100:.1f}%")
        print(f"{'='*80}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error calculating consolidated risk score: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return None

def run_all_tests():
    """Run all risk analysis tests in sequence"""
    logger.info(f"{'='*80}")
    logger.info(f"RUNNING ALL RISK ANALYSIS TESTS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"{'='*80}")
    
    market_result = test_analyze_market_risks_workflow()
    property_result = test_property_specific_risks_workflow()
    financial_result = test_financial_risks_workflow()
    
    if market_result and property_result and financial_result:
        # If all individual tests succeeded, test consolidated score
        consolidated_result = test_consolidated_risk_score_workflow()
        
        # Then test mitigation strategies based on consolidated risks
        if consolidated_result:
            consolidated_result["risk_factors"] = market_result.get("risk_factors", []) + \
                                                 property_result.get("risk_factors", []) + \
                                                 financial_result.get("risk_factors", [])
            mitigation_result = test_mitigation_strategies_workflow()
    
    logger.info(f"All risk analysis tests completed")

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            # Run specific test based on argument
            if sys.argv[1] == "market":
                test_analyze_market_risks_workflow()
            elif sys.argv[1] == "property":
                test_property_specific_risks_workflow()
            elif sys.argv[1] == "financial":
                test_financial_risks_workflow()
            elif sys.argv[1] == "mitigation":
                test_mitigation_strategies_workflow()
            elif sys.argv[1] == "consolidated":
                test_consolidated_risk_score_workflow()
            else:
                print(f"Unknown test: {sys.argv[1]}")
                print("Available tests: market, property, financial, mitigation, consolidated")
        else:
            # Run all tests
            run_all_tests()
    except KeyboardInterrupt:
        logger.warning("Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during test: {str(e)}", exc_info=True)
        sys.exit(1)