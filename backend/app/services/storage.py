"""
Storage service for file uploads and management
"""
import uuid
import hashlib
from typing import Optional, Tuple
from supabase import create_client, SupabaseClient

from app.core.config import settings
from app.core.security import get_supabase_admin


class StorageService:
    """File storage service using Supabase Storage"""
    
    def __init__(self):
        self.supabase: SupabaseClient = get_supabase_admin()
        self.upload_bucket = settings.UPLOAD_BUCKET
        self.output_bucket = settings.OUTPUT_BUCKET
    
    def _get_file_hash(self, content: bytes) -> str:
        """Generate SHA256 hash of file content"""
        return hashlib.sha256(content).hexdigest()
    
    def upload_file(
        self,
        content: bytes,
        filename: str,
        bucket: str,
        folder: str = "uploads"
    ) -> Tuple[str, str]:
        """
        Upload file to Supabase Storage
        Returns: (file_url, file_path)
        """
        file_hash = self._get_file_hash(content)
        ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
        unique_filename = f"{file_hash[:16]}_{uuid.uuid4().hex[:8]}.{ext}"
        file_path = f"{folder}/{unique_filename}"
        
        self.supabase.storage.from_(bucket).upload(
            file_path,
            content,
            {"content_type": self._get_mime_type(ext)}
        )
        
        # Get public URL
        file_url = self.supabase.storage.from_(bucket).get_public_url(file_path)
        
        return file_url, file_path
    
    def upload_user_file(
        self,
        content: bytes,
        filename: str,
        user_id: str
    ) -> Tuple[str, str]:
        """Upload user file to uploads bucket"""
        return self.upload_file(content, filename, self.upload_bucket, f"users/{user_id}")
    
    def upload_output_file(
        self,
        content: bytes,
        filename: str,
        job_id: str
    ) -> Tuple[str, str]:
        """Upload output file to outputs bucket"""
        return self.upload_file(content, filename, self.output_bucket, f"jobs/{job_id}")
    
    def delete_file(self, bucket: str, file_path: str) -> bool:
        """Delete file from storage"""
        try:
            self.supabase.storage.from_(bucket).remove([file_path])
            return True
        except Exception:
            return False
    
    def get_signed_url(self, bucket: str, file_path: str, expires_in: int = 3600) -> str:
        """Get signed URL for file download"""
        response = self.supabase.storage.from_(bucket).create_signed_url(file_path, expires_in)
        return response["signedURL"]
    
    def get_upload_signed_url(self, file_path: str, expires_in: int = 3600) -> dict:
        """Get signed URL for uploading"""
        response = self.supabase.storage.from_(self.upload_bucket).create_signed_upload_url(file_path)
        return {
            "url": response["signedURL"],
            "path": file_path
        }
    
    def _get_mime_type(self, ext: str) -> str:
        """Get MIME type from extension"""
        mime_types = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "webp": "image/webp",
            "bmp": "image/bmp",
            "svg": "image/svg+xml",
            "dst": "application/octet-stream",
            "json": "application/json"
        }
        return mime_types.get(ext.lower(), "application/octet-stream")


# Singleton instance
storage_service = StorageService()
