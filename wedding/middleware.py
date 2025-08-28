from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
import hashlib
import hmac

class WeddingAccessMiddleware:
    """Middleware do kontroli dostępu przez token zamiast logowania"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Pomijamy sprawdzanie dla admina i plików statycznych
        if (request.path.startswith('/admin/') or 
            request.path.startswith('/static/') or 
            request.path.startswith('/media/')):
            return self.get_response(request)
        
        # Sprawdzamy czy użytkownik ma ważny token w sesji
        if self.has_valid_session(request):
            return self.get_response(request)
        
        # Sprawdzamy czy URL zawiera token dostępu
        token_from_url = self.extract_token_from_url(request)
        if token_from_url and self.validate_token(token_from_url):
            # Zapisujemy token w sesji
            request.session['wedding_access_token'] = token_from_url
            request.session['wedding_access_verified'] = True
            
            # Przekieruj na stronę główną bez tokenu w URL (dla bezpieczeństwa)
            if 'token' in request.GET:
                return HttpResponseRedirect(reverse('wedding:home'))
            
            return self.get_response(request)
        
        # Brak dostępu - pokaż stronę z informacją
        return self.show_access_denied_page(request)

    def has_valid_session(self, request):
        """Sprawdza czy użytkownik ma ważną sesję"""
        return (request.session.get('wedding_access_verified') and 
                request.session.get('wedding_access_token') and
                self.validate_token(request.session.get('wedding_access_token')))

    def extract_token_from_url(self, request):
        """Wyciąga token z URL"""
        # Token może być przekazany jako parametr GET
        token = request.GET.get('token')
        if token:
            return token
        
        # Lub jako część ścieżki URL /wesele/TOKEN/
        path_parts = request.path.strip('/').split('/')
        if len(path_parts) >= 2 and path_parts[0] == 'wesele':
            return path_parts[1]
        
        return None

    def validate_token(self, token):
        """Waliduje token dostępu"""
        if not token:
            return False
        
        # Pobierz poprawny token z ustawień
        correct_token = getattr(settings, 'WEDDING_ACCESS_TOKEN', 'DEMO2024')
        
        # Prosta walidacja - możesz to ulepszyć
        if token == correct_token:
            return True
        
        # Opcjonalnie: walidacja z HMAC dla większego bezpieczeństwa
        secret_key = getattr(settings, 'SECRET_KEY', '')
        expected_hmac = hmac.new(
            secret_key.encode(),
            correct_token.encode(),
            hashlib.sha256
        ).hexdigest()[:12]  # Skróć do 12 znaków
        
        return token == expected_hmac

    def show_access_denied_page(self, request):
        """Pokazuje stronę z odmową dostępu"""
        html_content = """
        <!DOCTYPE html>
        <html lang="pl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dostęp do Aplikacji Weselnej</title>
            <style>
                body {
                    font-family: Georgia, serif;
                    background: linear-gradient(135deg, #f5f0e8 0%, #e8ddd4 100%);
                    color: #5d4e37;
                    margin: 0;
                    padding: 20px;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .access-card {
                    background: rgba(248, 245, 240, 0.95);
                    border: 1px solid rgba(212, 196, 168, 0.5);
                    border-radius: 20px;
                    padding: 40px 30px;
                    text-align: center;
                    max-width: 400px;
                    box-shadow: 0 12px 24px rgba(93, 78, 55, 0.15);
                }
                .icon {
                    font-size: 4rem;
                    margin-bottom: 20px;
                    color: #8b6f47;
                }
                h1 {
                    color: #5d4e37;
                    margin-bottom: 20px;
                    font-size: 1.5rem;
                }
                .message {
                    margin-bottom: 30px;
                    line-height: 1.6;
                    color: #6b5b4f;
                }
                .qr-hint {
                    background: #f8f5f0;
                    border: 1px solid #d4c4a8;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 20px 0;
                }
                .btn {
                    background: linear-gradient(145deg, #8b6f47, #5d4e37);
                    color: #f5f0e8;
                    padding: 12px 25px;
                    border: none;
                    border-radius: 25px;
                    text-decoration: none;
                    display: inline-block;
                    margin: 10px;
                    font-weight: bold;
                }
                .demo-link {
                    margin-top: 20px;
                    font-size: 0.9rem;
                    color: #8b6f47;
                }
            </style>
        </head>
        <body>
            <div class="access-card">
                <div class="icon">💐</div>
                <h1>Witamy na naszym weselu!</h1>
                <div class="message">
                    Aby uzyskać dostęp do aplikacji weselnej, zeskanuj kod QR 
                    znajdujący się na Waszych stolikach lub przy wejściu do sali.
                </div>
                <div class="qr-hint">
                    <strong>📱 Jak to działa?</strong><br>
                    1. Otwórz aparat w telefonie<br>
                    2. Zeskanuj kod QR<br>
                    3. Kliknij w link<br>
                    4. Gotowe! 🎉
                </div>
                <div class="demo-link">
                    <small>
                        Demo: <a href="?token=DEMO2024" style="color: #8b6f47;">Kliknij tutaj aby przetestować</a>
                    </small>
                </div>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html_content, content_type='text/html')


class WeddingSetupMiddleware:
    """Middleware to ensure wedding info is set up"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip for admin and static files
        if (request.path.startswith('/admin/') or 
            request.path.startswith('/static/') or
            request.path.startswith('/media/')):
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