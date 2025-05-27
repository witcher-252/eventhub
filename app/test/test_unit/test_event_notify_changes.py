from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.timezone import make_aware

from app.models import Event, Notification, Ticket

User = get_user_model()


class EventNotificationUnitTest(TestCase):
    def setUp(self):
        # Crear usuarios
        self.organizer = User.objects.create_user(
            username="organizer", 
            password="testpass",
            is_organizer=True
        )
        self.regular_user = User.objects.create_user(
            username="testuser", 
            password="testpass"
        )

        # Fecha original sin microsegundos
        self.initial_date = make_aware(datetime.now().replace(second=0, microsecond=0) + timedelta(days=7))

        # Crear evento inicial
        self.event = Event.objects.create(
            title="Test Event",
            description="Test Description",
            location="Original Location",
            scheduled_at=self.initial_date,
            organizer=self.organizer,
        )

        # Crear ticket
        self.ticket = Ticket.objects.create(
            usuario=self.regular_user,
            evento=self.event,
            quantity=1,
            buy_date=make_aware(datetime.now()),
            type="general"
        )

    def test_notification_created_when_date_changed_with_tickets(self):
        initial_notifications = Notification.objects.count()

        new_date = make_aware(datetime.now().replace(second=0, microsecond=0) + timedelta(days=10))
        # Le pasamos los datos nuevos, título y descripción pueden ser los mismos o nuevos
        self.event.update_with_notification(
            title=self.event.title,
            description=self.event.description,
            scheduled_at=new_date,
            location=self.event.location
        )

        self.assertEqual(Notification.objects.count(), initial_notifications + 1)
        notification = Notification.objects.last()
        self.assertIn("La fecha ha cambiado", notification.message) # type: ignore

    def test_notification_created_when_location_changed_with_tickets(self):
        initial_notifications = Notification.objects.count()

        new_location = "New Location"
        self.event.location = new_location
        self.event.update_with_notification(
            title=self.event.title,
            description=self.event.description,
            scheduled_at=self.event.scheduled_at,
            location=self.event.location
        )

        self.assertEqual(Notification.objects.count(), initial_notifications + 1)
        notification = Notification.objects.last()
        self.assertIn("El lugar ha cambiado", notification.message) # type: ignore
        self.assertEqual(notification.priority, Notification.PRIORITY_HIGH) # type: ignore
        self.assertIsNone(notification.user) # type: ignore
        self.assertEqual(notification.event, self.event) # type: ignore

    def test_notification_created_when_both_date_and_location_changed(self):
        initial_notifications = Notification.objects.count()

        new_date = make_aware(datetime.now().replace(second=0, microsecond=0) + timedelta(days=15))
        new_location = "Completely New Location"
        self.event.scheduled_at = new_date
        self.event.location = new_location
        self.event.update_with_notification(
            title=self.event.title,
            description=self.event.description,
            scheduled_at=self.event.scheduled_at,
            location=new_location
        )    

        self.assertEqual(Notification.objects.count(), initial_notifications + 1)
        notification = Notification.objects.last()
        self.assertIn("La fecha ha cambiado", notification.message) # type: ignore
        self.assertIn("El lugar ha cambiado", notification.message) # type: ignore
        self.assertEqual(notification.priority, Notification.PRIORITY_HIGH) # type: ignore

    def test_no_notification_when_no_tickets_sold(self):
        self.ticket.delete()
        initial_notifications = Notification.objects.count()

        new_date = make_aware(datetime.now().replace(second=0, microsecond=0) + timedelta(days=12))
        new_location = "Another Location"
        self.event.scheduled_at = new_date
        self.event.location = new_location
        self.event.update_with_notification(
            title=self.event.title,
            description=self.event.description,
            scheduled_at=self.event.scheduled_at,
            location=new_location
        )

        self.assertEqual(Notification.objects.count(), initial_notifications)

    def test_no_notification_when_only_title_or_description_changed(self):
        initial_notifications = Notification.objects.count()

        self.event.title = "Nuevo título"
        self.event.description = "Nueva descripción"
        # No se cambia ni fecha ni lugar
        self.event.update_with_notification(
            title=self.event.title,
            description=self.event.description,
            scheduled_at=self.event.scheduled_at,
            location=self.event.location
        )

        self.assertEqual(Notification.objects.count(), initial_notifications)
