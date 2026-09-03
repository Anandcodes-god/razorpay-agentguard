import pytest
from httpx import AsyncClient, ASGITransport
import asyncio
from backend.main import app
from backend.database import create_tables

@pytest.mark.asyncio
async def test_all_scenarios_match():
    # Ensure tables exist
    await create_tables()
    
    # Setup transport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Seed the DB first
        seed_res = await client.post("/api/seed")
        assert seed_res.status_code == 200

        # Run the scenarios
        res = await client.post("/api/simulate/all", timeout=60.0)
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
