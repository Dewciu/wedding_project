# wedding/models.py - Szybka poprawka konfliktu

from django.db import models
from django.contrib.auth.models import User
from PIL import Image
# Importy dla Cloudinary
from django.conf import settings
import cloudinary
import cloudinary.uploader
from cloudinary import CloudinaryImage

class WeddingInfo(models.Model):
    bride_name = models.CharField(max_length=100, verbose_name="Imię Panny Młodej")
    groom_name = models.CharField(max_length=100, verbose_name="Imię Pana Młodego")
    wedding_date = models.DateField(verbose_name="Data Ślubu")
    venue_name = models.CharField(max_length=200, verbose_name="Miejsce Wesela")
    welcome_message = models.TextField(verbose_name="Wiadomość Powitalna")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Informacje o Weselu"
        verbose_name_plural = "Informacje o Weselu"
    
    def __str__(self):
        return f"{self.bride_name} & {self.groom_name}"

class Guest(models.Model):
    # DODAŁEM related_name żeby uniknąć konfliktu
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='wedding_guest_profile'
    )
    phone_number = models.CharField(max_length=15, blank=True, verbose_name="Numer telefonu")
    table_number = models.IntegerField(null=True, blank=True, verbose_name="Numer stołu")
    chair_position = models.IntegerField(null=True, blank=True, verbose_name="Pozycja krzesła", help_text="Pozycja krzesła przy stole (1-N)")
    guest_type = models.CharField(max_length=50, blank=True, verbose_name="Typ gościa")
    dietary_requirements = models.TextField(blank=True, verbose_name="Wymagania dietetyczne")
    plus_one = models.BooleanField(default=False, verbose_name="Osoba towarzysząca")
    confirmed = models.BooleanField(default=True, verbose_name="Potwierdzony")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Gość"
        verbose_name_plural = "Goście"
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Table(models.Model):
    SHAPE_CHOICES = [
        ('circular', 'Okrągły'),
        ('rectangular', 'Prostokątny'),
        ('square', 'Kwadratowy'),
    ]
    
    number = models.IntegerField(unique=True, verbose_name="Numer stołu")
    name = models.CharField(max_length=100, blank=True, verbose_name="Nazwa stołu")
    capacity = models.IntegerField(default=8, verbose_name="Miejsca")
    description = models.TextField(blank=True, verbose_name="Opis")
    
    # Pozycja i wymiary stołu na mapie (współrzędne Leaflet)
    map_x = models.FloatField(default=300, verbose_name="Pozycja X", help_text="Współrzędna X na mapie (0-900)")
    map_y = models.FloatField(default=300, verbose_name="Pozycja Y", help_text="Współrzędna Y na mapie (0-600)")
    map_width = models.FloatField(default=85, verbose_name="Szerokość", help_text="Szerokość stołu na mapie")
    map_height = models.FloatField(default=85, verbose_name="Wysokość", help_text="Wysokość stołu na mapie")
    shape = models.CharField(max_length=20, choices=SHAPE_CHOICES, default='circular', verbose_name="Kształt stołu")
    
    # Opcje wizualne
    color = models.CharField(max_length=7, default='#d4c4a8', verbose_name="Kolor", help_text="Kolor w formacie hex np. #d4c4a8")
    border_color = models.CharField(max_length=7, default='#b8a082', verbose_name="Kolor obramowania", help_text="Kolor obramowania hex")
    
    class Meta:
        verbose_name = "Stół"
        verbose_name_plural = "Stoły"
        ordering = ['number']
    
    def __str__(self):
        return f"Stół {self.number}" + (f" - {self.name}" if self.name else "")
    
    @property
    def guests_count(self):
        return Guest.objects.filter(table_number=self.number).count()
    
    @property
    def available_seats(self):
        return self.capacity - self.guests_count
    
    @property
    def occupancy_percentage(self):
        if self.capacity > 0:
            return int((self.guests_count / self.capacity) * 100)
        return 0

class Photo(models.Model):
    CATEGORY_CHOICES = [
        ('ceremony', '💒 Ceremonia'),
        ('reception', '🎉 Przyjęcie'),
        ('party', '💃 Zabawa'),
        ('preparations', '👗 Przygotowania'),
        ('family', '👨‍👩‍👧‍👦 Rodzina'),
        ('friends', '👥 Przyjaciele'),
        ('other', '📷 Inne'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Tytuł")
    description = models.TextField(blank=True, verbose_name="Opis")
    image = models.ImageField(upload_to='photos/%Y/%m/', verbose_name="Zdjęcie")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', verbose_name="Kategoria")
    
    # NAPRAWIONY: Dodałem related_name żeby uniknąć konfliktu z cloudinary.Photo
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='wedding_photos',  # <-- KLUCZOWA ZMIANA!
        verbose_name="Przesłane przez"
    )
    
    # Dodajemy pole dla nazwy anonimowego użytkownika
    uploader_name = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="Imię przesyłającego",
        help_text="Dla gości bez konta"
    )
    
    approved = models.BooleanField(default=False, verbose_name="Zatwierdzone")
    featured = models.BooleanField(default=False, verbose_name="Wyróżnione")
    upload_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Zdjęcie"
        verbose_name_plural = "Zdjęcia"
        ordering = ['-upload_date']
    
    def __str__(self):
        return self.title
    
    @property
    def uploader_display_name(self):
        """Zwraca nazwę osoby przesyłającej - użytkownika lub anonimową"""
        if self.uploaded_by:
            return f"{self.uploaded_by.first_name} {self.uploaded_by.last_name}".strip()
        elif self.uploader_name:
            return self.uploader_name
        else:
            return "Anonimowy gość"
    
    def get_cloudinary_url(self, **kwargs):
        """Generuje URL dla Cloudinary z opcjami transformacji"""
        if not self.image:
            return None
            
        # Sprawdź czy używamy Cloudinary
        if not getattr(settings, 'USE_CLOUDINARY', False):
            return self.image.url
            
        try:
            # Napraw błędny URL (brakujący ukośnik)
            image_url = str(self.image)
            if 'https:/res.cloudinary.com' in image_url:
                image_url = image_url.replace('https:/res.cloudinary.com', 'https://res.cloudinary.com')
            
            # Jeśli URL już zawiera transformacje Cloudinary, zwróć poprawiony URL
            if 'cloudinary.com' in image_url:
                # Wyciągnij public_id z URLa Cloudinary
                # Format: https://res.cloudinary.com/cloud_name/image/upload/public_id
                parts = image_url.split('/upload/')
                if len(parts) > 1:
                    public_id = parts[1].split('?')[0]  # Usuń query params jeśli są
                    # Usuń rozszerzenie pliku
                    public_id = public_id.rsplit('.', 1)[0] if '.' in public_id else public_id
                else:
                    # Fallback - użyj prostej metody
                    public_id = image_url.split('/')[-1].rsplit('.', 1)[0]
                
                # Generuj URL z Cloudinary
                cloudinary_image = CloudinaryImage(public_id)
                return cloudinary_image.build_url(**kwargs)
            else:
                # Lokalny plik - użyj nazwy bez rozszerzenia
                public_id = str(self.image).rsplit('.', 1)[0]
                cloudinary_image = CloudinaryImage(public_id)
                return cloudinary_image.build_url(**kwargs)
            
        except Exception as e:
            print(f"Błąd przy generowaniu Cloudinary URL: {e}")
            # Zwróć poprawiony podstawowy URL
            fixed_url = str(self.image.url) if self.image else None
            if fixed_url and 'https:/res.cloudinary.com' in fixed_url:
                fixed_url = fixed_url.replace('https:/res.cloudinary.com', 'https://res.cloudinary.com')
            return fixed_url
    
    def get_thumbnail_url(self):
        """URL do miniaturki zdjęcia w bardzo wysokiej jakości (800x800)"""
        return self.get_cloudinary_url(
            width=800,
            height=800,
            crop='fill',
            quality='auto:best',
            fetch_format='auto',
            dpr='auto'  # Automatyczne dostosowanie do gęstości pikseli
        )
    
    def get_optimized_url(self):
        """URL do zoptymalizowanego zdjęcia w bardzo wysokiej jakości (1800px szerokość)"""
        return self.get_cloudinary_url(
            width=1800,
            quality='auto:best',
            fetch_format='auto',
            dpr='auto'  # Automatyczne dostosowanie do gęstości pikseli
        )
    
    def get_full_size_url(self):
        """URL do pełnego zdjęcia w najwyższej jakości"""
        return self.get_cloudinary_url(
            quality='auto:best',
            fetch_format='auto',
            dpr='auto'  # Automatyczne dostosowanie do gęstości pikseli
        )
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Optymalizacja zdjęć tylko dla lokalnego środowiska - dla Cloudinary ta optymalizacja jest niepotrzebna
        if self.image and not getattr(settings, 'USE_CLOUDINARY', False):
            try:
                img = Image.open(self.image.path)
                if img.height > 2400 or img.width > 2400:
                    # Zwiększamy maksymalny rozmiar dla lepszej jakości
                    output_size = (2400, 2400)
                    img.thumbnail(output_size, Image.Resampling.LANCZOS)
                    # Zwiększamy jakość do 95%
                    img.save(self.image.path, optimize=True, quality=95)
            except Exception as e:
                print(f"Błąd przy optymalizacji zdjęcia: {e}")
    
    # METODY DO OBSŁUGI URL-I CLOUDINARY (FALLBACK)
    def get_cloudinary_url_simple(self, size='medium'):
        """Zwraca URL do zdjęcia w chmurze Cloudinary w podanym rozmiarze."""
        if self.image:
            try:
                # Napraw błędny URL jeśli potrzeba
                image_url = str(self.image.url)
                if 'https:/res.cloudinary.com' in image_url:
                    return image_url.replace('https:/res.cloudinary.com', 'https://res.cloudinary.com')
                
                cloudinary_image = CloudinaryImage(self.image.name)
                return cloudinary_image.build_url(width=size, height=size, crop="limit")
            except Exception as e:
                print(f"Błąd przy generowaniu URL Cloudinary: {e}")
                # Zwróć poprawiony podstawowy URL
                if self.image.url and 'https:/res.cloudinary.com' in str(self.image.url):
                    return str(self.image.url).replace('https:/res.cloudinary.com', 'https://res.cloudinary.com')
        return ""
    
    def delete(self, *args, **kwargs):
        """Nadpisana metoda usuwania, aby także usuwać zdjęcia z Cloudinary."""
        if self.image:
            try:
                # Usuń zdjęcie z Cloudinary
                cloudinary.uploader.destroy(self.image.name, invalidate=True)
            except Exception as e:
                print(f"Błąd przy usuwaniu zdjęcia z Cloudinary: {e}")
        super().delete(*args, **kwargs)

class ScheduleEvent(models.Model):
    title = models.CharField(max_length=200, verbose_name="Tytuł")
    description = models.TextField(blank=True, verbose_name="Opis")
    start_time = models.TimeField(verbose_name="Czas rozpoczęcia")
    end_time = models.TimeField(null=True, blank=True, verbose_name="Czas zakończenia")
    location = models.CharField(max_length=200, blank=True, verbose_name="Miejsce")
    order = models.IntegerField(default=0, verbose_name="Kolejność")
    
    class Meta:
        ordering = ['order', 'start_time']
        verbose_name = "Wydarzenie"
        verbose_name_plural = "Wydarzenia"
    
    def __str__(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.title}"

class MenuItem(models.Model):
    COURSE_CHOICES = [
        ('appetizer', '🥗 Przystawka'),
        ('soup', '🍲 Zupa'), 
        ('main', '🍖 Danie główne'),
        ('dessert', '🍰 Deser'),
        ('drink', '🥤 Napój'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nazwa")
    description = models.TextField(blank=True, verbose_name="Opis")
    course = models.CharField(max_length=20, choices=COURSE_CHOICES, verbose_name="Kategoria")
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Cena")
    allergens = models.CharField(max_length=200, blank=True, verbose_name="Alergeny")
    vegetarian = models.BooleanField(default=False, verbose_name="Wegetariańskie")
    order = models.IntegerField(default=0, verbose_name="Kolejność")
    
    class Meta:
        ordering = ['course', 'order', 'name']
        verbose_name = "Pozycja Menu"
        verbose_name_plural = "Pozycje Menu"
    
    def __str__(self):
        return self.name