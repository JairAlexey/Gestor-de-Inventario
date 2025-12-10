from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Producto, Categoria  # Asegúrate de importar los modelos


# Clase CSS reutilizable para cumplir límite de longitud de línea
INPUT_CLASS = (
    "appearance-none block w-full px-3 py-2 border border-gray-300 "
    "rounded-md shadow-sm placeholder-gray-400 focus:outline-none "
    "focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
)


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'type': 'email'})
        self.fields['username'].label = 'Correo electrónico'

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if not email:
            raise ValidationError('El correo electrónico es obligatorio')
        if not password:
            raise ValidationError('La contraseña es obligatoria')

        return super().clean()


class ProductoForm(forms.ModelForm):
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        widget=forms.Select(attrs={'class': INPUT_CLASS})
    )

    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'cantidad_stock', 'categoria']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Nombre del producto'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Descripción del producto',
                'rows': '3'
            }),
            'precio': forms.NumberInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'cantidad_stock': forms.NumberInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': '0'
            }),
        }
