from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.timezone import make_aware

from app.models import Event, RefundRequest, Ticket

User = get_user_model()

class RefundRequestIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        self.event = Event.objects.create(
            title="Evento Integración",
            description="Evento de prueba integración",
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

        # Solicitud pendiente existente
        RefundRequest.objects.create(
            ticket_code=self.ticket.ticket_code,
            reason="Motivo anterior",
            user=self.user,
            status="pendiente"
        )

    def test_integration_user_with_pending_refund_redirected(self):
        # El usuario intenta acceder al formulario de nueva solicitud
        response = self.client.get(reverse("refund_create"), follow=True)

        # Verifica que fue redirigido correctamente
        self.assertRedirects(response, reverse("refund_list"))

        # Verifica que el mensaje de advertencia exacto esté presente
        messages = list(response.context["messages"])
        self.assertIn("Ya tienes una solicitud de reembolso pendiente.", [str(msg) for msg in messages])


