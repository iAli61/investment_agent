"""
Agent Orchestrator package that coordinates specialized agents using the Manager Pattern.
"""

from .orchestrator import AgentOrchestrator, TaskResult
from .manager_agent import create_manager_agent, ManagerAgentResult

# Create a singleton instance of the orchestrator
orchestrator = AgentOrchestrator()

__all__ = [
    "AgentOrchestrator", 
    "TaskResult",
    "create_manager_agent",
    "ManagerAgentResult",
    "orchestrator"
]