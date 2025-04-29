import pytest
from src.ai_agents.orchestrator.orchestrator import AgentOrchestrator

@pytest.mark.parametrize("message, history, expected", [
    ("Hello there", [], ["Enter property details"]),
    ("Can I upload a lease?", {"conversation_history": ["Hi"]}, ["Upload property document for analysis"]),
    ("Tell me more about analysis", {"conversation_history": ["Hi"]}, ["Continue with investment analysis"]),
])
@pytest.mark.asyncio
async def test_generate_suggestions(message, history, expected):
    orch = AgentOrchestrator(enable_rag=False, enable_memory=False)
    sugg = orch._generate_suggestions(message, None, history)
    assert sugg == expected
