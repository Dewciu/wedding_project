from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import Photo, Guest

class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'description', 'image', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Tytuł zdjęcia...'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Opisz zdjęcie...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('title', css_class='form-control-lg'),
            Field('description'),
            Field('category'),
            Field('image', css_class='form-control-file'),
            Submit('submit', 'Prześlij zdjęcie', css_class='btn btn-primary btn-lg btn-block')
        )

class GuestRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="Imię")
    last_name = forms.CharField(max_length=30, required=True, label="Nazwisko")
    email = forms.EmailField(required=True, label="Email")
    phone_number = forms.CharField(max_length=15, required=False, label="Telefon")
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
            ),
            Field('email'),
            Field('phone_number'),
            Field('username'),
            Field('password1'),
            Field('password2'),
            Submit('submit', 'Zarejestruj się', css_class='btn btn-success btn-lg btn-block')
        )
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            guest = Guest.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number']
            )
        return user

class TableSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Wpisz swoje imię i nazwisko...',
            'class': 'form-control form-control-lg'
        }),
        label="",
        required=False
    )