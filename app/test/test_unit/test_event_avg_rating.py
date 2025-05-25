import datetime

from django.test import TestCase
from django.utils import timezone

from app.models import Event, User, Rating

class EventRatingTestCase(TestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(
            username="organizador_test",
            email="organizador@example.com",
            password="password123",
            is_organizer=True,
        )

        # Crear evento
        self.event = Event.objects.create(
            title="Evento de prueba",
            description="Descripción del evento de prueba",
            scheduled_at=timezone.now() + datetime.timedelta(days=1),
            organizer=self.organizer,
        )
        self.regular_user = User.objects.create_user(
            username="regular",
            email="regular@test.com",
            password="password123",
            is_organizer=False,
        )

    def test_promedio_rating_sin_ratings(self):
        promedio = self.event.promedio_rating()
        self.assertEqual(promedio, 0)

    def test_promedio_rating_con_ratings(self):
        Rating.objects.create(
            usuario=self.regular_user,
            evento=self.event,
            title="Buena",
            text="Me gustó",
            rating=4
        )
        Rating.objects.create(
            usuario=self.regular_user,
            evento=self.event,
            title="Excelente",
            text="Muy buena experiencia",
            rating=5
        )
        Rating.objects.create(
            usuario=self.regular_user,
            evento=self.event,
            title="Regular",
            text="Podría mejorar",
            rating=3
        )

        promedio = self.event.promedio_rating()
        self.assertEqual(promedio, 4)  # (4 + 5 + 3) / 3 = 4.0

    def test_promedio_rating_con_rating_unico(self):
        Rating.objects.create(
            usuario=self.regular_user,
            evento=self.event,
            title="Excelente",
            text="Muy buena experiencia",
            rating=5
        )

        promedio = self.event.promedio_rating()
        self.assertEqual(promedio, 5)
