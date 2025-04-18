from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UserAuthenticationIntegrationTest(TestCase):
    def test_register_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "password1": "SuperSecure123",
                "password2": "SuperSecure123",
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_user(self):
        User.objects.create_user(username="testlogin", password="testpass123")
        response = self.client.post(
            reverse("login"),
            {
                "username": "testlogin",
                "password": "testpass123",
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
        self.assertTrue(response.url.startswith(reverse("dashboard")))
