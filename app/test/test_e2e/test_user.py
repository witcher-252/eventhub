import os

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import sync_playwright

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
        assert self.page.locator("form").is_visible()
        assert self.page.locator("input[name='email']").is_visible()
        assert self.page.locator("input[name='username']").is_visible()
        assert self.page.locator("input[name='password']").is_visible()
        assert self.page.locator("input[name='password-confirm']").is_visible()
        assert self.page.locator("button[type='submit']").is_visible()

    def test_successful_registration(self):
        """Test que verifica el proceso de registro exitoso"""
        self.page.goto(f"{self.live_server_url}/accounts/register/")

        # Llenar el formulario con datos válidos
        self.page.fill("input[name='email']", "nuevo@example.com")
        self.page.fill("input[name='username']", "nuevo_usuario")
        self.page.fill("input[name='password']", "password123")
        self.page.fill("input[name='password-confirm']", "password123")

        # Enviar el formulario
        self.page.click("button[type='submit']")

        # Verificar que se redirige al dashboard
        self.page.wait_for_url(f"{self.live_server_url}/dashboard/*")

        # Verificar que el usuario fue creado en la base de datos
        self.assertTrue(User.objects.filter(username="nuevo_usuario").exists())

    def test_duplicate_email_registration(self):
        """Test que verifica el intento de registro con un email existente"""
        # Crear un usuario con el email que vamos a intentar usar
        user = self.create_test_user()

        self.page.goto(f"{self.live_server_url}/accounts/register/")

        # Llenar el formulario con un email existente
        self.page.fill("input[name='email']", user.email)
        self.page.fill("input[name='username']", "otro_usuario")
        self.page.fill("input[name='password']", "password123")
        self.page.fill("input[name='password-confirm']", "password123")

        # Enviar el formulario
        self.page.click("button[type='submit']")

        # Verificar que permanecemos en la página de registro
        assert "/register/" in self.page.url

        # Verificar que se muestra el mensaje de error correspondiente
        error_message = self.page.locator("text=Ya existe un usuario con este email")
        assert error_message.is_visible()

    def test_duplicate_username_registration(self):
        """Test que verifica el intento de registro con un nombre de usuario existente"""
        # Crear un usuario con el username que vamos a intentar usar
        user = self.create_test_user()

        self.page.goto(f"{self.live_server_url}/accounts/register/")

        # Llenar el formulario con un username existente
        self.page.fill("input[name='email']", "otro@example.com")
        self.page.fill("input[name='username']", user.username)
        self.page.fill("input[name='password']", "password123")
        self.page.fill("input[name='password-confirm']", "password123")

        # Enviar el formulario
        self.page.click("button[type='submit']")

        # Verificar que permanecemos en la página de registro
        assert "/register/" in self.page.url

        # Verificar que se muestra el mensaje de error correspondiente
        error_message = self.page.locator("text=Ya existe un usuario con este nombre de usuario")
        assert error_message.is_visible()

    def test_password_mismatch_registration(self):
        """Test que verifica el intento de registro con contraseñas que no coinciden"""
        self.page.goto(f"{self.live_server_url}/accounts/register/")

        # Llenar el formulario con contraseñas diferentes
        self.page.fill("input[name='email']", "nuevo@example.com")
        self.page.fill("input[name='username']", "nuevo_usuario")
        self.page.fill("input[name='password']", "password123")
        self.page.fill("input[name='password-confirm']", "diferente456")

        # Enviar el formulario
        self.page.click("button[type='submit']")

        # Verificar que permanecemos en la página de registro
        assert "/register/" in self.page.url

        # Verificar que se muestra el mensaje de error correspondiente
        error_message = self.page.locator("text=Las contraseñas no coinciden")
        assert error_message.is_visible()

    def test_login_page_loads(self):
        """Test que verifica que la página de login carga correctamente"""
        self.page.goto(f"{self.live_server_url}/accounts/login/")

        # Verificar que el formulario está presente
        assert self.page.locator("form").is_visible()
        assert self.page.locator("input[name='username']").is_visible()
        assert self.page.locator("input[name='password']").is_visible()
        assert self.page.locator("button[type='submit']").is_visible()

    def test_successful_login(self):
        """Test que verifica el proceso de login exitoso"""
        # Crear un usuario para hacer login
        user = self.create_test_user()

        self.page.goto(f"{self.live_server_url}/accounts/login/")

        # Llenar el formulario con credenciales válidas
        self.page.fill("input[name='username']", user.username)
        self.page.fill("input[name='password']", "password123")

        # Enviar el formulario
        self.page.click("button[type='submit']")

        # Verificar que se redirige al dashboard
        self.page.wait_for_url(f"{self.live_server_url}/dashboard/*")

    def test_invalid_credentials_login(self):
        """Test que verifica el intento de login con credenciales inválidas"""
        self.page.goto(f"{self.live_server_url}/accounts/login/")

        # Llenar el formulario con credenciales inválidas
        self.page.fill("input[name='username']", "usuario_inexistente")
        self.page.fill("input[name='password']", "password_incorrecto")

        # Enviar el formulario
        self.page.click("button[type='submit']")

        # Verificar que permanecemos en la página de login
        assert "/login/" in self.page.url

        # Verificar que se muestra el mensaje de error correspondiente
        error_message = self.page.locator("text=Usuario o contraseña incorrectos")
        assert error_message.is_visible()

    def test_wrong_password_login(self):
        """Test que verifica el intento de login con contraseña incorrecta"""
        # Crear un usuario para probar
        user = self.create_test_user()

        self.page.goto(f"{self.live_server_url}/accounts/login/")

        # Llenar el formulario con username correcto pero password incorrecto
        self.page.fill("input[name='username']", user.username)
        self.page.fill("input[name='password']", "password_incorrecto")

        # Enviar el formulario
        self.page.click("button[type='submit']")

        # Verificar que permanecemos en la página de login
        assert "/login/" in self.page.url

        # Verificar que se muestra el mensaje de error correspondiente
        error_message = self.page.locator("text=Usuario o contraseña incorrectos")
        assert error_message.is_visible()
