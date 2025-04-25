"""
Tools for the AI agents to use with LangChain
"""
import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, Tool

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealEstateSearchInput(BaseModel):
    """Inputs for real estate search tool"""
    location: str = Field(..., description="The location to search for properties (city, district, etc.)")
    property_type: str = Field(..., description="The type of property (apartment, house, multi-family, commercial)")
    min_size: Optional[int] = Field(None, description="Minimum property size in square meters")
    max_size: Optional[int] = Field(None, description="Maximum property size in square meters")
    min_price: Optional[int] = Field(None, description="Minimum property price")
    max_price: Optional[int] = Field(None, description="Maximum property price")


class RealEstateSearchTool(BaseTool):
    """Tool for searching real estate listings"""
    name = "real_estate_search"
    description = "Searches for real estate listings based on location, property type, and other criteria"
    args_schema = RealEstateSearchInput
    
    def __init__(self):
        super().__init__()
        self.func = self._run
    
    def _run(self, location: str, property_type: str, min_size: Optional[int] = None, 
             max_size: Optional[int] = None, min_price: Optional[int] = None, 
             max_price: Optional[int] = None) -> Dict[str, Any]:
        """Run the real estate search tool"""
        logger.info(f"Searching for {property_type} in {location}")
        
        # In a real implementation, this would make API calls to real estate sites
        # or use web scraping to gather real estate listings
        
        # For this demo, we'll return mock data based on the input parameters
        listings = self._generate_mock_listings(
            location, 
            property_type, 
            min_size, 
            max_size, 
            min_price, 
            max_price
        )
        
        return {
            "success": True,
            "count": len(listings),
            "location": location,
            "property_type": property_type,
            "listings": listings,
            "source": "Mock real estate data source"
        }
    
    def _generate_mock_listings(self, location: str, property_type: str, 
                               min_size: Optional[int], max_size: Optional[int],
                               min_price: Optional[int], max_price: Optional[int]) -> List[Dict[str, Any]]:
        """Generate mock listings based on input parameters"""
        # Base property data by type and location
        base_data = {
            "apartment": {
                "berlin": {"base_price": 350000, "price_per_sqm": 5000, "base_size": 70},
                "munich": {"base_price": 550000, "price_per_sqm": 9000, "base_size": 65},
                "hamburg": {"base_price": 400000, "price_per_sqm": 5500, "base_size": 75},
                "default": {"base_price": 300000, "price_per_sqm": 4000, "base_size": 70}
            },
            "house": {
                "berlin": {"base_price": 650000, "price_per_sqm": 4000, "base_size": 150},
                "munich": {"base_price": 950000, "price_per_sqm": 8000, "base_size": 130},
                "hamburg": {"base_price": 750000, "price_per_sqm": 4500, "base_size": 160},
                "default": {"base_price": 550000, "price_per_sqm": 3500, "base_size": 150}
            },
            "multi-family": {
                "berlin": {"base_price": 1500000, "price_per_sqm": 3800, "base_size": 350},
                "munich": {"base_price": 2500000, "price_per_sqm": 7500, "base_size": 330},
                "hamburg": {"base_price": 1800000, "price_per_sqm": 4200, "base_size": 380},
                "default": {"base_price": 1300000, "price_per_sqm": 3500, "base_size": 350}
            },
            "commercial": {
                "berlin": {"base_price": 1800000, "price_per_sqm": 3500, "base_size": 500},
                "munich": {"base_price": 3000000, "price_per_sqm": 7000, "base_size": 450},
                "hamburg": {"base_price": 2200000, "price_per_sqm": 4000, "base_size": 550},
                "default": {"base_price": 1500000, "price_per_sqm": 3000, "base_size": 500}
            },
            "default": {
                "default": {"base_price": 300000, "price_per_sqm": 4000, "base_size": 70}
            }
        }
        
        # Get base data for the requested property type and location
        city = location.lower().split()[0]
        
        type_data = base_data.get(property_type.lower(), base_data["default"])
        location_data = type_data.get(city, type_data.get("default"))
        
        # Generate 5-10 mock listings
        listings = []
        import random
        num_listings = random.randint(5, 10)
        
        for i in range(num_listings):
            # Generate size with some variation
            size = location_data["base_size"] * random.uniform(0.8, 1.2)
            if min_size is not None and size < min_size:
                size = min_size * random.uniform(1.0, 1.1)
            if max_size is not None and size > max_size:
                size = max_size * random.uniform(0.9, 1.0)
            
            # Generate price based on size and price per sqm
            price = location_data["base_price"] * random.uniform(0.9, 1.1) + (size * location_data["price_per_sqm"] * random.uniform(0.8, 1.2))
            if min_price is not None and price < min_price:
                price = min_price * random.uniform(1.0, 1.1)
            if max_price is not None and price > max_price:
                price = max_price * random.uniform(0.9, 1.0)
            
            # Create listing
            listing = {
                "id": f"listing-{random.randint(10000, 99999)}",
                "title": f"{int(size)} sqm {property_type} in {location}",
                "location": location,
                "property_type": property_type,
                "size_sqm": int(size),
                "price": int(price),
                "price_per_sqm": int(price / size),
                "bedrooms": random.randint(1, 5),
                "bathrooms": random.choice([1, 1.5, 2, 2.5, 3]),
                "year_built": random.randint(1950, 2023),
                "features": random.sample(["balcony", "garden", "parking", "elevator", "fitted kitchen", "terrace"], 
                                          k=random.randint(1, 5)),
                "listing_url": f"https://example-realestate.com/listings/{random.randint(10000, 99999)}"
            }
            
            listings.append(listing)
        
        return listings
    
    async def _arun(self, location: str, property_type: str, min_size: Optional[int] = None, 
                  max_size: Optional[int] = None, min_price: Optional[int] = None, 
                  max_price: Optional[int] = None) -> Dict[str, Any]:
        """Async implementation of the real estate search tool"""
        # Simply call the sync version for now
        return self._run(location, property_type, min_size, max_size, min_price, max_price)


class RentEstimationInput(BaseModel):
    """Inputs for rent estimation tool"""
    location: str = Field(..., description="The location of the property (city, district, etc.)")
    property_type: str = Field(..., description="The type of property (apartment, house, etc.)")
    size_sqm: int = Field(..., description="Size of the property in square meters")
    bedrooms: Optional[int] = Field(None, description="Number of bedrooms")
    bathrooms: Optional[float] = Field(None, description="Number of bathrooms")
    features: Optional[List[str]] = Field(None, description="List of property features")


class RentEstimationTool(BaseTool):
    """Tool for estimating rental prices for properties"""
    name = "rent_estimation"
    description = "Estimates the potential rental income for properties based on location, size, and features"
    args_schema = RentEstimationInput
    
    def __init__(self):
        super().__init__()
        self.func = self._run
    
    def _run(self, location: str, property_type: str, size_sqm: int, 
             bedrooms: Optional[int] = None, bathrooms: Optional[float] = None, 
             features: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run the rent estimation tool"""
        logger.info(f"Estimating rent for {size_sqm} sqm {property_type} in {location}")
        
        # In a real implementation, this would use a trained ML model 
        # or an API call to a rent estimation service
        
        # For this demo, we'll calculate mock data based on the input parameters
        rent_data = self._calculate_rent_estimate(
            location, 
            property_type, 
            size_sqm, 
            bedrooms, 
            bathrooms, 
            features
        )
        
        return {
            "success": True,
            "location": location,
            "property_type": property_type,
            "size_sqm": size_sqm,
            "estimates": rent_data,
            "source": "Mock rent estimation model"
        }
    
    def _calculate_rent_estimate(self, location: str, property_type: str, size_sqm: int, 
                               bedrooms: Optional[int], bathrooms: Optional[float], 
                               features: Optional[List[str]]) -> Dict[str, Any]:
        """Calculate rent estimates based on input parameters"""
        # Base rent per sqm by location and property type
        base_rents = {
            "apartment": {
                "berlin": 15.0,
                "munich": 20.0,
                "hamburg": 14.5,
                "frankfurt": 16.0,
                "cologne": 13.0,
                "default": 12.0
            },
            "house": {
                "berlin": 12.0,
                "munich": 17.0,
                "hamburg": 13.0,
                "frankfurt": 14.0,
                "cologne": 12.0,
                "default": 10.0
            },
            "multi-family": {
                "berlin": 12.0,
                "munich": 16.0,
                "hamburg": 13.0,
                "frankfurt": 13.5,
                "cologne": 11.5,
                "default": 9.5
            },
            "commercial": {
                "berlin": 20.0,
                "munich": 26.0,
                "hamburg": 21.0,
                "frankfurt": 24.0,
                "cologne": 19.0,
                "default": 18.0
            },
            "default": {
                "default": 12.0
            }
        }
        
        # Get base rent for the requested property type and location
        city = location.lower().split()[0]
        
        type_data = base_rents.get(property_type.lower(), base_rents["default"])
        base_rent_sqm = type_data.get(city, type_data.get("default"))
        
        # Adjust base rent based on property features
        rent_adjustments = 0.0
        feature_adjustments = {
            "balcony": 0.05,
            "garden": 0.08,
            "parking": 0.03,
            "elevator": 0.04,
            "fitted kitchen": 0.06,
            "terrace": 0.07,
            "new building": 0.1,
            "renovated": 0.05,
            "furnished": 0.15
        }
        
        if features:
            for feature in features:
                if feature.lower() in feature_adjustments:
                    rent_adjustments += feature_adjustments[feature.lower()]
        
        # Apply adjustments to base rent
        adjusted_rent_sqm = base_rent_sqm * (1 + rent_adjustments)
        
        # Calculate monthly rent
        base_monthly_rent = size_sqm * adjusted_rent_sqm
        
        # Add some variance for different estimate types
        import random
        
        low_estimate = base_monthly_rent * random.uniform(0.85, 0.95)
        mid_estimate = base_monthly_rent
        high_estimate = base_monthly_rent * random.uniform(1.05, 1.15)
        
        # Build the estimation result
        rent_data = {
            "low_estimate": {
                "monthly_rent": round(low_estimate, 2),
                "rent_per_sqm": round(low_estimate / size_sqm, 2),
                "confidence": "medium"
            },
            "mid_estimate": {
                "monthly_rent": round(mid_estimate, 2),
                "rent_per_sqm": round(mid_estimate / size_sqm, 2),
                "confidence": "high"
            },
            "high_estimate": {
                "monthly_rent": round(high_estimate, 2),
                "rent_per_sqm": round(high_estimate / size_sqm, 2),
                "confidence": "medium"
            }
        }
        
        # Check for potential regulation limits (Mietpreisbremse)
        mietpreisbremse_cities = ["berlin", "munich", "hamburg", "frankfurt", "cologne"]
        if city in mietpreisbremse_cities:
            rent_cap = base_rent_sqm * 1.1  # 10% above local average
            if adjusted_rent_sqm > rent_cap:
                rent_data["regulation_warning"] = {
                    "type": "Mietpreisbremse",
                    "max_allowed_rent_sqm": round(rent_cap, 2),
                    "description": "The estimated rent may exceed legal limits under local rent control regulations."
                }
        
        return rent_data
    
    async def _arun(self, location: str, property_type: str, size_sqm: int, 
                  bedrooms: Optional[int] = None, bathrooms: Optional[float] = None, 
                  features: Optional[List[str]] = None) -> Dict[str, Any]:
        """Async implementation of the rent estimation tool"""
        # Simply call the sync version for now
        return self._run(location, property_type, size_sqm, bedrooms, bathrooms, features)


class MarketTrendInput(BaseModel):
    """Inputs for market trend analysis tool"""
    location: str = Field(..., description="The location to analyze (city, district, etc.)")
    property_type: str = Field(..., description="The type of property (apartment, house, etc.)")
    time_period: str = Field("12 months", description="Time period for trend analysis (e.g., '6 months', '1 year', '5 years')")


class MarketTrendTool(BaseTool):
    """Tool for analyzing real estate market trends"""
    name = "market_trend_analysis"
    description = "Analyzes real estate market trends for a specific location and property type"
    args_schema = MarketTrendInput
    
    def __init__(self):
        super().__init__()
        self.func = self._run
    
    def _run(self, location: str, property_type: str, time_period: str = "12 months") -> Dict[str, Any]:
        """Run the market trend analysis tool"""
        logger.info(f"Analyzing market trends for {property_type} in {location} over {time_period}")
        
        # In a real implementation, this would analyze historical data 
        # from real estate sources
        
        # For this demo, we'll generate mock trend data
        trend_data = self._generate_trend_data(location, property_type, time_period)
        
        return {
            "success": True,
            "location": location,
            "property_type": property_type,
            "time_period": time_period,
            "trends": trend_data,
            "source": "Mock market trend analysis"
        }
    
    def _generate_trend_data(self, location: str, property_type: str, time_period: str) -> Dict[str, Any]:
        """Generate mock trend data based on input parameters"""
        # Pattern for different cities
        trend_patterns = {
            "berlin": {"price_trend": 0.03, "rent_trend": 0.025, "inventory_trend": -0.02, "transaction_trend": 0.01},
            "munich": {"price_trend": 0.045, "rent_trend": 0.035, "inventory_trend": -0.03, "transaction_trend": -0.01},
            "hamburg": {"price_trend": 0.025, "rent_trend": 0.02, "inventory_trend": -0.01, "transaction_trend": 0.02},
            "frankfurt": {"price_trend": 0.035, "rent_trend": 0.03, "inventory_trend": -0.02, "transaction_trend": 0.01},
            "cologne": {"price_trend": 0.025, "rent_trend": 0.02, "inventory_trend": -0.015, "transaction_trend": 0.015},
            "default": {"price_trend": 0.02, "rent_trend": 0.015, "inventory_trend": -0.01, "transaction_trend": 0.01}
        }
        
        city = location.lower().split()[0]
        base_trends = trend_patterns.get(city, trend_patterns["default"])
        
        # Adjust trends based on property type
        property_adjustments = {
            "apartment": {"price": 1.1, "rent": 1.1, "inventory": 1.0, "transaction": 1.2},
            "house": {"price": 1.05, "rent": 0.95, "inventory": 0.9, "transaction": 0.8},
            "multi-family": {"price": 1.15, "rent": 1.0, "inventory": 0.8, "transaction": 0.7},
            "commercial": {"price": 0.9, "rent": 0.85, "inventory": 1.1, "transaction": 0.6},
            "default": {"price": 1.0, "rent": 1.0, "inventory": 1.0, "transaction": 1.0}
        }
        
        adjustments = property_adjustments.get(property_type.lower(), property_adjustments["default"])
        
        # Apply time period factor
        time_factors = {
            "3 months": 0.25,
            "6 months": 0.5,
            "12 months": 1.0,
            "24 months": 1.8,
            "36 months": 2.5,
            "5 years": 3.0,
            "10 years": 4.0,
            "default": 1.0
        }
        
        time_factor = time_factors.get(time_period.lower(), time_factors["default"])
        
        # Calculate adjusted trends
        price_trend = base_trends["price_trend"] * adjustments["price"] * time_factor
        rent_trend = base_trends["rent_trend"] * adjustments["rent"] * time_factor
        inventory_trend = base_trends["inventory_trend"] * adjustments["inventory"] * time_factor
        transaction_trend = base_trends["transaction_trend"] * adjustments["transaction"] * time_factor
        
        # Add some randomness
        import random
        price_trend *= random.uniform(0.8, 1.2)
        rent_trend *= random.uniform(0.8, 1.2)
        inventory_trend *= random.uniform(0.8, 1.2)
        transaction_trend *= random.uniform(0.8, 1.2)
        
        # Generate trend data
        trend_data = {
            "price_trends": {
                "trend_percentage": round(price_trend * 100, 2),
                "direction": "increasing" if price_trend > 0 else "decreasing",
                "strength": self._get_trend_strength(abs(price_trend)),
                "description": f"Property prices have been {self._get_trend_strength(abs(price_trend))} {'increasing' if price_trend > 0 else 'decreasing'} by approximately {abs(round(price_trend * 100, 2))}% over the past {time_period}."
            },
            "rent_trends": {
                "trend_percentage": round(rent_trend * 100, 2),
                "direction": "increasing" if rent_trend > 0 else "decreasing",
                "strength": self._get_trend_strength(abs(rent_trend)),
                "description": f"Rental prices have been {self._get_trend_strength(abs(rent_trend))} {'increasing' if rent_trend > 0 else 'decreasing'} by approximately {abs(round(rent_trend * 100, 2))}% over the past {time_period}."
            },
            "inventory_trends": {
                "trend_percentage": round(inventory_trend * 100, 2),
                "direction": "increasing" if inventory_trend > 0 else "decreasing",
                "strength": self._get_trend_strength(abs(inventory_trend)),
                "description": f"Property inventory has been {self._get_trend_strength(abs(inventory_trend))} {'increasing' if inventory_trend > 0 else 'decreasing'} by approximately {abs(round(inventory_trend * 100, 2))}% over the past {time_period}."
            },
            "transaction_volume_trends": {
                "trend_percentage": round(transaction_trend * 100, 2),
                "direction": "increasing" if transaction_trend > 0 else "decreasing",
                "strength": self._get_trend_strength(abs(transaction_trend)),
                "description": f"Transaction volume has been {self._get_trend_strength(abs(transaction_trend))} {'increasing' if transaction_trend > 0 else 'decreasing'} by approximately {abs(round(transaction_trend * 100, 2))}% over the past {time_period}."
            }
        }
        
        # Add prediction for the next 12 months
        future_bias = random.uniform(0.7, 1.3)  # Add some randomness to future prediction
        
        trend_data["future_outlook"] = {
            "time_frame": "next 12 months",
            "price_prediction": {
                "direction": "increase" if price_trend > 0 else "decrease",
                "estimated_change": f"{abs(round(price_trend * future_bias * 100, 2))}%",
                "confidence": "medium"
            },
            "summary": f"Based on current trends, property prices in {location} for {property_type} properties are expected to {('increase by approximately ' if price_trend > 0 else 'decrease by approximately ')}{abs(round(price_trend * future_bias * 100, 2))}% over the next 12 months."
        }
        
        return trend_data
    
    def _get_trend_strength(self, trend_value: float) -> str:
        """Determine the linguistic strength of a trend based on its value"""
        if trend_value < 0.01:
            return "slightly"
        elif trend_value < 0.03:
            return "steadily"
        elif trend_value < 0.05:
            return "significantly"
        elif trend_value < 0.1:
            return "strongly"
        else:
            return "dramatically"
    
    async def _arun(self, location: str, property_type: str, time_period: str = "12 months") -> Dict[str, Any]:
        """Async implementation of the market trend analysis tool"""
        # Simply call the sync version for now
        return self._run(location, property_type, time_period)


def create_real_estate_tools() -> List[BaseTool]:
    """Create a list of tools for real estate market data analysis"""
    return [
        RealEstateSearchTool(),
        RentEstimationTool(),
        MarketTrendTool()
    ]