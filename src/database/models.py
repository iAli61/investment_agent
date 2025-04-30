"""
Database models for the Property Investment Analysis Application
"""
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    """User model for authentication and user-specific data"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(200))
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    properties = relationship("Property", back_populates="user")
    scenarios = relationship("Scenario", back_populates="user")
    preferences = relationship("UserPreference", back_populates="user", uselist=False)
    
    def __repr__(self):
        return f"<User {self.username}>"

class UserPreference(Base):
    """User preferences for customization and personalization"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    expertise_level = Column(String(20), default="beginner")  # beginner, intermediate, advanced
    preferred_currency = Column(String(3), default="USD")
    ui_theme = Column(String(20), default="light")  # light, dark
    notification_preferences = Column(JSON, default={})
    language = Column(String(10), default="en")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Custom preferences stored as JSON
    custom_preferences = Column(JSON, default={})
    
    # Relationships
    user = relationship("User", back_populates="preferences")
    
    def __repr__(self):
        return f"<UserPreference for {self.user_id}>"

class Property(Base):
    """Property model for storing property information"""
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    public_id = Column(String(50), default=lambda: str(uuid.uuid4())[:8], unique=True)
    name = Column(String(100))
    address = Column(String(200))
    city = Column(String(100))
    state = Column(String(100))
    zip_code = Column(String(20))
    country = Column(String(100))
    property_type = Column(String(50))  # single-family, multi-family, commercial, etc.
    year_built = Column(Integer, nullable=True)
    size_sqm = Column(Float, nullable=True)
    num_units = Column(Integer, default=1)
    purchase_price = Column(Float, nullable=True)
    current_value = Column(Float, nullable=True)
    status = Column(String(20), default="draft")  # draft, active, archived, sold
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Property details as JSON
    property_details = Column(JSON, default={})
    
    # Relationships
    user = relationship("User", back_populates="properties")
    scenarios = relationship("Scenario", back_populates="property")
    
    def __repr__(self):
        return f"<Property {self.name}>"

class Scenario(Base):
    """Investment scenario model for storing different investment scenarios"""
    __tablename__ = "scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    property_id = Column(Integer, ForeignKey("properties.id"))
    name = Column(String(100))
    description = Column(Text, nullable=True)
    is_baseline = Column(Boolean, default=False)
    status = Column(String(20), default="draft")  # draft, active, archived
    
    # Financing parameters
    financing_params = Column(JSON, default={})
    # Rental parameters
    rental_params = Column(JSON, default={})
    # Expense parameters
    expense_params = Column(JSON, default={})
    
    # Results of calculations
    results = Column(JSON, nullable=True)
    # Warnings or alerts
    warnings = Column(JSON, nullable=True)
    # LLM cost for analysis
    llm_cost = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="scenarios")
    property = relationship("Property", back_populates="scenarios")
    
    def __repr__(self):
        return f"<Scenario {self.name} for Property {self.property_id}>"

class AgentMemoryItem(Base):
    """Memory item for AI agents"""
    __tablename__ = "agent_memory_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=True)
    
    memory_type = Column(String(50))  # conversation, preference, fact, error
    key = Column(String(100))
    value = Column(JSON)
    memory_metadata = Column(JSON, default={})
    ttl = Column(DateTime, nullable=True)  # Time to live, nullable for permanent memories
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AgentMemoryItem {self.key}>"

class CostTracker(Base):
    """Track API costs for LLM usage"""
    __tablename__ = "cost_tracker"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=True)
    
    operation_type = Column(String(50))  # analysis, conversation, extraction
    model = Column(String(50))  # gpt-4, gpt-3.5-turbo, etc.
    tokens_input = Column(Integer, default=0)
    tokens_output = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<CostTracker {self.operation_type} ${self.cost_usd}>"

class AnalyticsEvent(Base):
    """Track analytics events for monitoring usage patterns"""
    __tablename__ = "analytics_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    event_type = Column(String(50))  # page_view, feature_use, error
    event_name = Column(String(100))
    properties = Column(JSON, default={})
    session_id = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AnalyticsEvent {self.event_type} {self.event_name}>"