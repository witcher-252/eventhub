from django import forms
from datetime import datetime


class CompraTicketForm(forms.Form):
    TIPO_CHOICES = [('general', 'General'), ('VIP', 'VIP')]

    cantidad = forms.IntegerField(
        min_value=1,
        label='Cantidad de Tickets',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        label='Tipo de Ticket',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    numero_tarjeta = forms.CharField(
        max_length=16,
        label='Número de Tarjeta',
         widget=forms.TextInput(attrs={
        'class': 'form-control',
        'inputmode': 'numeric',  # Para mostrar teclado numérico en móviles
        'pattern': r'\d*',       # Solo dígitos
        'placeholder': 'Ej: 1234567812345678'
    })
    )
    expiracion = forms.DateField(
        input_formats=['%m/%y'],
        label='Fecha de Expiración',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/YY'})
    )
    cvv = forms.CharField(
        max_length=4,
        label='CVV',
         widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'inputmode': 'numeric',
        'pattern': r'\d{3,4}',
        'placeholder': 'Ej: 123'
    })
    )
    nombre_tarjeta = forms.CharField(
        max_length=100,
        label='Nombre en la Tarjeta',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    acepta_terminos = forms.BooleanField(
    required=True,
    label='Acepto los Términos y Condiciones y la Política de Privacidad'
    )
    id_evento = forms.IntegerField(widget=forms.HiddenInput())

    def clean_numero_tarjeta(self):
        data = self.cleaned_data['numero_tarjeta']
        if not data.isdigit():
            raise forms.ValidationError("El número de tarjeta debe contener solo dígitos.")
        if len(data) != 16:
            raise forms.ValidationError("El número de tarjeta debe tener exactamente 16 dígitos.")
        return data
    
    def clean_cvv(self):
        data = self.cleaned_data['cvv']
        if not data.isdigit():
            raise forms.ValidationError("El CVV debe contener solo números.")
        if len(data) not in [3, 4]:
            raise forms.ValidationError("El CVV debe tener 3 o 4 dígitos.")
        return data
    
    def clean_expiracion(self):
        expiracion = self.cleaned_data['expiracion']
        today = datetime.today()

        # Consideramos que la tarjeta expira al final del mes
        if expiracion.year < today.year or (expiracion.year == today.year and expiracion.month < today.month):
            raise forms.ValidationError("La tarjeta está vencida.")

        return expiracion

class TicketForm(forms.Form):
    ticketCode = forms.IntegerField(
        label="Código de ticket",
        widget=forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'})
    )

    buy_date = forms.DateTimeField(
    label="Fecha de compra",
    widget=forms.DateTimeInput(
        attrs={
            'readonly': 'readonly',
            'type': 'datetime-local',
            'class': 'form-control'
        },
        format='%Y-%m-%dT%H:%M'
    ),
    input_formats=['%Y-%m-%dT%H:%M']
    )
    
    cantidadTk = forms.IntegerField(
        label="Ingrese la cantidad",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    tipoEntrada = forms.ChoiceField(
        label="Seleccionó el tipo de Entrada",
        choices=[('general', 'general'), ('VIP', 'VIP')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
