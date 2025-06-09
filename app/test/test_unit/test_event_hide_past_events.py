from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.timezone import now

from app.models import Event


class HidePastEventsTest(TestCase):
    def test_future_events_are_returned(self):
        User = get_user_model()
        organizer = User.objects.create_user(username="testuser", password="12345")

        past_event = Event.objects.create(
            title="Pasado",
            scheduled_at=now() - timedelta(days=1),
            organizer=organizer
        )

        future_event = Event.objects.create(
            title="Futuro",
            scheduled_at=now() + timedelta(days=1),
            organizer=organizer
        )

        future_events = Event.objects.filter(scheduled_at__gte=now())

        self.assertIn(future_event, future_events)
        self.assertNotIn(past_event, future_events)