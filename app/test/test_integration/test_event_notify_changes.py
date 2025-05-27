from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.timezone import make_aware

from app.models import Event, Notification, Ticket

User = get_user_model()


class EventNotificationIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Crear organizador y usuarios regulares
        self.organizer = User.objects.create_user(
            username="organizer", 
            password="testpass",
            is_organizer=True
        )
        self.user1 = User.objects.create_user(
            username="user1", 
            password="testpass"
        )
        self.user2 = User.objects.create_user(
            username="user2", 
            password="testpass"
        )
        
        # Crear evento
        self.event = Event.objects.create(
            title="Evento Integración",
            description="Evento de prueba integración",
            location="Ubicación Original",
            scheduled_at=make_aware(datetime.now() + timedelta(days=7)),
            organizer=self.organizer,
        )
        
        # Crear tickets para múltiples usuarios
        self.ticket1 = Ticket.objects.create(
            usuario=self.user1,
            evento=self.event,
            quantity=2,
            buy_date=make_aware(datetime.now()),
            type="general"
        )
        self.ticket2 = Ticket.objects.create(
            usuario=self.user2,
            evento=self.event,
            quantity=1,
            buy_date=make_aware(datetime.now()),
            type="vip"
        )

    def test_integration_organizer_edits_event_creates_notification_flow(self):
        """
        Test de integración completo: organizador edita evento → se crea notificación 
        → usuarios pueden ver la notificación
        """
        # 1. Login como organizador
        self.client.login(username="organizer", password="testpass")
        
        # 2. Verificar que no hay notificaciones inicialmente
        initial_notifications = Notification.objects.count()
        self.assertEqual(initial_notifications, 0)

        # 3. Organizador accede al formulario de edición
        response = self.client.get(reverse("event_edit", args=[self.event.id])) # type: ignore
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Editar evento")
        self.assertContains(response, self.event.title)
        
        # 4. El organizador edita el evento (cambio de fecha y ubicación)
        new_datetime = datetime.now() + timedelta(days=10)
        new_date = new_datetime.date().isoformat()         # 'YYYY-MM-DD'
        new_time = new_datetime.time().strftime("%H:%M")   # 'HH:MM'

        response = self.client.post(reverse("event_edit", args=[self.event.id]), { # type: ignore
            "title": "Evento Modificado",
            "description": "Descripción modificada",
            "location": "Ubicación Nueva",
            "date": new_date,
            "time": new_time,
        })

        # 5. Verificamos redirección y que la edición fue exitosa
        self.assertEqual(response.status_code, 302)
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, "Evento Modificado")
        self.assertEqual(self.event.location, "Ubicación Nueva")

        # 6. Verificamos que se creó UNA notificación GLOBAL (user=None)
        self.assertEqual(Notification.objects.count(), initial_notifications + 1)
        
        # 7. Verificar que es una notificación global y su contenido
        notification = Notification.objects.last()
        self.assertIsNone(notification.user)  # type: ignore # Notificación global
        self.assertEqual(notification.event, self.event) # type: ignore
        self.assertEqual(notification.title, f"Actualización del evento: {self.event.title}") # type: ignore
        self.assertIn("La fecha ha cambiado", notification.message) # type: ignore
        self.assertIn("El lugar ha cambiado", notification.message) # type: ignore
        self.assertEqual(notification.priority, Notification.PRIORITY_HIGH) # type: ignore
        self.assertFalse(notification.is_read) # type: ignore

        # 8. Usuario 1 accede a sus notificaciones y ve la nueva notificación global
        self.client.login(username="user1", password="testpass")
        response = self.client.get(reverse("notification_list_user"))
        self.assertEqual(response.status_code, 200)
        
        # 9. Verificar que la notificación aparece en la lista del usuario
        self.assertContains(response, notification.title) # type: ignore
        self.assertContains(response, "La fecha ha cambiado")
        self.assertContains(response, "El lugar ha cambiado")
        
        # 10. Verificar contador de no leídas
        self.assertIn('unread_count', response.context)
        self.assertEqual(response.context['unread_count'], 1)
        self.assertContains(response, "1 nuevas")
        
        # 11. Usuario marca la notificación como leída
        response = self.client.post(reverse("mark_as_read", args=[notification.id])) # type: ignore
        self.assertRedirects(response, reverse("notification_list_user"))
        
        # 12. Verificar que la notificación se marcó como leída
        notification.refresh_from_db() # type: ignore
        self.assertTrue(notification.is_read) # type: ignore
        
        # 13. Verificar que el contador se actualizó después de marcar como leída
        response = self.client.get(reverse("notification_list_user"))
        self.assertEqual(response.context['unread_count'], 0)
        
        # 14. Usuario 2 también puede ver la misma notificación global
        self.client.login(username="user2", password="testpass")
        response = self.client.get(reverse("notification_list_user"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, notification.title) # type: ignore

    def test_integration_organizer_minor_edit_no_notification(self):
        """
        Test de integración: organizador hace cambios menores → no se crea notificación
        """
        # 1. Login como organizador
        self.client.login(username="organizer", password="testpass")
        
        # 2. Verificar estado inicial
        initial_notifications = Notification.objects.count()
        
        # 3. Organizador modifica solo título y descripción (NO fecha ni ubicación)
        response = self.client.post(reverse("event_edit", args=[self.event.id]), { # type: ignore
            "title": "Nuevo Título del Evento",
            "description": "Nueva descripción actualizada",
            "location": self.event.location,  # Sin cambios
            "date": self.event.scheduled_at.strftime("%Y-%m-%d"),  # Sin cambios
            "time": self.event.scheduled_at.strftime("%H:%M"),  # Sin cambios
        }, follow=True)
        
        # 4. Verificar que no se crearon notificaciones
        self.assertEqual(Notification.objects.count(), initial_notifications)
        
        # 5. Usuarios no ven nuevas notificaciones
        self.client.login(username="user1", password="testpass")
        response = self.client.get(reverse("notification_list_user"))
        self.assertEqual(response.context['unread_count'], 0)

    def test_integration_only_date_change_creates_notification(self):
        """
        Test: Solo cambio de fecha debe crear notificación
        """
        self.client.login(username="organizer", password="testpass")
        
        new_datetime = datetime.now() + timedelta(days=15)
        new_date = new_datetime.date().isoformat()
        new_time = new_datetime.time().strftime("%H:%M")

        response = self.client.post(reverse("event_edit", args=[self.event.id]), { # type: ignore  # noqa: F841
            "title": self.event.title,
            "description": self.event.description,
            "location": self.event.location,  # Sin cambios
            "date": new_date,  # CAMBIO
            "time": new_time,  # CAMBIO
        })
        
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertIn("La fecha ha cambiado", notification.message) # type: ignore
        self.assertNotIn("El lugar ha cambiado", notification.message) # type: ignore

    def test_integration_only_location_change_creates_notification(self):
        """
        Test: Solo cambio de ubicación debe crear notificación
        """
        self.client.login(username="organizer", password="testpass")

        response = self.client.post(reverse("event_edit", args=[self.event.id]), {  # noqa: F841 # type: ignore
            "title": self.event.title,
            "description": self.event.description,
            "location": "Nueva Ubicación Solo",  # CAMBIO
            "date": self.event.scheduled_at.strftime("%Y-%m-%d"),  # Sin cambios
            "time": self.event.scheduled_at.strftime("%H:%M"),  # Sin cambios
        })
        
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertIn("El lugar ha cambiado", notification.message) # type: ignore
        self.assertNotIn("La fecha ha cambiado", notification.message) # type: ignore

    def test_integration_event_without_tickets_no_notification(self):
        """
        Test de integración: evento sin tickets no genera notificaciones
        """
        # 1. Crear evento sin tickets
        event_no_tickets = Event.objects.create(
            title="Evento Sin Tickets",
            description="Evento sin ventas",
            location="Ubicación Original",
            scheduled_at=make_aware(datetime.now() + timedelta(days=5)),
            organizer=self.organizer,
        )
        
        # 2. Organizador modifica el evento
        self.client.login(username="organizer", password="testpass")
        
        new_datetime = datetime.now() + timedelta(days=12)
        response = self.client.post(reverse("event_edit", args=[event_no_tickets.id]), { # type: ignore
            "title": event_no_tickets.title,
            "description": event_no_tickets.description,
            "location": "Nueva Ubicación",  # CAMBIO
            "date": new_datetime.strftime("%Y-%m-%d"),  # CAMBIO
            "time": new_datetime.strftime("%H:%M"),  # CAMBIO
        })
        
        # 3. Verificar que no se crearon notificaciones (no hay tickets)
        self.assertEqual(Notification.objects.count(), 0)
        
        # 4. Usuarios no reciben notificaciones
        self.client.login(username="user1", password="testpass")
        response = self.client.get(reverse("notification_list_user"))
        self.assertEqual(response.context['unread_count'], 0)

    def test_integration_notification_visible_to_all_ticket_holders(self):
        """
        Test de integración: verificar que las notificaciones globales son visibles 
        para todos los usuarios con tickets del evento
        """
        # 1. Crear usuario adicional con ticket
        user3 = User.objects.create_user(username="user3", password="testpass")
        Ticket.objects.create(
            usuario=user3,
            evento=self.event,
            quantity=3,
            buy_date=make_aware(datetime.now()),
            type="general"
        )
        
        # 2. Organizador modifica el evento
        self.client.login(username="organizer", password="testpass")
        new_date = make_aware(datetime.now() + timedelta(days=10))
        
        self.client.post(reverse("event_edit", args=[self.event.id]), { # type: ignore
            "title": self.event.title,
            "description": self.event.description,
            "location": "Ubicación Completamente Nueva",
            "date": new_date.strftime("%Y-%m-%d"),
            "time": new_date.strftime("%H:%M"),
        })
        
        # 3. Verificar que se creó UNA notificación global
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertIsNone(notification.user)  # type: ignore # Global
        
        # 4. Verificar que todos los usuarios con tickets pueden ver la notificación
        for username in ["user1", "user2", "user3"]:
            self.client.login(username=username, password="testpass")
            response = self.client.get(reverse("notification_list_user"))
            
            # Cada usuario debería ver la notificación
            self.assertContains(response, notification.title) # type: ignore
            self.assertEqual(response.context['unread_count'], 1)
