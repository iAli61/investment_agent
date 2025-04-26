"""
AI Agents package for the Property Investment Analysis Application.

This package implements a Manager Pattern AI agent architecture with specialized agents
for different investment analysis tasks.
"""

from .agent_system import AIAgentSystem
from .orchestrator import AgentOrchestrator, TaskResult
from .specialized import (
    MarketDataRequest, MarketDataResult,
    RentEstimateRequest, RentEstimateResult,
    DocumentAnalysisRequest, DocumentAnalysisResult,
    OptimizationRequest, OptimizationResult
)

__all__ = [
    "AIAgentSystem",
    "AgentOrchestrator",
    "TaskResult",
    "MarketDataRequest",
    "MarketDataResult",
    "RentEstimateRequest",
    "RentEstimateResult",
    "DocumentAnalysisRequest",
    "DocumentAnalysisResult",
    "OptimizationRequest",
    "OptimizationResult"
]