from django import template
from django.utils.safestring import mark_safe
from django.core.serializers.json import DjangoJSONEncoder
import json
import re

register = template.Library()

@register.filter
def phone_format(value):
    """Format phone number to Polish format"""
    if not value:
        return value
    
    # Remove all non-digits
    digits = re.sub(r'\D', '', value)
    
    # Format as XXX-XXX-XXX
    if len(digits) == 9:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    return value

@register.filter
def truncate_words_html(value, arg):
    """Truncate text but preserve HTML"""
    try:
        length = int(arg)
        words = value.split()
        if len(words) <= length:
            return value
        return ' '.join(words[:length]) + '...'
    except (ValueError, TypeError):
        return value

@register.filter
def to_json(value):
    """Convert Python object to JSON string for JavaScript consumption"""
    return mark_safe(json.dumps(value, cls=DjangoJSONEncoder))

@register.simple_tag
def photo_count_by_category(category):
    """Get photo count for specific category"""
    from wedding.models import Photo
    return Photo.objects.filter(category=category, approved=True).count()

@register.simple_tag
def table_occupancy(table_number):
    """Get table occupancy info"""
    from wedding.models import Guest, Table
    try:
        table = Table.objects.get(number=table_number)
        guests = Guest.objects.filter(table_number=table_number).count()
        return f"{guests}/{table.capacity}"
    except Table.DoesNotExist:
        return "0/0"

@register.inclusion_tag('wedding/includes/photo_grid.html')
def photo_grid(photos, cols=3):
    """Render photo grid"""
    return {
        'photos': photos,
        'cols': cols
    }

@register.inclusion_tag('wedding/includes/table_map.html')
def table_map(tables, current_guest=None):
    """Render interactive table map"""
    return {
        'tables': tables,
        'current_guest': current_guest,
    }

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    return dictionary.get(key)

@register.simple_tag
def guest_avatar_initial(guest):
    """Get guest avatar initial"""
    if hasattr(guest, 'user') and guest.user.first_name:
        return guest.user.first_name[0].upper()
    elif hasattr(guest, 'first_name') and guest.first_name:
        return guest.first_name[0].upper()
    return '?'

@register.filter
def is_mobile_device(request):
    """Check if request is from mobile device"""
    if not request:
        return False
    
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    mobile_keywords = [
        'mobile', 'android', 'iphone', 'ipad', 'ipod', 
        'blackberry', 'webos', 'windows phone'
    ]
    return any(keyword in user_agent for keyword in mobile_keywords)