"""
File validation and malware scanning service
"""
importmagic
import hashlib
from typing import Tuple, Optional
from PIL import Image
import io
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class FileValidator:
    """File validation and malware scanning"""
    
    def __init__(self):
        self.allowed_mime_types = settings.ALLOWED_MIME_TYPES
        self.max_file_size = settings.MAX_FILE_SIZE
    
    def validate_image(self, content: bytes, filename: str) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded image file
        
        Args:
            content: File content as bytes
            filename: Original filename
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file size
        if len(content) > self.max_file_size:
            return False, f"File too large. Maximum size is {self.max_file_size / 1024 / 1024}MB"
        
        # Check file extension
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        allowed_ext = ["png", "jpg", "jpeg", "webp", "bmp"]
        
        if ext not in allowed_ext:
            return False, f"File extension not allowed. Allowed: {', '.join(allowed_ext)}"
        
        # Validate image integrity
        try:
            image = Image.open(io.BytesIO(content))
            image.verify()
            
            # Re-open after verify (verify() closes the file)
            image = Image.open(io.BytesIO(content))
            
            # Check if it's actually an image
            if image.format not in ['PNG', 'JPEG', 'JPG', 'WEBP', 'BMP']:
                return False, f"Invalid image format: {image.format}"
            
            # Check dimensions
            if image.width < 10 or image.height < 10:
                return False, "Image too small. Minimum 10x10 pixels"
            
            if image.width > 10000 or image.height > 10000:
                return False, "Image too large. Maximum 10000x10000 pixels"
            
            return True, None
        
        except Exception as e:
            logger.error(f"Image validation error: {e}")
            return False, f"Invalid image file: {str(e)}"
    
    def scan_for_malware(self, content: bytes) -> Tuple[bool, Optional[str]]:
        """
        Scan file content for malware patterns
        
        Note: This is a basic implementation. For production,
        consider integrating with ClamAV or similar.
        
        Args:
            content: File content as bytes
            
        Returns:
            Tuple of (is_clean, threat_type)
        """
        # Check for common malware signatures in file headers
        # These are basic patterns - real malware scanning needs ClamAV
        
        # Check for executable headers (MZ = DOS/Windows exe)
        if content[:2] == b'MZ':
            return False, "Executable content detected"
        
        # Check for script injection patterns
        content_str = content[:10000].decode('utf-8', errors='ignore')
        dangerous_patterns = [
            '<script',
            '<?php',
            '<%',
            'eval(',
            'base64_decode',
            'shell_exec',
            'system(',
        ]
        
        for pattern in dangerous_patterns:
            if pattern.lower() in content_str.lower():
                return False, "Suspicious content pattern detected"
        
        # Calculate file hash for logging
        file_hash = hashlib.sha256(content).hexdigest()
        logger.info(f"File hash: {file_hash}")
        
        return True, None
    
    def get_file_hash(self, content: bytes) -> str:
        """Get SHA256 hash of file content"""
        return hashlib.sha256(content).hexdigest()


# Singleton instance
file_validator = FileValidator()
