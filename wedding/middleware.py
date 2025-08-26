from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

class WeddingSetupMiddleware:
    """Middleware to ensure wedding info is set up"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip for admin and static files
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            response = self.get_response(request)
            return response
        
        # Check if wedding info exists (except for setup page)
        if not request.path.startswith('/setup/'):
            from wedding.models import WeddingInfo
            if not WeddingInfo.objects.exists() and request.user.is_superuser:
                messages.warning(
                    request, 
                    'Skonfiguruj informacje o weselu w panelu administracyjnym.'
                )
        
        response = self.get_response(request)
        return response