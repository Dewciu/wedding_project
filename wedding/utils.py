import os
from PIL import Image, ImageOps
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from io import BytesIO

def create_thumbnail(image_field, size=(300, 300)):
    """Create thumbnail for uploaded image"""
    if not image_field:
        return None
    
    try:
        # Open the image
        image = Image.open(image_field)
        
        # Fix orientation based on EXIF data
        image = ImageOps.exif_transpose(image)
        
        # Convert to RGB if necessary
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        
        # Create thumbnail
        image.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Save to BytesIO
        thumb_io = BytesIO()
        image.save(thumb_io, format='JPEG', quality=85)
        
        # Create filename
        name = os.path.splitext(os.path.basename(image_field.name))[0]
        thumb_name = f"thumbnails/{name}_thumb.jpg"
        
        # Save thumbnail
        thumbnail_file = ContentFile(thumb_io.getvalue())
        path = default_storage.save(thumb_name, thumbnail_file)
        
        return path
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        return None

def resize_image(image_field, max_size=(1200, 1200)):
    """Resize image if it's too large"""
    if not image_field:
        return
    
    try:
        # Open the image
        image = Image.open(image_field.path)
        
        # Fix orientation
        image = ImageOps.exif_transpose(image)
        
        # Check if resize is needed
        if image.height > max_size[1] or image.width > max_size[0]:
            # Resize maintaining aspect ratio
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save back to the same file
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            
            image.save(image_field.path, 'JPEG', quality=90)
    except Exception as e:
        print(f"Error resizing image: {e}")