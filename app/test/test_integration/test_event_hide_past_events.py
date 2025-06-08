from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from app.models import Event


class IntegrationHidePastEventsTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.organizer = User.objects.create_user(username="testuser", password="12345")

        # Crear eventos pasados y futuros
        self.past_event = Event.objects.create(
            title="Pasado",
            scheduled_at=now() - timedelta(days=1),
            organizer=self.organizer
        )
        self.future_event = Event.objects.create(
            title="Futuro",
            scheduled_at=now() + timedelta(days=1),
            organizer=self.organizer
        )

    def test_event_list_hides_past_events(self):
        # Loguear al usuario antes de acceder a la vista protegida
        self.client.login(username="testuser", password="12345")

        # URL de la vista que lista los eventos
        url = reverse('events')  
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Verificar que el evento futuro esté en la respuesta
        self.assertContains(response, "Futuro")

        # Verificar que el evento pasado NO esté en la respuesta
        self.assertNotContains(response, "Pasado")