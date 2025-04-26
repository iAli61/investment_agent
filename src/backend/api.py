"""
Main backend API for the Property Investment Analysis App
"""
import os
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uuid
import asyncio
import json
from datetime import datetime

from ..database.database import get_db
from ..database.models import User, Property, RentalUnit, Expense, Financing, Analysis
from ..ai_agents.orchestrator import orchestrator
from ..ai_agents import AIAgentSystem
from ..utils.financial_utils import analyze_property_investment

# Configure logging
logger = logging.getLogger(__name__)

# AI agent system instance
ai_agent_system = None

# Define AgentTask class
class AgentTask(BaseModel):
    task_id: str
    agent_type: str
    description: str
    parameters: Dict[str, Any]
    status: str = "pending"
    
    class Config:
        orm_mode = True

app = FastAPI(title="Property Investment Analysis API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to initialize AI agent system
@app.on_event("startup")
async def startup_event():
    global ai_agent_system
    
    try:
        # Check if Azure OpenAI environment variables are available
        use_azure = os.environ.get("USE_AZURE_OPENAI", "false").lower() == "true"
        if use_azure:
            azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
            azure_deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
            azure_api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2023-07-01-preview")
            use_managed_identity = os.environ.get("AZURE_USE_MANAGED_IDENTITY", "false").lower() == "true"
            
            # Initialize with Azure OpenAI if environment variables are set
            if azure_endpoint and azure_deployment:
                ai_agent_system = AIAgentSystem(
                    use_azure=True,
                    azure_deployment=azure_deployment,
                    azure_endpoint=azure_endpoint,
                    azure_api_version=azure_api_version,
                    use_managed_identity=use_managed_identity
                )
            else:
                # Fall back to standard OpenAI if Azure config is incomplete
                ai_agent_system = AIAgentSystem(model_name="gpt-4o")
        else:
            # Standard OpenAI initialization
            ai_agent_system = AIAgentSystem(model_name="gpt-4o")
            
        # Initialize the AI agent system
        ai_agent_system.initialize()
        
        # Make the orchestrator globally available
        global orchestrator
        orchestrator = ai_agent_system.orchestrator
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        logger.exception("Detailed stack trace follows:")
        raise

# Define Pydantic models for request/response validation
class PropertyBase(BaseModel):
    address: str
    purchase_price: float
    property_type: str
    year_built: Optional[int] = None
    size_sqm: Optional[float] = None
    num_units: int = 1
    condition_assessment: Optional[str] = None
    region: str = "berlin"
    
    class Config:
        orm_mode = True

class PropertyCreate(PropertyBase):
    pass

class PropertyResponse(PropertyBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    closing_costs: Optional[float] = None
    total_acquisition_cost: Optional[float] = None
    
    class Config:
        orm_mode = True

class RentalUnitBase(BaseModel):
    unit_number: Optional[str] = None
    size_sqm: Optional[float] = None
    num_bedrooms: Optional[int] = None
    num_bathrooms: Optional[float] = None
    is_occupied: bool = False
    current_rent: Optional[float] = None
    potential_rent: Optional[float] = None
    lease_start_date: Optional[datetime] = None
    lease_end_date: Optional[datetime] = None
    tenant_name: Optional[str] = None
    
    class Config:
        orm_mode = True

class RentalUnitCreate(RentalUnitBase):
    pass

class RentalUnitResponse(RentalUnitBase):
    id: int
    property_id: int
    
    class Config:
        orm_mode = True

class FinancingBase(BaseModel):
    loan_amount: float
    interest_rate: float
    repayment_rate: float
    term_years: int
    
    class Config:
        orm_mode = True

class FinancingCreate(FinancingBase):
    pass

class FinancingResponse(FinancingBase):
    id: int
    property_id: int
    monthly_payment: Optional[float] = None
    
    class Config:
        orm_mode = True

class ExpenseBase(BaseModel):
    name: str
    amount: float
    frequency: str
    is_percentage: bool = False
    
    class Config:
        orm_mode = True

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    id: int
    property_id: int
    
    class Config:
        orm_mode = True

class AnalysisBase(BaseModel):
    cash_flow_monthly: float
    cash_flow_annual: float
    cash_on_cash_return: float
    cap_rate: float
    roi: float
    tax_benefits_annual: Optional[float] = None
    risk_assessment: Optional[str] = None
    
    class Config:
        orm_mode = True

class AnalysisCreate(AnalysisBase):
    pass

class AnalysisResponse(AnalysisBase):
    id: int
    property_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class MarketDataRequest(BaseModel):
    location: str
    property_type: str
    additional_filters: Optional[Dict[str, Any]] = None

class RentEstimationRequest(BaseModel):
    location: str
    property_type: str
    size_sqm: float
    num_bedrooms: Optional[int] = None
    num_bathrooms: Optional[float] = None
    features: Optional[List[str]] = []
    condition: Optional[str] = "average"

class PropertyAnalysisRequest(BaseModel):
    property_data: Dict[str, Any]
    units_data: List[Dict[str, Any]]
    financing_data: Dict[str, Any]
    expenses_data: Dict[str, Any]
    tax_data: Dict[str, Any]

# API Routes

@app.get("/")
def read_root():
    return {"message": "Welcome to the Property Investment Analysis API"}

# Property routes
@app.post("/properties/", response_model=PropertyResponse)
async def create_property(property_data: PropertyCreate, db=Depends(get_db)):
    # In a real app, get user_id from auth token
    user_id = 1  # Placeholder
    
    # Create new property
    new_property = Property(
        user_id=user_id,
        address=property_data.address,
        purchase_price=property_data.purchase_price,
        property_type=property_data.property_type,
        year_built=property_data.year_built,
        size_sqm=property_data.size_sqm,
        num_units=property_data.num_units,
        condition_assessment=property_data.condition_assessment
    )
    
    db.add(new_property)
    db.commit()
    db.refresh(new_property)
    
    return new_property

@app.get("/properties/", response_model=List[PropertyResponse])
async def get_properties(db=Depends(get_db)):
    # In a real app, filter by authenticated user
    properties = db.query(Property).all()
    return properties

@app.get("/properties/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: int, db=Depends(get_db)):
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    return property

# Rental Unit routes
@app.post("/properties/{property_id}/units/", response_model=RentalUnitResponse)
async def create_rental_unit(property_id: int, unit_data: RentalUnitCreate, db=Depends(get_db)):
    # Check if property exists
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Create new rental unit
    new_unit = RentalUnit(
        property_id=property_id,
        unit_number=unit_data.unit_number,
        size_sqm=unit_data.size_sqm,
        num_bedrooms=unit_data.num_bedrooms,
        num_bathrooms=unit_data.num_bathrooms,
        is_occupied=unit_data.is_occupied,
        current_rent=unit_data.current_rent,
        potential_rent=unit_data.potential_rent,
        lease_start_date=unit_data.lease_start_date,
        lease_end_date=unit_data.lease_end_date,
        tenant_name=unit_data.tenant_name
    )
    
    db.add(new_unit)
    db.commit()
    db.refresh(new_unit)
    
    return new_unit

@app.get("/properties/{property_id}/units/", response_model=List[RentalUnitResponse])
async def get_rental_units(property_id: int, db=Depends(get_db)):
    # Check if property exists
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    units = db.query(RentalUnit).filter(RentalUnit.property_id == property_id).all()
    return units

# Financing routes
@app.post("/properties/{property_id}/financing/", response_model=FinancingResponse)
async def create_financing(property_id: int, financing_data: FinancingCreate, db=Depends(get_db)):
    # Check if property exists
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Check if financing already exists for this property
    existing_financing = db.query(Financing).filter(Financing.property_id == property_id).first()
    if existing_financing:
        # Update existing financing
        for key, value in financing_data.dict().items():
            setattr(existing_financing, key, value)
        
        db.commit()
        db.refresh(existing_financing)
        return existing_financing
    
    # Create new financing
    new_financing = Financing(
        property_id=property_id,
        loan_amount=financing_data.loan_amount,
        interest_rate=financing_data.interest_rate,
        repayment_rate=financing_data.repayment_rate,
        term_years=financing_data.term_years,
        monthly_payment=financing_data.loan_amount * (financing_data.interest_rate + financing_data.repayment_rate) / 1200
    )
    
    db.add(new_financing)
    db.commit()
    db.refresh(new_financing)
    
    return new_financing

@app.get("/properties/{property_id}/financing/", response_model=FinancingResponse)
async def get_financing(property_id: int, db=Depends(get_db)):
    financing = db.query(Financing).filter(Financing.property_id == property_id).first()
    if not financing:
        raise HTTPException(status_code=404, detail="Financing not found for this property")
    return financing

# Analysis routes
@app.post("/properties/{property_id}/analyze/")
async def analyze_property(property_id: int, analysis_request: PropertyAnalysisRequest):
    # Perform analysis using utility functions
    analysis_result = analyze_property_investment(
        analysis_request.property_data,
        analysis_request.units_data,
        analysis_request.financing_data,
        analysis_request.expenses_data,
        analysis_request.tax_data
    )
    
    return analysis_result

# AI Agent routes
@app.post("/ai/market-data/")
async def get_market_data(request: MarketDataRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    
    # Log the available agent types for debugging
    logger.info(f"Available agent types: {list(orchestrator.specialized_agents.keys())}")
    
    # Create task for market data agent
    task = AgentTask(
        task_id=task_id,
        agent_type="market_data",
        description=f"Get market data for {request.location}, {request.property_type}",
        parameters={
            "location": request.location,
            "property_type": request.property_type,
            "additional_filters": request.additional_filters or {}
        }
    )
    
    # Add task to orchestrator
    orchestrator.add_task(task)
    
    # Process task in background
    background_tasks.add_task(orchestrator.process_queue)
    
    return {"task_id": task_id, "status": "processing"}

@app.get("/ai/tasks/{task_id}")
async def get_task_result(task_id: str):
    result = orchestrator.get_result(task_id)
    if result is None:
        task_status = "pending"
        for task in orchestrator.task_queue.queue:
            if task.task_id == task_id:
                task_status = task.status
                break
        return {"task_id": task_id, "status": task_status}
    
    return {"task_id": task_id, "status": "completed", "result": result}

@app.post("/ai/rent-estimation/")
async def estimate_rent(request: RentEstimationRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    
    # Create task for rent estimation agent
    task = AgentTask(
        task_id=task_id,
        agent_type="rent_estimation",
        description=f"Estimate rent for {request.size_sqm} sqm {request.property_type} in {request.location}",
        parameters={
            "location": request.location,
            "property_type": request.property_type,
            "size_sqm": request.size_sqm,
            "num_bedrooms": request.num_bedrooms,
            "num_bathrooms": request.num_bathrooms,
            "features": request.features,
            "condition": request.condition
        }
    )
    
    # Add task to orchestrator
    orchestrator.add_task(task)
    
    # Process task in background
    background_tasks.add_task(orchestrator.process_queue)
    
    return {"task_id": task_id, "status": "processing"}