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

    def test_integration_user_can_create_refund_if_none_pending(self):
        # Eliminamos la solicitud pendiente creada en setUp
        RefundRequest.objects.all().delete()

        form_data = {
            "ticket_code": str(self.ticket.ticket_code),
            "reason": "Motivo válido de integración"
        }
        response = self.client.post(reverse("refund_create"), data=form_data, follow=True)

        self.assertRedirects(response, reverse("refund_list"))
        self.assertTrue(RefundRequest.objects.filter(user=self.user, reason="Motivo válido de integración").exists())
        messages = list(response.context["messages"])
        self.assertIn("Tu solicitud de reembolso fue enviada con éxito.", [str(msg) for msg in messages])

    def test_integration_refund_fails_with_invalid_ticket_code(self):
        # Asegura que no haya solicitudes pendientes para que no redirija
        RefundRequest.objects.all().delete()

        form_data = {
            "ticket_code": "99999999",  # Código inválido
            "reason": "Motivo válido"
        }

        response = self.client.post(reverse("refund_create"), data=form_data)
        
        # Verifica que NO redirige (sigue en el formulario)
        self.assertEqual(response.status_code, 200)

        # Asegura que el formulario esté presente en el contexto
        self.assertIn("form", response.context)

        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("ticket_code", form.errors)
        self.assertIn(
            "El ticket ingresado no existe o no pertenece a tu cuenta.",
            form.errors["ticket_code"]
        )

