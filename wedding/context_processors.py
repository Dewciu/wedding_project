from .models import WeddingInfo

def wedding_context(request):
    try:
        wedding_info = WeddingInfo.objects.first()
    except WeddingInfo.DoesNotExist:
        wedding_info = None
    
    return {
        'wedding_info': wedding_info,
    }