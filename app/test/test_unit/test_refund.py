from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.timezone import make_aware

from app.forms.refund_request_form import RefundRequestForm
from app.models import Event, RefundRequest, Ticket

User = get_user_model()

class RefundRequestFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")

        self.event = Event.objects.create(
            title="Test Event",
            description="Test Description",
            scheduled_at=make_aware(datetime.now()),
            organizer=self.user,
        )

        self.ticket = Ticket.objects.create(
            usuario=self.user,
            evento=self.event,
            quantity=1,
            buy_date=make_aware(datetime.now()),
            type="general"
        )

        # Solicitud ya pendiente
        RefundRequest.objects.create(
            ticket_code=self.ticket.ticket_code,
            reason="Motivo existente",
            user=self.user,
            status="pendiente"
        )

    def test_refund_form_fails_if_pending_exists(self):
        form_data = {
            "ticket_code": str(self.ticket.ticket_code),
            "reason": "Motivo válido de prueba"
        }
        form = RefundRequestForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("Ya tienes una solicitud de reembolso pendiente.", form.non_field_errors())

    def test_refund_form_valid_if_no_pending_request(self):
        # Eliminamos la solicitud pendiente
        RefundRequest.objects.all().delete()

        form_data = {
            "ticket_code": str(self.ticket.ticket_code),
            "reason": "Motivo válido de prueba con más de 10 caracteres"
        }
        form = RefundRequestForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())

    def test_refund_form_fails_with_invalid_ticket_code(self):
        form_data = {
            "ticket_code": "999999",  # Un código que no existe
            "reason": "Motivo válido"
        }
        form = RefundRequestForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("El ticket ingresado no existe o no pertenece a tu cuenta.", form.errors["ticket_code"])
