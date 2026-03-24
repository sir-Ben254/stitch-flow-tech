"""
Wallet API routes
"""
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.security import get_current_user
from app.schemas.schemas import WalletTopup, WalletBalance, TransactionResponse
from app.services import database, daraja

router = APIRouter(prefix="/wallet", tags=["Wallet"])


class WalletTopupResponse(BaseModel):
    success: bool
    checkout_request_id: str
    message: str


@router.get("/balance", response_model=WalletBalance)
async def get_balance(current_user: dict = Depends(get_current_user)):
    """Get wallet balance"""
    wallet = database.get_wallet(current_user["id"])
    
    if not wallet:
        # Create wallet if doesn't exist
        wallet = database.create_wallet(current_user["id"])
    
    return {
        "user_id": current_user["id"],
        "balance": wallet["balance"],
        "currency": wallet.get("currency", "KES")
    }


@router.post("/topup", response_model=WalletTopupResponse)
async def topup_wallet(
    request: WalletTopup,
    current_user: dict = Depends(get_current_user)
):
    """Top up wallet using STK Push"""
    
    # Create transaction record
    transaction_id = str(uuid.uuid4())
    transaction_data = {
        "id": transaction_id,
        "user_id": current_user["id"],
        "amount": request.amount,
        "type": "topup",
        "status": "pending",
        "description": f"Wallet top-up - KES {request.amount}",
        "reference": None
    }
    
    database.create_transaction(transaction_data)
    
    # Initiate STK Push
    try:
        result = daraja.daraja_service.initiate_stk_push(
            phone=request.phone,
            amount=request.amount,
            reference=f"WALLET:{transaction_id}",
            description=f"StitchFlow Wallet Top-up - KES {request.amount}"
        )
        
        if result.get("success"):
            # Update transaction with checkout ID
            database.get_supabase_admin().table("transactions").update({
                "reference": result.get("checkout_request_id"),
                "status": "processing"
            }).eq("id", transaction_id).execute()
            
            return {
                "success": True,
                "checkout_request_id": result.get("checkout_request_id"),
                "message": "Top-up initiated. Please check your phone."
            }
        else:
            # Update transaction status
            database.get_supabase_admin().table("transactions").update({
                "status": "failed",
                "description": f"Top-up failed: {result.get('error')}"
            }).eq("id", transaction_id).execute()
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Top-up initiation failed")
            )
    
    except Exception as e:
        database.get_supabase_admin().table("transactions").update({
            "status": "failed",
            "description": f"Top-up failed: {str(e)}"
        }).eq("id", transaction_id).execute()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment service unavailable"
        )


@router.post("/pay/{job_id}")
async def pay_with_wallet(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Pay for job using wallet balance"""
    
    # Get job
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
    
    if job.get("payment_status") == "paid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job already paid"
        )
    
    # Get wallet
    wallet = database.get_wallet(current_user["id"])
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wallet not found"
        )
    
    # Check balance
    if wallet["balance"] < job["price"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance"
        )
    
    # Deduct from wallet
    try:
        database.update_wallet_balance(current_user["id"], job["price"], "deduct")
        
        # Create payment record
        payment_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "job_id": job_id,
            "amount": job["price"],
            "phone": wallet.get("phone", ""),
            "status": "completed",
            "transaction_id": f"WALLET-{job_id}",
            "checkout_request_id": None
        }
        database.create_payment(payment_data)
        
        # Update job payment status
        database.get_supabase_admin().table("jobs").update({
            "payment_status": "paid"
        }).eq("id", job_id).execute()
        
        # Create transaction record
        transaction_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "amount": -job["price"],
            "type": "payment",
            "status": "completed",
            "description": f"Payment for {job['filename']}",
            "reference": job_id
        }
        database.create_transaction(transaction_data)
        
        return {
            "success": True,
            "message": "Payment successful",
            "new_balance": wallet["balance"] - job["price"]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment failed: {str(e)}"
        )


@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get transaction history"""
    transactions = database.get_transactions(current_user["id"], limit)
    return transactions
