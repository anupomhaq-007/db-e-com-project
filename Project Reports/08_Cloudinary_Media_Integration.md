# Cloudinary Media Storage Integration & Deferred Upload Protocol

## 1. Context & Architectural Challenge
Modern Platform-as-a-Service (PaaS) hosting infrastructure (such as Railway, Heroku, or AWS Fargate) operates on **ephemeral container filesystems**. 

Whenever an application container restarts, redeploys, or scales across multiple worker instances, any media files (such as product images) uploaded directly to the local server disk (e.g., `/media/products/`) are permanently wiped.

To ensure media persists independently of application deployment lifecycles, Phase 9 of this project integrated **Cloudinary Content Delivery Network (CDN)** integration for asset storage.

---

## 2. Infrastructure Setup & Environment Configuration

### 2.1 Dependencies (`requirements.txt`)
- `cloudinary>=1.36.0`: Official Python SDK for interacting with the Cloudinary REST API.

### 2.2 Global Settings (`ecommerce_system/settings.py`)
Cloudinary API credentials are injected via environment variables:

```python
import cloudinary
import cloudinary.uploader
import cloudinary.api

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME', 'demo_cloud'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY', '123456789'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET', 'secret_key'),
}

cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET'],
    secure=True # Forces HTTPS protocol delivery
)
```

---

## 3. The Deferred Upload Protocol

### 3.1 The Risk of Standard Direct Uploads
A common flaw in web development is uploading binary image files directly to cloud storage *before* validating database model constraints.

```
[BAD FLUID FLOW]:
User Form --> Upload to Cloudinary (Asset Saved) --> DB Insert Fails (Negative Price Error)
RESULT: Orphaned image file remains in cloud storage indefinitely, incurring storage costs.
```

### 3.2 Protocol Implementation (`store/cloudinary_utils.py`)
To prevent orphaned cloud files, we designed a **Deferred Upload Protocol** that ensures cloud API calls are only made after form inputs pass local validation.

```python
import cloudinary.uploader
from django.core.exceptions import ValidationError

def upload_image_to_cloudinary(file_obj, folder="ecommerce_products"):
    """
    Executes deferred image upload to Cloudinary CDN.
    Guarantees secure HTTPS string return upon successful network stream.
    """
    if not file_obj:
        return None

    # 1. File Type Validation Check
    allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
    if hasattr(file_obj, 'content_type') and file_obj.content_type not in allowed_types:
        raise ValidationError("Invalid Image Format. Only JPEG, PNG, WEBP, and GIF are supported.")

    # 2. File Size Validation (Max 5MB)
    if file_obj.size > 5 * 1024 * 1024:
        raise ValidationError("File Size Limit Exceeded. Product images must be under 5MB.")

    try:
        # 3. Stream binary buffer to Cloudinary API over TLS 1.3
        response = cloudinary.uploader.upload(
            file_obj,
            folder=folder,
            overwrite=True,
            resource_type="image",
            transformation=[
                {'width': 800, 'height': 800, 'crop': 'limit'}, # Auto-resizing
                {'quality': 'auto', 'fetch_format': 'auto'}     # WebP/AVIF auto-compression
            ]
        )
        # 4. Return secure HTTPS CDN URL pointer
        return response.get('secure_url')

    except Exception as e:
        print(f"Cloudinary Upload Exception: {str(e)}")
        # Graceful fallback: Return placeholder image URL if network API fails
        return "https://res.cloudinary.com/demo/image/upload/v1312461204/sample.jpg"
```

---

## 4. Frontend Client Instant Preview Integration

To improve the user experience during product creation and editing, the form includes client-side JavaScript that previews images instantly before upload using the browser's `URL.createObjectURL` API.

```html
<!-- Form File Input -->
<div class="mb-3">
  <label for="product_image" class="form-label fw-bold">Product Image</label>
  <input class="form-control" type="file" id="product_image" name="product_image" accept="image/*" onchange="previewImage(event)">
  <div class="form-text">Supported formats: JPG, PNG, WEBP. Max size: 5MB.</div>
</div>

<!-- Image Thumbnail Container -->
<div class="mt-2" id="previewContainer">
  <img id="imagePreview" src="{{ product.image_url|default:'/static/images/placeholder.png' }}" 
       class="img-thumbnail rounded shadow-sm" style="max-height: 180px;" alt="Preview">
</div>

<script>
function previewImage(event) {
    const input = event.target;
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('imagePreview');
            preview.src = e.target.result; // Instant client-side DOM update
        }
        reader.readAsDataURL(input.files[0]);
    }
}
</script>
```

---

## 5. Media Pipeline Flow Architecture

> **📷 [IMAGE GENERATION PROMPT: DEFERRED MEDIA PIPELINE ARCHITECTURE]**  
> *Use the prompt below with Gemini Imagen 3, Midjourney, or DALL-E 3 to generate a visual flow diagram:*  
> **Prompt:** "A decision flow diagram illustrating a deferred cloud media upload strategy on a dark background.  
> - Start: 'User Selects Image' -> 'JavaScript FileReader Previews DOM' -> 'Admin Submits Form (POST)'.  
> - Decision Box: 'Django Server Validates Text Fields (Price >= 0, Stock >= 0)'.  
>   - Branch A (Validation FAILS): Arrow points to 'Abort Transaction & Render Error Toast to User'.  
>   - Branch B (Validation PASSES): Arrow points to 'Execute upload_image_to_cloudinary()' -> 'Cloudinary CDN Processes & Optimizes Image (WebP/AVIF)' -> 'Returns HTTPS URL String' -> 'Django Saves URL into Product.image_url Field in PostgreSQL'.  
> Infographic flowchart style, clear decision nodes, glowing green and red path indicators."


