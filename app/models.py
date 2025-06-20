from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg


# === MODELOS PARA USERs ===
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


# === MODELOS PARA EVENTs ===
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    scheduled_at = models.DateTimeField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_events")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=255, default="Por definir")

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

    def promedio_rating(self):
        return self.organized_ratings.aggregate(promedio=Avg('rating'))['promedio'] or 0 # type: ignore
    
    def update_with_notification(self, title, description, scheduled_at, location):
        # Obtener valores originales desde la base de datos
        original = Event.objects.get(pk=self.pk)

        fecha_cambiada = original.scheduled_at.replace(second=0, microsecond=0) != scheduled_at.replace(second=0, microsecond=0)
        lugar_cambiado = original.location != location

        # Actualizar los campos
        self.title = title or self.title
        self.description = description or self.description
        self.scheduled_at = scheduled_at or self.scheduled_at
        self.location = location or self.location
        self.save()

        if (fecha_cambiada or lugar_cambiado) and Ticket.objects.filter(evento=self).exists():
            Notification.objects.create(
                title=f"Actualización del evento: {self.title}",
                message=f"El evento fue actualizado. "
                        f"{'La fecha ha cambiado. ' if fecha_cambiada else ''}"
                        f"{'El lugar ha cambiado. ' if lugar_cambiado else ''}"
                        f"Fecha: {self.scheduled_at.strftime('%d/%m/%Y %H:%M')}, "
                        f"Lugar: {self.location}",
                priority=Notification.PRIORITY_HIGH,
                user=None,  # Notificación global
                event=self
            )


# === MODELOS PARA COMMENTs ===
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


# === MODELOS PARA NOTIFICATIONs ===
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


# === MODELOS PARA REFUNDREQUESTs ===
class RefundRequest(models.Model):
    STATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]
    ticket_code = models.CharField(max_length=100)
    reason = models.TextField()
    approved = models.BooleanField(default=False)
    approval_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendiente')

    def __str__(self):
        return f"Solicitud de devolución para el ticket {self.ticket_code} por {self.user.username}"


# === MODELOS PARA TICKETs ===
class TicketType(models.TextChoices):
        GENERAL = 'general', 'General'
        VIP = 'VIP', 'VIP'

class Ticket(models.Model):
    # variables buy_date: date, ticket_code: string, quantity: integer, type : "general"| "VIP"
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_tickets")
    evento = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="organized_tickets")
    ticket_code = models.AutoField(primary_key=True)
    quantity = models.PositiveIntegerField()
    buy_date = models.DateTimeField()
    type = models.CharField(max_length=10, choices=TicketType.choices, default=TicketType.GENERAL)

    def __str__(self):
        texto = "{0} ({1})"
        return texto.format(self.ticket_code, self.buy_date)
    
    def save(self, *args, **kwargs):
        if self.quantity > 4:
            raise ValidationError("No se puede comprar más de 4 tickets.")
        super().save(*args, **kwargs)


# === MODELOS PARA RATINGs ===
class Rating(models.Model):
    # title: string, text: string, rating: integer, created_at: datetime
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_ratings")
    evento = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="organized_ratings")
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=30)
    text = models.CharField (max_length=250)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)  

