import pytest
from backend.policy.rules import (
    check_agent_verified,
    check_agent_not_expired,
    check_amount_within_intent,
    check_category_match,
    check_velocity,
    check_confirmation_threshold
)

def test_check_agent_verified():
    assert check_agent_verified({"is_verified": True}) == (True, "info", "Agent is verified.")
    assert check_agent_verified({"is_verified": False}) == (False, "block", "Agent is not verified.")
    assert check_agent_verified({}) == (False, "block", "Agent is not verified.")

def test_check_agent_not_expired():
    from datetime import datetime, timedelta, timezone
    future = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    
    assert check_agent_not_expired({"expires_at": future}) == (True, "info", "Agent authorization is active.")
    assert check_agent_not_expired({"expires_at": past}) == (False, "block", "Agent authorization has expired.")

def test_check_amount_within_intent():
    # Exactly at threshold
    assert check_amount_within_intent({"amount": 100}, {"max_amount": 100})[0] == True
    # Below threshold
    assert check_amount_within_intent({"amount": 50}, {"max_amount": 100})[0] == True
    # Above threshold
    assert check_amount_within_intent({"amount": 150}, {"max_amount": 100}) == (False, "block", "Amount ₹1.50 exceeds intent maximum ₹1.00 (+50.00%)")
    # Missing intent
    assert check_amount_within_intent({"amount": 100}, None)[0] == False
    # Negative values (even though schema blocks it, pure function should handle)
    assert check_amount_within_intent({"amount": -10}, {"max_amount": 100})[0] == True
    
def test_check_category_match():
    assert check_category_match({"category": "food"}, {"allowed_categories": ["food", "groceries"]})[0] == True
    assert check_category_match({"category": "electronics"}, {"allowed_categories": ["food", "groceries"]}) == (False, "review", "Category 'electronics' not in allowed categories: food, groceries")
    # Missing intent or categories
    assert check_category_match({"category": "food"}, None)[0] == False
    assert check_category_match({"category": "food"}, {"allowed_categories": []})[0] == True

def test_check_velocity():
    assert check_velocity({"recent_count": 2, "normal_hourly_rate": 1})[0] == True
    # > 3x threshold
    assert check_velocity({"recent_count": 10, "normal_hourly_rate": 2}) == (False, "review", "High velocity: 10 transactions in last hour (normal: 2/hr)")
    # 0 normal rate
    assert check_velocity({"recent_count": 5, "normal_hourly_rate": 0})[0] == True

def test_check_confirmation_threshold():
    assert check_confirmation_threshold({"amount": 50}, {"confirmation_threshold": 100})[0] == True
    assert check_confirmation_threshold({"amount": 150}, {"confirmation_threshold": 100}) == (False, "review", "Amount ₹1.50 exceeds confirmation threshold ₹1.00")
    # No threshold
    assert check_confirmation_threshold({"amount": 150}, {"confirmation_threshold": None})[0] == True
    assert check_confirmation_threshold({"amount": 150}, None)[0] == True
