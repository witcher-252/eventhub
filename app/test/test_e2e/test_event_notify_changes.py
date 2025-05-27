from datetime import datetime, timedelta

from django.utils.timezone import make_aware
from playwright.sync_api import expect

from app.models import Event, Ticket, User
from app.test.test_e2e.base import BaseE2ETest


class NotifyUsersOnEventUpdateTest(BaseE2ETest):
    def setUp(self):
        super().setUp()

        self.organizer = User.objects.create_user(
            username="organizador",
            email="org@example.com",
            password="password123",
            is_organizer=True,
        )
        self.user1 = User.objects.create_user(username="user1", password="testpass")
        self.user2 = User.objects.create_user(username="user2", password="testpass")

        self.event = Event.objects.create(
            title="Evento Integración",
            description="Evento de prueba integración",
            location="Ubicación Original",
            scheduled_at=make_aware(datetime.now() + timedelta(days=7)),
            organizer=self.organizer,
        )

        Ticket.objects.create(
            usuario=self.user1,
            evento=self.event,
            quantity=2,
            buy_date=make_aware(datetime.now()),
            type="general"
        )
        Ticket.objects.create(
            usuario=self.user2,
            evento=self.event,
            quantity=1,
            buy_date=make_aware(datetime.now()),
            type="vip"
        )

    def test_notification_sent_on_event_date_change(self):
        # Login como organizador y editar solo la fecha
        self.login_user("organizador", "password123")
        self.page.goto(f"{self.live_server_url}/events/{self.event.id}/edit/") # type: ignore
        self.page.fill("input#date", "2025-12-15")  # cambia solo la fecha
        self.page.fill("input#time", "18:00")       # hora opcional
        self.page.fill("input#location", "Ubicación Original")  # no cambia ubicación
        self.page.click("button.btn.btn-primary")
        
        # Logout organizador
        self.page.goto(f"{self.live_server_url}/accounts/logout/")
        self.context.clear_cookies()

        # Login como usuario1 y verificar notificación
        self.login_user("user1", "testpass")
        self.page.goto(f"{self.live_server_url}/notificaciones/usuario/")
        self.page.wait_for_load_state("networkidle")

        expect(self.page.locator('[data-testid="notification-header"]')).to_be_visible()
        expect(self.page.locator('[data-testid="notification-counter"]')).to_be_visible()
        notification_count = self.page.locator('[data-testid="notification-item"]').count()
        assert notification_count > 0, "El usuario no recibió notificación por el cambio de fecha."

    def test_notification_sent_on_event_location_change(self):
        # Login como organizador y editar solo el lugar
        self.login_user("organizador", "password123")
        self.page.goto(f"{self.live_server_url}/events/{self.event.id}/edit/") # type: ignore
        self.page.fill("input#date", self.event.scheduled_at.strftime("%Y-%m-%d"))  # mantiene la fecha
        self.page.fill("input#time", self.event.scheduled_at.strftime("%H:%M"))    # mantiene la hora
        self.page.fill("input#location", "Nueva ubicación distinta")
        self.page.click("button.btn.btn-primary")

        # Logout organizador
        self.page.goto(f"{self.live_server_url}/accounts/logout/")
        self.context.clear_cookies()

        # Login como usuario1 y verificar notificación
        self.login_user("user1", "testpass")
        self.page.goto(f"{self.live_server_url}/notificaciones/usuario/")
        self.page.wait_for_load_state("networkidle")

        expect(self.page.locator('[data-testid="notification-header"]')).to_be_visible()
        expect(self.page.locator('[data-testid="notification-counter"]')).to_be_visible()
        notification_count = self.page.locator('[data-testid="notification-item"]').count()
        assert notification_count > 0, "El usuario no recibió notificación por el cambio de lugar."

    def test_notification_sent_on_event_date_and_location_change(self):
        # Login como organizador y editar tanto la fecha como el lugar
        self.login_user("organizador", "password123")
        self.page.goto(f"{self.live_server_url}/events/{self.event.id}/edit/") # type: ignore
        nueva_fecha = (self.event.scheduled_at + timedelta(days=3)).strftime("%Y-%m-%d")
        nuevo_horario = self.event.scheduled_at.strftime("%H:%M")
        self.page.fill("input#date", nueva_fecha)
        self.page.fill("input#time", nuevo_horario)
        self.page.fill("input#location", "Lugar completamente nuevo")
        self.page.click("button.btn.btn-primary")

        # Logout organizador
        self.page.goto(f"{self.live_server_url}/accounts/logout/")
        self.context.clear_cookies()

        # Login como usuario1 y verificar notificación
        self.login_user("user1", "testpass")
        self.page.goto(f"{self.live_server_url}/notificaciones/usuario/")
        self.page.wait_for_load_state("networkidle")

        expect(self.page.locator('[data-testid="notification-header"]')).to_be_visible()
        expect(self.page.locator('[data-testid="notification-counter"]')).to_be_visible()
        notification_count = self.page.locator('[data-testid="notification-item"]').count()
        assert notification_count > 0, "El usuario no recibió notificación por el cambio de fecha y lugar."

    def test_no_notification_sent_if_no_spectators(self):
        # Crear un nuevo evento SIN usuarios con tickets
        event = Event.objects.create(
            title="Evento sin espectadores",
            description="Este evento no tiene espectadores.",
            scheduled_at=make_aware(datetime.now() + timedelta(days=7)),
            location="Lugar inicial",
            organizer=self.organizer,
        )

        # Login como organizador y editar el evento (cambiar fecha)
        self.login_user("organizador", "password123")
        self.page.goto(f"{self.live_server_url}/events/{event.id}/edit/") # type: ignore
        nueva_fecha = (event.scheduled_at + timedelta(days=2)).strftime("%Y-%m-%d")
        nuevo_horario = event.scheduled_at.strftime("%H:%M")
        self.page.fill("input#date", nueva_fecha)
        self.page.fill("input#time", nuevo_horario)
        self.page.fill("input#location", "Nuevo lugar sin espectadores")
        self.page.click("button.btn.btn-primary")

        # Logout organizador
        self.page.goto(f"{self.live_server_url}/accounts/logout/")
        self.context.clear_cookies()

        # Login como user1 y verificar que NO tiene notificaciones nuevas
        self.login_user("user1", "testpass")
        self.page.goto(f"{self.live_server_url}/notificaciones/usuario/")
        self.page.wait_for_load_state("networkidle")

        # Verificamos que el contador de notificaciones NO aparece o es 0
        contador = self.page.locator('[data-testid="notification-counter"]')
        if contador.count() > 0:
            text = contador.inner_text()
            assert "0" in text or "ninguna" in text.lower(), f"Se mostró notificación cuando no debía: {text}"
