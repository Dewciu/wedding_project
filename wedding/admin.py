from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import WeddingInfo, Guest, Table, Photo, ScheduleEvent, MenuItem

@admin.register(WeddingInfo)
class WeddingInfoAdmin(admin.ModelAdmin):
    list_display = ['bride_name', 'groom_name', 'wedding_date', 'venue_name']
    fields = ['bride_name', 'groom_name', 'wedding_date', 'venue_name', 'welcome_message']

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'table_number', 'chair_position', 'confirmed', 'plus_one']
    list_filter = ['table_number', 'confirmed', 'plus_one', 'chair_position']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    list_editable = ['table_number', 'chair_position', 'confirmed']
    
    fieldsets = (
        ('Podstawowe Informacje', {
            'fields': ('user', 'phone_number', 'guest_type', 'dietary_requirements')
        }),
        ('Miejsce przy stole', {
            'fields': ('table_number', 'chair_position'),
            'description': 'Pozycja krzesła przy stole - numery od 1 do liczby miejsc przy stole'
        }),
        ('Dodatkowe opcje', {
            'fields': ('plus_one', 'confirmed'),
            'classes': ('collapse',)
        })
    )
    
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
    list_display = ['title', 'image_preview', 'uploader_display', 'category', 'approved', 'featured', 'upload_date', 'same_batch']
    list_filter = ['category', 'approved', 'featured', 'upload_date', 'uploader_name']
    search_fields = ['title', 'description', 'uploaded_by__username', 'uploader_name']
    list_editable = ['approved', 'featured']
    ordering = ['-upload_date']
    actions = ['approve_selected', 'feature_selected', 'approve_batch']
    
    fieldsets = (
        ('Podstawowe Informacje', {
            'fields': ('title', 'description', 'image', 'category')
        }),
        ('Przesyłający', {
            'fields': ('uploaded_by', 'uploader_name'),
            'description': 'Automatycznie wypełniane na podstawie danych z formularza'
        }),
        ('Moderacja', {
            'fields': ('approved', 'featured'),
        })
    )
    
    def image_preview(self, obj):
        if obj.image:
            # Użyj wysokiej jakości thumbnail dla podglądu w adminie
            thumbnail_url = obj.get_thumbnail_url() if hasattr(obj, 'get_thumbnail_url') else obj.image.url
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);" />',
                thumbnail_url or obj.image.url
            )
        return "📷"
    image_preview.short_description = 'Podgląd'
    
    def uploader_display(self, obj):
        """Wyświetla kto przesłał zdjęcie z ikoną"""
        display = obj.uploader_display_name
        if obj.uploaded_by:
            return f"👤 {display}"
        else:
            return f"👥 {display}"
    uploader_display.short_description = 'Przesłane przez'
    
    def same_batch(self, obj):
        """Pokazuje czy zdjęcie było przesłane w tej samej partii co inne"""
        if obj.uploader_name:
            # Znajdź zdjęcia przesłane w tym samym czasie (±5 minut) przez tę samą osobę
            from django.utils import timezone
            from datetime import timedelta
            
            time_window = timedelta(minutes=5)
            similar_photos = Photo.objects.filter(
                uploader_name=obj.uploader_name,
                upload_date__range=[
                    obj.upload_date - time_window,
                    obj.upload_date + time_window
                ]
            ).exclude(id=obj.id)
            
            count = similar_photos.count()
            if count > 0:
                return f"📸 +{count}"
        return ""
    same_batch.short_description = 'Partia'
    
    def get_readonly_fields(self, request, obj=None):
        # Jeśli zdjęcie ma już przypisanego użytkownika, nie pozwalaj na zmianę
        if obj and obj.uploaded_by:
            return ['uploaded_by']
        return []
    
    # Custom actions
    def approve_selected(self, request, queryset):
        count = queryset.update(approved=True)
        self.message_user(request, f'Zatwierdzono {count} zdjęć.')
    approve_selected.short_description = "✅ Zatwierdź wybrane zdjęcia"
    
    def feature_selected(self, request, queryset):
        count = queryset.update(featured=True, approved=True)  # Wyróżnione musi być zatwierdzone
        self.message_user(request, f'Wyróżniono {count} zdjęć.')
    feature_selected.short_description = "⭐ Wyróż wybrane zdjęcia"
    
    def approve_batch(self, request, queryset):
        """Zatwierdza wszystkie zdjęcia od tych samych osób w tym samym czasie"""
        approved_count = 0
        
        for photo in queryset:
            if photo.uploader_name:
                from django.utils import timezone
                from datetime import timedelta
                
                time_window = timedelta(minutes=10)  # Szersze okno dla partii
                batch_photos = Photo.objects.filter(
                    uploader_name=photo.uploader_name,
                    upload_date__range=[
                        photo.upload_date - time_window,
                        photo.upload_date + time_window
                    ],
                    approved=False
                )
                approved_count += batch_photos.update(approved=True)
        
        self.message_user(request, f'Zatwierdzono {approved_count} zdjęć w partiach.')
    approve_batch.short_description = "📸 Zatwierdź całe partie zdjęć"

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

# Dodaj custom admin site header
admin.site.site_header = "🎉 Administracja Aplikacji Weselnej"
admin.site.site_title = "Panel Weselny"
admin.site.index_title = "Zarządzanie weselem"

# Dodaj custom dashboard info
from django.contrib.admin import AdminSite
from django.template.response import TemplateResponse

class WeddingAdminSite(AdminSite):
    def index(self, request, extra_context=None):
        # Dodaj statystyki na stronę główną admina
        extra_context = extra_context or {}
        
        try:
            from django.db.models import Count
            stats = {
                'total_photos': Photo.objects.count(),
                'pending_photos': Photo.objects.filter(approved=False).count(),
                'featured_photos': Photo.objects.filter(featured=True).count(),
                'total_guests': Guest.objects.count(),
                'recent_uploads': Photo.objects.order_by('-upload_date')[:5]
            }
            extra_context['wedding_stats'] = stats
        except:
            pass
            
        return super().index(request, extra_context)