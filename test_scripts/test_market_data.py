#!/usr/bin/env python3
"""
Test script for the /ai/market-data/ endpoint
"""
import requests
import json
import time
import sys
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_market_data():
    """Test the market data endpoint"""
    print(f"\n{'='*80}")
    print(f"MARKET DATA AGENT TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    
    print("\nPreparing request payload...")
    
    # Prepare the request payload
    payload = {
        "location": "berlin",
        "property_type": "apartment",
        "additional_filters": {
            "min_price": 100000,
            "max_price": 500000,
            "min_size": 50,
            "features": ["balcony", "elevator"]
        }
    }
    
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    print("\nSending request to market data agent...")
    
    # Make the initial POST request to start the task
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/ai/market-data/", json=payload)
    
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}")
        print(response.text)
        return
    
    # Get the task ID from the response
    response_data = response.json()
    task_id = response_data.get("task_id")
    
    if not task_id:
        print("Error: No task ID in response")
        return
    
    print(f"\n✅ Successfully created task with ID: {task_id}")
    print(f"Initial status: {response_data.get('status')}")
    
    # Poll for the task result
    max_attempts = 20
    attempts = 0
    
    print("\nPolling for task completion:")
    print(f"{'='*80}")
    
    while attempts < max_attempts:
        attempts += 1
        
        # Progress indicator
        progress = "#" * attempts + " " * (max_attempts - attempts)
        elapsed = time.time() - start_time
        sys.stdout.write(f"\r[{progress}] Attempt {attempts}/{max_attempts} - Elapsed: {elapsed:.1f}s")
        sys.stdout.flush()
        
        # Get the task result
        result_response = requests.get(f"{BASE_URL}/ai/tasks/{task_id}")
        
        if result_response.status_code != 200:
            print(f"\nError checking task: {result_response.status_code}")
            time.sleep(5)  # Increased from 3 to 5 seconds
            continue
        
        result_data = result_response.json()
        status = result_data.get("status")
        
        if status == "completed":
            print("\n\n✅ Task completed!")
            print(f"Total time: {time.time() - start_time:.2f} seconds")
            print(f"\nRESULT SUMMARY:")
            print(f"{'='*80}")
            
            result = result_data.get("result", {})
            
            # Print a more structured summary of the results
            if result:
                location = result.get("location", "Unknown location")
                property_type = result.get("property_type", "Unknown type")
                
                print(f"📍 Location: {location}")
                print(f"🏢 Property Type: {property_type}")
                
                # Price data summary
                if "price_data" in result:
                    price_data = result["price_data"]
                    print(f"\n💰 PRICE DATA:")
                    print(f"  Average Price: {price_data.get('average_price_sqm', 'N/A')} EUR/sqm")
                    print(f"  Price Range: {price_data.get('price_range', {}).get('min', 'N/A')} - {price_data.get('price_range', {}).get('max', 'N/A')} EUR/sqm")
                    print(f"  Trend: {price_data.get('price_trend', 'N/A')}")
                
                # Rental data summary
                if "rental_data" in result:
                    rental_data = result["rental_data"]
                    print(f"\n🏠 RENTAL DATA:")
                    print(f"  Average Rent: {rental_data.get('average_rent_sqm', 'N/A')} EUR/sqm/month")
                    print(f"  Rent Range: {rental_data.get('rent_range', {}).get('min', 'N/A')} - {rental_data.get('rent_range', {}).get('max', 'N/A')} EUR/sqm/month")
                    print(f"  Vacancy Rate: {rental_data.get('vacancy_rate', 'N/A')}%")
                
                # Historical data summary
                if "historical_data" in result and result["historical_data"]:
                    hist_data = result["historical_data"]
                    print(f"\n📈 HISTORICAL DATA:")
                    if "summary" in hist_data:
                        summary = hist_data["summary"]
                        print(f"  Price Appreciation: {summary.get('price_appreciation', 'N/A')}%")
                        print(f"  Rent Appreciation: {summary.get('rent_appreciation', 'N/A')}%")
                        print(f"  Timeframe: {summary.get('years', 'N/A')} years")
                
                # Development news summary
                if "development_news" in result and result["development_news"]:
                    dev_news = result["development_news"]
                    print(f"\n📰 DEVELOPMENT NEWS:")
                    print(f"  Number of news items: {len(dev_news.get('news', []))}")
                    
                    # Impact summary if available
                    if "impact_summary" in dev_news:
                        impact = dev_news["impact_summary"]
                        print(f"  Impact Summary:")
                        for impact_type, count in impact.items():
                            if count > 0:
                                print(f"    - {impact_type}: {count}")
                
                # Confidence scores
                if "confidence_scores" in result:
                    conf = result["confidence_scores"]
                    print(f"\n🎯 CONFIDENCE SCORES:")
                    for data_type, score in conf.items():
                        print(f"  {data_type}: {score:.2f}")
                
                # Sources
                if "sources" in result:
                    sources = result["sources"]
                    print(f"\n📚 SOURCES: {len(sources)}")
            
            # Option to view full JSON result
            show_full = input("\nShow full JSON result? (y/n): ")
            if show_full.lower() == 'y':
                print("\nFULL RESULT JSON:")
                print(f"{'='*80}")
                print(json.dumps(result, indent=2))
            
            return
        
        # If still processing, wait a bit before checking again
        time.sleep(5)  # Increased from 3 to 5 seconds
    
    print("\n\n⚠️ Task did not complete within the timeout period")
    print(f"Last known status: {status}")

if __name__ == "__main__":
    try:
        test_market_data()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during test: {str(e)}")
        sys.exit(1)
