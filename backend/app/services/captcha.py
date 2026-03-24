"""
CAPTCHA validation service using Cloudflare Turnstile
"""
import requests
from typing import Optional, Dict
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class CaptchaService:
    """Cloudflare Turnstile CAPTCHA validation"""
    
    def __init__(self):
        self.verify_url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
        self.secret_key = settings.TURNSTILE_SECRET_KEY if hasattr(settings, 'TURNSTILE_SECRET_KEY') else ""
    
    def verify(self, token: str, remote_ip: Optional[str] = None) -> Dict:
        """
        Verify Turnstile token
        
        Args:
            token: The Turnstile token from the client
            remote_ip: The client's IP address
            
        Returns:
            Dict with success status and error details
        """
        if not self.secret_key:
            # If no secret key configured, allow for development
            logger.warning("CAPTCHA secret not configured - skipping validation")
            return {
                "success": True,
                "score": 1.0,
                "action": "login"
            }
        
        payload = {
            "secret": self.secret_key,
            "response": token,
        }
        
        if remote_ip:
            payload["remoteip"] = remote_ip
        
        try:
            response = requests.post(self.verify_url, data=payload, timeout=10)
            result = response.json()
            
            if result.get("success"):
                return {
                    "success": True,
                    "score": result.get("score", 1.0),
                    "action": result.get("action", ""),
                    "challenge_ts": result.get("challenge_ts")
                }
            else:
                logger.warning(f"CAPTCHA verification failed: {result}")
                return {
                    "success": False,
                    "error_codes": result.get("error-codes", [])
                }
        
        except Exception as e:
            logger.error(f"CAPTCHA verification error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
captcha_service = CaptchaService()
