"""
Example usage of the AI Agent System for property investment analysis.

This script demonstrates how to initialize and use the AI agent system with both
the manager agent approach and direct calls to specialized agents, supporting
both standard OpenAI and Azure OpenAI options.
"""

import os
import asyncio
import json
from dotenv import load_dotenv

from src.ai_agents import (
    AIAgentSystem,
    MarketDataRequest,
    RentEstimateRequest,
    DocumentAnalysisRequest,
    OptimizationRequest
)

# Load environment variables (including API keys)
load_dotenv()

async def example_standard_openai():
    """Example of using the AI agent system with standard OpenAI API."""
    print("\n=== Example: Using Standard OpenAI API ===\n")
    
    # Initialize the AI agent system with standard OpenAI
    agent_system = AIAgentSystem(model_name="gpt-4o")
    agent_system.initialize()
    
    # Example user request
    user_request = """
    I'm considering buying a 2-bedroom apartment in Berlin Mitte that's 80 square meters.
    It was built in 2010 and is in good condition. The asking price is €550,000.
    Can you help me analyze if this would be a good investment? I'd like to know about
    potential rental income and any optimizations I could make to improve returns.
    """
    
    print(f"User request: {user_request}")
    print("\nProcessing with standard OpenAI...\n")
    
    # Process the request
    result = await agent_system.process_user_request(user_request)
    print_result(result)

async def example_azure_openai():
    """Example of using the AI agent system with Azure OpenAI services."""
    print("\n=== Example: Using Azure OpenAI Services ===\n")
    
    # Check if Azure OpenAI environment variables are set
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    if not azure_api_key or not azure_endpoint or not azure_deployment:
        print("Azure OpenAI environment variables not set. Skipping Azure example.")
        print("To use Azure OpenAI, set the following environment variables:")
        print("  - AZURE_OPENAI_API_KEY")
        print("  - AZURE_OPENAI_ENDPOINT")
        print("  - AZURE_OPENAI_DEPLOYMENT_NAME")
        return
    
    # Initialize the AI agent system with Azure OpenAI
    agent_system = AIAgentSystem(
        use_azure=True,
        azure_deployment=azure_deployment,
        azure_endpoint=azure_endpoint,
        azure_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2023-07-01-preview"),
        use_managed_identity=os.getenv("AZURE_OPENAI_USE_MANAGED_IDENTITY", "false").lower() == "true"
    )
    agent_system.initialize()
    
    # Example user request
    user_request = """
    I'm considering buying a 2-bedroom apartment in Berlin Mitte that's 80 square meters.
    It was built in 2010 and is in good condition. The asking price is €550,000.
    Can you help me analyze if this would be a good investment? I'd like to know about
    potential rental income and any optimizations I could make to improve returns.
    """
    
    print(f"User request: {user_request}")
    print("\nProcessing with Azure OpenAI...\n")
    
    # Process the request
    result = await agent_system.process_user_request(user_request)
    print_result(result)

async def example_direct_agent_calls(use_azure=False):
    """Example of making direct calls to specialized agents."""
    service_type = "Azure OpenAI" if use_azure else "Standard OpenAI"
    print(f"\n=== Example: Using Specialized Agents Directly with {service_type} ===\n")
    
    # Initialize the AI agent system
    if use_azure:
        # Check if Azure OpenAI environment variables are set
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        if not azure_api_key or not azure_endpoint or not azure_deployment:
            print("Azure OpenAI environment variables not set. Skipping Azure example.")
            return
        
        agent_system = AIAgentSystem(
            use_azure=True,
            azure_deployment=azure_deployment,
            azure_endpoint=azure_endpoint,
            azure_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2023-07-01-preview")
        )
    else:
        agent_system = AIAgentSystem(model_name="gpt-4o")
    
    agent_system.initialize()
    
    # Example: Market Data Search Agent
    print("\n--- Market Data Search Agent ---\n")
    market_request = json.dumps({
        "location": "Berlin Mitte",
        "property_type": "apartment",
        "data_types": ["prices", "rents", "trends"],
        "timeframe": "5 years"
    })
    
    print(f"Request: {market_request}")
    market_result = await agent_system.execute_direct_task("market_data", market_request)
    print(f"Result status: {market_result.status}")
    if market_result.status == "success":
        print(f"Content: {market_result.content}\n")

def print_result(result):
    """Helper function to print results in a readable format."""
    if result["status"] == "success":
        print("Success!")
        print(f"Result: {result['result']}")
    else:
        print("Error!")
        print(f"Error message: {result['error']}")

async def main():
    """Run the example usage demonstrations."""
    # Check for API key
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("AZURE_OPENAI_API_KEY"):
        print("Error: No API key environment variable is set")
        print("Please create a .env file with either OPENAI_API_KEY or AZURE_OPENAI_API_KEY")
        return
    
    try:
        # Example of using the standard OpenAI API
        if os.getenv("OPENAI_API_KEY"):
            await example_standard_openai()
        
        # Example of using Azure OpenAI services
        if os.getenv("AZURE_OPENAI_API_KEY"):
            await example_azure_openai()
        
        # Example of direct calls to specialized agents (using standard OpenAI)
        if os.getenv("OPENAI_API_KEY"):
            await example_direct_agent_calls(use_azure=False)
        
        # Example of direct calls to specialized agents (using Azure OpenAI)
        if os.getenv("AZURE_OPENAI_API_KEY"):
            await example_direct_agent_calls(use_azure=True)
        
    except Exception as e:
        print(f"Error during execution: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())