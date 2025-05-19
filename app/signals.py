# events/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Event, Notification

@receiver(pre_save, sender=Event)
def notify_event_change(sender, instance, **kwargs):
    # Si el evento no existía antes, no hacemos nada
    if not instance.pk:
        return
    
    try:
        old_event = Event.objects.get(pk=instance.pk)
    except Event.DoesNotExist:
        return
    
    # Comparamos si cambió la fecha o el lugar
    fecha_cambiada = old_event.scheduled_at != instance.scheduled_at
    lugar_cambiado = old_event.place != instance.place

    if fecha_cambiada or lugar_cambiado:
        cambios = []
        if fecha_cambiada:
            cambios.append(f"fecha de {old_event.scheduled_at} a {instance.scheduled_at}")
        if lugar_cambiado:
            cambios.append(f"lugar de '{old_event.place}' a '{instance.place}'")

        mensaje_cambios = " y ".join(cambios)

        Notification.objects.create(
            title="Cambio en evento",
            message=f"El evento '{instance.title}' ha cambiado: {mensaje_cambios}.",
            priority=Notification.PRIORITY_HIGH,
            user=None,  # Notificación general
            event=instance
        )
