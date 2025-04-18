from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from app.models import Event

User = get_user_model()

class EventModelTest(TestCase):
    def test_create_event(self):
        organizer = User.objects.create_user(username="eventorganizer", password="pass")
        event = Event.objects.create(
            title="Sample Event",
            description="This is a test event",
            date=timezone.now(),
            organizer=organizer,
        )
        self.assertEqual(event.title, "Sample Event")
        self.assertEqual(event.organizer.username, "eventorganizer")
        self.assertIsNotNone(event.created_at)
        self.assertIsNotNone(event.updated_at)
