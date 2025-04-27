#!/usr/bin/env python3
"""
Comprehensive test script for the enhanced logging across all investment agent components.
This script performs a complete investment property analysis scenario to demonstrate
the improved logging transparency.
"""
import requests
import json
import time
import sys
import os
import logging
from datetime import datetime

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler("investment_agent_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("investment_test")

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_investment_scenario():
    """Test a complete investment property analysis scenario"""
    logger.info(f"{'='*80}")
    logger.info(f"INVESTMENT AGENT SYSTEM TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"{'='*80}")
    
    # Prepare test data
    property_location = "berlin"
    property_type = "apartment"
    property_size = 75.0  # sqm
    purchase_price = 350000  # EUR
    
    logger.info(f"Test scenario: Analyzing {property_size}sqm {property_type} in {property_location}")
    logger.info(f"Purchase price: €{purchase_price}")
    
    # Stage 1: Market Data Analysis
    logger.info("\n[STAGE 1] MARKET DATA ANALYSIS")
    market_data_result = run_market_data_analysis(property_location, property_type)
    
    if not market_data_result:
        logger.error("Market data analysis failed or timed out. Continuing with mock data.")
        # Create mock market data so we can continue the test
        market_data_result = create_mock_market_data(property_location, property_type)
    else:
        logger.info("Market data analysis completed successfully!")
    
    # Stage 2: Document Analysis
    logger.info("\n[STAGE 2] DOCUMENT ANALYSIS")
    document_result = run_document_analysis()
    
    if not document_result:
        logger.error("Document analysis failed. Continuing with mock data.")
        document_result = create_mock_document_data()
    else:
        logger.info("Document analysis completed successfully!")
    
    # Stage 3: Rent Estimation
    logger.info("\n[STAGE 3] RENT ESTIMATION")
    rent_result = run_rent_estimation(property_location, property_type, property_size)
    
    if not rent_result:
        logger.error("Rent estimation failed. Continuing with mock data.")
        rent_result = create_mock_rent_data(property_location, property_type, property_size)
    else:
        logger.info("Rent estimation completed successfully!")
    
    # Stage 4: Investment Optimization
    logger.info("\n[STAGE 4] INVESTMENT OPTIMIZATION")
    optimization_result = run_optimization_analysis(
        property_location, 
        property_type,
        property_size,
        purchase_price,
        rent_result.get("estimated_rent", 1500)
    )
    
    if not optimization_result:
        logger.error("Optimization analysis failed. Continuing with mock data.")
        optimization_result = create_mock_optimization_data(
            property_location, property_type, property_size, purchase_price, 
            rent_result.get("estimated_rent", 1500)
        )
    else:
        logger.info("Optimization analysis completed successfully!")
    
    # Final Results Summary
    logger.info("\n[SUMMARY] INVESTMENT ANALYSIS COMPLETE")
    logger.info(f"{'='*80}")
    print_investment_summary(
        property_location,
        property_type,
        property_size,
        purchase_price,
        market_data_result,
        document_result,
        rent_result,
        optimization_result
    )

def run_market_data_analysis(location, property_type):
    """Run market data analysis on the specified location and property type"""
    logger.info(f"Starting market data analysis for {property_type} in {location}")
    
    # Prepare the request payload
    payload = {
        "location": location,
        "property_type": property_type,
        "additional_filters": {
            "min_price": 100000,
            "max_price": 500000,
            "min_size": 50,
            "features": ["balcony", "elevator"]
        }
    }
    
    logger.info(f"Market data request payload: {json.dumps(payload)}")
    
    # Make the initial POST request to start the task
    start_time = time.time()
    try:
        response = requests.post(f"{BASE_URL}/ai/market-data/", json=payload, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making market data request: {str(e)}")
        return None
    
    # Get the task ID from the response
    response_data = response.json()
    task_id = response_data.get("task_id")
    
    if not task_id:
        logger.error("No task ID in market data response")
        return None
    
    logger.info(f"Market data task created with ID: {task_id}")
    logger.info(f"Initial status: {response_data.get('status')}")
    
    # Poll for the task result with exponential backoff
    max_attempts = 20  # Increased from 12 to 20
    attempts = 0
    wait_time = 3  # Start with 3 seconds, will increase
    max_wait_time = 15  # Maximum wait is 15 seconds
    total_wait_time = 0
    max_total_wait = 180  # Maximum total wait time of 3 minutes
    
    while attempts < max_attempts and total_wait_time < max_total_wait:
        attempts += 1
        logger.info(f"Polling attempt {attempts}/{max_attempts} for market data task (waited {total_wait_time}s so far)")
        
        try:
            result_response = requests.get(f"{BASE_URL}/ai/tasks/{task_id}", timeout=10)
            result_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking market data task: {str(e)}")
            time.sleep(wait_time)
            total_wait_time += wait_time
            wait_time = min(wait_time * 1.5, max_wait_time)  # Exponential backoff
            continue
        
        result_data = result_response.json()
        status = result_data.get("status")
        logger.info(f"Market data task status: {status}")
        
        if status == "completed":
            execution_time = time.time() - start_time
            logger.info(f"Market data analysis completed in {execution_time:.2f} seconds")
            
            # Return the result data
            return result_data.get("result", {})
        
        # If in progress or processing, wait shorter time
        if status == "processing" or status == "in_progress":
            wait_time = min(wait_time * 1.2, max_wait_time)  # Slower backoff for in-progress tasks
        else:
            wait_time = min(wait_time * 1.5, max_wait_time)  # Faster backoff for pending tasks
            
        # If still processing, wait before checking again
        logger.info(f"Waiting {wait_time:.1f} seconds before next poll")
        time.sleep(wait_time)
        total_wait_time += wait_time
    
    time_message = f"Task did not complete within timeout ({total_wait_time}s)"
    logger.warning(time_message)
    print(f"\n⚠️ {time_message}")
    return None

def create_mock_market_data(location, property_type):
    """Create mock market data for testing when the real API fails or times out"""
    logger.info(f"Creating mock market data for {property_type} in {location}")
    
    return {
        "location": location,
        "property_type": property_type,
        "price_data": {
            "average_price_sqm": "4,500",
            "price_range": {"min": 3500, "max": 5500},
            "price_trend": "Rising (5.2% yearly)"
        },
        "rental_data": {
            "average_rent_sqm": "25.5",
            "rent_range": {"min": 22, "max": 29},
            "vacancy_rate": 3.0
        },
        "historical_data": {
            "summary": {
                "price_appreciation": 13.64,
                "rent_appreciation": 13.64,
                "years": 5
            }
        },
        "development_news": {
            "news": [
                {"title": "New Shopping Center", "impact": "positive"},
                {"title": "Public Transport Expansion", "impact": "very positive"},
                {"title": "School Renovation", "impact": "positive"}
            ],
            "impact_summary": {"positive": 2, "very positive": 1}
        },
        "confidence_scores": {
            "price_data": 0.85,
            "rental_data": 0.90,
            "trend_data": 0.75
        }
    }

def run_document_analysis():
    """Run document analysis on a sample lease agreement"""
    logger.info("Starting document analysis for sample lease agreement")
    
    # Sample lease agreement text
    lease_text = """
    LEASE AGREEMENT
    
    This Lease Agreement is made on April 15, 2025 between Landlord GmbH (Landlord)
    and Jane Doe (Tenant) for the property at Musterstraße 123, 10115 Berlin.
    
    1. TERM: The lease begins on June 1, 2025 and ends on May 31, 2027.
    2. RENT: Tenant agrees to pay €1,500 per month, due on the 1st of each month.
    3. SECURITY DEPOSIT: Tenant has paid €3,000 as security deposit.
    4. UTILITIES: Tenant is responsible for electricity, internet, and heating costs.
    5. MAINTENANCE: Landlord is responsible for major repairs. Tenant must maintain cleanliness.
    6. SPECIAL PROVISIONS: No pets allowed. No smoking inside the apartment.
    """
    
    # Prepare the request payload
    payload = {
        "document_type": "lease_agreement",
        "document_text": lease_text,
        "extraction_targets": ["rent_amount", "deposit", "term_duration", "responsibilities"]
    }
    
    logger.info("Document analysis request prepared")
    
    # Mock document analysis result (in a real implementation, this would make an API call)
    start_time = time.time()
    time.sleep(2)  # Simulate processing time
    
    # Sample document analysis result
    result = {
        "extracted_data": {
            "rent_amount": 1500,
            "security_deposit": 3000,
            "term_duration": "24 months",
            "start_date": "2025-06-01",
            "end_date": "2027-05-31",
            "tenant_responsibilities": ["electricity", "internet", "heating", "cleanliness"],
            "landlord_responsibilities": ["major repairs"],
            "special_provisions": ["no pets", "no smoking"]
        },
        "confidence_scores": {
            "rent_amount": 0.98,
            "security_deposit": 0.97,
            "term_duration": 0.95,
            "responsibilities": 0.85
        },
        "key_insights": [
            "Lease term is 24 months with no specified renewal option",
            "Rent-to-deposit ratio is 1:2 (two months' rent as deposit)",
            "Tenant is responsible for all utilities including heating",
            "No pets clause may limit tenant pool"
        ]
    }
    
    execution_time = time.time() - start_time
    logger.info(f"Document analysis completed in {execution_time:.2f} seconds")
    logger.info(f"Extracted {len(result['extracted_data'])} data points from document")
    logger.info(f"Identified {len(result['key_insights'])} key insights from lease agreement")
    
    return result

def create_mock_document_data():
    """Create mock document analysis data for testing"""
    logger.info("Creating mock document analysis data")
    
    return {
        "extracted_data": {
            "rent_amount": 1500,
            "security_deposit": 3000,
            "term_duration": "24 months",
            "special_provisions": ["no pets", "no smoking"]
        },
        "confidence_scores": {
            "overall": 0.95
        },
        "key_insights": [
            "Lease term is 24 months with no specified renewal option",
            "Rent-to-deposit ratio is 1:2 (two months' rent as deposit)",
            "No pets clause may limit tenant pool"
        ]
    }

def run_rent_estimation(location, property_type, size_sqm):
    """Run rent estimation for the specified property"""
    logger.info(f"Starting rent estimation for {size_sqm}sqm {property_type} in {location}")
    
    # Prepare the request payload
    payload = {
        "location": location,
        "property_type": property_type,
        "size_sqm": size_sqm,
        "year_built": 2010,
        "condition": "good",
        "features": ["balcony", "elevator", "parking", "storage"],
        "check_rent_control": True
    }
    
    logger.info(f"Rent estimation request prepared with {len(payload['features'])} property features")
    
    # Mock rent estimation result (in a real implementation, this would make an API call)
    start_time = time.time()
    time.sleep(2)  # Simulate processing time
    
    # Calculate estimated rent based on size and location factor
    base_rate = 20  # EUR per sqm
    location_factor = 1.2 if location.lower() == "berlin" else 1.0
    estimated_rent = round(size_sqm * base_rate * location_factor)
    
    # Sample rent estimation result
    result = {
        "property_address": f"{location}, Example St.",
        "estimated_rent": estimated_rent,
        "low_range": round(estimated_rent * 0.9),
        "high_range": round(estimated_rent * 1.1),
        "rent_per_sqm": round(estimated_rent / size_sqm, 2),
        "comparable_properties": [
            {
                "address": f"{location}, Street A",
                "size_sqm": size_sqm - 5,
                "rent": estimated_rent - 100,
                "rent_per_sqm": round((estimated_rent - 100) / (size_sqm - 5), 2)
            },
            {
                "address": f"{location}, Street B",
                "size_sqm": size_sqm + 8,
                "rent": estimated_rent + 150,
                "rent_per_sqm": round((estimated_rent + 150) / (size_sqm + 8), 2)
            }
        ],
        "key_factors": ["size", "location", "condition", "amenities"],
        "rent_control_flag": location.lower() == "berlin",
        "confidence_score": 0.85
    }
    
    execution_time = time.time() - start_time
    logger.info(f"Rent estimation completed in {execution_time:.2f} seconds")
    logger.info(f"Estimated rent: €{result['estimated_rent']} (€{result['rent_per_sqm']}/sqm)")
    logger.info(f"Rent range: €{result['low_range']} - €{result['high_range']}")
    
    if result['rent_control_flag']:
        logger.info(f"Property subject to rent control regulations in {location}")
    
    return result

def create_mock_rent_data(location, property_type, size_sqm):
    """Create mock rent estimation data for testing"""
    logger.info(f"Creating mock rent data for {size_sqm}sqm {property_type} in {location}")
    
    base_rate = 20  # EUR per sqm
    location_factor = 1.2 if location.lower() == "berlin" else 1.0
    estimated_rent = round(size_sqm * base_rate * location_factor)
    
    return {
        "property_address": f"{location}, Example St.",
        "estimated_rent": estimated_rent,
        "low_range": round(estimated_rent * 0.9),
        "high_range": round(estimated_rent * 1.1),
        "rent_per_sqm": round(estimated_rent / size_sqm, 2),
        "key_factors": ["size", "location", "condition", "amenities"],
        "rent_control_flag": location.lower() == "berlin",
        "confidence_score": 0.85
    }

def run_optimization_analysis(location, property_type, size_sqm, purchase_price, estimated_rent):
    """Run investment optimization analysis"""
    logger.info(f"Starting optimization analysis for {property_type} investment in {location}")
    
    # Calculate basic financial metrics
    annual_rent = estimated_rent * 12
    gross_yield = (annual_rent / purchase_price) * 100
    
    # Prepare sample financial data
    financial_data = {
        "purchase_price": purchase_price,
        "monthly_rent": estimated_rent,
        "annual_rent": annual_rent,
        "mortgage_details": {
            "loan_amount": purchase_price * 0.7,
            "interest_rate": 3.5,
            "term_years": 25,
            "monthly_payment": round((purchase_price * 0.7) * (0.035 / 12) * (1 + 0.035 / 12) ** (25 * 12) / ((1 + 0.035 / 12) ** (25 * 12) - 1))
        },
        "monthly_expenses": {
            "property_tax": round(purchase_price * 0.0035 / 12),
            "insurance": 35,
            "maintenance": round(purchase_price * 0.01 / 12),
            "property_management": round(estimated_rent * 0.08),
            "vacancy_reserve": round(estimated_rent * 0.05)
        }
    }
    
    # Calculate monthly cash flow
    monthly_expenses = sum(financial_data["monthly_expenses"].values())
    monthly_mortgage = financial_data["mortgage_details"]["monthly_payment"]
    monthly_cash_flow = estimated_rent - monthly_expenses - monthly_mortgage
    
    financial_data["monthly_expenses_total"] = monthly_expenses
    financial_data["monthly_cash_flow"] = monthly_cash_flow
    financial_data["cash_on_cash_return"] = (monthly_cash_flow * 12) / (purchase_price * 0.3) * 100
    
    logger.info(f"Investment financial data prepared:")
    logger.info(f"  - Purchase price: €{purchase_price}")
    logger.info(f"  - Monthly rent: €{estimated_rent}")
    logger.info(f"  - Gross yield: {gross_yield:.2f}%")
    logger.info(f"  - Monthly cash flow: €{monthly_cash_flow}")
    
    # Mock optimization analysis (in a real implementation, this would make an API call)
    start_time = time.time()
    time.sleep(2)  # Simulate processing time
    
    # Sample optimization result
    result = {
        "recommendations": [
            {
                "category": "financing",
                "action": "Refinance at lower interest rate (3.0% vs current 3.5%)",
                "impact": {
                    "monthly_cash_flow": "+€87",
                    "cash_on_cash_roi": "+1.16%",
                    "implementation_cost": "€2000",
                    "payback_period": "23 months"
                },
                "priority": "high"
            },
            {
                "category": "rental_income",
                "action": "Adjust rent to market rate (currently 5% below market)",
                "impact": {
                    "monthly_cash_flow": "+€75",
                    "cash_on_cash_roi": "+1.0%",
                    "implementation_cost": "€0",
                    "payback_period": "immediate"
                },
                "priority": "high"
            },
            {
                "category": "expenses",
                "action": "Switch to a lower-cost property management service (6% vs current 8%)",
                "impact": {
                    "monthly_cash_flow": "+€30",
                    "cash_on_cash_roi": "+0.4%",
                    "implementation_cost": "€0",
                    "payback_period": "immediate"
                },
                "priority": "medium"
            }
        ],
        "projected_impact": {
            "total_monthly_cash_flow_improvement": "+€192",
            "total_annual_cash_flow_improvement": "+€2304",
            "cash_on_cash_roi_improvement": "+2.56%"
        },
        "implementation_costs": {
            "total": "€2000",
            "breakdown": {"financing": "€2000", "rental_income": "€0", "expenses": "€0"}
        },
        "prioritized_actions": [
            "1. Adjust rent to market rate",
            "2. Switch to lower-cost property management",
            "3. Refinance mortgage"
        ]
    }
    
    execution_time = time.time() - start_time
    logger.info(f"Optimization analysis completed in {execution_time:.2f} seconds")
    logger.info(f"Generated {len(result['recommendations'])} optimization recommendations")
    logger.info(f"Total potential monthly cash flow improvement: {result['projected_impact']['total_monthly_cash_flow_improvement']}")
    logger.info(f"Total potential ROI improvement: {result['projected_impact']['cash_on_cash_roi_improvement']}")
    
    return result

def create_mock_optimization_data(location, property_type, size_sqm, purchase_price, estimated_rent):
    """Create mock optimization data for testing"""
    logger.info(f"Creating mock optimization data for {property_type} in {location}")
    
    return {
        "recommendations": [
            {
                "category": "financing",
                "action": "Refinance at lower interest rate (3.0% vs current 3.5%)",
                "impact": {
                    "monthly_cash_flow": "+€87"
                },
                "priority": "high"
            },
            {
                "category": "rental_income",
                "action": "Adjust rent to market rate (currently 5% below market)",
                "impact": {
                    "monthly_cash_flow": "+€75"
                },
                "priority": "high"
            }
        ],
        "projected_impact": {
            "total_monthly_cash_flow_improvement": "+€192",
            "total_annual_cash_flow_improvement": "+€2304",
            "cash_on_cash_roi_improvement": "+2.56%"
        },
        "prioritized_actions": [
            "1. Adjust rent to market rate",
            "2. Refinance mortgage"
        ]
    }

def print_investment_summary(location, property_type, size_sqm, purchase_price, 
                            market_data, document_data, rent_data, optimization_data):
    """Print a comprehensive summary of the investment analysis"""
    print(f"\n{'='*80}")
    print(f"INVESTMENT ANALYSIS SUMMARY")
    print(f"{'='*80}")
    
    print(f"\n📍 PROPERTY DETAILS:")
    print(f"  Location: {location}")
    print(f"  Type: {property_type}")
    print(f"  Size: {size_sqm} sqm")
    print(f"  Purchase Price: €{purchase_price}")
    
    if market_data:
        print(f"\n📊 MARKET ANALYSIS:")
        if "price_data" in market_data:
            price_data = market_data["price_data"]
            print(f"  Average Market Price: {price_data.get('average_price_sqm', 'N/A')} EUR/sqm")
            print(f"  Market Trend: {price_data.get('price_trend', 'N/A')}")
        
        if "historical_data" in market_data and "summary" in market_data["historical_data"]:
            hist_summary = market_data["historical_data"]["summary"]
            print(f"  5-Year Price Appreciation: {hist_summary.get('price_appreciation', 'N/A')}%")
    
    if rent_data:
        print(f"\n💰 RENTAL ANALYSIS:")
        print(f"  Estimated Monthly Rent: €{rent_data.get('estimated_rent', 'N/A')}")
        print(f"  Rent per sqm: €{rent_data.get('rent_per_sqm', 'N/A')}")
        print(f"  Rent Range: €{rent_data.get('low_range', 'N/A')} - €{rent_data.get('high_range', 'N/A')}")
        print(f"  Rent Control Applicable: {'Yes' if rent_data.get('rent_control_flag', False) else 'No'}")
    
    if document_data:
        print(f"\n📄 DOCUMENT INSIGHTS:")
        for insight in document_data.get("key_insights", []):
            print(f"  • {insight}")
    
    if optimization_data:
        print(f"\n⚡ OPTIMIZATION OPPORTUNITIES:")
        for action in optimization_data.get("prioritized_actions", []):
            print(f"  • {action}")
        
        impact = optimization_data.get("projected_impact", {})
        print(f"\n  Potential Improvements:")
        print(f"  - Monthly Cash Flow: {impact.get('total_monthly_cash_flow_improvement', 'N/A')}")
        print(f"  - Annual Cash Flow: {impact.get('total_annual_cash_flow_improvement', 'N/A')}")
        print(f"  - ROI Improvement: {impact.get('cash_on_cash_roi_improvement', 'N/A')}")
    
    print(f"\n{'='*80}")
    print(f"End of Investment Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    
    # Write summary to log file
    logger.info("Investment analysis summary generated")
    logger.info(f"Property: {size_sqm}sqm {property_type} in {location}")
    logger.info(f"Purchase Price: €{purchase_price}")
    logger.info(f"Estimated Rent: €{rent_data.get('estimated_rent', 'N/A')}")
    logger.info(f"Potential Monthly Cash Flow Improvement: {impact.get('total_monthly_cash_flow_improvement', 'N/A')}")

if __name__ == "__main__":
    try:
        test_investment_scenario()
    except KeyboardInterrupt:
        logger.warning("Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during test: {str(e)}", exc_info=True)
        sys.exit(1)