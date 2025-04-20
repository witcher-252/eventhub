import os
import re

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import expect, sync_playwright

from app.models import User

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
headless = os.environ.get("HEADLESS", 1) == 1
slow_mo = os.environ.get("SLOW_MO", 0)


class AuthenticationE2ETest(StaticLiveServerTestCase):
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

    def test_registration_page_loads(self):
        """Test que verifica que la página de registro carga correctamente"""
        self.page.goto(f"{self.live_server_url}/accounts/register/")

        # Verificar que el formulario está presente
        expect(self.page.locator("form")).to_be_visible()
        expect(self.page.locator("input[name='csrfmiddlewaretoken']")).to_be_hidden()
        expect(self.page.locator("input[name='email']")).to_be_visible()
        expect(self.page.locator("input[name='username']")).to_be_visible()
        expect(self.page.locator("input[name='password']")).to_be_visible()
        expect(self.page.locator("input[name='password-confirm']")).to_be_visible()
        expect(self.page.locator("input[name='is-organizer']")).to_be_visible()
        expect(self.page.locator("button[type='submit']")).to_be_visible()

    def test_successful_registration(self):
        """Test que verifica el proceso de registro exitoso"""
        self.page.goto(f"{self.live_server_url}/accounts/register/")

        # Llenar el formulario con datos válidos
        self.page.get_by_label("Email").fill("nuevo@example.com")
        self.page.get_by_label("Usuario").fill("nuevo_usuario")
        self.page.get_by_label("Contraseña", exact=True).fill("password123")
        self.page.get_by_label("Confirmar contraseña").fill("password123")

        # Enviar el formulario
        self.page.click("button[type='submit']")

        # Verificar que se redirige a events
        self.page.wait_for_url(f"{self.live_server_url}/events/*")

        # Verificar que el usuario fue creado en la base de datos
        self.assertTrue(User.objects.filter(username="nuevo_usuario").exists())

    def test_successful_registration_organizer(self):
        """Test que verifica el proceso de registro exitoso de un organizador"""
        self.page.goto(f"{self.live_server_url}/accounts/register/")

        # Llenar el formulario con datos válidos
        self.page.get_by_label("Email").fill("nuevo@example.com")
        self.page.get_by_label("Usuario").fill("nuevo_usuario")
        self.page.get_by_label("Contraseña", exact=True).fill("password123")
        self.page.get_by_label("Confirmar contraseña").fill("password123")
        self.page.get_by_label("Es organizador?").click()

        # Enviar el formulario
        self.page.click("button[type='submit']")

        # Verificar que se redirige a events
        self.page.wait_for_url(f"{self.live_server_url}/events/*")

        # Verificar que el usuario fue creado en la base de datos
        self.assertTrue(User.objects.filter(username="nuevo_usuario").exists())

    def test_duplicate_email_registration(self):
        """Test que verifica el intento de registro con un email existente"""
        # Crear un usuario con el email que vamos a intentar usar
        user = self.create_test_user()

        self.page.goto(f"{self.live_server_url}/accounts/register/")

        # Llenar el formulario con un email existente
        self.page.get_by_label("Email").fill(user.email)
        self.page.get_by_label("Usuario").fill("otro_usuario")
        self.page.get_by_label("Contraseña", exact=True).fill("password123")
        self.page.get_by_label("Confirmar contraseña").fill("password123")

        # Enviar el formulario
        self.page.click("button[type='submit']")

        # Verificar que permanecemos en la página de registro
        expect(self.page).to_have_url(re.compile(r".*/register"))

        # Verificar que se muestra el mensaje de error correspondiente
        error_message = self.page.get_by_text("Ya existe un usuario con este email")
        expect(error_message).to_be_visible()

    def test_duplicate_username_registration(self):
        """Test que verifica el intento de registro con un nombre de usuario existente"""
        # Crear un usuario con el username que vamos a intentar usar
        user = self.create_test_user()

        self.page.goto(f"{self.live_server_url}/accounts/register/")

        # Llenar el formulario con un username existente
        self.page.get_by_label("Email").fill("otro@example.com")
        self.page.get_by_label("Usuario").fill(user.username)
        self.page.get_by_label("Contraseña", exact=True).fill("password123")
        self.page.get_by_label("Confirmar contraseña").fill("password123")

        # Enviar el formulario
        self.page.click("button[type='submit']")

        # Verificar que permanecemos en la página de registro
        expect(self.page).to_have_url(re.compile(r".*/register"))

        # Verificar que se muestra el mensaje de error correspondiente
        error_message = self.page.get_by_text("Ya existe un usuario con este nombre de usuario")
        expect(error_message).to_be_visible()

    def test_password_mismatch_registration(self):
        """Test que verifica el intento de registro con contraseñas que no coinciden"""
        self.page.goto(f"{self.live_server_url}/accounts/register/")

        # Llenar el formulario con contraseñas diferentes
        self.page.get_by_label("Email").fill("nuevo@example.com")
        self.page.get_by_label("Usuario").fill("nuevo_usuario")
        self.page.get_by_label("Contraseña", exact=True).fill("password123")
        self.page.get_by_label("Confirmar contraseña").fill("diferente456")

        # Enviar el formulario
        self.page.click("button[type='submit']")

        # Verificar que permanecemos en la página de registro
        expect(self.page).to_have_url(re.compile(r".*/register"))

        # Verificar que se muestra el mensaje de error correspondiente
        error_message = self.page.get_by_text("Las contraseñas no coinciden")
        expect(error_message).to_be_visible()

    def test_login_page_loads(self):
        """Test que verifica que la página de login carga correctamente"""
        self.page.goto(f"{self.live_server_url}/accounts/login/")

        # Verificar que el formulario está presente
        expect(self.page.locator("form")).to_be_visible()
        expect(self.page.locator("input[name='csrfmiddlewaretoken']")).to_be_hidden()
        expect(self.page.locator("input[name='username']")).to_be_visible()
        expect(self.page.locator("input[name='password']")).to_be_visible()
        expect(self.page.locator("button[type='submit']")).to_be_visible()

    def test_successful_login(self):
        """Test que verifica el proceso de login exitoso"""
        # Crear un usuario para hacer login
        user = self.create_test_user()

        self.page.goto(f"{self.live_server_url}/accounts/login/")

        # Llenar el formulario con credenciales válidas
        self.page.get_by_label("Usuario").fill(user.username)
        self.page.get_by_label("Contraseña").fill("password123")

        # Enviar el formulario
        self.page.click("button[type='submit']")

        # Verificar que se redirige a events
        self.page.wait_for_url(f"{self.live_server_url}/events/*")

    def test_invalid_credentials_login(self):
        """Test que verifica el intento de login con credenciales inválidas"""
        self.page.goto(f"{self.live_server_url}/accounts/login/")

        # Llenar el formulario con credenciales inválidas
        self.page.get_by_label("Usuario").fill("usuario_inexistente")
        self.page.get_by_label("Contraseña").fill("password_incorrecto")

        # Enviar el formulario
        self.page.click("button[type='submit']")

        # Verificar que permanecemos en la página de login
        expect(self.page).to_have_url(re.compile(r".*/login"))

        # Verificar que se muestra el mensaje de error correspondiente
        error_message = self.page.get_by_text("Usuario o contraseña incorrectos")
        expect(error_message).to_be_visible()

    def test_wrong_password_login(self):
        """Test que verifica el intento de login con contraseña incorrecta"""
        # Crear un usuario para probar
        user = self.create_test_user()

        self.page.goto(f"{self.live_server_url}/accounts/login/")

        # Llenar el formulario con username correcto pero password incorrecto
        self.page.get_by_label("Usuario").fill(user.username)
        self.page.get_by_label("Contraseña").fill("password_incorrecto")

        # Enviar el formulario
        self.page.click("button[type='submit']")

        # Verificar que permanecemos en la página de login
        expect(self.page).to_have_url(re.compile(r".*/login"))

        # Verificar que se muestra el mensaje de error correspondiente
        error_message = self.page.get_by_text("Usuario o contraseña incorrectos")
        expect(error_message).to_be_visible()
