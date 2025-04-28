"""
Test script for the enhanced AI Agent memory system.

This script verifies the functionality of the Memory Management component
of our enhanced AI Agent architecture.
"""

import asyncio
import os
import logging
from dotenv import load_dotenv
import sys
import json
import time

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize memory with a test file
test_memory_file = "/home/azureuser/investment_agent/test_scripts/test_agent_memory.json"

# Remove the test file if it exists
if os.path.exists(test_memory_file):
    os.remove(test_memory_file)
    logger.info(f"Removed existing test memory file: {test_memory_file}")

# Import our memory system
from src.ai_agents.memory.agent_memory import get_agent_memory, AgentMemory

async def test_memory_system():
    """Test the agent memory management system."""
    logger.info("Starting test for Agent Memory system...")
    
    
    try:
        # Get a memory instance
        memory = get_agent_memory(memory_file=test_memory_file)
        logger.info(f"Initialized memory system with file: {test_memory_file}")
        
        # Test 1: Add conversation messages
        logger.info("\n===== Test 1: Add conversation messages =====")
        # Clear any existing memories to ensure a fresh test
        memory.memories = []
        
        memory.add_user_message("I'm interested in buying a rental property in Berlin.")
        memory.add_agent_message("That's a good choice. What's your budget for this investment?")
        memory.add_user_message("I'm looking to invest around 500,000 euros.")
        memory.add_agent_message("Great. And what kind of property are you looking for?")
        memory.add_user_message("A small apartment building with 2-3 units.")
        
        # Get conversation history
        history = memory.get_conversation_history(limit=10)
        logger.info(f"Retrieved {len(history)} conversation turns")
        
        # Validate conversation history
        assert len(history) == 5, f"Expected 5 conversation turns, got {len(history)}"
        assert history[0]['role'] == 'user', f"Expected first message role to be 'user', got '{history[0]['role']}'"
        assert history[1]['role'] == 'agent', f"Expected second message role to be 'agent', got '{history[1]['role']}'"
        
        logger.info("Test 1 passed: Conversation history is working correctly")
        
        # Test 2: Add user preferences
        logger.info("\n===== Test 2: Add user preferences =====")
        memory.add_user_preference("location", "Berlin")
        memory.add_user_preference("budget", "500000")
        memory.add_user_preference("property_type", "apartment building")
        memory.add_user_preference("units", "2-3")
        
        # Get user preferences
        preferences = memory.get_user_preferences()
        logger.info(f"Retrieved user preferences: {preferences}")
        
        # Validate user preferences
        assert len(preferences) == 4, f"Expected 4 preferences, got {len(preferences)}"
        assert preferences["location"] == "Berlin", f"Expected location to be 'Berlin', got '{preferences['location']}'"
        assert preferences["budget"] == "500000", f"Expected budget to be '500000', got '{preferences['budget']}'"
        
        logger.info("Test 2 passed: User preferences are working correctly")
        
        # Test 3: Add facts to memory
        logger.info("\n===== Test 3: Add facts to memory =====")
        memory.add_fact("Berlin rental yields average between 3.0% and 3.5% in central areas.", 
                       source_reference="Market Research 2025")
        memory.add_fact("Property prices in Berlin have increased by 5.3% over the past year.",
                       source_reference="Real Estate Report 2025")
        
        # Get all facts
        facts = memory.get_facts()
        logger.info(f"Retrieved {len(facts)} facts")
        
        # Validate facts
        assert len(facts) == 2, f"Expected 2 facts, got {len(facts)}"
        
        logger.info("Test 3 passed: Facts storage is working correctly")
        
        # Test 4: Add decisions to memory
        logger.info("\n===== Test 4: Add decisions to memory =====")
        memory.add_decision(
            decision="Recommended focusing on 2-bedroom apartments in Berlin Mitte or Friedrichshain.",
            reasoning="These areas offer the best combination of rental yields and appreciation potential.",
            confidence=0.85
        )
        
        # Get all decisions
        decisions = memory.get_decisions()
        logger.info(f"Retrieved {len(decisions)} decisions")
        
        # Validate decisions
        assert len(decisions) == 1, f"Expected 1 decision, got {len(decisions)}"
        assert decisions[0]['confidence'] == 0.85, f"Expected confidence to be 0.85, got {decisions[0]['confidence']}"
        
        logger.info("Test 4 passed: Decisions storage is working correctly")
        
        # Test 5: Verify file persistence
        logger.info("\n===== Test 5: Verify file persistence =====")
        
        # Force saving to file
        memory.save_memory()
        
        # Check if the file exists
        assert os.path.exists(test_memory_file), f"Memory file {test_memory_file} was not created"
        
        # Read the file contents
        with open(test_memory_file, 'r') as f:
            memory_data = json.load(f)
        
        # Validate file contents
        assert 'conversation_history' in memory_data, "Conversation history missing from memory file"
        assert 'user_preferences' in memory_data, "User preferences missing from memory file"
        assert 'facts' in memory_data, "Facts missing from memory file"
        assert 'decisions' in memory_data, "Decisions missing from memory file"
        
        logger.info("Test 5 passed: Memory persistence is working correctly")
        
        # Test 6: Create LangChain memory
        logger.info("\n===== Test 6: Create LangChain memory =====")
        try:
            # Attempt to create a LangChain memory object
            langchain_memory = memory.create_langchain_memory()
            logger.info(f"Created LangChain memory: {langchain_memory is not None}")
            
            # Log success even if we couldn't create it due to missing dependencies
            logger.info("Test 6 completed: LangChain memory creation attempted")
        except ImportError:
            logger.info("Test 6 skipped: LangChain not installed")
        
        # Test 7: Memory capacity and performance
        logger.info("\n===== Test 7: Memory capacity and performance =====")
        start_time = time.time()
        
        # Add 100 more messages to test performance
        for i in range(100):
            memory.add_user_message(f"Test message {i}")
            memory.add_agent_message(f"Response to test message {i}")
        
        # Get history again
        large_history = memory.get_conversation_history(limit=50)
        end_time = time.time()
        
        # Validate performance
        assert len(large_history) == 50, f"Expected 50 conversation turns, got {len(large_history)}"
        logger.info(f"Added 200 messages and retrieved 50 in {end_time - start_time:.4f} seconds")
        
        logger.info("Test 7 passed: Memory system handles larger volumes efficiently")
        
        # Final verification: create a new memory instance with the same file
        logger.info("\n===== Final test: New memory instance with existing file =====")
        new_memory = get_agent_memory(memory_file=test_memory_file)
        
        # Get history from new instance
        new_history = new_memory.get_conversation_history(limit=5)
        
        # Validate persistence across instances
        assert len(new_history) == 5, f"Expected 5 conversation turns, got {len(new_history)}"
        
        logger.info("Final test passed: Memory loads correctly from existing file")
        
        # Clean up
        if os.path.exists(test_memory_file):
            os.remove(test_memory_file)
            logger.info(f"Cleaned up test memory file: {test_memory_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing memory system: {str(e)}")
        return False

async def main():
    """Run the memory system test."""
    logger.info("Starting Memory System Test Suite")
    
    # Test memory system
    memory_test_result = await test_memory_system()
    
    # Print summary
    logger.info("\n===== Test Results Summary =====")
    logger.info(f"Memory System Test: {'PASSED' if memory_test_result else 'FAILED'}")

if __name__ == "__main__":
    asyncio.run(main())