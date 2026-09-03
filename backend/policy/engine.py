from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .rules import (
    check_agent_verified,
    check_agent_not_expired,
    check_agent_has_principal,
    check_amount_within_intent,
    check_merchant_blocked,
    check_merchant_allowlisted,
    check_category_match,
    check_confirmation_threshold,
    check_velocity,
    check_time_of_day
)

@dataclass
class PolicyResult:
    decision: str  # 'ALLOW', 'REVIEW', 'BLOCK'
    reasons: List[str] = field(default_factory=list)
    checks_passed: List[str] = field(default_factory=list)
    checks_failed: List[str] = field(default_factory=list)
    flags: Dict[str, bool] = field(default_factory=dict)  # Maps to the boolean flags in RiskAssessment

class PolicyGate:
    """Deterministic policy engine. Runs all rules and produces a final decision.
    
    Priority: any BLOCK → result is BLOCK
              any REVIEW (no BLOCKs) → result is REVIEW
              all pass → result is ALLOW
    
    BLOCK rules are checked first. If a BLOCK fires, we still record why
    but don't necessarily run all remaining checks.
    """
    
    def evaluate(self, agent: Dict[str, Any], transaction: Dict[str, Any], 
                 intent_contract: Optional[Dict[str, Any]], 
                 transaction_history: Optional[Dict[str, Any]]) -> PolicyResult:
        """Run all policy rules and return the final decision."""
        
        result = PolicyResult(decision="ALLOW")
        has_block = False
        has_review = False
        
        # Define BLOCK checks
        block_checks = [
            ("agent_unverified", check_agent_verified, [agent]),
            ("agent_expired", check_agent_not_expired, [agent]),
            ("no_principal", check_agent_has_principal, [agent]),
            ("intent_amount_exceeded", check_amount_within_intent, [transaction, intent_contract]),
            ("merchant_blocked", check_merchant_blocked, [transaction, intent_contract]),
        ]
        
        # Define REVIEW checks
        review_checks = [
            ("category_mismatch", check_category_match, [transaction, intent_contract]),
            ("merchant_not_allowlisted", check_merchant_allowlisted, [transaction, intent_contract]),
            ("confirmation_needed", check_confirmation_threshold, [transaction, intent_contract]),
            ("high_velocity", check_velocity, [transaction_history]),
            ("unusual_time", check_time_of_day, [transaction]),
        ]
        
        # Initialize flags
        for flag_name, _, _ in block_checks + review_checks:
            result.flags[flag_name] = False
            
        # Run BLOCK checks
        for flag_name, func, args in block_checks:
            passed, severity, message = func(*args)
            if not passed:
                has_block = True
                result.checks_failed.append(func.__name__)
                result.reasons.append(message)
                result.flags[flag_name] = True
            else:
                result.checks_passed.append(func.__name__)
                
        # Review signals are only useful when the transaction is otherwise eligible.
        if not has_block:
            for flag_name, func, args in review_checks:
                passed, severity, message = func(*args)
                if not passed:
                    has_review = True
                    result.checks_failed.append(func.__name__)
                    result.reasons.append(message)
                    result.flags[flag_name] = True
                else:
                    result.checks_passed.append(func.__name__)

        # Determine final decision
        if has_block:
            result.decision = "BLOCK"
        elif has_review:
            result.decision = "REVIEW"
        else:
            result.decision = "ALLOW"
            
        return result
