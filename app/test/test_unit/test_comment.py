from django.test import TestCase, Client  # TestCase para pruebas, Client para simular requests
from django.urls import reverse  # reverse permite obtener la URL de una vista por su nombre
from app.models import Event, User, Comment  # Importamos nuestros modelos
from django.utils import timezone  # Para manejar fechas

class RegistrarComentarioTests(TestCase):
    def setUp(self):
        # Se ejecuta antes de cada test
        self.client = Client()  # Cliente de prueba
        self.user = User.objects.create_user(username='testuser', password='12345')  # Creamos un usuario
        self.event = Event.objects.create(  # Creamos un evento
            title="Evento de prueba",
            description="Descripción de prueba",
            scheduled_at=timezone.now(),
            place="Lugar de prueba",
            organizer=self.user
        )

    def test_registrar_comentario_crea_un_comentario(self):
        # Logueamos al usuario
        self.client.login(username='testuser', password='12345')

        # Simulamos un POST a la vista 'registrar_comentario'
        response = self.client.post(reverse('registrar_comentario'), {
            'event_id': self.event.id,
            'title': 'Comentario de prueba',
            'text': 'Este es un texto de prueba'
        })

        # Esperamos una redirección luego del comentario (código 302)
        self.assertEqual(response.status_code, 302)

        # Comprobamos que se haya creado un solo comentario en la base
        self.assertEqual(Comment.objects.count(), 1)

        # Tomamos el comentario y verificamos su contenido
        comentario = Comment.objects.first()
        self.assertEqual(comentario.title, 'Comentario de prueba')
        self.assertEqual(comentario.text, 'Este es un texto de prueba')
        self.assertEqual(comentario.user, self.user)
        self.assertEqual(comentario.event, self.event)
