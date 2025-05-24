from django import forms

from ..models import RefundRequest, Ticket


class RefundRequestForm(forms.ModelForm):
    class Meta:
        model = RefundRequest
        fields = ['ticket_code', 'reason']
        widgets = {
            'ticket_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código del ticket'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Motivo de la devolución'}),
        }

    # Validación para 'ticket_code'
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Capturamos el usuario desde la vista
        super().__init__(*args, **kwargs)

    def clean_ticket_code(self):
        ticket_code = self.cleaned_data.get('ticket_code')
        if not ticket_code:
            raise forms.ValidationError("El código de ticket no puede estar vacío.")
        
        if not str(ticket_code).isdigit():
            raise forms.ValidationError("El código de ticket debe ser un número.")

        try:
            Ticket.objects.get(ticket_code=ticket_code, usuario=self.user)
        except Ticket.DoesNotExist:
            raise forms.ValidationError("El ticket ingresado no existe o no pertenece a tu cuenta.")

        return ticket_code

    # Validación para 'reason'
    def clean_reason(self):
        reason = self.cleaned_data.get('reason')
        if not reason:
            raise forms.ValidationError("El motivo no puede estar vacío.")
        if len(reason) < 10:
            raise forms.ValidationError("El motivo debe tener al menos 10 caracteres.")
        return reason
