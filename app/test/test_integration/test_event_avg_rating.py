import datetime
import time

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from app.models import Event, User, Rating

class EventDetailIntegrationTest(TestCase):
    def setUp(self):
        # Usuario organizador
         self.organizer = User.objects.create_user(
            username="organizador_test",
            email="organizador@example.com",
            password="password123",
            is_organizer=True,
        )
        # Usuario no organizador
         self.regular_user = User.objects.create_user(
            username="regular",
            email="regular@test.com",
            password="password123",
            is_organizer=False,
        )
        # Crear algunos eventos de prueba
         self.event1 = Event.objects.create(
            title="Evento 1",
            description="Descripción del evento 1",
            scheduled_at=timezone.now() + datetime.timedelta(days=1),
            organizer=self.organizer,
        )

         Rating.objects.create(usuario=self.regular_user, evento=self.event1, title="Buena", text="Me gustó", rating=4)
         Rating.objects.create(usuario=self.regular_user, evento=self.event1, title="Excelente", text="Muy buena experiencia", rating=3)
         Rating.objects.create(usuario=self.regular_user, evento=self.event1, title="Buena", text="Me gustó", rating=3)
         Rating.objects.create(usuario=self.regular_user, evento=self.event1, title="Excelente", text="Muy buena experiencia", rating=1)

    def test_event_detail_muestra_promedio_si_es_organizador(self):

        self.client.login(username='organizador_test', password='password123')
        response = self.client.get(reverse("event_detail", args=[self.event1.id])) # type: ignore

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2,75")  # el promedio esperado

    def test_event_detail_no_muestra_promedio_si_no_es_organizador(self):
        self.client.login(username='regular', password='password123')
        response = self.client.get(reverse("event_detail", args=[self.event1.id])) # type: ignore

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "2,75")
