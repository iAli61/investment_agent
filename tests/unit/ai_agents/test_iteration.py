"""
Tests for the BaseAgent iteration functionality
"""
import unittest
import asyncio
from unittest.mock import patch, MagicMock
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.ai_agents.base_agent import BaseAgent

class TestAgentIteration(unittest.TestCase):
    """Test cases for agent iteration functionality"""
    
    class SimpleTestAgent(BaseAgent):
        """A simple agent implementation for testing"""
        
        def _get_agent_name(self):
            return "TestAgent"
            
        def _get_agent_description(self):
            return "A test agent for unit testing"
            
        async def _execute_logic(self, parameters, context):
            # Mock implementation that just returns what it receives
            return {
                "processed_parameters": parameters,
                "context_received": context
            }
    
    def setUp(self):
        """Set up test cases"""
        self.agent = self.SimpleTestAgent()
    
    def test_initial_iteration_state(self):
        """Test the initial iteration state of a new agent"""
        self.assertEqual(self.agent.iteration_count, 0)
        self.assertEqual(self.agent.max_iterations, 10)  # Default value
        self.assertTrue(self.agent.should_continue)
    
    def test_reset_iteration(self):
        """Test resetting the iteration state"""
        # Set some values
        self.agent.iteration_count = 5
        self.agent.should_continue = False
        
        # Reset
        self.agent.reset_iteration()
        
        # Check values were reset
        self.assertEqual(self.agent.iteration_count, 0)
        self.assertTrue(self.agent.should_continue)
    
    def test_set_max_iterations(self):
        """Test setting max iterations"""
        self.agent.set_max_iterations(20)
        self.assertEqual(self.agent.max_iterations, 20)
        
        # Test invalid value
        with self.assertRaises(ValueError):
            self.agent.set_max_iterations(0)
            
        with self.assertRaises(ValueError):
            self.agent.set_max_iterations(-5)
    
    def test_execute_increments_iteration(self):
        """Test that execute increments the iteration counter"""
        result = asyncio.run(self.agent.execute({}, {}))
        self.assertEqual(self.agent.iteration_count, 1)
        self.assertEqual(result["iteration"], 1)
        
        # Execute again
        result = asyncio.run(self.agent.execute({}, {}))
        self.assertEqual(self.agent.iteration_count, 2)
        self.assertEqual(result["iteration"], 2)
    
    def test_continue_iteration_parameter(self):
        """Test the continue_iteration parameter"""
        # Test with continue = yes
        result = asyncio.run(self.agent.execute({"continue_iteration": "yes"}, {}))
        self.assertTrue(self.agent.should_continue)
        self.assertTrue(result["should_continue"])
        
        # Test with continue = no
        result = asyncio.run(self.agent.execute({"continue_iteration": "no"}, {}))
        self.assertFalse(self.agent.should_continue)
        self.assertFalse(result["should_continue"])
        
        # Reset
        self.agent.reset_iteration()
        
        # Test with continue = true (case insensitive)
        result = asyncio.run(self.agent.execute({"continue_iteration": "TRUE"}, {}))
        self.assertTrue(self.agent.should_continue)
        
        # Test with continue = false (case insensitive)
        result = asyncio.run(self.agent.execute({"continue_iteration": "False"}, {}))
        self.assertFalse(self.agent.should_continue)
    
    def test_max_iterations_reached(self):
        """Test behavior when max iterations is reached"""
        # Set max iterations to 3
        self.agent.set_max_iterations(3)
        
        # Execute three times
        for i in range(3):
            result = asyncio.run(self.agent.execute({}, {}))
            # For iterations 1 and 2, should_continue is true
            if i < 2:
                self.assertTrue(self.agent.should_continue)
                self.assertTrue(result["should_continue"])
                self.assertEqual(result["message"], "Continue to iterate?")
            else:
                # For iteration 3, should_continue is false
                self.assertFalse(self.agent.should_continue)
                self.assertFalse(result["should_continue"])
                self.assertEqual(result["message"], "Iteration complete.")
    
    def test_continue_to_iterate_message(self):
        """Test that the correct message is included in the result"""
        # When should_continue is true
        result = asyncio.run(self.agent.execute({}, {}))
        self.assertEqual(result["message"], "Continue to iterate?")
        
        # When should_continue is false
        result = asyncio.run(self.agent.execute({"continue_iteration": "no"}, {}))
        self.assertEqual(result["message"], "Iteration complete.")
    
    def test_error_stops_iteration(self):
        """Test that an error stops iteration"""
        # Create an agent that raises an exception
        error_agent = self.SimpleTestAgent()
        
        # Mock _execute_logic to raise an exception
        async def mock_execute_logic(*args, **kwargs):
            raise ValueError("Test error")
            
        error_agent._execute_logic = mock_execute_logic
        
        # Execute and check result
        result = asyncio.run(error_agent.execute({}, {}))
        self.assertFalse(result["success"])
        self.assertEqual(result["error_type"], "ValueError")
        self.assertEqual(result["error"], "Test error")
        self.assertFalse(result["should_continue"])

if __name__ == "__main__":
    unittest.main()