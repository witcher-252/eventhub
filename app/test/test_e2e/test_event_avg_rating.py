import datetime
import re

from django.utils import timezone
from playwright.sync_api import expect

from app.models import Event, User

from app.test.test_e2e.base import BaseE2ETest


class RatingPromedioTest(BaseE2ETest):

    def setUp(self):
        super().setUp()

        # Crear usuario organizador
        self.organizer = User.objects.create_user(
            username="organizador",
            email="organizador@example.com",
            password="password123",
            is_organizer=True,
        )

        # Crear usuario regular
        self.regular_user = User.objects.create_user(
            username="usuario",
            email="usuario@example.com",
            password="password123",
            is_organizer=False,
        )

         # Crear usuario regular 2
        self.regular_user = User.objects.create_user(
            username="usuario2",
            email="usuario@example.com",
            password="password123",
            is_organizer=False,
        )

        # Crear eventos de prueba
        # Evento 1
        event_date1 = timezone.make_aware(datetime.datetime(2025, 2, 10, 10, 10))
        self.event1 = Event.objects.create(
            title="Evento de prueba 1",
            description="Descripción del evento 1",
            scheduled_at=event_date1,
            organizer=self.organizer,
        )

    def test_validate_average_visible(self):

        # Iniciar sesión como regular
       self.login_user("organizador", "password123")

        # Ir a la página de eventos
       self.page.goto(f"{self.live_server_url}/events/")

        # Hacer clic en el primer link de ver detalle de evento
       with self.page.expect_navigation():
           self.page.locator("a[aria-label='Ver detalle']").first.click()

       expect(self.page.get_by_text("Promedio de calificación:")).to_be_visible()
       expect(self.page.get_by_text("0,00")).to_be_visible()

    def test_validate_average_not_visible(self):

        # Iniciar sesión como regular
       self.login_user("usuario", "password123")

        # Ir a la página de eventos
       self.page.goto(f"{self.live_server_url}/events/")

        # Hacer clic en el primer link de ver detalle de evento
       with self.page.expect_navigation():
           self.page.locator("a[aria-label='Ver detalle']").first.click()

       expect(self.page.get_by_text("Promedio de calificación:")).not_to_be_visible()

    def test_calcular_promedio_rating_1_calificacion(self):
       
        # Iniciar sesión como regular
       self.login_user("usuario", "password123")

        # Ir a la página de eventos
       self.page.goto(f"{self.live_server_url}/events/")

        # Hacer clic en el primer link de ver detalle de evento
       with self.page.expect_navigation():
           self.page.locator("a[aria-label='Ver detalle']").first.click()

        # confirmo la existencia del formulario
       form = self.page.locator('form[action="/rating/crearRating"]')
       expect(form).to_be_visible()

       # cargo el formulario
       self.page.fill('input[name="tituloR"]', "Excelente evento")
       self.page.fill('textarea[name="descripcionR"]', "Muy buena organización y ambiente.")
       self.page.locator('.star-selectable i[data-value="4"]').click()
       
       with self.page.expect_navigation() as nav2:
        self.page.get_by_role("button", name="Enviar calificación").click()
     
       response2 = nav2.value
       assert response2.status == 200
       
       expect(self.page.get_by_text("Excelente evento")).to_be_visible()
       
       logout_btn = self.page.get_by_role("button", name="Salir")
       logout_btn.click()
       expect(logout_btn).to_have_count(0)

       self.login_user("organizador", "password123")

        # Ir a la página de eventos
       self.page.goto(f"{self.live_server_url}/events/")

        # Hacer clic en el primer link de ver detalle de evento
       with self.page.expect_navigation():
           self.page.locator("a[aria-label='Ver detalle']").first.click()

       expect(self.page.get_by_text("Promedio de calificación:")).to_be_visible()
       expect(self.page.get_by_text("4,00")).to_be_visible()