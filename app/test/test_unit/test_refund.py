from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.timezone import make_aware

from app.models import Event, RefundRequest, Ticket

User = get_user_model()

class RefundRequestViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

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

        # Crear una solicitud de reembolso pendiente existente
        RefundRequest.objects.create(
            ticket_code=self.ticket.ticket_code,
            reason="Motivo de prueba",
            user=self.user,
            status="pendiente"
        )

    def test_create_refund_fails_if_pending_exists(self):
        response = self.client.post(reverse("refund_create"), {
            "ticket_code": self.ticket.ticket_code,
            "reason": "Otro motivo"
        })

        # Verifica redirección a refund_list porque ya tiene una solicitud pendiente
        self.assertRedirects(response, reverse("refund_list"))

        # Verifica que NO se haya creado una segunda solicitud
        self.assertEqual(RefundRequest.objects.filter(user=self.user).count(), 1)

        # Verifica que se haya mostrado el mensaje de advertencia
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Ya tienes una solicitud de reembolso pendiente.")
