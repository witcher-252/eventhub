from django.test import TestCase
from django.core.exceptions import ValidationError
from ...models import Ticket, Event, User
from django.utils import timezone

class TicketModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="organizador_test",
            email="organizador@example.com",
            password="password123",
            is_organizer=True,
        )
        self.event = Event.objects.create(
            title="Evento de prueba",
            description="Descripción del evento de prueba",
            scheduled_at=timezone.now(),
            organizer=self.user,
        )

    def test_ticket_quantity_no_mayor_a_4(self):
        ticket = Ticket(
            usuario=self.user,
            evento=self.event,
            quantity=5,
            buy_date=timezone.now(),
            type="general"
        )
        with self.assertRaises(ValidationError) as context:
            ticket.save()

        self.assertIn("No se puede comprar más de 4 tickets", str(context.exception))

    def test_ticket_quantity_valida(self):
        ticket = Ticket(
            usuario=self.user,
            evento=self.event,
            quantity=3,
            buy_date=timezone.now(),
            type="general",
        )
        try:
            ticket.save()
        except ValidationError:
            self.fail("El ticket con quantity <= 4 no debería lanzar ValidationError")