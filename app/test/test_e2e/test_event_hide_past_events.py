from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth import get_user_model
from app.models import Event
import time

class EventVisibilityE2ETest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = webdriver.Chrome()  # O webdriver.Firefox(), según lo que uses
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='12345')

        # Crear eventos
        Event.objects.create(
            title="Evento pasado",
            scheduled_at=now() - timedelta(days=2),
            organizer=self.user
        )
        Event.objects.create(
            title="Evento futuro",
            scheduled_at=now() + timedelta(days=2),
            organizer=self.user
        )

    def test_only_future_events_visible(self):
        # Iniciar sesión
        self.driver.get(f"{self.live_server_url}/accounts/login/")  # Ajustá si tu login tiene otra URL
        self.driver.find_element(By.NAME, "username").send_keys("testuser")
        self.driver.find_element(By.NAME, "password").send_keys("12345")
        self.driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)

        # Esperar y navegar a eventos
        time.sleep(1)
        self.driver.get(f"{self.live_server_url}{reverse('events')}")

        # Verificar que solo se vea el evento futuro
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("Evento futuro", body_text)
        self.assertNotIn("Evento pasado", body_text)