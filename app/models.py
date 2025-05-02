from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_organizer = models.BooleanField(default=False)

    @classmethod
    def validate_new_user(cls, email, username, password, password_confirm):
        errors = {}

        if email is None:
            errors["email"] = "El email es requerido"
        elif User.objects.filter(email=email).exists():
            errors["email"] = "Ya existe un usuario con este email"

        if username is None:
            errors["username"] = "El username es requerido"
        elif User.objects.filter(username=username).exists():
            errors["username"] = "Ya existe un usuario con este nombre de usuario"

        if password is None or password_confirm is None:
            errors["password"] = "Las contraseñas son requeridas"
        elif password != password_confirm:
            errors["password"] = "Las contraseñas no coinciden"

        return errors


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    scheduled_at = models.DateTimeField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_events")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @classmethod
    def validate(cls, title, description, scheduled_at):
        errors = {}

        if title == "":
            errors["title"] = "Por favor ingrese un titulo"

        if description == "":
            errors["description"] = "Por favor ingrese una descripcion"

        return errors

    @classmethod
    def new(cls, title, description, scheduled_at, organizer):
        errors = Event.validate(title, description, scheduled_at)

        if len(errors.keys()) > 0:
            return False, errors

        Event.objects.create(
            title=title,
            description=description,
            scheduled_at=scheduled_at,
            organizer=organizer,
        )

        return True, None

    def update(self, title, description, scheduled_at, organizer):
        self.title = title or self.title
        self.description = description or self.description
        self.scheduled_at = scheduled_at or self.scheduled_at
        self.organizer = organizer or self.organizer

        self.save()


# === MODELOS DE COMMENTS ===
class Comment(models.Model):
    title = models.CharField(max_length=30) 
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    #Relaciona el comentario con un usuario
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    
    #Relaciona el comentario con un evento
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="comments")

    #Para visualizar el contenido de un comentario
    def __str__(self):
        return f"Comentario de {self.user.username} sobre {self.event.title}"


    

class Notification(models.Model):
    
    PRIORITY_HIGH = 'HIGH'
    PRIORITY_MEDIUM = 'MEDIUM'
    PRIORITY_LOW = 'LOW'

    PRIORITY_CHOICES = [
        (PRIORITY_HIGH, 'Alta'),
        (PRIORITY_MEDIUM, 'Media'),
        (PRIORITY_LOW, 'Baja'),
    ]
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    is_read = models.BooleanField(default=False)

    event = models.ForeignKey("Event", on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.title
class RefundRequest(models.Model):
    ticket_code = models.CharField(max_length=100)
    reason = models.TextField()
    approved = models.BooleanField(default=False)
    approval_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Solicitud de devolución para el ticket {self.ticket_code} por {self.user.username}"