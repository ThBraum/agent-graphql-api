import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_assistant_prompt_query():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post(
            "/graphql",
            json={"query": "query { assistantPrompt }"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    prompt = data["data"]["assistantPrompt"]
    assert isinstance(prompt, str)
    assert "Matheus Braum's website assistant" in prompt
