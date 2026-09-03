import pytest
from httpx import AsyncClient, ASGITransport
import asyncio
from backend.main import app
from backend.database import create_tables
from backend.config import settings

@pytest.mark.asyncio
async def test_simulation_requires_admin_key():
    settings.admin_api_key = "test-admin-key"
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/simulate/run?scenario_id=1")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_all_scenarios_match():
    # Ensure tables exist
    settings.debug = True
    settings.admin_api_key = "test-admin-key"
    await create_tables()
    
    # Setup transport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Seed the DB first
        headers = {"X-API-Key": "test-admin-key"}
        seed_res = await client.post("/api/seed", headers=headers)
        assert seed_res.status_code == 200

        # Run the scenarios
        res = await client.post("/api/simulate/all", headers=headers, timeout=60.0)
        assert res.status_code == 200
        
        data = res.json()
        results = data.get("results", [])
        
        # We expect exactly 5 scenarios
        assert len(results) == 5
        
        for scenario_result in results:
            scenario = scenario_result.get("scenario", {})
            expected = scenario.get("expected_decision")
            actual = scenario_result.get("actual_decision")
            match = scenario_result.get("match")
            
            assert match is True, f"Scenario {scenario.get('id')} ({scenario.get('name')}) failed. Expected: {expected}, Got: {actual}. Error: {scenario_result.get('error')}"
