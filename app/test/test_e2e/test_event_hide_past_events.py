import datetime
import re

from django.utils import timezone
from playwright.sync_api import expect

from app.models import Event, User

from app.test.test_e2e.base import BaseE2ETest

class EventVisibilityE2ETest(BaseE2ETest):
    def setUp(self):
        super().setUp()

        # Crear usuario organizador
        self.organizer = User.objects.create_user(
            username="organizador",
            email="organizador@example.com",
            password="password123",
            is_organizer=True,
        )

        # Crear eventos de prueba
        # Evento 1
        event_date1 = timezone.make_aware(datetime.datetime(2025, 2, 10, 10, 10))
        self.event1 = Event.objects.create(
            title="Evento Pasado",
            description="Descripción del evento 1",
            scheduled_at=event_date1,
            organizer=self.organizer,
        )

        event_date1 = timezone.make_aware(datetime.datetime(2026, 2, 10, 10, 10))
        self.event1 = Event.objects.create(
            title="Evento Futuro",
            description="Descripción del evento 1",
            scheduled_at=event_date1,
            organizer=self.organizer,
        )
    
    def test_only_future_events_visible(self):
         # Iniciar sesión como organizador
       self.login_user("organizador", "password123")

        # Ir a la página de eventos
       self.page.goto(f"{self.live_server_url}/events/")

       # Verificar que solo se vea el evento futuro
       expect(self.page.get_by_text("Evento Futuro")).to_be_visible()
       expect(self.page.get_by_text("Evento Pasado")).not_to_be_visible()