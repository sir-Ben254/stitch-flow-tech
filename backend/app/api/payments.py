"""
Payment API routes
"""
import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.security import get_current_user
from app.schemas.schemas import PaymentRequest, PaymentStatus, PaymentCallback
from app.services import database, daraja

router = APIRouter(prefix="/payments", tags=["Payments"])


class PaymentInitResponse(BaseModel):
    success: bool
    checkout_request_id: str
    message: str


class PaymentJobRequest(BaseModel):
    job_id: str


@router.post("/stkpush", response_model=PaymentInitResponse)
async def initiate_stk_push(
    request: PaymentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Initiate STK Push payment for a job"""
    
    # Get job
    job = database.get_job(request.job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check ownership
    if job["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Check if already paid
    if job.get("payment_status") == "paid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job already paid"
        )
    
    # Create payment record
    payment_id = str(uuid.uuid4())
    payment_data = {
        "id": payment_id,
        "user_id": current_user["id"],
        "job_id": job["id"],
        "amount": job["price"],
        "phone": request.phone,
        "status": "pending",
        "checkout_request_id": None,
        "transaction_id": None
    }
    
    database.create_payment(payment_data)
    
    # Initiate STK Push
    try:
        result = daraja.daraja_service.initiate_stk_push(
            phone=request.phone,
            amount=job["price"],
            reference=job["id"],
            description=f"StitchFlow - {job['filename']}"
        )
        
        if result.get("success"):
            # Update payment with checkout ID
            database.get_supabase_admin().table("payments").update({
                "checkout_request_id": result.get("checkout_request_id")
            }).eq("id", payment_id).execute()
            
            return {
                "success": True,
                "checkout_request_id": result.get("checkout_request_id"),
                "message": "Payment initiated. Please check your phone."
            }
        else:
            # Update payment status
            database.get_supabase_admin().table("payments").update({
                "status": "failed",
                "error_message": result.get("error")
            }).eq("id", payment_id).execute()
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Payment initiation failed")
            )
    
    except Exception as e:
        database.get_supabase_admin().table("payments").update({
            "status": "failed",
            "error_message": str(e)
        }).eq("id", payment_id).execute()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment service unavailable"
        )


@router.post("/callback")
async def payment_callback(callback: PaymentCallback):
    """Handle payment callback from Safaricom"""
    
    # Log callback
    print(f"Payment callback received: {callback}")
    
    # Find payment by account reference (job_id)
    payment = database.get_payment_by_job(callback.bill_ref)
    
    if not payment:
        # Try to find by transaction ID
        payment = database.get_payment_by_transaction_id(callback.trans_id)
    
    if not payment:
        return {"status": "ignored", "message": "Payment not found"}
    
    # Update payment status
    if callback.trans_amount > 0:
        database.update_payment_status(payment["id"], "completed", callback.trans_id)
        
        # Update job payment status
        database.get_supabase_admin().table("jobs").update({
            "payment_status": "paid"
        }).eq("id", payment["job_id"]).execute()
    else:
        database.update_payment_status(payment["id"], "failed", callback.trans_id)
    
    return {"status": "success"}


@router.get("/status/{job_id}", response_model=PaymentStatus)
async def get_payment_status(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get payment status for a job"""
    
    job = database.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    payment = database.get_payment_by_job(job_id)
    
    if not payment:
        return {
            "job_id": job_id,
            "status": "unpaid",
            "transaction_id": None,
            "amount": job["price"],
            "phone": "",
            "created_at": job["created_at"]
        }
    
    return {
        "job_id": payment["job_id"],
        "status": payment["status"],
        "transaction_id": payment.get("transaction_id"),
        "amount": payment["amount"],
        "phone": payment["phone"],
        "created_at": payment["created_at"]
    }


@router.post("/verify/{checkout_request_id}")
async def verify_payment(
    checkout_request_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Verify payment status"""
    
    result = daraja.daraja_service.verify_payment(checkout_request_id)
    
    return result
