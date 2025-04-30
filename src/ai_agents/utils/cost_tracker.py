"""
Cost tracking middleware for monitoring and recording API and compute costs
"""
import time
import uuid
import logging
from typing import Dict, Any, Optional, List, Callable
import json
from functools import wraps
from datetime import datetime

from ..database.database import get_db
from ..database.models import CostTracker, Scenario

logger = logging.getLogger(__name__)

# Pricing information for different models (USD per 1K tokens)
MODEL_PRICING = {
    "gpt-4o": {
        "input": 0.01,
        "output": 0.03
    },
    "gpt-4o-2024-05-13": {
        "input": 0.01,
        "output": 0.03
    },
    "gpt-4-turbo": {
        "input": 0.01,
        "output": 0.03
    },
    "gpt-4": {
        "input": 0.03,
        "output": 0.06
    },
    "gpt-3.5-turbo": {
        "input": 0.0015,
        "output": 0.002
    },
    "text-embedding-ada-002": {
        "input": 0.0001,
        "output": 0.0001
    },
    "azure-gpt-4": {  # Azure pricing may differ based on contract
        "input": 0.03,
        "output": 0.06
    },
    "azure-gpt-4o": {
        "input": 0.01,
        "output": 0.03
    },
    "azure-gpt-3.5-turbo": {
        "input": 0.0015,
        "output": 0.002
    },
    "azure-embedding": {
        "input": 0.0001,
        "output": 0.0001
    },
    "default": {  # Fallback pricing
        "input": 0.01,
        "output": 0.03
    }
}

# Global state for tracking operation in progress
current_operation = {
    "request_id": None,
    "user_id": None,
    "scenario_id": None,
    "operation_type": None,
    "start_time": None
}

class CostTrackingMiddleware:
    """
    Middleware for tracking the cost of API calls to LLM providers and compute resources
    """
    
    def __init__(self, db_session_getter: Callable = get_db):
        """
        Initialize the cost tracking middleware
        
        Args:
            db_session_getter (Callable, optional): Function to get a database session.
                Defaults to the standard get_db function.
        """
        self.db_session_getter = db_session_getter
        self.records = []  # Store cost records for batch processing
    
    def start_operation(self, operation_type: str, user_id: int, scenario_id: Optional[int] = None) -> str:
        """
        Start tracking an operation
        
        Args:
            operation_type (str): Type of operation (e.g., conversation, analysis)
            user_id (int): User ID
            scenario_id (int, optional): Scenario ID, if applicable
            
        Returns:
            str: Request ID for the operation
        """
        request_id = str(uuid.uuid4())
        current_operation["request_id"] = request_id
        current_operation["user_id"] = user_id
        current_operation["scenario_id"] = scenario_id
        current_operation["operation_type"] = operation_type
        current_operation["start_time"] = time.time()
        
        logger.info(f"Starting operation: {operation_type} with request ID: {request_id}")
        return request_id
    
    def end_operation(self) -> Dict[str, Any]:
        """
        End the current operation and return operation details
        
        Returns:
            Dict[str, Any]: Operation details including duration
        """
        if not current_operation["start_time"]:
            logger.warning("Attempted to end operation, but no operation was started")
            return {}
        
        duration_ms = int((time.time() - current_operation["start_time"]) * 1000)
        operation_details = {
            "request_id": current_operation["request_id"],
            "user_id": current_operation["user_id"],
            "scenario_id": current_operation["scenario_id"],
            "operation_type": current_operation["operation_type"],
            "duration_ms": duration_ms
        }
        
        # Reset current operation
        current_operation.update({
            "request_id": None,
            "user_id": None,
            "scenario_id": None,
            "operation_type": None,
            "start_time": None
        })
        
        logger.info(f"Ended operation with duration: {duration_ms}ms")
        return operation_details
    
    def track_tokens(self, model: str, tokens_input: int, tokens_output: int, 
                     operation_details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Track token usage and calculate cost
        
        Args:
            model (str): LLM model used
            tokens_input (int): Number of input tokens
            tokens_output (int): Number of output tokens
            operation_details (Dict[str, Any], optional): Operation details.
                If None, current operation details will be used.
                
        Returns:
            Dict[str, Any]: Cost tracking details
        """
        # Use provided operation details or current operation
        if operation_details is None:
            if not current_operation["request_id"]:
                logger.warning("No active operation found when tracking tokens")
                # Create a minimal operation record
                operation_details = {
                    "request_id": str(uuid.uuid4()),
                    "user_id": 1,  # Default user ID
                    "operation_type": "unknown",
                    "duration_ms": 0
                }
            else:
                # Get current operation details
                duration_ms = int((time.time() - current_operation["start_time"]) * 1000) if current_operation["start_time"] else 0
                operation_details = {
                    "request_id": current_operation["request_id"],
                    "user_id": current_operation["user_id"],
                    "scenario_id": current_operation["scenario_id"],
                    "operation_type": current_operation["operation_type"],
                    "duration_ms": duration_ms
                }
        
        # Get pricing for the model
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["default"])
        
        # Calculate cost
        input_cost = (tokens_input / 1000) * pricing["input"]
        output_cost = (tokens_output / 1000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        # Create cost record
        cost_record = {
            "request_id": operation_details["request_id"],
            "user_id": operation_details["user_id"],
            "scenario_id": operation_details.get("scenario_id"),
            "model": model,
            "tokens_input": tokens_input,
            "tokens_output": tokens_output,
            "cost_usd": total_cost,
            "operation_type": operation_details.get("operation_type", "unknown"),
            "duration_ms": operation_details.get("duration_ms", 0),
            "created_at": datetime.utcnow()
        }
        
        logger.info(f"Tracked token usage: {tokens_input} input, {tokens_output} output tokens for model {model}. "
                    f"Cost: ${total_cost:.4f}")
        
        # Add to records for batch processing
        self.records.append(cost_record)
        
        # If we have accumulated enough records or this is a high-cost operation, save immediately
        if len(self.records) >= 10 or total_cost > 0.1:
            self.save_records()
        
        return cost_record
    
    def save_records(self) -> None:
        """Save accumulated cost records to the database"""
        if not self.records:
            return
        
        try:
            db = next(self.db_session_getter())
            
            # Create CostTracker objects and add to database
            for record in self.records:
                cost_tracker = CostTracker(
                    request_id=record["request_id"],
                    user_id=record["user_id"],
                    scenario_id=record["scenario_id"],
                    model=record["model"],
                    tokens_input=record["tokens_input"],
                    tokens_output=record["tokens_output"],
                    cost_usd=record["cost_usd"],
                    operation_type=record["operation_type"],
                    duration_ms=record["duration_ms"]
                )
                db.add(cost_tracker)
            
            # Update scenario costs if applicable
            scenario_costs = {}
            for record in self.records:
                if record["scenario_id"]:
                    scenario_id = record["scenario_id"]
                    if scenario_id not in scenario_costs:
                        scenario_costs[scenario_id] = 0
                    scenario_costs[scenario_id] += record["cost_usd"]
            
            # Update scenarios with accumulated costs
            for scenario_id, cost in scenario_costs.items():
                scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
                if scenario:
                    scenario.llm_cost = (scenario.llm_cost or 0) + cost
            
            db.commit()
            logger.info(f"Saved {len(self.records)} cost records to database")
            
            # Clear records after saving
            self.records = []
            
        except Exception as e:
            logger.error(f"Error saving cost records: {str(e)}")
    
    def __del__(self):
        """Destructor to ensure records are saved when the object is destroyed"""
        self.save_records()

# Decorator for tracking API calls
def track_api_cost(operation_type: str, model: str):
    """
    Decorator for tracking the cost of API calls
    
    Args:
        operation_type (str): Type of operation
        model (str): Model being used
        
    Returns:
        Callable: Decorated function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get user_id and scenario_id from kwargs or use defaults
            user_id = kwargs.get("user_id", 1)
            scenario_id = kwargs.get("scenario_id")
            
            # Initialize cost tracker
            cost_tracker = CostTrackingMiddleware()
            
            # Start operation
            request_id = cost_tracker.start_operation(operation_type, user_id, scenario_id)
            
            try:
                # Call the original function
                result = await func(*args, **kwargs)
                
                # Extract token usage from result if available
                token_usage = {}
                if isinstance(result, dict) and "usage" in result:
                    token_usage = result["usage"]
                elif hasattr(result, "usage") and result.usage:
                    token_usage = result.usage
                
                # Default token counts if not available
                tokens_input = token_usage.get("prompt_tokens", 0)
                tokens_output = token_usage.get("completion_tokens", 0)
                
                # End operation and get details
                operation_details = cost_tracker.end_operation()
                
                # Track tokens
                cost_tracker.track_tokens(model, tokens_input, tokens_output, operation_details)
                
                return result
            except Exception as e:
                # End operation even if an error occurred
                operation_details = cost_tracker.end_operation()
                
                # Track minimal usage for failed operations
                cost_tracker.track_tokens(model, 10, 0, operation_details)
                
                # Re-raise the exception
                raise e
        
        return wrapper
    
    return decorator

# Global singleton instance
cost_tracking_middleware = CostTrackingMiddleware()