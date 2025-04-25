"""
Database models for the Property Investment Analysis App
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User model for authentication and personalization"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(200))
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    properties = relationship("Property", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"

class Property(Base):
    """Property model to store property details"""
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    address = Column(String(255), nullable=False)
    purchase_price = Column(Float, nullable=False)
    property_type = Column(String(50))  # apartment, house, multi-family, commercial
    year_built = Column(Integer, nullable=True)
    size_sqm = Column(Float, nullable=True)
    num_units = Column(Integer, default=1)
    condition_assessment = Column(String(50), nullable=True)  # excellent, good, average, fair, poor
    region = Column(String(50), default="berlin")
    location = Column(String(100), nullable=True)
    property_age_years = Column(Integer, nullable=True)
    closing_costs = Column(Float, nullable=True)
    total_acquisition_cost = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="properties")
    rental_units = relationship("RentalUnit", back_populates="property", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="property", cascade="all, delete-orphan")
    financing = relationship("Financing", back_populates="property", cascade="all, delete-orphan", uselist=False)
    analyses = relationship("Analysis", back_populates="property", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Property {self.address}>"

class RentalUnit(Base):
    """Rental unit model for multi-unit properties"""
    __tablename__ = "rental_units"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    unit_number = Column(String(20), nullable=True)
    size_sqm = Column(Float, nullable=True)
    num_bedrooms = Column(Integer, nullable=True)
    num_bathrooms = Column(Float, nullable=True)  # Allow 0.5 for half bathrooms
    is_occupied = Column(Boolean, default=False)
    current_rent = Column(Float, nullable=True)
    potential_rent = Column(Float, nullable=True)
    lease_start_date = Column(DateTime, nullable=True)
    lease_end_date = Column(DateTime, nullable=True)
    tenant_name = Column(String(100), nullable=True)
    features = Column(JSON, nullable=True)  # Store features as JSON array
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    property = relationship("Property", back_populates="rental_units")
    
    def __repr__(self):
        return f"<RentalUnit {self.unit_number} of Property {self.property_id}>"

class Financing(Base):
    """Financing model for property financing details"""
    __tablename__ = "financing"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), unique=True)
    loan_amount = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False)
    repayment_rate = Column(Float, nullable=False)
    term_years = Column(Integer, nullable=False)
    monthly_payment = Column(Float, nullable=True)
    available_cash = Column(Float, nullable=True)
    down_payment = Column(Float, nullable=True)
    down_payment_percentage = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    property = relationship("Property", back_populates="financing")
    
    def __repr__(self):
        return f"<Financing for Property {self.property_id}>"

class Expense(Base):
    """Expense model for property operating expenses"""
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    name = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    frequency = Column(String(20), nullable=False)  # annual, monthly, quarterly
    is_percentage = Column(Boolean, default=False)  # True if amount is a percentage of income
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    property = relationship("Property", back_populates="expenses")
    
    def __repr__(self):
        return f"<Expense {self.name} for Property {self.property_id}>"

class Analysis(Base):
    """Analysis model to store property investment analysis results"""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    cash_flow_monthly = Column(Float, nullable=False)
    cash_flow_annual = Column(Float, nullable=False)
    cash_on_cash_return = Column(Float, nullable=False)
    cap_rate = Column(Float, nullable=False)
    roi = Column(Float, nullable=False)
    tax_benefits_annual = Column(Float, nullable=True)
    risk_assessment = Column(Text, nullable=True)
    full_analysis_data = Column(JSON, nullable=True)  # Store full analysis results as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    property = relationship("Property", back_populates="analyses")
    
    def __repr__(self):
        return f"<Analysis for Property {self.property_id}>"

class MarketData(Base):
    """Market data model to store property market data collected by AI agents"""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(100), index=True)
    property_type = Column(String(50), index=True)
    avg_price_sqm = Column(Float, nullable=True)
    avg_rent_sqm = Column(Float, nullable=True)
    vacancy_rate = Column(Float, nullable=True)
    price_trend = Column(Float, nullable=True)  # Percentage change YoY
    rent_trend = Column(Float, nullable=True)  # Percentage change YoY
    sources = Column(JSON, nullable=True)  # List of data sources
    confidence_level = Column(Float, nullable=True)  # 0-1 range
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<MarketData for {self.location}, {self.property_type}>"

class AgentTask(Base):
    """Agent task model to track AI agent tasks and results"""
    __tablename__ = "agent_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(50), unique=True, index=True)
    agent_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    parameters = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AgentTask {self.task_id} for {self.agent_type}>"