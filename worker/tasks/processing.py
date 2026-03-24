"""
Celery tasks for image processing
"""
import os
import io
import json
import logging
import requests
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import cv2

from celery import Celery
from supabase import create_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

app = Celery("stitchflow_worker", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max
    task_soft_time_limit=540,  # 9 minutes soft limit
)


def get_supabase():
    """Get Supabase client"""
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY", "")
    return create_client(supabase_url, supabase_key)


def update_job_status(job_id: str, status: str, progress: int = 0, output_urls: dict = None):
    """Update job status in database"""
    supabase = get_supabase()
    
    update_data = {
        "status": status,
        "progress": progress
    }
    
    if output_urls:
        if "dst" in output_urls:
            update_data["output_dst_url"] = output_urls["dst"]
        if "svg" in output_urls:
            update_data["output_svg_url"] = output_urls["svg"]
        if "json" in output_urls:
            update_data["output_json_url"] = output_urls["json"]
    
    supabase.table("jobs").update(update_data).eq("id", job_id).execute()


def download_image(url: str) -> bytes:
    """Download image from URL"""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.content


def upload_output(content: bytes, filename: str, job_id: str) -> str:
    """Upload output file to storage"""
    supabase = get_supabase()
    bucket = os.getenv("OUTPUT_BUCKET", "outputs")
    
    ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
    file_path = f"jobs/{job_id}/{filename}"
    
    supabase.storage.from_(bucket).upload(file_path, content)
    
    return supabase.storage.from_(bucket).get_public_url(file_path)


def clean_image(image: Image.Image) -> Image.Image:
    """Clean and enhance image for embroidery"""
    # Convert to RGB if needed
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    # Resize if too large
    max_size = 2000
    if image.width > max_size or image.height > max_size:
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    
    # Convert to numpy for processing
    img_array = np.array(image)
    
    # Apply denoising
    img_array = cv2.fastNlMeansDenoisingColored(img_array, None, 10, 10, 7, 21)
    
    # Increase contrast
    lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge([l, a, b])
    img_array = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    
    # Convert back to PIL
    image = Image.fromarray(img_array)
    
    # Apply sharpening
    image = image.filter(ImageFilter.SHARPEN)
    
    return image


def detect_complexity(image: Image.Image) -> str:
    """Detect image complexity"""
    # Convert to grayscale
    gray = image.convert("L")
    gray_array = np.array(gray)
    
    # Calculate edge density
    edges = cv2.Canny(gray_array, 50, 150)
    edge_density = np.sum(edges > 0) / edges.size
    
    # Calculate color variance
    img_array = np.array(image)
    color_variance = np.var(img_array)
    
    # Determine complexity
    if edge_density < 0.1 and color_variance < 2000:
        return "simple"
    elif edge_density > 0.3 or color_variance > 8000:
        return "complex"
    else:
        return "auto"


def vectorize_image(image: Image.Image) -> list:
    """Convert image to vector paths (simplified)"""
    # Convert to grayscale
    gray = image.convert("L")
    
    # Threshold
    threshold = 128
    binary = gray.point(lambda x: 255 if x > threshold else 0)
    
    # Simple edge detection for path generation
    edges = cv2.Canny(np.array(binary), 50, 150)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    paths = []
    for contour in contours:
        if len(contour) > 10:  # Filter small contours
            points = [(int(p[0][0]), int(p[0][1])) for p in contour]
            paths.append(points)
    
    return paths


def generate_svg(image: Image.Image, paths: list) -> str:
    """Generate SVG from paths"""
    width, height = image.size
    
    svg_parts = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'  <defs>',
        f'    <style>',
        f'      .stitch {{ fill: none; stroke: #000; stroke-width: 1; stroke-linecap: round; }}',
        f'    </style>',
        f'  </defs>',
    ]
    
    # Add paths
    for i, path in enumerate(paths):
        if len(path) > 2:
            path_str = " ".join([f"{x},{y}" for x, y in path])
            svg_parts.append(f'  <path class="stitch" d="M {path_str}" data-color="black" data-stitch-type="fill"/>')
    
    svg_parts.append('</svg>')
    
    return "\n".join(svg_parts)


def generate_wilcom_json(image: Image.Image, paths: list) -> dict:
    """Generate Wilcom-compatible JSON structure"""
    width, height = image.size
    
    # Extract colors from image
    img_array = np.array(image)
    colors = []
    for i in range(min(10, len(np.unique(img_array.reshape(-1, img_array.shape[2]), axis=0)))):
        unique_colors = np.unique(img_array.reshape(-1, img_array.shape[2]), axis=0)
        if i < len(unique_colors):
            colors.append({
                "name": f"Color_{i+1}",
                "hex": f"#{unique_colors[i][0]:02x}{unique_colors[i][1]:02x}{unique_colors[i][2]:02x}",
                "rgb": unique_colors[i].tolist()
            })
    
    # Create layers
    layers = []
    for i, path in enumerate(paths[:20]):  # Limit to 20 layers
        if len(path) > 2:
            layers.append({
                "id": i + 1,
                "name": f"Layer_{i+1}",
                "color": colors[i % len(colors)] if colors else {"hex": "#000000"},
                "stitch_type": "fill",
                "path": path[:100]  # Limit path points
            })
    
    return {
        "version": "1.0",
        "application": "StitchFlow",
        "dimensions": {
            "width": width,
            "height": height,
            "units": "pixels"
        },
        "colors": colors,
        "layers": layers,
        "metadata": {
            "created_by": "StitchFlow",
            "description": "Embroidery design generated from image"
        }
    }


def generate_dst(image: Image.Image) -> str:
    """Generate DST embroidery file (simplified)"""
    width, height = image.size
    
    # DST header
    dst_lines = [
        "LA:StitchFlow Design",
        "ST:1000",  # Stitch count (simplified)
        "CO:1",     # Color count
        f"XW:{width}",
        f"YW:{height}",
    ]
    
    # Convert to grayscale and get stitch points
    gray = image.convert("L")
    gray_array = np.array(gray)
    
    # Simple stitch pattern generation
    step = 5  # Every 5 pixels
    for y in range(0, height, step):
        for x in range(0, width, step):
            if gray_array[y, x] < 128:  # Dark pixels
                dst_lines.append(f"X:{x}Y:{y}")
    
    dst_lines.append("NE:0")  # End
    
    return "\n".join(dst_lines)


@app.task(bind=True, name="process_image")
def process_image(self, job_id: str, image_url: str, complexity: str):
    """
    Process image for embroidery
    
    Steps:
    1. Download image
    2. Clean and enhance
    3. Detect complexity
    4. Generate output files
    5. Upload results
    """
    try:
        logger.info(f"Starting processing for job {job_id}")
        
        # Update status to processing
        update_job_status(job_id, "processing", 10)
        
        # Download image
        image_content = download_image(image_url)
        image = Image.open(io.BytesIO(image_content))
        
        # Clean image
        update_job_status(job_id, "processing", 30)
        cleaned_image = clean_image(image)
        
        # Detect complexity if auto
        if complexity == "auto":
            complexity = detect_complexity(cleaned_image)
            logger.info(f"Detected complexity: {complexity}")
        
        # Vectorize
        update_job_status(job_id, "processing", 50)
        paths = vectorize_image(cleaned_image)
        
        # Generate outputs
        output_urls = {}
        
        if complexity == "simple":
            # Generate DST
            update_job_status(job_id, "processing", 70)
            dst_content = generate_dst(cleaned_image)
            dst_url = upload_output(
                dst_content.encode(),
                "output.dst",
                job_id
            )
            output_urls["dst"] = dst_url
        
        # Always generate SVG for complex designs
        if complexity == "complex" or complexity == "auto":
            # Generate SVG
            update_job_status(job_id, "processing", 80)
            svg_content = generate_svg(cleaned_image, paths)
            svg_url = upload_output(
                svg_content.encode(),
                "output.svg",
                job_id
            )
            output_urls["svg"] = svg_url
            
            # Generate Wilcom JSON
            wilcom_content = generate_wilcom_json(cleaned_image, paths)
            json_url = upload_output(
                json.dumps(wilcom_content, indent=2).encode(),
                "output.json",
                job_id
            )
            output_urls["json"] = json_url
        
        # Update status to completed
        update_job_status(job_id, "completed", 100, output_urls)
        
        logger.info(f"Completed processing for job {job_id}")
        
        return {
            "status": "completed",
            "output_urls": output_urls
        }
    
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        update_job_status(job_id, "failed", 0)
        raise


@app.task(name="cleanup_old_jobs")
def cleanup_old_jobs(days: int = 30):
    """Clean up old jobs and temporary files"""
    logger.info(f"Cleaning up jobs older than {days} days")
    # Implementation would clean up old files from storage
    return {"deleted": 0}
