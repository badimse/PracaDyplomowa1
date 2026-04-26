from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, ClientProfile, ServiceProfile


class UserRegistrationForm(UserCreationForm):
    """Formularz rejestracji użytkownika"""
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']


class ClientProfileForm(forms.ModelForm):
    """Formularz profilu klienta"""
    class Meta:
        model = ClientProfile
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'postal_code', 'voivodeship']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
        }


class ServiceProfileForm(forms.ModelForm):
    """Formularz profilu serwisu"""
    class Meta:
        model = ServiceProfile
        fields = ['company_name', 'nip', 'email', 'phone', 'address', 'city', 'postal_code', 'voivodeship', 'description', 'specializes_in']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class LoginForm(AuthenticationForm):
    """Formularz logowania"""
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nazwa użytkownika'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Hasło'}))
