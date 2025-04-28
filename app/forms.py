from django import forms
from .models import Notification, Event
from django.contrib.auth.models import User

class NotificationForm(forms.ModelForm):
    destinatario_tipo = forms.ChoiceField(
        choices=[
            ('todos', 'Todos los asistentes del evento'),
            ('usuario', 'Usuario específico')
        ],
        widget=forms.RadioSelect,
        label="Destinatarios"
    )
    
    class Meta:
        model = Notification
        fields = ['title', 'message', 'priority', 'event', 'user', 'is_read']
        
             
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'event': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(choices=Notification.PRIORITY_CHOICES, attrs={'class': 'form-select'}),
            'is_read': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].label = "Selecciona un usuario"
        self.fields['user'].widget.attrs.update({'class': 'form-select'})
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and len(title.strip()) < 5:
            raise forms.ValidationError("El título debe tener al menos 5 caracteres.")
        return title

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if not message or message.strip() == "":
            raise forms.ValidationError("El mensaje no puede estar vacío.")
        return message

    def clean(self):
        cleaned_data = super().clean()
        destinatario_tipo = cleaned_data.get('destinatario_tipo')
        user = cleaned_data.get('user')

        if destinatario_tipo == 'usuario' and not user:
            raise forms.ValidationError("Debes seleccionar un usuario específico si el destinatario es 'usuario'.")    