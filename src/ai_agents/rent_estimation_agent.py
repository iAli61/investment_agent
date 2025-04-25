"""
Rent Estimation Agent for predicting rental income
"""
import logging
import random
import asyncio
import datetime
import os
import json
from typing import Dict, Any, List, Optional, Tuple
import uuid

# LangChain imports
from langchain.agents import AgentExecutor
from langchain.schema import AgentAction, AgentFinish
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

# Local imports
from .base_agent import BaseAgent, LangChainAgent
from .tools import create_real_estate_tools, RentEstimationTool

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RentEstimationAgent(BaseAgent):
    """
    Agent responsible for estimating potential rental income for properties
    
    Implementation of AI-002: Rent Estimation Agent
    """
    
    def __init__(self):
        """Initialize the rent estimation agent"""
        super().__init__()
        # Initialize feature value multipliers
        self.feature_multipliers = {
            "balcony": 1.05,
            "garden": 1.08,
            "terrace": 1.06,
            "parking": 1.04,
            "elevator": 1.03,
            "furnished": 1.10,
            "modern_kitchen": 1.05,
            "floor_heating": 1.04
        }
        
        # Initialize condition multipliers
        self.condition_multipliers = {
            "excellent": 1.15,
            "good": 1.05,
            "average": 1.0,
            "fair": 0.9,
            "poor": 0.8
        }
        
        # Initialize location adjustments
        self.location_categories = {
            "central": 1.2,
            "urban": 1.0,
            "suburban": 0.9,
            "rural": 0.8
        }
    
    def _get_agent_name(self) -> str:
        """Get the name of the agent"""
        return "rent_estimation_agent"
    
    def _get_agent_description(self) -> str:
        """Get the description of the agent"""
        return "Agent responsible for estimating potential rental income for properties"
    
    async def _execute_logic(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate rent based on property characteristics and market data
        
        Args:
            parameters: Dictionary containing:
                - location: str - The location of the property
                - property_type: str - The type of property
                - size_sqm: float - Size in square meters
                - num_bedrooms: Optional[int] - Number of bedrooms
                - num_bathrooms: Optional[float] - Number of bathrooms
                - features: Optional[List[str]] - Property features/amenities
                - condition: Optional[str] - Property condition
            context: Shared context from the orchestrator, may contain market data
            
        Returns:
            Dictionary containing rent estimation results
        """
        # Validate the input parameters
        validation_result = await self.validate_input(parameters)
        if not validation_result:
            logger.error("Invalid input parameters for rent estimation")
            return {"error": "Invalid input parameters", "success": False}
        
        try:
            # Get parameters
            location = parameters.get("location", "")
            property_type = parameters.get("property_type", "")
            size_sqm = parameters.get("size_sqm", 0)
            num_bedrooms = parameters.get("num_bedrooms")
            num_bathrooms = parameters.get("num_bathrooms")
            features = parameters.get("features", [])
            condition = parameters.get("condition", "average")
            
            # For this demo, we'll simulate the process with realistic mock data
            await asyncio.sleep(1.5)  # Simulate processing delay
            
            # Use market data from context if available, otherwise use default values
            market_data = context.get("market_data", {})
            if not market_data:
                # Default values if market data not available
                base_rent_sqm = self._get_default_rent_sqm(location, property_type)
                logger.info(f"Using default rent values: {base_rent_sqm}/sqm")
            else:
                base_rent_sqm = market_data.get("avg_rent_sqm", self._get_default_rent_sqm(location, property_type))
                logger.info(f"Using market data rent value: {base_rent_sqm}/sqm")
            
            # Get base rent
            base_rent = size_sqm * base_rent_sqm
            
            # Apply adjustments
            adjusted_rent = self._apply_adjustments(
                base_rent, 
                size_sqm, 
                num_bedrooms, 
                num_bathrooms, 
                features, 
                condition, 
                location
            )
            
            # Calculate confidence level
            confidence_level = self.get_confidence_level({
                "has_market_data": bool(market_data),
                "property_details_completeness": self._calculate_details_completeness(parameters),
                "location_specificity": 0.9,  # Simulated value
                "property_type_match": True  # Simulated value
            })
            
            # Calculate rent range (for uncertainty)
            rent_range = self._calculate_rent_range(adjusted_rent, confidence_level)
            
            # Check if estimate exceeds legal limits (in regulated markets like Berlin)
            legal_limit_warning, legal_limit = self._check_legal_limits(
                adjusted_rent, location, size_sqm, property_type, condition
            )
            
            # Generate comparable properties
            comparable_properties = self._generate_comparable_properties(
                location, property_type, size_sqm, adjusted_rent, 
                num_bedrooms, features
            )
            
            return {
                "success": True,
                "estimated_rent": round(adjusted_rent, 2),
                "rent_per_sqm": round(adjusted_rent / size_sqm, 2),
                "rent_range": rent_range,
                "comparable_properties": comparable_properties,
                "confidence_level": confidence_level,
                "legal_limit_warning": legal_limit_warning,
                "legal_limit": legal_limit,
                "explanation": self._generate_explanation(
                    base_rent, adjusted_rent, features, condition, location, 
                    num_bedrooms, size_sqm, legal_limit_warning
                ),
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in rent estimation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def _get_default_rent_sqm(self, location: str, property_type: str) -> float:
        """
        Get default rent per square meter when market data is not available
        
        Args:
            location: Property location
            property_type: Type of property
            
        Returns:
            Default rent per square meter
        """
        # Default base values per property type (EUR/sqm)
        base_values = {
            "apartment": 14.0,
            "house": 12.0,
            "multi-family": 11.5,
            "commercial": 20.0
        }
        
        # Adjustments based on location (simplified)
        location_lower = location.lower()
        location_factor = 1.0
        
        if "berlin" in location_lower:
            location_factor = 1.0
        elif "munich" in location_lower:
            location_factor = 1.5
        elif "hamburg" in location_lower:
            location_factor = 1.1
        elif "frankfurt" in location_lower:
            location_factor = 1.2
        elif "cologne" in location_lower:
            location_factor = 0.9
        
        # Apply some variance to make it realistic
        variance = random.uniform(0.95, 1.05)
        
        return base_values.get(property_type, base_values["apartment"]) * location_factor * variance
    
    def _apply_adjustments(self, base_rent: float, size_sqm: float, 
                          num_bedrooms: Optional[int], num_bathrooms: Optional[float],
                          features: List[str], condition: str, 
                          location: str) -> float:
        """
        Apply various adjustments to the base rent
        
        Args:
            base_rent: Base rent calculated from size and market rate
            size_sqm: Size in square meters
            num_bedrooms: Number of bedrooms
            num_bathrooms: Number of bathrooms
            features: List of property features
            condition: Property condition
            location: Property location
            
        Returns:
            Adjusted rent
        """
        adjusted_rent = base_rent
        
        # Size adjustment (economies of scale)
        if size_sqm < 40:
            adjusted_rent *= 1.05  # Small apartments command premium per sqm
        elif size_sqm > 120:
            adjusted_rent *= 0.95  # Large units typically get discount per sqm
        
        # Bedroom adjustment
        if num_bedrooms is not None:
            if num_bedrooms == 0:  # Studio
                adjusted_rent *= 0.95
            elif num_bedrooms >= 3:  # Family-sized
                adjusted_rent *= 1.02
        
        # Bathroom adjustment
        if num_bathrooms is not None:
            if num_bathrooms >= 2:
                adjusted_rent *= 1.03
        
        # Feature adjustments
        feature_multiplier = 1.0
        for feature in features:
            feature_multiplier *= self.feature_multipliers.get(feature, 1.0)
        
        adjusted_rent *= feature_multiplier
        
        # Condition adjustment
        condition_multiplier = self.condition_multipliers.get(condition, 1.0)
        adjusted_rent *= condition_multiplier
        
        # Location category adjustment (simplified)
        location_category = "urban"  # Default
        location_lower = location.lower()
        
        if any(term in location_lower for term in ["center", "mitte", "downtown", "central"]):
            location_category = "central"
        elif any(term in location_lower for term in ["outside", "suburb", "outskirts"]):
            location_category = "suburban"
        elif any(term in location_lower for term in ["rural", "countryside", "village"]):
            location_category = "rural"
        
        location_multiplier = self.location_categories.get(location_category, 1.0)
        adjusted_rent *= location_multiplier
        
        return adjusted_rent
    
    def _calculate_details_completeness(self, parameters: Dict[str, Any]) -> float:
        """
        Calculate completeness of property details provided
        
        Args:
            parameters: Property parameters
            
        Returns:
            Completeness score between 0.0 and 1.0
        """
        # List of parameters that contribute to completeness
        detail_params = ["size_sqm", "num_bedrooms", "num_bathrooms", "features", "condition"]
        
        # Count how many are provided
        provided = sum(1 for param in detail_params if parameters.get(param) is not None)
        
        # Calculate completeness score
        completeness = provided / len(detail_params)
        
        # Features deserve more weight if provided
        if parameters.get("features") and len(parameters.get("features", [])) > 2:
            completeness = min(1.0, completeness + 0.1)
        
        return completeness
    
    def _calculate_rent_range(self, estimated_rent: float, confidence: float) -> Dict[str, float]:
        """
        Calculate a range of possible rent values based on confidence level
        
        Args:
            estimated_rent: The estimated rent
            confidence: Confidence level (0.0-1.0)
            
        Returns:
            Dictionary with low, medium, and high rent estimates
        """
        # Inverse of confidence gives us uncertainty
        uncertainty = 1.0 - confidence
        
        # Higher uncertainty means wider range
        variance_factor = 0.05 + (uncertainty * 0.15)
        
        low_estimate = estimated_rent * (1.0 - variance_factor)
        high_estimate = estimated_rent * (1.0 + variance_factor)
        
        return {
            "low": round(low_estimate, 2),
            "medium": round(estimated_rent, 2),
            "high": round(high_estimate, 2)
        }
    
    def _check_legal_limits(self, estimated_rent: float, location: str, size_sqm: float,
                           property_type: str, condition: str) -> Tuple[bool, float]:
        """
        Check if estimated rent exceeds legal limits in regulated markets
        
        Args:
            estimated_rent: Estimated monthly rent
            location: Property location
            size_sqm: Size in square meters
            property_type: Type of property
            condition: Property condition
            
        Returns:
            Tuple of (warning_flag, legal_limit)
        """
        # Check if in a rent-controlled area
        location_lower = location.lower()
        rent_controlled = any(city in location_lower for city in ["berlin", "frankfurt"])
        
        if not rent_controlled:
            return False, 0.0
        
        # Simplified rent cap calculation (Berlin's Mietpreisbremse as example)
        # In reality, this would be a complex calculation based on the local rent index
        base_limit_sqm = 13.0  # EUR/sqm baseline for regulated cities
        
        # Adjustments based on property type and condition
        if condition == "excellent":
            base_limit_sqm *= 1.1
        elif condition == "poor":
            base_limit_sqm *= 0.9
            
        if property_type == "apartment":
            base_limit_sqm *= 1.0
        elif property_type == "house":
            base_limit_sqm *= 1.1
        
        # Calculate legal limit
        legal_limit = base_limit_sqm * size_sqm
        
        # Check if estimated rent exceeds legal limit
        exceeds_limit = estimated_rent > legal_limit
        
        return exceeds_limit, round(legal_limit, 2)
    
    def _generate_comparable_properties(self, location: str, property_type: str, size_sqm: float,
                                       estimated_rent: float, bedrooms: Optional[int],
                                       features: List[str]) -> List[Dict[str, Any]]:
        """
        Generate comparable properties to support the rent estimate
        
        Args:
            location: Property location
            property_type: Type of property
            size_sqm: Size in square meters
            estimated_rent: Estimated monthly rent
            bedrooms: Number of bedrooms
            features: Property features
            
        Returns:
            List of comparable properties
        """
        comparable_properties = []
        
        # Generate 3-5 comparable properties
        for i in range(random.randint(3, 5)):
            # Create similar but slightly different properties
            size_variance = random.uniform(0.85, 1.15)
            comp_size = round(size_sqm * size_variance, 1)
            
            rent_variance = random.uniform(0.9, 1.1)
            comp_rent = round(estimated_rent * rent_variance, 2)
            
            # Adjust bedrooms based on size
            comp_bedrooms = bedrooms
            if bedrooms is None:
                if comp_size < 50:
                    comp_bedrooms = 1
                elif comp_size < 80:
                    comp_bedrooms = 2
                else:
                    comp_bedrooms = 3
            
            # Random subset of features
            if features:
                comp_features = random.sample(features, k=min(len(features), random.randint(0, len(features))))
            else:
                comp_features = random.sample(list(self.feature_multipliers.keys()), k=random.randint(0, 3))
            
            # Distance from target property (fictional)
            distance_km = round(random.uniform(0.2, 3.0), 1)
            
            # Compile comparable property
            comparable = {
                "id": f"comp-{uuid.uuid4().hex[:8]}",
                "address": f"{random.choice(['Hauptstrasse', 'Bergstrasse', 'Marktplatz', 'Schillerstrasse'])} {random.randint(1, 120)}, {location}",
                "size_sqm": comp_size,
                "bedrooms": comp_bedrooms,
                "rent": comp_rent,
                "rent_per_sqm": round(comp_rent / comp_size, 2),
                "features": comp_features,
                "distance_km": distance_km
            }
            
            comparable_properties.append(comparable)
        
        # Sort by distance
        comparable_properties.sort(key=lambda x: x["distance_km"])
        
        return comparable_properties
    
    def _generate_explanation(self, base_rent: float, adjusted_rent: float, features: List[str],
                             condition: str, location: str, bedrooms: Optional[int],
                             size_sqm: float, legal_warning: bool) -> str:
        """
        Generate a human-readable explanation of the rent estimate
        
        Args:
            base_rent: Initial base rent
            adjusted_rent: Final adjusted rent
            features: Property features
            condition: Property condition
            location: Property location
            bedrooms: Number of bedrooms
            size_sqm: Size in square meters
            legal_warning: Whether there's a legal limit warning
            
        Returns:
            Human-readable explanation
        """
        explanation = f"Based on a {size_sqm} sqm property in {location}, "
        
        if bedrooms is not None:
            bedroom_desc = "studio" if bedrooms == 0 else f"{bedrooms} bedroom"
            explanation += f"with {bedroom_desc}, "
        
        explanation += f"the estimated rent is €{adjusted_rent:.2f} per month.\n\n"
        
        # Explain key factors
        explanation += "Key factors affecting this estimate:\n"
        
        # Location factor
        location_categories = []
        location_lower = location.lower()
        
        if any(term in location_lower for term in ["center", "mitte", "downtown", "central"]):
            location_categories.append("central location (premium)")
        elif any(term in location_lower for term in ["outside", "suburb", "outskirts"]):
            location_categories.append("suburban location")
        elif any(term in location_lower for term in ["rural", "countryside", "village"]):
            location_categories.append("rural location")
        else:
            location_categories.append("urban location")
        
        explanation += f"- Location: {location} ({', '.join(location_categories)})\n"
        
        # Size factor
        size_factor = ""
        if size_sqm < 40:
            size_factor = "small apartments typically command a premium per sqm"
        elif size_sqm > 120:
            size_factor = "larger units typically rent for less per sqm"
        else:
            size_factor = "standard size with typical pricing"
        
        explanation += f"- Size: {size_sqm} sqm ({size_factor})\n"
        
        # Condition factor
        explanation += f"- Condition: {condition} (affects rental value significantly)\n"
        
        # Features
        if features:
            explanation += f"- Notable features: {', '.join(features)}\n"
        
        # Legal information
        if legal_warning:
            explanation += "\nNote: The estimated rent exceeds typical legal limits in this regulated market. "
            explanation += "Consider checking local rent control regulations before finalizing.\n"
        
        # Market trends
        explanation += "\nMarket trends in this area show "
        explanation += random.choice([
            "strong demand for rental properties, suggesting stable or increasing rental values.",
            "moderate demand with relatively stable rental prices.",
            "high competition among landlords, which may put downward pressure on achievable rents.",
            "limited supply of comparable properties, which may support higher rental values."
        ])
        
        return explanation
    
    async def validate_input(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate the input parameters
        
        Args:
            parameters: Dictionary of parameters to validate
            
        Returns:
            True if parameters are valid, False otherwise
        """
        required_params = ["location", "property_type", "size_sqm"]
        for param in required_params:
            if param not in parameters:
                logger.error(f"Missing required parameter: {param}")
                return False
        
        valid_property_types = ["apartment", "house", "multi-family", "commercial"]
        if parameters.get("property_type") not in valid_property_types:
            logger.error(f"Invalid property type: {parameters.get('property_type')}")
            return False
        
        if parameters.get("size_sqm", 0) <= 0:
            logger.error(f"Invalid size_sqm: {parameters.get('size_sqm')}")
            return False
        
        valid_conditions = ["excellent", "good", "average", "fair", "poor"]
        if "condition" in parameters and parameters["condition"] not in valid_conditions:
            logger.error(f"Invalid condition: {parameters.get('condition')}")
            return False
        
        return True
    
    def get_confidence_level(self, data: Dict[str, Any]) -> float:
        """
        Calculate confidence level for the rent estimation
        
        Args:
            data: Dictionary with factors affecting confidence:
                - has_market_data: Whether market data was available
                - property_details_completeness: Completeness of property details (0.0-1.0)
                - location_specificity: How specific the location match was (0.0-1.0)
                - property_type_match: Whether the property type exactly matched the request
            
        Returns:
            Confidence level as a float between 0.0 and 1.0
        """
        # Base confidence level
        confidence = 0.5
        
        # Adjust based on market data availability
        if data.get("has_market_data", False):
            confidence += 0.2
        else:
            confidence -= 0.1
        
        # Adjust based on property details completeness
        completeness = data.get("property_details_completeness", 0)
        confidence += completeness * 0.2
        
        # Adjust based on location specificity
        location_specificity = data.get("location_specificity", 0)
        confidence += location_specificity * 0.1
        
        # Adjust based on property type match
        if data.get("property_type_match", False):
            confidence += 0.1
        else:
            confidence -= 0.1
        
        # Ensure confidence is between 0.0 and 1.0
        return max(0.0, min(1.0, confidence))


class LangChainRentEstimationAgent(LangChainAgent):
    """
    LangChain implementation of the rent estimation agent
    
    This agent leverages LangChain's agent framework to estimate rental income
    for properties using a combination of tools and LLM reasoning.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LangChain rent estimation agent
        
        Args:
            api_key: OpenAI API key for the LLM. If not provided, will look for OPENAI_API_KEY env variable
        """
        # Set up OpenAI API key
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required either as parameter or OPENAI_API_KEY environment variable")
        
        # Create LLM
        llm = ChatOpenAI(
            temperature=0.2,
            model_name="gpt-3.5-turbo",
            api_key=self.api_key
        )
        
        # Create tools - we only need the rent estimation tool for this agent
        tools = [RentEstimationTool()]
        
        # Define the prompt template
        prompt_template = """
        You are a real estate rent estimation expert. Your job is to estimate the potential rental 
        income for various properties and provide detailed analysis to help investors make informed 
        decisions. You have access to the following tools:
        
        {tools}
        
        Use these tools to provide accurate rent estimations with comprehensive explanations.
        
        User Query: {input}
        
        Think step by step about how to approach this rent estimation:
        1. What are the key property characteristics that will affect the rent?
        2. Are there any special features or location factors to consider?
        3. Are there any local regulations (like rent control) that might be relevant?
        
        Previous steps: {intermediate_steps}
        
        Based on the information so far, what tool should you use next and why?
        
        Tool:
        """
        
        # Initialize LangChain Agent
        super().__init__(
            llm=llm,
            tools=tools,
            prompt_template=prompt_template,
            input_variables=["input", "intermediate_steps", "tools"]
        )
    
    def _get_agent_name(self) -> str:
        """Get the name of the agent"""
        return "langchain_rent_estimation_agent"
    
    def _get_agent_description(self) -> str:
        """Get the description of the agent"""
        return "LangChain agent for estimating rental income for properties"
    
    async def _execute_logic(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's core logic
        
        Args:
            parameters: Parameters specific to this agent execution
            context: Shared context from the orchestrator
            
        Returns:
            Dictionary with execution results
        """
        # Format the input query for the agent
        location = parameters.get("location", "")
        property_type = parameters.get("property_type", "")
        size_sqm = parameters.get("size_sqm", 0)
        
        # Build a natural language query from the parameters
        query = f"Estimate the monthly rent for a {size_sqm} sqm {property_type} in {location}. "
        
        # Add optional parameters if available
        if "num_bedrooms" in parameters and parameters["num_bedrooms"] is not None:
            query += f"It has {parameters['num_bedrooms']} bedrooms. "
            
        if "num_bathrooms" in parameters and parameters["num_bathrooms"] is not None:
            query += f"It has {parameters['num_bathrooms']} bathrooms. "
            
        if "features" in parameters and parameters["features"]:
            query += f"Features include: {', '.join(parameters['features'])}. "
            
        if "condition" in parameters and parameters["condition"]:
            query += f"The property is in {parameters['condition']} condition. "
        
        # Create an agent executor
        agent_executor = self.create_agent_executor(
            max_iterations=5,  # Rent estimation shouldn't need many iterations
            early_stopping_method="generate",
        )
        
        # Run the agent
        try:
            result = await agent_executor.arun(input=query)
            
            # Extract numerical rent estimate from result if possible
            import re
            rent_numbers = re.findall(r'€?(\d+[,\d]*(?:\.\d+)?)', result)
            estimated_rent = None
            if rent_numbers:
                try:
                    # Try to extract the main rent figure
                    estimated_rent = float(rent_numbers[0].replace(',', ''))
                except (ValueError, IndexError):
                    pass
            
            return {
                "success": True,
                "query": query,
                "analysis": result,
                "estimated_rent": estimated_rent,
                "location": location,
                "property_type": property_type,
                "size_sqm": size_sqm,
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error executing LangChain agent: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "location": location,
                "property_type": property_type,
                "size_sqm": size_sqm
            }


# Factory function to create the appropriate rent estimation agent
def create_rent_estimation_agent(use_langchain: bool = True, api_key: Optional[str] = None) -> BaseAgent:
    """
    Create a rent estimation agent
    
    Args:
        use_langchain: Whether to use the LangChain implementation
        api_key: OpenAI API key if using LangChain
        
    Returns:
        A rent estimation agent
    """
    if use_langchain:
        try:
            return LangChainRentEstimationAgent(api_key=api_key)
        except Exception as e:
            logger.error(f"Failed to create LangChain rent estimation agent: {str(e)}")
            logger.info("Falling back to basic rent estimation agent")
            return RentEstimationAgent()
    else:
        return RentEstimationAgent()