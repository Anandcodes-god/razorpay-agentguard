from backend.policy.engine import PolicyGate
from backend.models.transaction import Transaction

def test_policy_gate_block_overrides_review():
    gate = PolicyGate()
    result = gate.evaluate(
        agent={"is_verified": False, "principal_id": "x", "expires_at": None},
        transaction={"amount": 100, "merchant_category": "food", "created_at": "2024-01-15T10:00:00+05:30"},
        intent_contract={"max_amount": 200, "allowed_categories": ["food"], "confirmation_threshold": None},
        transaction_history=[]
    )
    # The agent is unverified, which is a BLOCK condition.
    # The transaction amount is within limits, which is ALLOW/REVIEW.
    # The BLOCK must win.
    assert result.decision == "BLOCK"

def test_policy_gate_blocks_blocked_merchant():
    result = PolicyGate().evaluate(
        agent={"is_verified": True, "principal_id": "human", "expires_at": None},
        transaction={"amount": 100, "category": "food", "merchant_name": "SteamGames", "created_at": "2024-01-15T10:00:00+05:30"},
        intent_contract={
            "max_amount": 200,
            "allowed_categories": ["food"],
            "merchant_constraints": {"blocked": ["SteamGames"]},
            "confirmation_threshold": None,
        },
        transaction_history=None,
    )
    assert result.decision == "BLOCK"
    assert result.flags["merchant_blocked"] is True

def test_policy_gate_reviews_non_allowlisted_merchant():
    result = PolicyGate().evaluate(
        agent={"is_verified": True, "principal_id": "human", "expires_at": None},
        transaction={"amount": 100, "category": "food", "merchant_name": "OtherShop", "created_at": "2024-01-15T10:00:00+05:30"},
        intent_contract={
            "max_amount": 200,
            "allowed_categories": ["food"],
            "merchant_constraints": {"allowed": ["PreferredShop"]},
            "confirmation_threshold": None,
        },
        transaction_history=None,
    )
    assert result.decision == "REVIEW"
    assert result.flags["merchant_not_allowlisted"] is True
