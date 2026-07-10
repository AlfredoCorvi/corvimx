from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.html import strip_tags
import re


def _rechazar_html(valor, mensaje='Este campo no debe contener etiquetas HTML.'):
    """Rechaza (en vez de solo limpiar) cualquier entrada que contenga
    etiquetas HTML, como defensa adicional en servidor contra XSS
    almacenado, además del auto-escape que ya aplican los templates
    de Django."""
    if valor and strip_tags(valor) != valor:
        raise forms.ValidationError(mensaje)
    return valor


class RegistroForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50,
        label='Nombre',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'}),
    )
    last_name = forms.CharField(
        max_length=50,
        label='Apellido',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu apellido'}),
    )
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'usuario123'}),
        }
        labels = {
            'username': 'Nombre de usuario',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': '••••••••'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': '••••••••'})
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise forms.ValidationError('Solo letras, números y guion bajo.')
        return username

    def clean_first_name(self):
        return _rechazar_html(self.cleaned_data.get('first_name', ''))

    def clean_last_name(self):
        return _rechazar_html(self.cleaned_data.get('last_name', ''))

    # Verificación humana: el frontend solo maneja la UI del checkbox;
    # aquí se valida de forma obligatoria en el servidor.
    captcha_ok = forms.CharField(required=True)

    def clean_captcha_ok(self):
        valor = self.cleaned_data.get('captcha_ok')
        if valor != '1':
            raise forms.ValidationError('Debes confirmar que no eres un robot.')
        return valor


class ContactoForm(forms.Form):
    nombre = forms.CharField(
        max_length=100,
        label='Nombre',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre completo'}),
    )
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
    )
    asunto = forms.CharField(
        max_length=150,
        label='Asunto',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Asunto de tu mensaje'}),
    )
    mensaje = forms.CharField(
        label='Mensaje',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Escribe tu mensaje aquí...'}),
        min_length=20,
        max_length=5000,
    )
    # Verificación humana: validada obligatoriamente en el servidor.
    captcha_ok = forms.CharField(required=True)

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '')
        if any(char.isdigit() for char in nombre):
            raise forms.ValidationError('El nombre no debe contener números.')
        return _rechazar_html(nombre)

    def clean_asunto(self):
        return _rechazar_html(self.cleaned_data.get('asunto', ''))

    def clean_mensaje(self):
        return _rechazar_html(self.cleaned_data.get('mensaje', ''))

    def clean_captcha_ok(self):
        valor = self.cleaned_data.get('captcha_ok')
        if valor != '1':
            raise forms.ValidationError('Confirma que no eres un robot.')
        return valor


class BuzonForm(forms.Form):
    asunto = forms.CharField(
        max_length=150,
        label='Asunto',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Asunto del mensaje'}),
    )
    mensaje = forms.CharField(
        label='Mensaje',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Tu mensaje...'}),
        min_length=10,
        max_length=5000,
    )

    def clean_asunto(self):
        return _rechazar_html(self.cleaned_data.get('asunto', ''))

    def clean_mensaje(self):
        return _rechazar_html(self.cleaned_data.get('mensaje', ''))


class BusquedaForm(forms.Form):
    q = forms.CharField(
        max_length=200,
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar en el sitio...',
            'autocomplete': 'off',
        }),
    )

    def clean_q(self):
        return _rechazar_html(self.cleaned_data.get('q', ''))
