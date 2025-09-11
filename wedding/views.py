from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Case, When, IntegerField
from django.db.models.functions import Concat
from django.db.models import Value
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
import json
import os
import re
import qrcode
from io import BytesIO
import base64
from .models import WeddingInfo, Photo, Guest, Table, ScheduleEvent, MenuItem
from .forms import MultiPhotoUploadForm, TableSearchForm

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

def upload_photo(request):
    """Multi-upload photos - bardzo prosty interfejs"""
    if request.method == 'POST':
        form = MultiPhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('photos')
            uploader_name = form.cleaned_data.get('uploader_name', '').strip()
            category = form.cleaned_data.get('category', 'party')
            description = form.cleaned_data.get('description', '').strip()
            
            uploaded_count = 0
            
            for uploaded_file in files:
                try:
                    # Automatyczne generowanie tytułu z nazwy pliku
                    title = generate_title_from_filename(uploaded_file.name)
                    
                    # Tworzenie nowego zdjęcia
                    photo = Photo(
                        title=title,
                        description=description,
                        image=uploaded_file,
                        category=category,
                        uploader_name=uploader_name,
                        uploaded_by=request.user if request.user.is_authenticated else None
                    )
                    photo.save()
                    uploaded_count += 1
                    
                except Exception as e:
                    print(f"Błąd przy zapisywaniu {uploaded_file.name}: {e}")
                    continue
            
            if uploaded_count > 0:
                if uploaded_count == 1:
                    messages.success(request, 'Zdjęcie zostało przesłane! Czeka na zatwierdzenie.')
                else:
                    messages.success(request, f'Przesłano {uploaded_count} zdjęć! Czekają na zatwierdzenie.')
            else:
                messages.error(request, 'Nie udało się przesłać żadnego zdjęcia. Spróbuj ponownie.')
                
            return redirect('wedding:gallery')
    else:
        form = MultiPhotoUploadForm()
    
    return render(request, 'wedding/upload.html', {'form': form})

def generate_title_from_filename(filename):
    """Generuje ładny tytuł z nazwy pliku"""
    # Usuń rozszerzenie
    name = os.path.splitext(filename)[0]
    
    # Zamień podkreślenia i myślniki na spacje
    name = name.replace('_', ' ').replace('-', ' ')
    
    # Usuń liczby na początku (np. "IMG_" "DSC_")
    import re
    name = re.sub(r'^(IMG|DSC|PHOTO|PIC)[\s_-]*\d*[\s_-]*', '', name, flags=re.IGNORECASE)
    
    # Jeśli zostały tylko liczby, użyj generycznego tytułu
    if re.match(r'^\d+$', name.strip()):
        return "Zdjęcie z wesela"
    
    # Pierwsza litera każdego słowa wielka
    if name.strip():
        return ' '.join(word.capitalize() for word in name.split())
    else:
        return "Zdjęcie z wesela"

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
    """Naprawione wyszukiwanie stolika"""
    print("=== DEBUG TABLE FINDER START ===")
    
    form = TableSearchForm()
    guest_info = None
    table_info = None
    table_guests = []
    
    if request.method == 'GET' and 'search_query' in request.GET:
        form = TableSearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['search_query'].strip()
            print(f"Wyszukiwanie dla: '{query}'")
            
            if query:
                # Ulepszone wyszukiwanie - obsługuje pełne imię i nazwisko
                guests = Guest.objects.annotate(
                    full_name_concat=Concat('user__first_name', Value(' '), 'user__last_name')
                ).filter(
                    Q(user__first_name__icontains=query) |
                    Q(user__last_name__icontains=query) |
                    Q(user__username__icontains=query) |
                    Q(full_name_concat__icontains=query)  # Wyszukiwanie po pełnym imieniu i nazwisku
                ).select_related('user')
                
                print(f"Znaleziono {guests.count()} gości")
                
                if guests.exists():
                    guest_info = guests.first()
                    print(f"Wybrany gość: {guest_info.full_name}")
                    
                    if guest_info.table_number:
                        try:
                            table_info = Table.objects.get(number=guest_info.table_number)
                            table_guests = Guest.objects.filter(
                                table_number=guest_info.table_number
                            ).exclude(id=guest_info.id).select_related('user')
                            print(f"Stół {guest_info.table_number}, {table_guests.count()} innych gości")
                        except Table.DoesNotExist:
                            table_info = None
                            print(f"Stół {guest_info.table_number} nie istnieje w bazie")
    
    # Get all tables with their guests for the seating plan
    tables = Table.objects.all().order_by('number')
    print(f"Found {tables.count()} tables in database")
    
    # Prepare tables data for JavaScript
    tables_data = []
    for table in tables:
        guest_list = Guest.objects.filter(
            table_number=table.number
        ).select_related('user').order_by('user__first_name')
        
        table.guest_list = guest_list  # For template rendering
        
        print(f"Processing table {table.number}: {guest_list.count()} guests")
        
        # Prepare JSON-serializable data for JavaScript
        guests_json = []
        for guest in guest_list:
            guests_json.append({
                'id': guest.id,
                'full_name': guest.full_name,
                'guest_type': guest.guest_type or 'Gość',
                'chair_position': guest.chair_position,
                'user': {
                    'first_name': guest.user.first_name,
                    'last_name': guest.user.last_name
                }
            })
        
        # Create table data with positioning info
        table_dict = {
            'number': table.number,
            'name': table.name,
            'description': table.description,
            'capacity': table.capacity,
            'guests_count': guest_list.count(),
            'guest_list': guests_json,
            # Positioning data from database (with fallbacks)
            'map_x': float(table.map_x) if hasattr(table, 'map_x') and table.map_x else 300.0,
            'map_y': float(table.map_y) if hasattr(table, 'map_y') and table.map_y else 300.0,
            'map_width': float(table.map_width) if hasattr(table, 'map_width') and table.map_width else 85.0,
            'map_height': float(table.map_height) if hasattr(table, 'map_height') and table.map_height else 85.0,
            'shape': getattr(table, 'shape', 'circular'),
            'color': getattr(table, 'color', '#d4c4a8'),
            'border_color': getattr(table, 'border_color', '#b8a082'),
        }
        
        tables_data.append(table_dict)
        print(f"Table {table.number} data: x={table_dict['map_x']}, y={table_dict['map_y']}, shape={table_dict['shape']}")
    
    # Prepare current guest info for JavaScript
    guest_info_json = None
    if guest_info:
        guest_info_json = {
            'id': guest_info.id,
            'full_name': guest_info.full_name,
            'table_number': guest_info.table_number,
            'guest_type': guest_info.guest_type or 'Gość'
        }
        print(f"Current guest: {guest_info_json}")
    
    # Convert to JSON strings
    try:
        tables_json_str = json.dumps(tables_data, cls=DjangoJSONEncoder)
        guest_info_json_str = json.dumps(guest_info_json, cls=DjangoJSONEncoder)
        print(f"Tables JSON length: {len(tables_json_str)}")
        print(f"Guest info JSON: {guest_info_json_str}")
    except Exception as e:
        print(f"JSON serialization error: {e}")
        tables_json_str = "[]"
        guest_info_json_str = "null"
    
    context = {
        'form': form,
        'guest_info': guest_info,
        'table_info': table_info,
        'table_guests': table_guests,
        'tables': tables,
        'tables_json': tables_json_str,
        'guest_info_json': guest_info_json_str,
    }
    
    print("=== DEBUG TABLE FINDER END ===")
    print(f"Context keys: {list(context.keys())}")
    
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

# AJAX endpoint for table search - również naprawione
@require_http_methods(["GET"])
def ajax_table_search(request):
    """Naprawione AJAX wyszukiwanie stolika - szuka po imieniu I nazwisku"""
    query = request.GET.get('q', '').strip()
    results = {'found': False}
    
    print(f"AJAX search for: '{query}'")
    
    if len(query) >= 2:
        # Lepsze wyszukiwanie - szuka pełnego imienia i nazwiska
        guests = Guest.objects.annotate(
            full_name_concat=Concat('user__first_name', Value(' '), 'user__last_name')
        ).filter(
            # Szuka po połączeniu imienia i nazwiska (główne kryterium)
            Q(full_name_concat__icontains=query) |
            # Lub po imieniu jeśli wpisano tylko imię
            Q(user__first_name__icontains=query) |
            # Lub po nazwisku jeśli wpisano tylko nazwisko
            Q(user__last_name__icontains=query) |
            # Lub po username jako fallback
            Q(user__username__icontains=query)
        ).select_related('user')
        
        print(f"AJAX found {guests.count()} guests")
        
        if guests.exists():
            # Priorytet dla dokładnych dopasowań pełnego imienia i nazwiska
            exact_match = guests.filter(full_name_concat__iexact=query).first()
            if exact_match:
                guest = exact_match
                print(f"AJAX exact match: {guest.full_name}")
            else:
                guest = guests.first()
                print(f"AJAX partial match: {guest.full_name}")
            
            results['found'] = True
            results['guest_name'] = guest.full_name
            results['table_number'] = guest.table_number or 'Nie przypisano'
            results['guest_id'] = guest.id
            
            print(f"AJAX selected guest: {guest.full_name}, table: {guest.table_number}")
            
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
    
    print(f"AJAX results: {results}")
    return JsonResponse(results)


@staff_member_required
def generate_qr_code(request):
    """Generuje QR kod dla dostępu do aplikacji weselnej"""
    
    # Pobierz token z ustawień
    token = getattr(settings, 'WEDDING_ACCESS_TOKEN', 'DEMO2024')
    
    # Stwórz URL z tokenem
    domain = request.get_host()
    protocol = 'https' if request.is_secure() else 'http'
    access_url = f"{protocol}://{domain}/?token={token}"
    
    # Wygeneruj QR kod
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(access_url)
    qr.make(fit=True)
    
    # Stwórz obrazek
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Konwertuj na base64 dla wyświetlenia w przeglądarce
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_image_b64 = base64.b64encode(buffer.getvalue()).decode()
    
    # Pobierz informacje o weselu
    try:
        wedding_info = WeddingInfo.objects.first()
    except WeddingInfo.DoesNotExist:
        wedding_info = None
    
    # HTML dla administratora z kodem QR
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Generator QR Code - Aplikacja Weselna</title>
        <style>
            body {{
                font-family: Georgia, serif;
                background: linear-gradient(135deg, #f5f0e8 0%, #e8ddd4 100%);
                color: #5d4e37;
                margin: 0;
                padding: 20px;
                min-height: 100vh;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background: rgba(248, 245, 240, 0.95);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 12px 24px rgba(93, 78, 55, 0.15);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .qr-section {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                align-items: start;
                margin: 30px 0;
            }}
            .qr-image {{
                text-align: center;
                background: white;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 15px rgba(93, 78, 55, 0.1);
            }}
            .qr-image img {{
                max-width: 100%;
                height: auto;
                border-radius: 10px;
            }}
            .instructions {{
                background: #f8f5f0;
                border: 1px solid #d4c4a8;
                border-radius: 15px;
                padding: 20px;
            }}
            .info-card {{
                background: #ede8dd;
                border: 1px solid #d4c4a8;
                border-radius: 10px;
                padding: 15px;
                margin: 15px 0;
            }}
            .url {{
                background: white;
                padding: 10px;
                border-radius: 8px;
                font-family: monospace;
                word-break: break-all;
                font-size: 0.9rem;
                border: 1px solid #d4c4a8;
            }}
            .btn {{
                background: linear-gradient(145deg, #8b6f47, #5d4e37);
                color: #f5f0e8;
                padding: 12px 25px;
                border: none;
                border-radius: 25px;
                text-decoration: none;
                display: inline-block;
                margin: 10px 5px;
                font-weight: bold;
                cursor: pointer;
            }}
            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(93, 78, 55, 0.3);
            }}
            @media (max-width: 768px) {{
                .qr-section {{
                    grid-template-columns: 1fr;
                }}
            }}
            .warning {{
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 8px;
                padding: 15px;
                margin: 20px 0;
                color: #856404;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Generator QR Code</h1>
                <h2>Aplikacja Weselna</h2>
                {f"<p><strong>{wedding_info.bride_name} & {wedding_info.groom_name}</strong><br>{wedding_info.wedding_date}</p>" if wedding_info else ""}
            </div>
            
            <div class="qr-section">
                <div class="qr-image">
                    <h3>Kod QR do skanowania</h3>
                    <img src="data:image/png;base64,{qr_image_b64}" alt="QR Code">
                    <p><small>Wydrukuj i umieść na stolikach</small></p>
                </div>
                
                <div class="instructions">
                    <h3>📱 Instrukcje dla gości:</h3>
                    <ol>
                        <li><strong>Otwórz aparat</strong> w telefonie</li>
                        <li><strong>Zeskanuj kod QR</strong> z tablicy lub stolika</li>
                        <li><strong>Kliknij w link</strong> który się pojawi</li>
                        <li><strong>Gotowe!</strong> Możesz korzystać z aplikacji</li>
                    </ol>
                    
                    <h4>✨ Co mogą robić goście:</h4>
                    <ul>
                        <li>Przesyłać wiele zdjęć naraz</li>
                        <li>Przeglądać galerię</li>
                        <li>Sprawdzać numer stolika</li>
                        <li>Oglądać harmonogram i menu</li>
                    </ul>
                </div>
            </div>
            
            <div class="info-card">
                <h3>🔗 Link dostępu:</h3>
                <div class="url">{access_url}</div>
                <p><small>Goście mogą też wpisać ten link bezpośrednio w przeglądarce</small></p>
            </div>
            
            <div class="info-card">
                <h3>🔑 Informacje techniczne:</h3>
                <p><strong>Token dostępu:</strong> <code>{token}</code></p>
                <p><strong>Ważność sesji:</strong> 7 dni</p>
                <p><small>Token można zmienić w ustawieniach (WEDDING_ACCESS_TOKEN)</small></p>
            </div>
            
            <div class="warning">
                <strong>⚠️ Bezpieczeństwo:</strong><br>
                • Nie udostępniaj tokenu publicznie w internecie<br>
                • Zmień token po weselu<br>
                • Kod QR jest bezpieczny dla gości weselnych
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="javascript:window.print()" class="btn">🖨️ Wydrukuj QR Code</a>
                <a href="/admin/" class="btn">👩‍💼 Panel Admina</a>
                <a href="{access_url}" class="btn">🎉 Testuj Aplikację</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HttpResponse(html_content)

@csrf_exempt
@require_http_methods(["POST"])
def ajax_update_chair_position(request):
    """Aktualizacja pozycji krzesła gościa przy stole"""
    try:
        data = json.loads(request.body)
        guest_id = data.get('guest_id')
        chair_position = data.get('chair_position')
        
        if not guest_id or chair_position is None:
            return JsonResponse({
                'success': False,
                'message': 'Brak wymaganych danych'
            })
        
        guest = get_object_or_404(Guest, id=guest_id)
        guest.chair_position = chair_position
        guest.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Pozycja gościa {guest.full_name} została zaktualizowana'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Nieprawidłowe dane JSON'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Błąd: {str(e)}'
        })

def debug_data(request):
    """Debug view to inspect data being passed to JavaScript"""
    # Reuse the same logic as table_finder but render debug template
    tables = Table.objects.all().order_by('number')
    print(f"Found {tables.count()} tables in database")
    
    tables_data = []
    for table in tables:
        guest_list = Guest.objects.filter(
            table_number=table.number
        ).select_related('user').order_by('user__first_name')
        
        print(f"Processing table {table.number}: {guest_list.count()} guests")
        
        # Prepare JSON-serializable data for JavaScript
        guests_json = []
        for guest in guest_list:
            guests_json.append({
                'id': guest.id,
                'full_name': guest.full_name,
                'guest_type': guest.guest_type or 'Gość',
                'chair_position': guest.chair_position,
                'user': {
                    'first_name': guest.user.first_name,
                    'last_name': guest.user.last_name
                }
            })
        
        # Create table data with positioning info
        table_dict = {
            'number': table.number,
            'name': table.name,
            'description': table.description,
            'capacity': table.capacity,
            'guests_count': guest_list.count(),
            'guest_list': guests_json,
            # Positioning data from database (with fallbacks)
            'map_x': float(table.map_x) if hasattr(table, 'map_x') and table.map_x else 300.0,
            'map_y': float(table.map_y) if hasattr(table, 'map_y') and table.map_y else 300.0,
            'map_width': float(table.map_width) if hasattr(table, 'map_width') and table.map_width else 85.0,
            'map_height': float(table.map_height) if hasattr(table, 'map_height') and table.map_height else 85.0,
            'shape': getattr(table, 'shape', 'circular'),
            'color': getattr(table, 'color', '#d4c4a8'),
            'border_color': getattr(table, 'border_color', '#b8a082'),
        }
        
        tables_data.append(table_dict)
        print(f"Table {table.number} has {len(guests_json)} guests in JSON data")
    
    # Convert to JSON strings
    try:
        tables_json_str = json.dumps(tables_data, cls=DjangoJSONEncoder, indent=2)
        guest_info_json_str = json.dumps(None, cls=DjangoJSONEncoder)
        print(f"JSON created successfully, {len(tables_data)} tables")
    except Exception as e:
        print(f"JSON serialization error: {e}")
        tables_json_str = "[]"
        guest_info_json_str = "null"
    
    context = {
        'tables_json': tables_json_str,
        'guest_info_json': guest_info_json_str,
    }
    
    return render(request, 'wedding/debug_data.html', context)

def debug_token(request):
    """Debug endpoint to check token validation"""
    token_from_url = request.GET.get('token')
    expected_token = getattr(settings, 'WEDDING_ACCESS_TOKEN', 'DEMO2024')
    session_token = request.session.get('wedding_access_token')
    session_verified = request.session.get('wedding_access_verified')
    
    return JsonResponse({
        'token_from_url': token_from_url,
        'expected_token': expected_token,
        'session_token': session_token,
        'session_verified': session_verified,
        'validation_result': token_from_url == expected_token if token_from_url else False
    })