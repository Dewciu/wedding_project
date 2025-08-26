from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'wedding'

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_photo, name='upload'),
    path('gallery/', views.gallery, name='gallery'),
    path('table-finder/', views.table_finder, name='table_finder'),
    path('schedule/', views.schedule, name='schedule'),
    path('menu/', views.menu, name='menu'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='wedding/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('ajax/table-search/', views.ajax_table_search, name='ajax_table_search'),
]