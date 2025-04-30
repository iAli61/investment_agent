"""
Test script for the enhanced AI Agent system using OpenAI Agents SDK with Azure OpenAI.

This script demonstrates how to integrate the OpenAI Agents SDK with Azure OpenAI
for the Property Investment Analysis Application.
"""
import os
import sys
import asyncio
import logging
from dotenv import load_dotenv
import logfire

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import OpenAI and Agents SDK
from openai import AsyncAzureOpenAI
from agents import Agent, Runner, set_default_openai_client, function_tool, OpenAIChatCompletionsModel
from agents.tracing.processors import ConsoleSpanExporter, BatchTraceProcessor
from agents import add_trace_processor, set_tracing_export_api_key, trace, set_tracing_disabled

# Import our enhanced agent system components
from src.ai_agents.memory.agent_memory import get_agent_memory
from src.ai_agents.rag.vector_store import get_vector_store

# Load environment variables
load_dotenv()

async def setup_azure_openai_client():
    """Set up Azure OpenAI client for use with Agents SDK."""
    
    # Load environment variables
    load_dotenv()
    
    # Check if Azure OpenAI is configured
    if not os.getenv("AZURE_OPENAI_API_KEY") or not os.getenv("AZURE_OPENAI_ENDPOINT"):
        logger.error("Azure OpenAI is not configured. Please set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT in your .env file.")
        return None
    
    try:
        # Disable tracing completely for the Agents SDK before client creation
        # This ensures tracing is disabled before any client operations
        os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1"
        set_tracing_disabled(True)
        logger.info("Tracing has been disabled for the Agents SDK")
        
        # Create Azure OpenAI client with explicit API version
        openai_client = AsyncAzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
        )
        
        # Set as default client for Agents SDK
        set_default_openai_client(openai_client)
        
        logger.info(f"Azure OpenAI client set up successfully using API version: {os.getenv('AZURE_OPENAI_API_VERSION', '2025-03-01-preview')}")
        return openai_client
    
    except Exception as e:
        logger.error(f"Error setting up Azure OpenAI client: {str(e)}")
        return None

# Define agent tools that will utilize our enhanced RAG and memory capabilities
@function_tool
async def search_property_knowledge(query: str) -> str:
    """
    Search for relevant knowledge about property investment.
    
    Args:
        query: The search query about property investment
        
    Returns:
        Relevant information about the property investment topic
    """
    logger.info(f"Searching property knowledge for: {query}")
    
    # Initialize our vector store
    vector_store = get_vector_store(vector_db_path="./test_vector_db", use_faiss=True)
    
    # Search for relevant information
    results = vector_store.search(query, k=3)
    
    if not results:
        return f"I couldn't find any specific information about {query}. Would you like to try a different search query?"
    
    # Format results
    knowledge = "\n\n".join([f"Source: {result.metadata.get('source', 'Unknown')}\n{result.text}" 
                           for result in results])
    
    return f"Here's what I found about {query}:\n\n{knowledge}"

@function_tool
async def get_user_investment_preferences() -> dict:
    """
    Retrieve the user's saved investment preferences.
    
    Returns:
        Dictionary of user investment preferences
    """
    logger.info("Retrieving user investment preferences")
    
    # Initialize our memory system
    memory = get_agent_memory(memory_file="./test_agent_memory.json")
    
    # Get user preferences
    preferences = memory.get_user_preferences()
    
    if not preferences:
        return {
            "preferences": {},
            "message": "No investment preferences found. You can set preferences using the save_user_investment_preference tool."
        }
    
    return {
        "preferences": preferences,
        "message": "Successfully retrieved user investment preferences."
    }

@function_tool
async def save_user_investment_preference(key: str, value: str) -> str:
    """
    Save a user investment preference.
    
    Args:
        key: The preference key (e.g., "location", "budget", "property_type")
        value: The preference value
        
    Returns:
        Confirmation message
    """
    logger.info(f"Saving user investment preference: {key}={value}")
    
    # Initialize our memory system
    memory = get_agent_memory(memory_file="./test_agent_memory.json")
    
    # Save the preference
    memory.add_user_preference(key, value)
    
    return f"Successfully saved your preference for {key}: {value}"

@function_tool
async def get_conversation_history() -> str:
    """
    Retrieve recent conversation history.
    
    Returns:
        Recent conversation turns
    """
    logger.info("Retrieving conversation history")
    
    # Initialize our memory system
    memory = get_agent_memory(memory_file="./test_agent_memory.json")
    
    # Get conversation history
    history = memory.get_conversation_history(limit=5)
    
    if not history:
        return "No conversation history found."
    
    # Format history
    formatted_history = "\n".join([
        f"{turn['role']}: {turn['content']}"
        for turn in history
    ])
    
    return f"Here's our recent conversation:\n\n{formatted_history}"

@function_tool
async def calculate_mortgage_payment(principal: float, interest_rate: float, years: int) -> dict:
    """
    Calculate monthly mortgage payment.
    
    Args:
        principal: Loan amount in dollars
        interest_rate: Annual interest rate (as a percentage, e.g., 4.5 for 4.5%)
        years: Loan term in years
        
    Returns:
        Dictionary with payment details
    """
    logger.info(f"Calculating mortgage payment: principal=${principal}, rate={interest_rate}%, term={years} years")
    
    # Convert annual interest rate to monthly rate and years to months
    monthly_rate = interest_rate / 100 / 12
    months = years * 12
    
    # Calculate monthly payment using the loan payment formula
    if monthly_rate == 0:
        monthly_payment = principal / months
    else:
        monthly_payment = principal * monthly_rate * (1 + monthly_rate) ** months / ((1 + monthly_rate) ** months - 1)
    
    # Calculate total payment and interest
    total_payment = monthly_payment * months
    total_interest = total_payment - principal
    
    return {
        "monthly_payment": round(monthly_payment, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2),
        "loan_term_months": months
    }

@function_tool
async def analyze_property_investment(
    purchase_price: float,
    monthly_rental_income: float,
    monthly_expenses: float,
    annual_appreciation: float = 3.0,
    holding_period: int = 5
) -> dict:
    """
    Analyze a property investment.
    
    Args:
        purchase_price: Property purchase price in dollars
        monthly_rental_income: Expected monthly rental income in dollars
        monthly_expenses: Monthly expenses (excluding mortgage) in dollars
        annual_appreciation: Expected annual property appreciation rate (%)
        holding_period: Investment holding period in years
        
    Returns:
        Dictionary with investment analysis
    """
    logger.info(f"Analyzing property investment: price=${purchase_price}, rent=${monthly_rental_income}/mo")
    
    # Calculate annual values
    annual_rental_income = monthly_rental_income * 12
    annual_expenses = monthly_expenses * 12
    
    # Calculate net operating income (NOI)
    noi = annual_rental_income - annual_expenses
    
    # Calculate cap rate
    cap_rate = (noi / purchase_price) * 100
    
    # Calculate cash on cash return (assuming 25% down payment and 5% interest rate)
    down_payment = purchase_price * 0.25
    loan_amount = purchase_price - down_payment
    
    # Estimate mortgage payment (30-year fixed at 5%)
    mortgage_result = await calculate_mortgage_payment(loan_amount, 5.0, 30)
    annual_mortgage = mortgage_result["monthly_payment"] * 12
    
    # Cash flow
    cash_flow = noi - annual_mortgage
    cash_on_cash_return = (cash_flow / down_payment) * 100
    
    # Future value after holding period
    future_value = purchase_price * (1 + annual_appreciation / 100) ** holding_period
    
    # Return analysis
    return {
        "purchase_price": purchase_price,
        "down_payment": down_payment,
        "monthly_rental_income": monthly_rental_income,
        "monthly_expenses": monthly_expenses,
        "monthly_cash_flow": round(cash_flow / 12, 2),
        "cap_rate": round(cap_rate, 2),
        "cash_on_cash_return": round(cash_on_cash_return, 2),
        "future_value": round(future_value, 2),
        "total_profit": round(future_value - purchase_price + (cash_flow * holding_period), 2),
        "roi": round(((future_value - purchase_price + (cash_flow * holding_period)) / (down_payment + (annual_expenses * holding_period))) * 100, 2)
    }

async def create_property_investment_agent():
    """Create a property investment assistant using the OpenAI Agents SDK with Azure OpenAI."""
    
    # Set up the OpenAI client
    client = await setup_azure_openai_client()
    if not client:
        logger.error("Failed to set up Azure OpenAI client. Cannot create agent.")
        return None
    
    # Create the property investment agent
    investment_agent = Agent(
        name="Property Investment Assistant",
        instructions="""You are a helpful property investment assistant that provides information and analysis about real estate investments.
        
You can use various tools to help the user, including:
1. Searching for property investment knowledge
2. Retrieving the user's saved investment preferences
3. Saving new user investment preferences
4. Retrieving conversation history to maintain context
5. Calculating mortgage payments
6. Analyzing property investments

Always provide accurate, helpful information and focus on the financial aspects of property investment.
When analyzing investments, consider factors like cash flow, appreciation potential, tax benefits, and risk.

If the user asks about a specific location or property type, try to provide tailored information based on their preferences.
""",
        model=OpenAIChatCompletionsModel(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
            openai_client=client
        ),
        tools=[
            search_property_knowledge,
            get_user_investment_preferences,
            save_user_investment_preference,
            get_conversation_history,
            calculate_mortgage_payment,
            analyze_property_investment
        ]
    )
    
    logger.info("Property investment agent created successfully")
    return investment_agent

async def test_property_investment_agent():
    """Test the property investment agent with the Agents SDK and Azure OpenAI."""
    
    # Create the agent
    agent = await create_property_investment_agent()
    if not agent:
        logger.error("Failed to create property investment agent.")
        return False
    
    try:
        # Add some test data to memory and vector store
        vector_store = get_vector_store(vector_db_path="./test_vector_db")
        
        # Add sample property investment knowledge
        sample_texts = [
            "Rental yield is calculated by dividing the annual rental income by the property purchase price, then multiplying by 100 to get a percentage. A good rental yield is typically considered to be 5-8%.",
            "When investing in property, location is a critical factor. Properties near public transportation, schools, and amenities tend to command higher rents and appreciation.",
            "Cash-on-cash return measures the annual pre-tax cash flow divided by the total cash invested, expressed as a percentage. It's a key metric for rental property investors.",
            "Cap rate (capitalization rate) is calculated by dividing a property's net operating income (NOI) by its current market value or acquisition cost. Higher cap rates generally indicate higher risk investments."
        ]
        
        sample_metadata = [
            {"source": "Investment Guide", "topic": "Rental Yield"},
            {"source": "Location Analysis", "topic": "Property Value Factors"},
            {"source": "Financial Metrics", "topic": "Cash-on-Cash Return"},
            {"source": "Financial Metrics", "topic": "Cap Rate"}
        ]
        
        vector_store.add_documents(sample_texts, sample_metadata)
        logger.info("Added sample knowledge to vector store for testing")
        
        # Set up test scenarios with different questions
        test_questions = [
            "What factors affect property value?",
            "Can you calculate the mortgage payment for a $300,000 loan at 4.5% for 30 years?",
            "What is a good rental yield for investment properties?",
            "Can you analyze an investment property that costs $400,000 with $2,500 monthly rent and $500 monthly expenses?"
        ]
        
        # Run tests
        for i, question in enumerate(test_questions):
            print(f"\n===== Test Question {i+1}: {question} =====\n")
            
            # Run the agent
            result = await Runner.run(agent, input=question)
            
            # Print the response
            print(f"Agent Response:")
            print("-" * 50)
            
            # Display the result as a string - this works for any RunResult object
            print(str(result))
            print("-" * 50)
        
        print("\n===== Test Complete =====\n")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing property investment agent: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def main():
    """Run the OpenAI Agents SDK with Azure OpenAI test."""
    logger.info("Starting test for OpenAI Agents SDK with Azure OpenAI integration...")
    
    # Test property investment agent
    result = await test_property_investment_agent()
    
    logger.info("\n===== Test Result =====")
    logger.info(f"Property Investment Agent with Azure OpenAI: {'PASSED' if result else 'FAILED'}")
    
    # Clean up test files
    try:
        import shutil
        import os
        
        # Delete test vector store and memory files
        if os.path.exists("./test_vector_db"):
            shutil.rmtree("./test_vector_db")
            logger.info("Cleaned up test vector store")
            
        if os.path.exists("./test_agent_memory.json"):
            os.remove("./test_agent_memory.json")
            logger.info("Cleaned up test agent memory")
            
    except Exception as e:
        logger.error(f"Error cleaning up test files: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())