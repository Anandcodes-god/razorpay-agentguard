from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

SCENARIOS: List[Dict[str, Any]] = [
    {
        'id': 1,
        'name': 'Normal Purchase',
        'description': 'Verified agent makes a grocery purchase within budget. Expected: ALLOW.',
        'expected_decision': 'ALLOW',
        'transaction': {
            'agent_id': 'agent_shopbot_001',
            'intent_contract_id': 'ic_grocery_001',
            'merchant_name': 'BigBasket',
            'merchant_category': 'groceries',
            'amount': 145000,  # ₹1,450
            'currency': 'INR',
            'description': 'Weekly grocery order'
        }
    },
    {
        'id': 2,
        'name': 'Unknown Agent',
        'description': 'Unverified agent with no human principal attempts a purchase. Expected: BLOCK.',
        'expected_decision': 'BLOCK',
        'transaction': {
            'agent_id': 'agent_unknown_002',
            'intent_contract_id': None,
            'merchant_name': 'ElectroMart',
            'merchant_category': 'electronics',
            'amount': 800000,  # ₹8,000
            'currency': 'INR',
            'description': 'Electronics purchase'
        }
    },
    {
        'id': 3,
        'name': 'Budget Exceeded',
        'description': 'Verified agent attempts purchase far exceeding intent maximum (₹29,798 vs ₹5,000 max). Possible context manipulation. Expected: BLOCK.',
        'expected_decision': 'BLOCK',
        'transaction': {
            'agent_id': 'agent_shopbot_001',
            'intent_contract_id': 'ic_shoes_002',
            'merchant_name': 'ShoesPlus',
            'merchant_category': 'footwear',
            'amount': 2979800,  # ₹29,798
            'currency': 'INR',
            'description': 'Running shoes + premium protection package'
        }
    },
    {
        'id': 4,
        'name': 'Category Drift',
        'description': 'Verified agent uses grocery intent to buy gaming products. Amount within budget but wrong category. Expected: REVIEW.',
        'expected_decision': 'REVIEW',
        'transaction': {
            'agent_id': 'agent_shopbot_001',
            'intent_contract_id': 'ic_grocery_001',
            'merchant_name': 'GameStop',
            'merchant_category': 'gaming',
            'amount': 180000,  # ₹1,800
            'currency': 'INR',
            'description': 'Gaming accessories'
        }
    },
    {
        'id': 5,
        'name': 'Velocity Spike + Odd Hours',
        'description': 'Verified agent makes purchase at 3:17 AM after unusually high transaction volume. Expected: REVIEW.',
        'expected_decision': 'REVIEW',
        'transaction': {
            'agent_id': 'agent_shopbot_001',
            'intent_contract_id': 'ic_grocery_001',
            'merchant_name': 'QuickMart',
            'merchant_category': 'groceries',
            'amount': 90000,  # ₹900
            'currency': 'INR',
            'description': 'Late night grocery order',
        },
        'setup': {
            'inject_velocity_spike': True,
            'spike_count': 12,
            'override_time_hour': 3,
            'override_time_minute': 17
        }
    }
]


def get_scenario(scenario_id: int) -> Optional[Dict[str, Any]]:
    """Get a scenario by ID (1-5)."""
    for s in SCENARIOS:
        if s['id'] == scenario_id:
            return s
    return None


def get_all_scenarios() -> List[Dict[str, Any]]:
    """Get all 5 scenarios."""
    return SCENARIOS
