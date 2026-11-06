from django import forms
from .models import Plant

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class PlantForm(forms.ModelForm):
    class Meta:
        model = Plant

        fields = (
            'name',
            'species',
            'acquired_date',
            'watering_interval',
            'last_watered',
            'location',
            'notes'
        )

        widgets = {
            'acquired_date': forms.DateInput(attrs={'type': 'date'}),
            'last_watered': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3})
        }

        labels = {
            'name': 'Назва рослини',
            'species': 'Вид рослини',
            'acquired_date': 'Дата придбання',
            'watering_interval': 'Інтервал поливу (днів)',
            'last_watered': 'Дата останнього поливу',
            'location': 'Розташування',
            'notes': 'Додаткова інформація'
        }


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')






