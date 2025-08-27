from django.contrib import admin
from django.utils.html import format_html
from .models import WeddingInfo, Guest, Table, Photo, ScheduleEvent, MenuItem

@admin.register(WeddingInfo)
class WeddingInfoAdmin(admin.ModelAdmin):
    list_display = ['bride_name', 'groom_name', 'wedding_date', 'venue_name']
    fields = ['bride_name', 'groom_name', 'wedding_date', 'venue_name', 'welcome_message']

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'table_number', 'confirmed', 'plus_one']
    list_filter = ['table_number', 'confirmed', 'plus_one']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    list_editable = ['table_number', 'confirmed']
    
    def full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    full_name.short_description = 'Imię i nazwisko'

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['number', 'name', 'capacity', 'guests_count', 'available_seats', 'shape', 'position_display']
    list_filter = ['shape', 'capacity']
    list_editable = ['name', 'capacity', 'shape']
    ordering = ['number']
    
    fieldsets = (
        ('Podstawowe Informacje', {
            'fields': ('number', 'name', 'capacity', 'description')
        }),
        ('Pozycja na Mapie', {
            'fields': (
                ('map_x', 'map_y'),
                ('map_width', 'map_height'),
                'shape'
            ),
            'description': 'Współrzędne: X (0-900), Y (0-600). Wymiary w pikselach na mapie.'
        }),
        ('Wygląd', {
            'fields': (('color', 'border_color'),),
            'classes': ('collapse',),
            'description': 'Kolory w formacie hex (np. #d4c4a8)'
        })
    )
    
    def guests_count(self, obj):
        return obj.guests_count
    guests_count.short_description = 'Obsadzone miejsca'
    
    def available_seats(self, obj):
        return obj.available_seats
    available_seats.short_description = 'Wolne miejsca'
    
    def position_display(self, obj):
        return f"({obj.map_x}, {obj.map_y})"
    position_display.short_description = 'Pozycja (X, Y)'
    
    class Media:
        css = {
            'all': ('wedding/css/admin_table_positioning.css',)
        }
        js = ('wedding/js/admin_table_positioning.js',)

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'image_preview', 'category', 'uploaded_by', 'approved', 'featured', 'upload_date']
    list_filter = ['category', 'approved', 'featured', 'upload_date']
    search_fields = ['title', 'description', 'uploaded_by__username']
    list_editable = ['approved', 'featured']
    ordering = ['-upload_date']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return "Brak zdjęcia"
    image_preview.short_description = 'Podgląd'

@admin.register(ScheduleEvent)
class ScheduleEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_time', 'end_time', 'location', 'order']
    list_editable = ['order']
    ordering = ['order', 'start_time']

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'price', 'vegetarian', 'order']
    list_filter = ['course', 'vegetarian']
    list_editable = ['price', 'order']
    ordering = ['course', 'order']