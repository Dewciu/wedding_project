from django.core.management.base import BaseCommand
from django.conf import settings
import secrets
import string
import qrcode
from io import BytesIO

class Command(BaseCommand):
    help = 'Zarządza tokenem dostępu do aplikacji weselnej'

    def add_arguments(self, parser):
        parser.add_argument(
            '--generate',
            action='store_true',
            help='Generuje nowy bezpieczny token',
        )
        parser.add_argument(
            '--show-current',
            action='store_true',
            help='Pokazuje aktualny token',
        )
        parser.add_argument(
            '--validate',
            type=str,
            help='Sprawdza czy podany token jest poprawny',
        )
        parser.add_argument(
            '--create-qr',
            action='store_true',
            help='Tworzy plik QR kodu (wymaga PIL)',
        )
        parser.add_argument(
            '--custom-token',
            type=str,
            help='Ustawia custom token (np. ANNA_TOMEK_2024)',
        )

    def handle(self, *args, **options):
        current_token = getattr(settings, 'WEDDING_ACCESS_TOKEN', 'DEMO2024')
        
        if options['show_current']:
            self.show_current_token(current_token)
            
        elif options['generate']:
            self.generate_new_token()
            
        elif options['validate']:
            self.validate_token(options['validate'], current_token)
            
        elif options['create_qr']:
            self.create_qr_code(current_token)
            
        elif options['custom_token']:
            self.suggest_custom_token(options['custom_token'])
            
        else:
            self.show_help()

    def show_current_token(self, token):
        self.stdout.write(self.style.SUCCESS('🔑 Aktualny token dostępu:'))
        self.stdout.write(f'   {token}')
        self.stdout.write('')
        self.stdout.write('📱 URL dostępu:')
        self.stdout.write(f'   http://localhost:8000/?token={token}')
        
    def generate_new_token(self):
        """Generuje bezpieczny token"""
        # Generuj 12-znakowy token z liter i cyfr
        alphabet = string.ascii_uppercase + string.digits
        secure_token = ''.join(secrets.choice(alphabet) for _ in range(12))
        
        self.stdout.write(self.style.SUCCESS('🔐 Wygenerowany bezpieczny token:'))
        self.stdout.write(f'   {secure_token}')
        self.stdout.write('')
        self.stdout.write('💡 Aby go użyć, dodaj do .env:')
        self.stdout.write(f'   WEDDING_ACCESS_TOKEN={secure_token}')
        self.stdout.write('')
        self.stdout.write('🔄 Potem zrestartuj serwer Django')

    def validate_token(self, test_token, current_token):
        """Sprawdza czy token jest poprawny"""
        if test_token == current_token:
            self.stdout.write(self.style.SUCCESS('✅ Token jest POPRAWNY'))
        else:
            self.stdout.write(self.style.ERROR('❌ Token jest NIEPOPRAWNY'))
            self.stdout.write(f'   Oczekiwany: {current_token}')
            self.stdout.write(f'   Otrzymany:  {test_token}')

    def create_qr_code(self, token):
        """Tworzy plik QR kodu"""
        try:
            # URL z tokenem
            url = f"http://localhost:8000/?token={token}"
            
            # Generuj QR kod
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            # Zapisz do pliku
            img = qr.make_image(fill_color="black", back_color="white")
            filename = f"wedding_qr_{token}.png"
            img.save(filename)
            
            self.stdout.write(self.style.SUCCESS(f'📱 QR kod zapisany jako: {filename}'))
            self.stdout.write(f'🔗 URL: {url}')
            
        except ImportError:
            self.stdout.write(
                self.style.ERROR('❌ Brak biblioteki qrcode. Zainstaluj: pip install qrcode[pil]')
            )

    def suggest_custom_token(self, custom_token):
        """Sugeruje formatowanie custom tokenu"""
        # Oczyść i sformatuj token
        clean_token = custom_token.upper().replace(' ', '_').replace('-', '_')
        
        # Usuń polskie znaki
        replacements = {
            'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N',
            'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
        }
        for pl, en in replacements.items():
            clean_token = clean_token.replace(pl, en)
        
        # Pozostaw tylko litery, cyfry i podkreślenia
        clean_token = ''.join(c for c in clean_token if c.isalnum() or c == '_')
        
        self.stdout.write(self.style.SUCCESS('🎨 Sugerowany format tokenu:'))
        self.stdout.write(f'   Oryginalny: {custom_token}')
        self.stdout.write(f'   Oczyszczony: {clean_token}')
        self.stdout.write('')
        self.stdout.write('💡 Dodaj do .env:')
        self.stdout.write(f'   WEDDING_ACCESS_TOKEN={clean_token}')
        
        # Sprawdź długość
        if len(clean_token) < 8:
            self.stdout.write(self.style.WARNING('⚠️  Token jest krótki (< 8 znaków). Rozważ dodanie roku lub daty.'))
        elif len(clean_token) > 30:
            self.stdout.write(self.style.WARNING('⚠️  Token jest długi (> 30 znaków). QR kod może być trudny do zeskanowania.'))

    def show_help(self):
        """Pokazuje pomoc"""
        self.stdout.write(self.style.SUCCESS('🎉 Manager Tokenu Dostępu - Aplikacja Weselna'))
        self.stdout.write('')
        self.stdout.write('Dostępne opcje:')
        self.stdout.write('  --show-current        Pokaż aktualny token')
        self.stdout.write('  --generate            Wygeneruj bezpieczny token')
        self.stdout.write('  --validate TOKEN      Sprawdź czy token jest poprawny')
        self.stdout.write('  --create-qr           Stwórz QR kod')
        self.stdout.write('  --custom-token TEXT   Sformatuj custom token')
        self.stdout.write('')
        self.stdout.write('Przykłady:')
        self.stdout.write('  python manage.py manage_access_token --show-current')
        self.stdout.write('  python manage.py manage_access_token --generate')
        self.stdout.write('  python manage.py manage_access_token --custom-token "Anna i Tomek 2024"')
        self.stdout.write('  python manage.py manage_access_token --validate DEMO2024')
        self.stdout.write('  python manage.py manage_access_token --create-qr')