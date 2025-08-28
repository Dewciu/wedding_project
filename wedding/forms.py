from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, HTML
from .models import Photo

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class MultiPhotoUploadForm(forms.Form):
    # Pole na wiele plików
    photos = MultipleFileField(
        widget=MultipleFileInput(attrs={
            'accept': 'image/*',
            'class': 'form-control-file',
            'id': 'photo-files'
        }),
        help_text="Wybierz wiele zdjęć naraz",
        required=True
    )
    
    # Opcjonalne pola
    uploader_name = forms.CharField(
        max_length=100, 
        required=False,
        label="Twoje imię (opcjonalne)",
        widget=forms.TextInput(attrs={
            'placeholder': 'np. Anna i Tomek', 
            'class': 'form-control'
        })
    )
    
    category = forms.ChoiceField(
        choices=Photo.CATEGORY_CHOICES,
        required=False,
        initial='party',
        label="Kategoria (opcjonalnie)",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 2, 
            'placeholder': 'Opcjonalny komentarz do wszystkich zdjęć...', 
            'class': 'form-control'
        }),
        required=False,
        label="Komentarz (opcjonalnie)"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'multi-upload-form'
        self.helper.layout = Layout(
            HTML('<div class="upload-section">'),
            HTML('<h5 style="color: #5d4e37; margin-bottom: 15px;"><i class="fas fa-images"></i> Wybierz zdjęcia:</h5>'),
            Field('photos'),
            HTML('<div id="photo-preview" class="mt-3"></div>'),
            HTML('</div>'),
            
            HTML('<div class="details-section mt-4" style="background: #f8f5f0; padding: 20px; border-radius: 10px;">'),
            HTML('<h6 style="color: #5d4e37; margin-bottom: 15px;"><i class="fas fa-edit"></i> Opcjonalne detale:</h6>'),
            Field('uploader_name'),
            Field('category'),
            Field('description'),
            HTML('</div>'),
            
            HTML('<div class="upload-controls mt-4">'),
            Submit('submit', 'Prześlij wszystkie zdjęcia', 
                   css_class='btn btn-custom-primary btn-lg btn-block', 
                   id='upload-button'),
            HTML('<div id="upload-progress" class="mt-3" style="display: none;"></div>'),
            HTML('</div>')
        )

class TableSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Wpisz swoje imię i/lub nazwisko...',
            'class': 'form-control form-control-lg'
        }),
        label="",
        required=False
    )

# Usuwamy GuestRegistrationForm ponieważ nie potrzebujemy już rejestracji