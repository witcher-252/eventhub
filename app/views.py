import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Comment, Event, User


def register(request):
    if request.method == "POST":
        email = request.POST.get("email")
        username = request.POST.get("username")
        is_organizer = request.POST.get("is-organizer") is not None
        password = request.POST.get("password")
        password_confirm = request.POST.get("password-confirm")

        errors = User.validate_new_user(email, username, password, password_confirm)

        if len(errors) > 0:
            return render(
                request,
                "accounts/register.html",
                {
                    "errors": errors,
                    "data": request.POST,
                },
            )
        else:
            user = User.objects.create_user(
                email=email, username=username, password=password, is_organizer=is_organizer
            )
            login(request, user)
            return redirect("events")

    return render(request, "accounts/register.html", {})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(
                request, "accounts/login.html", {"error": "Usuario o contraseña incorrectos"}
            )

        login(request, user)
        return redirect("events")

    return render(request, "accounts/login.html")


def home(request):
    return render(request, "home.html")


@login_required
def events(request):
    events = Event.objects.all().order_by("scheduled_at")
    return render(
        request,
        "app/events.html",
        {"events": events, "user_is_organizer": request.user.is_organizer},
    )


@login_required
def event_detail(request, id):
    event = get_object_or_404(Event, pk=id)
    return render(request, "app/event_detail.html", {"event": event})


@login_required
def event_delete(request, id):
    user = request.user
    if not user.is_organizer:
        return redirect("events")

    if request.method == "POST":
        event = get_object_or_404(Event, pk=id)
        event.delete()
        return redirect("events")

    return redirect("events")


@login_required
def event_form(request, id=None):
    user = request.user

    if not user.is_organizer:
        return redirect("events")

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        date = request.POST.get("date")
        time = request.POST.get("time")

        [year, month, day] = date.split("-")
        [hour, minutes] = time.split(":")

        scheduled_at = timezone.make_aware(
            datetime.datetime(int(year), int(month), int(day), int(hour), int(minutes))
        )

        if id is None:
            Event.new(title, description, scheduled_at, request.user)
        else:
            event = get_object_or_404(Event, pk=id)
            event.update(title, description, scheduled_at, request.user)

        return redirect("events")

    event = {}
    if id is not None:
        event = get_object_or_404(Event, pk=id)

    return render(
        request,
        "app/event_form.html",
        {"event": event, "user_is_organizer": request.user.is_organizer},
    )

# ---- Comments view ----

@login_required
def comment(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    comments = Comment.objects.filter(event=event).order_by("-created_at")
    
    paginator = Paginator(comments, 20)
    page_number = request.GET.get("page")
    comments_page = paginator.get_page(page_number)
    
    return render(request, "comments.html", {
        "event": event,
        "comments": comments_page
    })


def registrar_comentario(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        text = request.POST.get('text')
        event_id = request.POST.get('event_id')

        if not event_id:
            # Manejar el error si el event_id no se proporciona
            return HttpResponseBadRequest("No se ha proporcionado el ID del evento.")

        event = get_object_or_404(Event, id=event_id)

        Comment.objects.create(
            title=title,
            text=text,
            user=request.user,
            event=event
        )

        return redirect("comments", event_id=event.id) # type: ignore
    return HttpResponseBadRequest("Método no permitido.")


def delete_comment(request, event_id, id):
    comment = get_object_or_404(Comment, id=id)
    
    # Verificar si el comentario pertenece al usuario logueado
    if comment.user != request.user:
        return HttpResponseForbidden("No tienes permiso para eliminar este comentario")
    
    # Eliminar el comentario
    comment.delete()

    # Redirigir al evento después de eliminar el comentario
    messages.success(request, "Comentario eliminado con éxito.")
    return redirect('comments', event_id=event_id)


@login_required
def edit_comment(request, id):
    comment = get_object_or_404(Comment, id=id)

    if comment.user != request.user:
        return HttpResponseForbidden("No tenés permiso para editar este comentario.")

    if request.method == "POST":
        comment.title = request.POST.get('title')
        comment.text = request.POST.get('text')
        comment.save()
        return redirect("comments", event_id=comment.event.id) # type: ignore

    return render(request, "edit_comment.html", {"comment": comment})
