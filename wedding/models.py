from django.db import models
from django.contrib.auth.models import User
from PIL import Image

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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, verbose_name="Numer telefonu")
    table_number = models.IntegerField(null=True, blank=True, verbose_name="Numer stołu")
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
    number = models.IntegerField(unique=True, verbose_name="Numer stołu")
    name = models.CharField(max_length=100, blank=True, verbose_name="Nazwa stołu")
    capacity = models.IntegerField(default=8, verbose_name="Miejsca")
    description = models.TextField(blank=True, verbose_name="Opis")
    
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
        ('ceremony', 'Ceremonia'),
        ('reception', 'Przyjęcie'),
        ('party', 'Zabawa'),
        ('preparations', 'Przygotowania'),
        ('family', 'Rodzina'),
        ('friends', 'Przyjaciele'),
        ('other', 'Inne'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Tytuł")
    description = models.TextField(blank=True, verbose_name="Opis")
    image = models.ImageField(upload_to='photos/%Y/%m/', verbose_name="Zdjęcie")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', verbose_name="Kategoria")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Przesłane przez")
    approved = models.BooleanField(default=False, verbose_name="Zatwierdzone")
    featured = models.BooleanField(default=False, verbose_name="Wyróżnione")
    upload_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Zdjęcie"
        verbose_name_plural = "Zdjęcia"
        ordering = ['-upload_date']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 1200 or img.width > 1200:
                output_size = (1200, 1200)
                img.thumbnail(output_size)
                img.save(self.image.path)

class ScheduleEvent(models.Model):
    title = models.CharField(max_length=200, verbose_name="Tytuł")
    description = models.TextField(blank=True, verbose_name="Opis")
    start_time = models.TimeField(verbose_name="Godzina rozpoczęcia")
    end_time = models.TimeField(null=True, blank=True, verbose_name="Godzina zakończenia")
    location = models.CharField(max_length=200, blank=True, verbose_name="Miejsce")
    order = models.IntegerField(default=0, verbose_name="Kolejność")
    
    class Meta:
        verbose_name = "Wydarzenie"
        verbose_name_plural = "Wydarzenia"
        ordering = ['order', 'start_time']
    
    def __str__(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.title}"

class MenuItem(models.Model):
    COURSE_CHOICES = [
        ('welcome', 'Koktajl powitalny'),
        ('appetizer', 'Przystawka'),
        ('soup', 'Zupa'),
        ('main', 'Danie główne'),
        ('dessert', 'Deser'),
        ('drinks', 'Napoje'),
        ('other', 'Inne'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nazwa")
    description = models.TextField(verbose_name="Opis")
    course = models.CharField(max_length=20, choices=COURSE_CHOICES, verbose_name="Rodzaj")
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Cena")
    allergens = models.CharField(max_length=200, blank=True, verbose_name="Alergeny")
    vegetarian = models.BooleanField(default=False, verbose_name="Wegetariańskie")
    order = models.IntegerField(default=0, verbose_name="Kolejność")
    
    class Meta:
        verbose_name = "Pozycja Menu"
        verbose_name_plural = "Menu"
        ordering = ['course', 'order']
    
    def __str__(self):
        return self.name