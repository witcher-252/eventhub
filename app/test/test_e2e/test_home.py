import os
import re

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import expect, sync_playwright

from app.models import User

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
headless = os.environ.get("HEADLESS", 1) == 1
slow_mo = os.environ.get("SLOW_MO", 0)


class HomeE2ETest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=headless, slow_mo=int(slow_mo))

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    def setUp(self):
        # Crear una página nueva para cada test
        self.page = self.browser.new_page()

    def tearDown(self):
        # Cerrar la página después de cada test
        self.page.close()

    def create_test_user(self):
        """Crea un usuario de prueba en la base de datos"""
        return User.objects.create_user(
            username="usuario_test", email="test@example.com", password="password123"
        )

    def test_home_page_loads(self):
        """Test que verifica que la home carga correctamente"""
        self.page.goto(f"{self.live_server_url}/")

        # Verificar que el logo este presente
        logo = self.page.get_by_text("EventHub", exact=True)
        expect(logo).to_be_visible()
        expect(logo).to_have_attribute("href", "/")

        # Verificar que el boton de iniciar sesion este presente
        login_btn = self.page.get_by_role("button", name="Ingresá")
        expect(login_btn).to_be_visible()

        # Verificar que el boton de crear cuenta este presente
        signup_btn = self.page.get_by_role("button", name="Creá tu cuenta")
        expect(signup_btn).to_be_visible()

        # Verificar que el boton de cerrar sesion no este presente
        logout_btn = self.page.get_by_role("button", name="Salir")
        expect(logout_btn).to_have_count(0)

        expect(self.page.get_by_text("Eventos y Entradas")).to_be_visible()
        expect(
            self.page.get_by_text(
                "Descubre, organiza y participa en los mejores eventos. Compra entradas, deja comentarios y califica tus experiencias."
            )
        ).to_be_visible()

    def test_login_button_navigates_to_login_page(self):
        """Test que verifica que la home carga correctamente"""
        self.page.goto(f"{self.live_server_url}/")

        self.page.get_by_role("button", name="Ingresá").click()
        expect(self.page).to_have_url(re.compile(".*/login"))

    def test_login_button_and_signup_button_not_visible_if_user_authenticated(self):
        """Test que verifica que la home carga correctamente"""
        user = self.create_test_user()

        self.page.goto(f"{self.live_server_url}/")
        self.page.get_by_role("button", name="Ingresá").click()

        # Llenar el formulario con credenciales válidas
        self.page.get_by_label("Usuario").fill(user.username)
        self.page.get_by_label("Contraseña").fill("password123")

        # Enviar el formulario
        self.page.get_by_role("button", name="Iniciar sesión").click()

        # Verificar que se redirige al dashboard
        # self.page.wait_for_url(f"{self.live_server_url}/dashboard/*")

        # Verificar que el boton de iniciar sesion este presente
        login_btn = self.page.get_by_role("button", name="Ingresá")
        expect(login_btn).to_have_count(0)

        # Verificar que el boton de crear cuenta este presente
        signup_btn = self.page.get_by_role("button", name="Creá tu cuenta")
        expect(signup_btn).to_have_count(0)

        # Verificar que el boton de cerrar sesion no este presente
        logout_btn = self.page.get_by_role("button", name="Salir")
        expect(logout_btn).to_be_visible()
