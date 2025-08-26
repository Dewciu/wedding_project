from django import template
from django.utils.safestring import mark_safe
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