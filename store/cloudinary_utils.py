import os
import uuid
from django.conf import settings
from django.core.files.storage import FileSystemStorage

def upload_product_image_to_cloudinary(uploaded_file, product_id):
    """
    Uploads a confirmed product image file to Cloudinary if CLOUDINARY_URL is configured.
    If CLOUDINARY_URL is not set or Cloudinary upload encounters an exception,
    gracefully saves the file locally to /media/products/ and returns the local media URL.
    
    CRITICAL WORKFLOW REQUIREMENT:
    This function is ONLY called AFTER all product form fields have passed validation in Django,
    ensuring no unwanted, draft, or incomplete images are uploaded to Cloudinary storage.
    """
    cloudinary_url = os.environ.get('CLOUDINARY_URL', '').strip()
    
    if cloudinary_url:
        try:
            import cloudinary
            import cloudinary.uploader
            
            # Ensure config is initialized with configured CLOUDINARY_URL
            cloudinary.config(cloudinary_url=cloudinary_url)
            
            # Upload file directly to Cloudinary folder 'ecommerce_products'
            public_id = f"product_{product_id}_{uuid.uuid4().hex[:6]}"
            result = cloudinary.uploader.upload(
                uploaded_file,
                folder="ecommerce_products",
                public_id=public_id,
                overwrite=True,
                resource_type="image"
            )
            
            secure_url = result.get('secure_url') or result.get('url')
            if secure_url:
                print(f"[Cloudinary] Successfully uploaded product #{product_id} image to {secure_url}")
                return secure_url, "Cloudinary upload successful"
        except Exception as e:
            error_msg = f"Cloudinary upload failed ({str(e)})"
            print(f"[Cloudinary Warning] {error_msg}. Falling back to local storage.")
    
    # Fallback: Save locally if CLOUDINARY_URL is missing or fails
    try:
        media_products_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        os.makedirs(media_products_dir, exist_ok=True)
        fs = FileSystemStorage(location=media_products_dir, base_url='/media/products/')
        filename = fs.save(f"prod_{product_id}_{uploaded_file.name}", uploaded_file)
        local_url = fs.url(filename)
        return local_url, "Saved locally (CLOUDINARY_URL not set or fallback)"
    except Exception as e:
        print(f"[Local Storage Error] {e}")
        return None, f"Failed to save image: {str(e)}"


def upload_slide_image_to_cloudinary(uploaded_file, slide_id):
    """
    Uploads a header slider image file to Cloudinary if CLOUDINARY_URL is set,
    otherwise saves locally to /media/slides/ and returns the media URL.
    """
    cloudinary_url = os.environ.get('CLOUDINARY_URL', '').strip()
    
    if cloudinary_url:
        try:
            import cloudinary
            import cloudinary.uploader
            
            cloudinary.config(cloudinary_url=cloudinary_url)
            
            public_id = f"slide_{slide_id}_{uuid.uuid4().hex[:6]}"
            result = cloudinary.uploader.upload(
                uploaded_file,
                folder="ecommerce_slides",
                public_id=public_id,
                overwrite=True,
                resource_type="image"
            )
            
            secure_url = result.get('secure_url') or result.get('url')
            if secure_url:
                print(f"[Cloudinary] Successfully uploaded slide #{slide_id} image to {secure_url}")
                return secure_url, "Cloudinary upload successful"
        except Exception as e:
            error_msg = f"Cloudinary upload failed ({str(e)})"
            print(f"[Cloudinary Warning] {error_msg}. Falling back to local storage.")
    
    # Fallback: Save locally
    try:
        media_slides_dir = os.path.join(settings.MEDIA_ROOT, 'slides')
        os.makedirs(media_slides_dir, exist_ok=True)
        fs = FileSystemStorage(location=media_slides_dir, base_url='/media/slides/')
        filename = fs.save(f"slide_{slide_id}_{uploaded_file.name}", uploaded_file)
        local_url = fs.url(filename)
        return local_url, "Saved locally (CLOUDINARY_URL not set or fallback)"
    except Exception as e:
        print(f"[Local Storage Error] {e}")
        return None, f"Failed to save image: {str(e)}"

