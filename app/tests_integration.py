from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from app.models import Event

User = get_user_model()

class UserAuthenticationIntegrationTest(TestCase):
    def test_register_user(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'SuperSecure123',
            'password2': 'SuperSecure123',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_user(self):
        user = User.objects.create_user(username='testlogin', password='testpass123')
        response = self.client.post(reverse('login'), {
            'username': 'testlogin',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
        self.assertTrue(response.url.startswith(reverse('dashboard')))

class EventIntegrationTest(TestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(username="organizer", password="pass")
        self.event1 = Event.objects.create(
            title="Event One",
            description="First Event",
            date=timezone.now(),
            organizer=self.organizer,
        )
        self.event2 = Event.objects.create(
            title="Event Two",
            description="Second Event",
            date=timezone.now(),
            organizer=self.organizer,
        )
        self.client.login(username="organizer", password="pass")

    def test_dashboard_lists_events(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Event One")
        self.assertContains(response, "Event Two")

    def test_event_detail_view(self):
        response = self.client.get(reverse('event_detail', args=[self.event1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Event One")
        self.assertContains(response, "First Event")
