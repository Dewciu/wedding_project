from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Photo, Guest

@require_GET
def api_photos(request):
    """API endpoint for photos with pagination"""
    page = request.GET.get('page', 1)
    category = request.GET.get('category', '')
    
    photos = Photo.objects.filter(approved=True).order_by('-upload_date')
    
    if category:
        photos = photos.filter(category=category)
    
    paginator = Paginator(photos, 12)
    page_obj = paginator.get_page(page)
    
    data = {
        'photos': [
            {
                'id': photo.id,
                'title': photo.title,
                'description': photo.description,
                'image_url': photo.get_thumbnail_url() or photo.image.url if photo.image else None,
                'full_image_url': photo.get_optimized_url() or photo.image.url if photo.image else None,
                'category': photo.category,
                'uploaded_by': photo.uploader_display_name,
                'upload_date': photo.upload_date.isoformat(),
            }
            for photo in page_obj
        ],
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'num_pages': paginator.num_pages,
        'current_page': page_obj.number,
        'total_count': paginator.count,
    }
    
    return JsonResponse(data)

@require_GET
@login_required
def api_guest_search(request):
    """API endpoint for guest search"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    guests = Guest.objects.filter(
        user__first_name__icontains=query
    ).select_related('user')[:10]
    
    results = [
        {
            'id': guest.id,
            'name': guest.full_name,
            'table_number': guest.table_number,
            'phone_number': guest.phone_number,
        }
        for guest in guests
    ]
    
    return JsonResponse({'results': results})