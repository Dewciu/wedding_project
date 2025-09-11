from django.urls import path
from . import views

app_name = 'wedding'

urlpatterns = [
    # Debug endpoint
    path('debug-token/', views.debug_token, name='debug_token'),
    
    # Główne strony aplikacji
    path('', views.home, name='home'),
    path('upload/', views.upload_photo, name='upload'),
    path('gallery/', views.gallery, name='gallery'),
    path('table-finder/', views.table_finder, name='table_finder'),
    path('debug-data/', views.debug_data, name='debug_data'),  # Debug view for data inspection
    path('schedule/', views.schedule, name='schedule'),
    path('menu/', views.menu, name='menu'),
    
    # AJAX endpoints
    path('ajax/table-search/', views.ajax_table_search, name='ajax_table_search'),
    path('ajax/update-chair-position/', views.ajax_update_chair_position, name='ajax_update_chair_position'),
    
    # Admin utilities (dla organizatorów)
    path('admin-tools/qr-generator/', views.generate_qr_code, name='qr_generator'),
]

# Usuwamy:
# - path('register/', views.register, name='register'),
# - path('login/', auth_views.LoginView.as_view(template_name='wedding/login.html'), name='login'),
# - path('logout/', auth_views.LogoutView.as_view(), name='logout'),