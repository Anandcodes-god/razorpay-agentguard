from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime, timezone
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Try to import AuditLog from models if it exists
try:
    from backend.models import AuditLog
except ImportError:
    # Basic fallback if model isn't built yet
    class AuditLog:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

class AuditLogger:
    """Service for logging audit trail events."""
    
    def __init__(self, session: AsyncSession, assessment_id: str):
        self.session = session
        self.assessment_id = assessment_id
        self.step_counter = 0
    
    async def log(self, event_type: str, title: str, 
                  detail: str, severity: str = 'info') -> None:
        """Add a timestamped step to the audit trail.
        
        Args:
            event_type: observe/reason/check/decide/action
            title: Short description of the event
            detail: Detailed information about the event
            severity: info/warning/critical
        """
        self.step_counter += 1
        try:
            log_entry = AuditLog(
                id=str(uuid.uuid4()),
                assessment_id=self.assessment_id,
                step_number=self.step_counter,
                event_type=event_type,
                title=title,
                detail=detail,
                severity=severity,
                timestamp=datetime.now(timezone.utc)
            )
            self.session.add(log_entry)
            # Depending on usage, might not want to flush immediately, but generally good for audit
            await self.session.flush()
        except Exception as e:
            logger.error(f"Failed to create audit log entry: {e}")
    
    async def log_observe(self, title: str, detail: str) -> None:
        """Log an observation event."""
        await self.log('observe', title, detail)
    
    async def log_check(self, title: str, detail: str, passed: bool) -> None:
        """Log a check event, severity depends on passed status."""
        severity = 'info' if passed else 'warning'
        await self.log('check', title, detail, severity)
    
    async def log_decide(self, title: str, detail: str, decision: str) -> None:
        """Log a decision event, severity depends on decision outcome."""
        severity = 'critical' if decision == 'BLOCK' else \
                   'warning' if decision == 'REVIEW' else 'info'
        await self.log('decide', title, detail, severity)
    
    async def log_reason(self, title: str, detail: str) -> None:
        """Log a reasoning event."""
        await self.log('reason', title, detail)
