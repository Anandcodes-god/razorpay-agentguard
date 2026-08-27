from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timezone, timedelta
import json

async def get_agent_profile(session: AsyncSession, agent_id: str) -> dict:
    """Fetch agent's identity, scope, budget, verification status, and expiry.
    Returns dict with: id, name, principal_id, is_verified, scope (parsed from JSON),
    max_budget, created_at, expires_at, is_expired (computed bool)."""
    # Assuming Agent model queries below
    if not session:
        return {}
    query = text("SELECT id, name, principal_id, is_verified, scope, max_budget, created_at, expires_at FROM agents WHERE id = :id")
    result = await session.execute(query, {"id": agent_id})
    row = result.fetchone()
    
    if not row:
        return {}
        
    scope = json.loads(row.scope) if row.scope and isinstance(row.scope, str) else (row.scope or {})
    expires_at = row.expires_at
    is_expired = False
    if expires_at:
        # SQLite may return datetime as string
        if isinstance(expires_at, str):
            try:
                expires_at = datetime.fromisoformat(expires_at)
            except ValueError:
                expires_at = None
        if expires_at:
            # Make timezone-aware if naïve
            if hasattr(expires_at, 'tzinfo') and expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            is_expired = expires_at < datetime.now(timezone.utc)

    return {
        "id": row.id,
        "name": row.name,
        "principal_id": row.principal_id,
        "is_verified": row.is_verified,
        "scope": scope,
        "max_budget": row.max_budget,
        "created_at": row.created_at,
        "expires_at": row.expires_at,
        "is_expired": is_expired
    }

async def get_intent_contract(session: AsyncSession, contract_id: str) -> dict:
    """Fetch the structured intent contract.
    Returns dict with all fields, categories parsed from JSON string to list."""
    if not session:
        return {}
    query = text("SELECT id, purpose, categories, max_amount, merchant_constraints, requires_confirmation_above FROM intent_contracts WHERE id = :id")
    result = await session.execute(query, {"id": contract_id})
    row = result.fetchone()
    
    if not row:
        return {}
        
    categories = json.loads(row.categories) if row.categories and isinstance(row.categories, str) else (row.categories or [])
    merchant_constraints = json.loads(row.merchant_constraints) if row.merchant_constraints and isinstance(row.merchant_constraints, str) else (row.merchant_constraints or {})
    
    return {
        "id": row.id,
        "purpose": row.purpose,
        "categories": categories,
        "max_amount": row.max_amount,
        "merchant_constraints": merchant_constraints,
        "requires_confirmation_above": row.requires_confirmation_above
    }

def check_intent_deviation(transaction: dict, intent_contract: dict) -> dict:
    """Compare transaction against intent contract. Pure computation, no DB needed.
    Returns: {
        'amount_deviation_pct': float,  # e.g. 495.96
        'amount_exceeds_max': bool,
        'category_match': bool,
        'merchant_allowed': bool, 
        'within_budget': bool,
        'budget_usage_pct': float  # e.g. 72.5
    }"""
    if not intent_contract:
        return {}
        
    tx_amount = transaction.get("amount", 0)
    tx_category = transaction.get("merchant_category", "")
    tx_merchant = transaction.get("merchant_name", "")
    
    max_amount = intent_contract.get("max_amount", 0)
    amount_deviation_pct = 0.0
    amount_exceeds_max = False
    if tx_amount > max_amount and max_amount > 0:
        amount_exceeds_max = True
        amount_deviation_pct = ((tx_amount - max_amount) / max_amount) * 100
        
    categories = intent_contract.get("categories", [])
    category_match = tx_category in categories if categories else True
    
    merchant_constraints = intent_contract.get("merchant_constraints", {})
    allowed_merchants = merchant_constraints.get("allowed", [])
    blocked_merchants = merchant_constraints.get("blocked", [])
    
    merchant_allowed = True
    if blocked_merchants and tx_merchant in blocked_merchants:
        merchant_allowed = False
    if allowed_merchants and tx_merchant not in allowed_merchants:
        merchant_allowed = False
        
    within_budget = True
    budget_usage_pct = 0.0
    if max_amount > 0:
        budget_usage_pct = min(100.0, (tx_amount / max_amount) * 100)
        
    return {
        'amount_deviation_pct': amount_deviation_pct,
        'amount_exceeds_max': amount_exceeds_max,
        'category_match': category_match,
        'merchant_allowed': merchant_allowed,
        'within_budget': within_budget,
        'budget_usage_pct': budget_usage_pct
    }

async def get_transaction_history(session: AsyncSession, agent_id: str, hours: int = 24) -> dict:
    """Fetch agent's recent transaction history.
    Returns: {
        'total_count': int,
        'total_amount': int,  # paise
        'recent_1h_count': int,
        'normal_hourly_rate': float,  # avg transactions per hour over 24h
        'velocity_ratio': float,  # recent_1h / normal_hourly_rate
        'categories': list[str],
        'merchants': list[str]
    }"""
    if not session:
        return {'total_count': 0, 'total_amount': 0, 'recent_1h_count': 0, 'normal_hourly_rate': 0.0, 'velocity_ratio': 0.0, 'categories': [], 'merchants': []}
    
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    query = text("SELECT amount, merchant_category, merchant_name, created_at FROM transactions WHERE agent_id = :agent_id AND created_at >= :since")
    result = await session.execute(query, {"agent_id": agent_id, "since": since})
    rows = result.fetchall()
    
    total_count = len(rows)
    total_amount = sum(row.amount for row in rows)
    
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    
    def _parse_dt(val):
        if val is None:
            return None
        if isinstance(val, str):
            try:
                dt = datetime.fromisoformat(val)
            except ValueError:
                return None
        else:
            dt = val
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    
    recent_1h_count = sum(1 for row in rows if _parse_dt(row.created_at) and _parse_dt(row.created_at) >= one_hour_ago)
    
    normal_hourly_rate = total_count / hours if hours > 0 else 0
    velocity_ratio = recent_1h_count / normal_hourly_rate if normal_hourly_rate > 0 else 0.0
    
    categories = list(set(row.merchant_category for row in rows if row.merchant_category))
    merchants = list(set(row.merchant_name for row in rows if row.merchant_name))
    
    return {
        'total_count': total_count,
        'total_amount': total_amount,
        'recent_1h_count': recent_1h_count,
        'normal_hourly_rate': normal_hourly_rate,
        'velocity_ratio': velocity_ratio,
        'categories': categories,
        'merchants': merchants
    }

def check_merchant_trust(merchant_name: str, merchant_category: str) -> dict:
    """Simple merchant lookup. In a real system this would hit a database.
    For demo, use a hardcoded trust map.
    Returns: {
        'trust_level': 'high'|'medium'|'low'|'unknown',
        'trust_score': int (0-100),
        'known_issues': list[str],
        'category_verified': bool
    }"""
    TRUSTED_MERCHANTS = {
        'BigBasket': {'trust_level': 'high', 'trust_score': 95, 'categories': ['groceries', 'food']},
        'QuickMart': {'trust_level': 'high', 'trust_score': 90, 'categories': ['groceries', 'food']},
        'ShoesPlus': {'trust_level': 'medium', 'trust_score': 70, 'categories': ['footwear', 'sports']},
        'GameStop': {'trust_level': 'medium', 'trust_score': 75, 'categories': ['gaming', 'electronics']},
        'ElectroMart': {'trust_level': 'medium', 'trust_score': 65, 'categories': ['electronics']},
    }
    
    if merchant_name in TRUSTED_MERCHANTS:
        data = TRUSTED_MERCHANTS[merchant_name]
        return {
            'trust_level': data['trust_level'],
            'trust_score': data['trust_score'],
            'known_issues': [],
            'category_verified': merchant_category in data['categories']
        }
    
    return {
        'trust_level': 'unknown',
        'trust_score': 50,
        'known_issues': ['New or unverified merchant'],
        'category_verified': False
    }

def compute_agent_trust_score(agent_profile: dict) -> int:
    """Compute a simple trust score for the agent (0-100).
    Scoring:
    - is_verified: +40 points
    - has principal_id: +25 points  
    - not expired: +20 points
    - has valid scope: +15 points
    """
    if not agent_profile:
        return 0
        
    score = 0
    if agent_profile.get('is_verified'):
        score += 40
    if agent_profile.get('principal_id'):
        score += 25
    if not agent_profile.get('is_expired', True):
        score += 20
    if agent_profile.get('scope'):
        score += 15
    
    return min(100, max(0, score))

def compute_overall_risk_score(intent_deviation_score: int, 
                               agent_trust_score: int,
                               transaction_risk_score: int) -> int:
    """Weighted combination: intent 40%, agent 35%, transaction 25%.
    Higher score = SAFER (100 = no risk, 0 = maximum risk)."""
    score = (intent_deviation_score * 0.40) + (agent_trust_score * 0.35) + (transaction_risk_score * 0.25)
    return min(100, max(0, int(score)))
