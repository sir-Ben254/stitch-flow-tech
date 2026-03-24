"""
Database service for Supabase operations
"""
from typing import Optional, List
from supabase import create_client, SupabaseClient
from datetime import datetime

from app.core.config import settings
from app.core.security import get_supabase_admin


def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email"""
    supabase = get_supabase_admin()
    response = supabase.table("users").select("*").eq("email", email).execute()
    return response.data[0] if response.data else None


def get_user_by_id(user_id: str) -> Optional[dict]:
    """Get user by ID"""
    supabase = get_supabase_admin()
    response = supabase.table("users").select("*").eq("id", user_id).execute()
    return response.data[0] if response.data else None


def create_user(user_data: dict) -> dict:
    """Create new user"""
    supabase = get_supabase_admin()
    response = supabase.table("users").insert(user_data).execute()
    return response.data[0]


def get_wallet(user_id: str) -> Optional[dict]:
    """Get user wallet"""
    supabase = get_supabase_admin()
    response = supabase.table("wallets").select("*").eq("user_id", user_id).execute()
    return response.data[0] if response.data else None


def create_wallet(user_id: str) -> dict:
    """Create user wallet"""
    supabase = get_supabase_admin()
    response = supabase.table("wallets").insert({
        "user_id": user_id,
        "balance": 0.0,
        "currency": "KES"
    }).execute()
    return response.data[0]


def update_wallet_balance(user_id: str, amount: float, operation: str = "add") -> dict:
    """Update wallet balance"""
    supabase = get_supabase_admin()
    
    if operation == "add":
        response = supabase.table("wallets").update(
            {"balance": supabase.rpc("add_wallet_balance", {"p_user_id": user_id, "p_amount": amount})}
        ).eq("user_id", user_id).execute()
    else:
        response = supabase.table("wallets").update(
            {"balance": supabase.rpc("deduct_wallet_balance", {"p_user_id": user_id, "p_amount": amount})}
        ).eq("user_id", user_id).execute()
    
    return response.data[0]


def create_transaction(transaction_data: dict) -> dict:
    """Create transaction record"""
    supabase = get_supabase_admin()
    response = supabase.table("transactions").insert(transaction_data).execute()
    return response.data[0]


def get_transactions(user_id: str, limit: int = 50) -> List[dict]:
    """Get user transactions"""
    supabase = get_supabase_admin()
    response = supabase.table("transactions").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
    return response.data


def create_job(job_data: dict) -> dict:
    """Create job record"""
    supabase = get_supabase_admin()
    response = supabase.table("jobs").insert(job_data).execute()
    return response.data[0]


def get_job(job_id: str) -> Optional[dict]:
    """Get job by ID"""
    supabase = get_supabase_admin()
    response = supabase.table("jobs").select("*").eq("id", job_id).execute()
    return response.data[0] if response.data else None


def get_user_jobs(user_id: str, limit: int = 50) -> List[dict]:
    """Get user jobs"""
    supabase = get_supabase_admin()
    response = supabase.table("jobs").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
    return response.data


def update_job_status(job_id: str, status: str, output_urls: Optional[dict] = None) -> dict:
    """Update job status"""
    supabase = get_supabase_admin()
    update_data = {
        "status": status,
        "updated_at": datetime.utcnow().isoformat()
    }
    
    if status == "completed":
        update_data["completed_at"] = datetime.utcnow().isoformat()
    
    if output_urls:
        if "dst" in output_urls:
            update_data["output_dst_url"] = output_urls["dst"]
        if "svg" in output_urls:
            update_data["output_svg_url"] = output_urls["svg"]
        if "json" in output_urls:
            update_data["output_json_url"] = output_urls["json"]
    
    response = supabase.table("jobs").update(update_data).eq("id", job_id).execute()
    return response.data[0]


def create_payment(payment_data: dict) -> dict:
    """Create payment record"""
    supabase = get_supabase_admin()
    response = supabase.table("payments").insert(payment_data).execute()
    return response.data[0]


def get_payment_by_job(job_id: str) -> Optional[dict]:
    """Get payment by job ID"""
    supabase = get_supabase_admin()
    response = supabase.table("payments").select("*").eq("job_id", job_id).execute()
    return response.data[0] if response.data else None


def update_payment_status(payment_id: str, status: str, transaction_id: str = None) -> dict:
    """Update payment status"""
    supabase = get_supabase_admin()
    update_data = {"status": status}
    if transaction_id:
        update_data["transaction_id"] = transaction_id
    
    response = supabase.table("payments").update(update_data).eq("id", payment_id).execute()
    return response.data[0]


def get_payment_by_transaction_id(transaction_id: str) -> Optional[dict]:
    """Get payment by transaction ID"""
    supabase = get_supabase_admin()
    response = supabase.table("payments").select("*").eq("transaction_id", transaction_id).execute()
    return response.data[0] if response.data else None
