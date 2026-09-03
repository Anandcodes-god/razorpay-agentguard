import json
from datetime import datetime
from typing import Tuple, Dict, Any

def format_rupees(paise: int) -> str:
    """Format an amount from paise to rupees."""
    return f"₹{paise / 100:,.2f}"

def check_agent_verified(agent: Dict[str, Any]) -> Tuple[bool, str, str]:
    """BLOCK if agent is not verified."""
    if not agent.get("is_verified", False):
        return False, "block", "Agent is not verified."
    return True, "info", "Agent is verified."

def check_agent_not_expired(agent: Dict[str, Any]) -> Tuple[bool, str, str]:
    """BLOCK if agent authorization has expired."""
    expires_at = agent.get("expires_at")
    if expires_at:
        try:
            if isinstance(expires_at, str):
                expires_at_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            else:
                expires_at_dt = expires_at
                
            now = datetime.now(expires_at_dt.tzinfo)
            if expires_at_dt < now:
                return False, "block", "Agent authorization has expired."
        except (ValueError, TypeError):
             return False, "block", "Invalid expiry date format."
    return True, "info", "Agent authorization is active."

def check_agent_has_principal(agent: Dict[str, Any]) -> Tuple[bool, str, str]:
    """BLOCK if no human principal is bound."""
    if not agent.get("principal_id"):
        return False, "block", "No human principal is bound to this agent."
    return True, "info", "Agent has a bound principal."

def check_amount_within_intent(transaction: Dict[str, Any], intent_contract: Dict[str, Any]) -> Tuple[bool, str, str]:
    """BLOCK if amount exceeds intent contract maximum. Include deviation %."""
    if not intent_contract:
        return False, "block", "Missing intent contract."
    
    amount = transaction.get("amount", 0)
    max_amount = intent_contract.get("max_amount", 0)
    
    if max_amount > 0 and amount > max_amount:
        deviation = ((amount - max_amount) / max_amount) * 100
        msg = f"Amount {format_rupees(amount)} exceeds intent maximum {format_rupees(max_amount)} (+{deviation:.2f}%)"
        return False, "block", msg
    return True, "info", "Amount is within intent limits."

def check_category_match(transaction: Dict[str, Any], intent_contract: Dict[str, Any]) -> Tuple[bool, str, str]:
    """REVIEW if transaction category doesn't match intent categories. Parse categories from JSON string if needed."""
    if not intent_contract:
        return False, "review", "Missing intent contract for category check."
        
    tx_category = transaction.get("category")
    if not tx_category:
        return True, "info", "No category on transaction to check."
        
    allowed_categories = intent_contract.get("allowed_categories", [])
    if isinstance(allowed_categories, str):
        try:
            allowed_categories = json.loads(allowed_categories)
        except json.JSONDecodeError:
            allowed_categories = []
            
    if not allowed_categories:
         return True, "info", "No restricted categories in intent."

    if tx_category not in allowed_categories:
        return False, "review", f"Category '{tx_category}' not in allowed categories: {', '.join(allowed_categories)}"
        
    return True, "info", "Category matches intent."

def check_confirmation_threshold(transaction: Dict[str, Any], intent_contract: Dict[str, Any]) -> Tuple[bool, str, str]:
    """REVIEW if amount exceeds the confirmation threshold set in the intent contract."""
    if not intent_contract:
        return True, "info", "No intent contract to check confirmation threshold."
        
    amount = transaction.get("amount", 0)
    threshold = intent_contract.get("confirmation_threshold")
    
    if threshold is not None and amount > threshold:
        return False, "review", f"Amount {format_rupees(amount)} exceeds confirmation threshold {format_rupees(threshold)}"
    return True, "info", "Amount below confirmation threshold."

def check_velocity(transaction_history: Dict[str, Any]) -> Tuple[bool, str, str]:
    """REVIEW if transaction count in last hour is >3x the agent's normal rate. transaction_history has 'recent_count', 'normal_hourly_rate' fields."""
    if not transaction_history:
        return True, "info", "No transaction history available."
        
    recent_count = transaction_history.get("recent_count", 0)
    normal_rate = transaction_history.get("normal_hourly_rate", 0)
    
    if normal_rate > 0 and recent_count > (3 * normal_rate):
        return False, "review", f"High velocity: {recent_count} transactions in last hour (normal: {normal_rate}/hr)"
    return True, "info", "Transaction velocity is normal."

from datetime import timezone
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

def check_time_of_day(transaction: dict):
    created_at = transaction.get("created_at")
    if not created_at:
        created_at_dt = datetime.now(IST)
    elif isinstance(created_at, str):
        try:
            created_at_dt = datetime.fromisoformat(
                created_at.replace("Z", "+00:00")
            ).astimezone(IST)
        except (ValueError, TypeError):
            created_at_dt = datetime.now(IST)
    else:
        created_at_dt = (created_at.replace(tzinfo=timezone.utc)
                         if created_at.tzinfo is None else created_at).astimezone(IST)
    
    hour = created_at_dt.hour
    if hour < 6 or hour >= 23:
        return False, "review", f"Transaction outside normal hours (6am-11pm IST): {created_at_dt.strftime('%H:%M IST')}"
    return True, "info", "Transaction within normal hours."
