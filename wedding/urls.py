from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.generic import RedirectView

def favicon_view(request):
    # Simple favicon response - you can replace with actual favicon.ico file
    return HttpResponse(
        (
            b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x08\x00h\x05\x00\x00'
            b'\x16\x00\x00\x00(\x00\x00\x00\x10\x00\x00\x00 \x00\x00\x00\x01\x00\x08'
            b'\x00\x00\x00\x00\x00@\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x01\x00\x00\x00\x01\x00\x00'
        ),
        content_type="image/x-icon"
    )

urlpatterns = [
    path('admin/', admin.site.urls),
    path('favicon.ico', favicon_view, name='favicon'),
    path('', include('wedding.urls')),
]

# Static files handling
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # In production, whitenoise will handle static files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)