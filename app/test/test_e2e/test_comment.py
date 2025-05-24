# app/test/test_e2e/test_comment.py

from django.test import TestCase, Client
from django.urls import reverse
from app.models import User, Event, Comment
import datetime
from django.utils import timezone

class RegistrarComentarioE2ETest(TestCase):
    def setUp(self):
        # Crear un usuario y hacer login con el cliente de pruebas
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client = Client()
        self.client.login(username='testuser', password='12345')

        # Crear un evento para asociar el comentario
        self.event = Event.objects.create(
            title="Evento de prueba",
            description="Descripción de prueba",
            scheduled_at=timezone.make_aware(datetime.datetime(2024, 1, 1, 12, 0)),
            place="Lugar de prueba",
            organizer=self.user
        )

    def test_registrar_comentario_e2e(self):
        # Simular POST para registrar un comentario en el evento
        response = self.client.post(reverse('registrar_comentario'), {
            'event_id': self.event.id,
            'title': 'Comentario e2e',
            'text': 'Este es un comentario registrado en el test e2e.'
        })

        # Verificar que la respuesta sea una redirección (status 302)
        self.assertEqual(response.status_code, 302)

        # Verificar que redirige a la vista 'event_detail' con el ID correcto
        self.assertRedirects(response, reverse('event_detail', args=[self.event.id]))

        # Confirmar que el comentario se creó en la base de datos
        comentario = Comment.objects.filter(
            event=self.event,
            user=self.user,
            title='Comentario e2e'
        ).first()

        self.assertIsNotNone(comentario)  # El comentario debe existir
        self.assertEqual(comentario.text, 'Este es un comentario registrado en el test e2e.')

