#### forms.py
from django import forms

class SubscribeForm(forms.Form):
    email = forms.EmailField(label="Tu Correo Electrónico", widget=forms.EmailInput(attrs={'class': 'form-control'})) #aka almacenamos los datos del form con forms.Form de Django


# app/forms.py

from django import forms

class RegisterUserForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100) # <-- ¡CAMBIADO AQUÍ!
    username = forms.CharField(max_length=100)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

#class SubscribeForm(forms.Form):
#   email = forms.EmailField()
