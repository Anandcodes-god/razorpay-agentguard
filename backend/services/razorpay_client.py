import logging
from typing import Dict, Any, Optional
import razorpay
from backend.config import get_settings

logger = logging.getLogger(__name__)

class RazorpayService:
    """Service wrapper for Razorpay API operations."""
    
    def __init__(self):
        settings = get_settings()
        self._client = razorpay.Client(
            auth=(settings.razorpay_key_id, settings.razorpay_key_secret)
        )
    
    def create_order(self, amount: int, currency: str = 'INR', 
                     notes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a Razorpay order. Amount is in paise.
        
        Args:
            amount: Order amount in paise.
            currency: Currency code (default: INR).
            notes: Optional metadata dictionary.
            
        Returns:
            Dict containing the order details or error information.
        """
        try:
            data = {
                "amount": amount,
                "currency": currency,
                "notes": notes or {}
            }
            order = self._client.order.create(data=data)
            return order
        except Exception as e:
            logger.error(f"Failed to create Razorpay order: {e}")
            return {"error": str(e)}
    
    def fetch_payment(self, payment_id: str) -> Dict[str, Any]:
        """Fetch payment details by ID."""
        try:
            payment = self._client.payment.fetch(payment_id)
            return payment
        except Exception as e:
            logger.error(f"Failed to fetch Razorpay payment {payment_id}: {e}")
            return {"error": str(e)}
    
    def fetch_order(self, order_id: str) -> Dict[str, Any]:
        """Fetch order details by ID."""
        try:
            order = self._client.order.fetch(order_id)
            return order
        except Exception as e:
            logger.error(f"Failed to fetch Razorpay order {order_id}: {e}")
            return {"error": str(e)}
    
    def create_customer(self, name: str, email: str, contact: str) -> Dict[str, Any]:
        """Create a Razorpay customer."""
        try:
            data = {
                "name": name,
                "email": email,
                "contact": contact
            }
            customer = self._client.customer.create(data=data)
            return customer
        except Exception as e:
            logger.error(f"Failed to create Razorpay customer: {e}")
            return {"error": str(e)}

def get_razorpay_service() -> RazorpayService:
    """Factory function for RazorpayService."""
    return RazorpayService()
