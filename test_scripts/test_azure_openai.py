#!/usr/bin/env python3
"""
Test script for the enhanced AI Agent system with Azure OpenAI integration.

This script verifies the LangChain-enhanced agent architecture using Azure OpenAI.
"""

import asyncio
import os
import logging
from dotenv import load_dotenv
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_azure_openai_integration():
    """Test Azure OpenAI connection and basic functionality."""
    
    # Load environment variables
    load_dotenv()
    
    # Check if Azure OpenAI is configured
    if not os.getenv("AZURE_OPENAI_API_KEY") or not os.getenv("AZURE_OPENAI_ENDPOINT"):
        logger.error("Azure OpenAI is not configured. Please set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT in your .env file.")
        return False
    
    try:
        # Import here to avoid errors if dependencies aren't installed
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_openai import AzureChatOpenAI
        
        # Initialize Azure OpenAI chat model using LangChain
        model = AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            temperature=0.7
        )
        
        # Test basic chat completion
        messages = [
            SystemMessage(content="You are a helpful assistant specialized in property investment analysis."),
            HumanMessage(content="What are the key factors to consider when evaluating a rental property investment?")
        ]
        
        # Call the model
        logger.info("Sending test request to Azure OpenAI...")
        response = model.invoke(messages)
        
        logger.info(f"Response received from Azure OpenAI: {response.content[:100]}...")
        logger.info("Azure OpenAI connection test passed!")
        
        # Print the full response for verification
        print("\nFull Response from Azure OpenAI:")
        print("-" * 50)
        print(response.content)
        print("-" * 50)
        
        # Test with the OpenAI client directly
        try:
            from openai import AzureOpenAI
            
            # Create Azure OpenAI client
            client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )
            
            # Call the model
            logger.info("Testing with OpenAI client directly...")
            completion = client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
                messages=[
                    {"role": "system", "content": "You are a helpful assistant specialized in property investment analysis."},
                    {"role": "user", "content": "What are the key factors to consider when evaluating a rental property investment?"}
                ],
                temperature=0.7
            )
            
            # Print response
            logger.info(f"Response received from OpenAI client: {completion.choices[0].message.content[:100]}...")
            logger.info("OpenAI client test passed!")
            
            print("\nFull Response from OpenAI Client:")
            print("-" * 50)
            print(completion.choices[0].message.content)
            print("-" * 50)
            
        except Exception as e:
            logger.error(f"Error testing with OpenAI client: {str(e)}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error testing Azure OpenAI integration: {str(e)}")
        return False

async def main():
    """Run Azure OpenAI integration test."""
    logger.info("Starting test for Azure OpenAI integration...")
    
    # Test Azure OpenAI integration
    azure_test_result = await test_azure_openai_integration()
    
    # Print summary
    logger.info("\n===== Test Results Summary =====")
    logger.info(f"Azure OpenAI Integration: {'PASSED' if azure_test_result else 'FAILED'}")

if __name__ == "__main__":
    asyncio.run(main())