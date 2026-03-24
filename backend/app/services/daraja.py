"""
Safaricom Daraja API service for STK Push payments
"""
import base64
import hashlib
import json
import requests
from datetime import datetime
from typing import Optional, Dict
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class DarajaService:
    """Safaricom Daraja API Service"""
    
    def __init__(self):
        self.consumer_key = settings.DARAJA_CONSUMER_KEY
        self.consumer_secret = settings.DARAJA_CONSUMER_SECRET
        self.shortcode = settings.DARAJA_SHORTCODE
        self.callback_url = settings.DARAJA_CALLBACK_URL
        self.passkey = settings.DARAJA_PASSKEY
        self.environment = settings.DARAJA_ENVIRONMENT
        
        self.base_url = "https://sandbox.safaricom.co.ke" if self.environment == "sandbox" else "https://api.safaricom.co.ke"
    
    def _get_access_token(self) -> str:
        """Get OAuth access token"""
        auth = base64.b64encode(f"{self.consumer_key}:{self.consumer_secret}".encode()).decode()
        
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            raise Exception(f"Failed to get access token: {response.text}")
    
    def _generate_password(self) -> str:
        """Generate password for STK Push"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password_string = f"{self.shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(password_string.encode()).decode()
    
    def initiate_stk_push(
        self,
        phone: str,
        amount: float,
        reference: str,
        description: str = "StitchFlow Payment"
    ) -> Dict:
        """
        Initiate STK Push payment
        Returns the checkout request ID and response
        """
        access_token = self._get_access_token()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = self._generate_password()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerBuyGoodsOnline",
            "Amount": int(amount),
            "PartyA": phone,
            "PartyB": self.shortcode,
            "PhoneNumber": phone,
            "CallBackURL": self.callback_url,
            "AccountReference": reference,
            "TransactionDesc": description
        }
        
        response = requests.post(
            f"{self.base_url}/mpesa/stkpush/v1/processrequest",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        result = response.json()
        
        logger.info(f"STK Push initiated: {result}")
        
        if response.status_code == 200 and result.get("ResponseCode") == "0":
            return {
                "success": True,
                "checkout_request_id": result.get("CheckoutRequestID"),
                "merchant_request_id": result.get("MerchantRequestID"),
                "response_code": result.get("ResponseCode"),
                "response_description": result.get("ResponseDescription"),
                "customer_message": result.get("CustomerMessage")
            }
        else:
            return {
                "success": False,
                "error": result.get("errorMessage", "Payment initiation failed"),
                "response_code": result.get("ResponseCode")
            }
    
    def query_stk_status(self, checkout_request_id: str) -> Dict:
        """Query STK Push status"""
        access_token = self._get_access_token()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = self._generate_password()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id
        }
        
        response = requests.post(
            f"{self.base_url}/mpesa/stkpushquery/v1/query",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        return response.json()
    
    def verify_payment(self, checkout_request_id: str, max_retries: int = 3) -> Dict:
        """
        Verify payment by querying status
        Implements retry logic for failed queries
        """
        for attempt in range(max_retries):
            try:
                result = self.query_stk_status(checkout_request_id)
                
                if result.get("ResponseCode") == "0":
                    # Payment successful
                    return {
                        "verified": True,
                        "status": "success",
                        "result_code": result.get("ResultCode"),
                        "result_desc": result.get("ResultDesc")
                    }
                elif result.get("ResultCode") == "1032":
                    # Cancelled
                    return {
                        "verified": False,
                        "status": "cancelled",
                        "result_code": result.get("ResultCode"),
                        "result_desc": result.get("ResultDesc")
                    }
                elif attempt < max_retries - 1:
                    # Retry after delay
                    import time
                    time.sleep(2 ** attempt)
                    continue
                else:
                    return {
                        "verified": False,
                        "status": "pending",
                        "result_code": result.get("ResultCode"),
                        "result_desc": result.get("ResultDesc")
                    }
            except Exception as e:
                logger.error(f"Payment verification error: {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)
                    continue
                else:
                    return {
                        "verified": False,
                        "status": "error",
                        "error": str(e)
                    }
        
        return {
            "verified": False,
            "status": "timeout"
        }


# Singleton instance
daraja_service = DarajaService()
