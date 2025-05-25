from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from ...models import Event, Ticket, User

class ConfirmTicketViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        # crea un usuario organizador
        self.organizer = User.objects.create_user(
            username="organizador",
            email="organizador@test.com",
            password="password123",
            is_organizer=True,
        )
         # Crear un usuario regular
        self.regular_user = User.objects.create_user(
            username="regular",
            email="regular@test.com",
            password="password123",
            is_organizer=False,
        )
        self.event = Event.objects.create(
            title="Evento de prueba",
            description="Descripción del evento de prueba",
            scheduled_at=timezone.now(),
            organizer=self.organizer,
        )
        self.url = reverse('confirm_ticket')  # Asegúrate que este nombre esté en tu urls.py

    def test_ticket_compra_valida(self):
        self.client.login(username="regular", password="password123")

        form_data = {
            'id_evento': self.event.pk,
            'cantidad': 2,
            'tipo': 'general',
            'numero_tarjeta': '1234567812345678',
            'expiracion': timezone.now().strftime('%m/%y'),
            'cvv': '123',
            'nombre_tarjeta': 'Juan Pérez',
            'acepta_terminos': True,
        }

        response = self.client.post(self.url, data=form_data)

        # Se espera una redirección si la compra fue válida
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Ticket.objects.filter(usuario=self.regular_user, evento=self.event).exists())


    def test_ticket_excede_limite(self):
        self.client.login(username="regular", password="password123")

        # Usuario ya compró 3 entradas
        Ticket.objects.create(usuario=self.regular_user, evento=self.event, quantity=3, type='general', buy_date=timezone.now())

        form_data = {
            'id_evento': self.event.pk,
            'cantidad': 2,
            'tipo': 'general',
            'numero_tarjeta': '1234567812345678',
            'expiracion': timezone.now().strftime('%m/%y'),
            'cvv': '123',
            'nombre_tarjeta': 'Juan Pérez',
            'acepta_terminos': True,
        }

        response = self.client.post(self.url, data=form_data)

        # Debe retornar el formulario con error (código 200, no redirección)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "superarías el límite de 4 entradas")
        self.assertEqual(Ticket.objects.filter(usuario=self.regular_user, evento=self.event).count(), 1)  # No se creó uno nuevo

    
