from django.test import TestCase, Client
from django.urls import reverse
from app.models import User, Event, Comment
import datetime
from django.utils import timezone

class RegistrarComentarioIntegrationTests(TestCase):
    def setUp(self):
        # Creamos un usuario con el que haremos las peticiones
        self.user = User.objects.create_user(username='testuser', password='12345')

        # Creamos un evento para asociar los comentarios
        self.event = Event.objects.create(
            title='Evento prueba',
            description='Descripción de prueba',
            scheduled_at=timezone.make_aware(datetime.datetime(2025, 1, 1, 12, 0)),
            place='Lugar de prueba',
            organizer=self.user
        )

        # Creamos un cliente de pruebas para simular peticiones HTTP
        self.client = Client()

    def test_registrar_comentario_funciona_correctamente(self):
        # Primero hacemos login con el usuario creado
        login = self.client.login(username='testuser', password='12345')
        self.assertTrue(login)  # Verificamos que el login fue exitoso

        # Datos que enviamos en el POST para crear un comentario
        datos_comentario = {
            'event_id': self.event.id,
            'title': 'Comentario de prueba',
            'text': 'Este es el texto del comentario de prueba'
        }

        # Hacemos la petición POST a la vista 'registrar_comentario'
        response = self.client.post(reverse('registrar_comentario'), datos_comentario)

        # Verificamos que la respuesta sea un redireccionamiento (HTTP 302)
        self.assertEqual(response.status_code, 302)

        # Comprobamos que el comentario fue creado en la base de datos
        comentario = Comment.objects.filter(event=self.event, user=self.user, title='Comentario de prueba').first()
        self.assertIsNotNone(comentario)
        self.assertEqual(comentario.text, 'Este es el texto del comentario de prueba')

        # Finalmente, verificamos que la redirección sea a la página de detalle del evento
        self.assertEqual(response.url, reverse('event_detail', args=[self.event.id]))
