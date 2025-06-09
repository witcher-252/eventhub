import datetime
import re

from django.utils import timezone
from playwright.sync_api import expect

from app.models import Event, User
from app.test.test_e2e.base import BaseE2ETest


class LimitTicketTest(BaseE2ETest):

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

        # Crear eventos de prueba
        # Evento 1
        event_date1 = timezone.make_aware(datetime.datetime(2026, 2, 10, 10, 10))
        self.event1 = Event.objects.create(
            title="Evento de prueba 1",
            description="Descripción del evento 1",
            scheduled_at=event_date1,
            organizer=self.organizer,
        )

    def test_validate_limit_purchase(self):

        # Iniciar sesión como organizador
       self.login_user("usuario", "password123")

        # Ir a la página de eventos
       self.page.goto(f"{self.live_server_url}/events/")

        # Hacer clic en el primer link de ver detalle de evento
       with self.page.expect_navigation():
           self.page.locator("a[aria-label='Ver detalle']").first.click()

       create_button = self.page.get_by_role("link", name="Comprar entrada")
       expect(create_button).to_be_visible()
       create_button.click()

       # confirmar que se dirige al template donde se encuentra el formulario del ticket
       expect(self.page).to_have_url(f"{self.live_server_url}/tickets/entrada/{self.event1.pk}")
       
       # confirmo la existencia del formulario
       form = self.page.locator('form[action="/tickets/confirmarEntrada"]')
       expect(form).to_be_visible()

       # cargo el formulario
       self.page.fill('input[name="cantidad"]', '4')
       self.page.select_option('select[name="tipo"]', 'general')
       self.page.fill('input[name="numero_tarjeta"]', '1234567812345678')
       self.page.fill('input[name="expiracion"]', '12/30')
       self.page.fill('input[name="cvv"]', '123')
       self.page.fill('input[name="nombre_tarjeta"]', 'Juan Pérez')
       self.page.check('input[name="acepta_terminos"]')

       # Enviar el formulario 
       self.page.get_by_role("button", name="Confirmar Compra").click()

       # Verificar que redirige , demostrando la compra exitosa 
       expect(self.page).to_have_url(re.compile(".*/tickets/gestion.*"))

       # vuelvo a la pagima de eventos
       self.page.goto(f"{self.live_server_url}/events/")

       # Hacer clic en el primer link de ver detalle de evento
       with self.page.expect_navigation():
           self.page.locator("a[aria-label='Ver detalle']").first.click()

       # Intento realizar otro ticket superando el limite de entradas.
       create_button = self.page.get_by_role("link", name="Comprar entrada")
       expect(create_button).to_be_visible()
       create_button.click()

       expect(self.page).to_have_url(f"{self.live_server_url}/tickets/entrada/{self.event1.pk}")

       form = self.page.locator('form[action="/tickets/confirmarEntrada"]')
       expect(form).to_be_visible()

       self.page.fill('input[name="cantidad"]', '1')
       self.page.select_option('select[name="tipo"]', 'general')
       self.page.fill('input[name="numero_tarjeta"]', '1234567812345678')
       self.page.fill('input[name="expiracion"]', '12/30')
       self.page.fill('input[name="cvv"]', '123')
       self.page.fill('input[name="nombre_tarjeta"]', 'Juan Pérez')
       self.page.check('input[name="acepta_terminos"]')

       # 4. Enviar el formulario 
       self.page.get_by_role("button", name="Confirmar Compra").click()

       # verifico que en la respuesta se encuentre el mensaje de error.
       error_list = self.page.locator("ul.errorlist li")
       expect(error_list).to_contain_text("superarías el límite de 4 entradas")


    