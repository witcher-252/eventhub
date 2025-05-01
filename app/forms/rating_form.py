from django import forms
from django.core.exceptions import ValidationError

class RatingForm(forms.Form):
    tituloR = forms.CharField(
        label="Título de tu reseña *",
        max_length=100,
        min_length=5,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'tituloR',
            'placeholder': 'Ej: Gran experiencia'
        })
    )

    idEventoRating = forms.IntegerField(
        widget=forms.HiddenInput(attrs={'id': 'idEventoRating'})
    )

    califiqueR = forms.IntegerField(
        widget=forms.HiddenInput(attrs={'id': 'califiqueR'})
    )

    descripcionR = forms.CharField(
        label="Tu reseña (opcional)",
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'id': 'descripcionR',
            'placeholder': 'Comparte tu experiencia...'
        })
    )

    # Validación individual para califiqueR
    def clean_califiqueR(self):
        calificacion = self.cleaned_data['califiqueR']
        if not 1 <= calificacion <= 5:
            raise ValidationError("La calificación debe estar entre 1 y 5.")
        return calificacion

    # Validación individual para título
    def clean_tituloR(self):
        titulo = self.cleaned_data['tituloR'].strip()
        if len(titulo) < 5:
            raise ValidationError("El título debe tener al menos 5 caracteres.")
        return titulo