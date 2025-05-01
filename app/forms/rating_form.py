from django import forms

class RatingForm(forms.Form):
    tituloR = forms.CharField(
        label="Título de tu reseña *",
        max_length=100,
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
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'id': 'descripcionR',
            'placeholder': 'Comparte tu experiencia...'
        })
    )