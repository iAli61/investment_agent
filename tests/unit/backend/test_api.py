import unittest
import os
import json
import asyncio
from unittest.mock import patch, MagicMock

# Import Pydantic models and other necessary components
from src.database.database import get_db, Base, engine, SessionLocal
from src.backend.api import read_root, create_property, get_properties, get_property
from src.backend.api import create_rental_unit, get_rental_units
from src.backend.api import create_financing, get_financing
from src.backend.api import get_market_data, get_task_result, estimate_rent
from src.backend.api import PropertyCreate, RentalUnitCreate, FinancingCreate
from src.backend.api import MarketDataRequest, RentEstimationRequest


# Simple test database setup for direct function testing
def setup_test_db():
    """Create test database and return a session factory"""
    # Create the test database and tables
    Base.metadata.create_all(bind=engine)
    
    # Create session factory
    def _get_test_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    return _get_test_db


class AsyncTestCase(unittest.TestCase):
    """Base class for async tests"""
    
    def run_async(self, coro):
        """Helper method to run coroutines in tests"""
        return asyncio.get_event_loop().run_until_complete(coro)


class DirectAPIFunctionTests(AsyncTestCase):
    """Test API functions directly, bypassing FastAPI middleware"""
    
    def setUp(self):
        self.test_db = setup_test_db()
        self.db = next(self.test_db())
    
    def tearDown(self):
        self.db.close()
    
    def test_read_root(self):
        """Test the root endpoint function directly"""
        result = read_root()
        self.assertEqual(result, {"message": "Welcome to the Property Investment Analysis API"})
    
    def test_property_functions(self):
        """Test property CRUD functions directly"""
        # Test create_property using Pydantic model
        property_data = PropertyCreate(
            address="123 Test Street",
            purchase_price=300000,
            property_type="apartment",
            year_built=2005,
            size_sqm=85,
            num_units=1,
            region="berlin",
            condition_assessment="good"  # Add required fields
        )
        
        # Create property and handle SQLAlchemy model
        created = self.run_async(create_property(property_data, self.db))
        self.assertEqual(created.address, "123 Test Street")
        self.assertEqual(created.purchase_price, 300000)
        property_id = created.id
        
        # Test get_property
        retrieved = self.run_async(get_property(property_id, self.db))
        self.assertEqual(retrieved.id, property_id)
        self.assertEqual(retrieved.address, "123 Test Street")
        
        # Test get_properties
        all_properties = self.run_async(get_properties(self.db))
        self.assertGreaterEqual(len(all_properties), 1)
        self.assertTrue(any(p.id == property_id for p in all_properties))
    
    def test_rental_unit_functions(self):
        """Test rental unit functions directly"""
        # First create a property
        property_data = PropertyCreate(
            address="456 Test Avenue",
            purchase_price=350000,
            property_type="multi-family",
            year_built=2000,
            size_sqm=150,
            num_units=2,
            region="berlin",
            condition_assessment="good"
        )
        
        property_result = self.run_async(create_property(property_data, self.db))
        property_id = property_result.id
        
        # Test creating a rental unit with Pydantic model
        unit_data = RentalUnitCreate(
            unit_number="1A",
            size_sqm=75,
            num_bedrooms=2,
            num_bathrooms=1,
            is_occupied=True,
            current_rent=1200
        )
        
        created_unit = self.run_async(create_rental_unit(property_id, unit_data, self.db))
        self.assertEqual(created_unit.unit_number, "1A")
        self.assertEqual(created_unit.current_rent, 1200)
        self.assertEqual(created_unit.property_id, property_id)
        
        # Test getting units
        units = self.run_async(get_rental_units(property_id, self.db))
        self.assertGreaterEqual(len(units), 1)
        self.assertEqual(units[0].unit_number, "1A")
    
    def test_financing_functions(self):
        """Test financing functions directly"""
        # First create a property
        property_data = PropertyCreate(
            address="789 Test Boulevard",
            purchase_price=400000,
            property_type="house",
            year_built=2010,
            size_sqm=120,
            num_units=1,
            region="berlin",
            condition_assessment="excellent"
        )
        
        property_result = self.run_async(create_property(property_data, self.db))
        property_id = property_result.id
        
        # Test creating financing with Pydantic model
        financing_data = FinancingCreate(
            loan_amount=300000,
            interest_rate=3.5,
            repayment_rate=2.0,
            term_years=30
        )
        
        created_financing = self.run_async(create_financing(property_id, financing_data, self.db))
        self.assertEqual(created_financing.loan_amount, 300000)
        self.assertEqual(created_financing.interest_rate, 3.5)
        self.assertEqual(created_financing.property_id, property_id)
        self.assertTrue(hasattr(created_financing, "monthly_payment"))
        
        # Test getting financing
        retrieved_financing = self.run_async(get_financing(property_id, self.db))
        self.assertEqual(retrieved_financing.loan_amount, 300000)


class MockedAITests(AsyncTestCase):
    """Test AI-related functions with mocks"""
    
    def setUp(self):
        self.test_db = setup_test_db()
        self.db = next(self.test_db())
    
    def tearDown(self):
        self.db.close()
    
    @patch("src.backend.api.orchestrator")
    @patch("src.backend.api.BackgroundTasks")
    def test_market_data_function(self, mock_bg_tasks, mock_orchestrator):
        """Test market data function directly with mock"""
        # Setup mocks
        mock_result = {
            "location": "Berlin",
            "property_type": "apartment",
            "avg_price_sqm": 5200,
            "avg_rent_sqm": 15.8,
            "confidence_level": 0.85
        }
        mock_orchestrator.add_task.return_value = "mock-task-id"
        
        # Create mock background tasks
        bg_tasks = MagicMock()
        mock_bg_tasks.return_value = bg_tasks
        
        # Create Pydantic request model
        request_data = MarketDataRequest(
            location="Berlin",
            property_type="apartment",
            additional_filters={}
        )
        
        # Test the function
        result = self.run_async(get_market_data(request_data, bg_tasks))
        self.assertIn("task_id", result)
        self.assertEqual(result["status"], "processing")
        
        # Test get_task_result
        mock_orchestrator.get_result.return_value = mock_result
        
        # Call get_task_result with just task_id as per signature 
        task_result = self.run_async(get_task_result("mock-task-id"))
        
        # Verify we call the orchestrator
        mock_orchestrator.get_result.assert_called_once()
    
    @patch("src.backend.api.orchestrator")
    @patch("src.backend.api.BackgroundTasks")
    def test_rent_estimation_function(self, mock_bg_tasks, mock_orchestrator):
        """Test rent estimation function directly with mock"""
        # Setup mocks
        mock_result = {
            "estimated_rent": 1350,
            "rent_range": {"min": 1250, "max": 1450},
            "confidence_level": 0.83
        }
        mock_orchestrator.add_task.return_value = "mock-task-id"
        
        # Create mock background tasks
        bg_tasks = MagicMock()
        mock_bg_tasks.return_value = bg_tasks
        
        # Create Pydantic request model
        request_data = RentEstimationRequest(
            location="Berlin Mitte",
            property_type="apartment",
            size_sqm=85,
            num_bedrooms=2,
            num_bathrooms=1,
            features=["balcony", "renovated"],
            condition="good"
        )
        
        # Test the function
        result = self.run_async(estimate_rent(request_data, bg_tasks))
        self.assertIn("task_id", result)
        self.assertEqual(result["status"], "processing")
        
        # Test get_task_result
        mock_orchestrator.get_result.return_value = mock_result
        
        # Call get_task_result with just task_id as per signature
        task_result = self.run_async(get_task_result("mock-task-id"))
        
        # Verify we call the orchestrator
        mock_orchestrator.get_result.assert_called_once()


if __name__ == "__main__":
    unittest.main()