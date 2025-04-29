import sys, os
# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch
from src.backend.api import app

@pytest.mark.asyncio
async def test_conversation_endpoint():
    # Mock the manager_agent's converse method
    class MockManagerAgent:
        async def converse(self, message, context):
            return {
                "response": f"Echo: {message}",
                "suggestions": ["Next step suggestion"],
                "context": context or {"step": 1}
            }
    # Patch orchestrator.manager_agent
    with patch("src.backend.api.orchestrator") as mock_orch:
        mock_orch.manager_agent = MockManagerAgent()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            payload = {"message": "How do I start?", "context": {"step": 0}}
            response = await ac.post("/ai/conversation/", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["response"].startswith("Echo:")
            assert data["suggestions"] == ["Next step suggestion"]
            assert data["context"]["step"] == 0
