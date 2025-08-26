from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from .models import WeddingInfo, Photo, Guest, Table, ScheduleEvent, MenuItem
from .forms import PhotoUploadForm, GuestRegistrationForm, TableSearchForm

def home(request):
    try:
        wedding_info = WeddingInfo.objects.first()
    except WeddingInfo.DoesNotExist:
        wedding_info = None
    
    featured_photos = Photo.objects.filter(approved=True, featured=True)[:4]
    recent_photos = Photo.objects.filter(approved=True).order_by('-upload_date')[:8]
    
    context = {
        'wedding_info': wedding_info,
        'featured_photos': featured_photos,
        'recent_photos': recent_photos,
    }
    return render(request, 'wedding/home.html', context)

@login_required
def upload_photo(request):
    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.uploaded_by = request.user
            photo.save()
            messages.success(request, 'Zdjęcie zostało przesłane! Czeka na zatwierdzenie.')
            return redirect('wedding:gallery')
    else:
        form = PhotoUploadForm()
    
    return render(request, 'wedding/upload.html', {'form': form})

def gallery(request):
    category = request.GET.get('category', '')
    photos_list = Photo.objects.filter(approved=True)
    
    if category:
        photos_list = photos_list.filter(category=category)
    
    paginator = Paginator(photos_list, 12)
    page_number = request.GET.get('page')
    photos = paginator.get_page(page_number)
    
    categories = Photo.CATEGORY_CHOICES
    
    context = {
        'photos': photos,
        'categories': categories,
        'current_category': category,
        'total_photos': photos_list.count(),
    }
    return render(request, 'wedding/gallery.html', context)

def table_finder(request):
    form = TableSearchForm()
    guest_info = None
    table_info = None
    table_guests = []
    
    if request.method == 'GET' and 'search_query' in request.GET:
        form = TableSearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['search_query']
            if query:
                # Search for guest
                guests = Guest.objects.filter(
                    Q(user__first_name__icontains=query) |
                    Q(user__last_name__icontains=query) |
                    Q(user__username__icontains=query)
                ).select_related('user')
                
                if guests.exists():
                    guest_info = guests.first()
                    if guest_info.table_number:
                        try:
                            table_info = Table.objects.get(number=guest_info.table_number)
                            table_guests = Guest.objects.filter(
                                table_number=guest_info.table_number
                            ).exclude(id=guest_info.id).select_related('user')
                        except Table.DoesNotExist:
                            table_info = None
    
    # Get all tables with their guests for the seating plan
    tables = Table.objects.all().order_by('number')
    
    # Add guest count and guest list to each table
    for table in tables:
        table.guest_list = Guest.objects.filter(
            table_number=table.number
        ).select_related('user').order_by('user__first_name')
    
    context = {
        'form': form,
        'guest_info': guest_info,
        'table_info': table_info,
        'table_guests': table_guests,
        'tables': tables,
    }
    return render(request, 'wedding/table_finder.html', context)

def schedule(request):
    events = ScheduleEvent.objects.all()
    return render(request, 'wedding/schedule.html', {'events': events})

def menu(request):
    menu_items = {}
    for course_key, course_name in MenuItem.COURSE_CHOICES:
        items = MenuItem.objects.filter(course=course_key)
        if items.exists():
            menu_items[course_name] = items
    
    return render(request, 'wedding/menu.html', {'menu_items': menu_items})

def register(request):
    if request.method == 'POST':
        form = GuestRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Witamy na naszym weselu! Twoje konto zostało utworzone.')
            return redirect('wedding:home')
    else:
        form = GuestRegistrationForm()
    
    return render(request, 'wedding/register.html', {'form': form})

# AJAX endpoint for table search
@require_http_methods(["GET"])
def ajax_table_search(request):
    query = request.GET.get('q', '')
    results = {'found': False}
    
    if len(query) > 2:
        guests = Guest.objects.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        ).select_related('user')
        
        if guests.exists():
            guest = guests.first()
            results['found'] = True
            results['guest_name'] = guest.full_name
            results['table_number'] = guest.table_number or 'Nie przypisano'
            results['guest_id'] = guest.id
            
            if guest.table_number:
                # Get table info
                try:
                    table = Table.objects.get(number=guest.table_number)
                    results['table_name'] = table.name
                    results['table_description'] = table.description
                except Table.DoesNotExist:
                    pass
                
                # Get other guests at the table
                table_guests = Guest.objects.filter(
                    table_number=guest.table_number
                ).exclude(id=guest.id).select_related('user')
                
                results['table_guests'] = [
                    {
                        'name': g.full_name,
                        'first_name': g.user.first_name,
                        'last_name': g.user.last_name
                    }
                    for g in table_guests
                ]
    
    return JsonResponse(results)