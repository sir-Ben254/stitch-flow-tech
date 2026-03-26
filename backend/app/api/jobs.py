"""
Jobs API routes for image upload and processing
"""
import uuid
import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form

from app.core.config import settings
from app.core.security import get_current_user
from app.schemas.schemas import JobCreate, JobResponse, JobStatus, UploadResponse
from app.services import database, storage

router = APIRouter(prefix="/jobs", tags=["Jobs"])
PRICING = {
    "simple": 100.0,   # KES
    "complex": 250.0,  # KES
    "auto": 150.0       # KES
}


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_image(
    file: UploadFile = File(...),
    complexity: str = Form("auto"),
    captcha_token: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload image for processing"""
    
    # Validate complexity
    if complexity not in ["auto", "simple", "complex"]:
        complexity = "auto"
    
    # Validate file type
    if file.content_type not in settings.ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed"
        )
    
    # Validate file size
    file_size = 0
    content = b""
    chunk_size = 1024 * 1024  # 1MB chunks
    
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        file_size += len(chunk)
        content += chunk
        
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large"
            )
    
    # Create job record
    job_id = str(uuid.uuid4())
    
    job_data = {
        "id": job_id,
        "user_id": current_user["id"],
        "filename": file.filename,
        "status": "pending",
        "complexity": complexity,
        "mime_type": file.content_type,
        "file_size": file_size,
        "price": PRICING.get(complexity, 150.0),
        "original_url": None,
        "payment_status": "unpaid"
    }
    
    database.create_job(job_data)
    
    # Upload file to storage
    file_url, file_path = storage.storage_service.upload_user_file(
        content,
        file.filename,
        current_user["id"]
    )
    
    # Update job with file URL
    database.get_supabase_admin().table("jobs").update({
        "original_url": file_url,
        "file_path": file_path
    }).eq("id", job_id).execute()
    
    # Queue processing task
    # Check if we're running with Celery or as standalone
    if os.getenv("CELERY_BROKER_URL"):
        from worker.tasks import process_image
        process_image.delay(job_id, file_url, complexity)
    else:
        # Fallback: call processing directly (for testing/development)
        from worker.tasks.processing import process_image
        process_image(job_id, image_url=file_url, complexity=complexity)
    
    return {
        "upload_url": file_url,
        "fields": {},
        "job_id": job_id
    }


@router.get("/status/{job_id}", response_model=JobStatus)
async def get_job_status(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get job status"""
    job = database.get_job(job_id)
    
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
    
    # Build output URLs
    output_urls = None
    if job["status"] == "completed":
        output_urls = {}
        if job.get("output_dst_url"):
            output_urls["dst"] = job["output_dst_url"]
        if job.get("output_svg_url"):
            output_urls["svg"] = job["output_svg_url"]
        if job.get("output_json_url"):
            output_urls["json"] = job["output_json_url"]
    
    # Calculate progress
    progress = 0
    if job["status"] == "queued":
        progress = 10
    elif job["status"] == "processing":
        progress = 50
    elif job["status"] == "completed":
        progress = 100
    
    return {
        "id": job["id"],
        "status": job["status"],
        "progress": progress,
        "message": None,
        "output_urls": output_urls
    }


@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """List user jobs"""
    jobs = database.get_user_jobs(current_user["id"], limit)
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get job details"""
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
    
    return job


@router.get("/{job_id}/download/{file_type}")
async def download_file(
    job_id: str,
    file_type: str,
    current_user: dict = Depends(get_current_user)
):
    """Download output file"""
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
    
    if job["status"] != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job not completed"
        )
    
    # Get file URL based on type
    file_url = None
    if file_type == "dst":
        file_url = job.get("output_dst_url")
    elif file_type == "svg":
        file_url = job.get("output_svg_url")
    elif file_type == "json":
        file_url = job.get("output_json_url")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type"
        )
    
    if not file_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Redirect to signed URL
    return {"download_url": file_url}
