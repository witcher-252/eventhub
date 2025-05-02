import datetime
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Event, User, Rating
from .forms import RatingForm


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
    # creo formulario para rating - gerardo
    listaRating = Rating.objects.filter(evento=event)
    form = RatingForm(initial={'idEventoRating': event.pk})
    for r in listaRating:
        r.full_stars = range(r.rating)
        r.empty_stars = range(5 - r.rating)
    # fin 
    return render(request, "app/event_detail.html", {"event": event, "form": form,  "ratings": listaRating ,"user_is_organizer": request.user.is_organizer })

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
# codigo de Rating - inicio
@login_required
def inicio_rating(request):
    if request.user.is_organizer:
        return redirect('events')
    listaRating = Rating.objects.all()

    for r in listaRating:
        r.full_stars = range(r.rating)
        r.empty_stars = range(5 - r.rating)

    return render(request, "rating/inicioRating.html", {"listaRating": listaRating})

@login_required
def formulario_rating(request):
    usuario = request.user
    form = RatingForm(request.POST)
    if form.is_valid():
        # Accedés a los datos con form.cleaned_data
        idEvento = form.cleaned_data['idEventoRating']
        event = get_object_or_404(Event, pk=idEvento)
        titulo = form.cleaned_data['tituloR']
        descripcion = form.cleaned_data['descripcionR']
        rating = form.cleaned_data['califiqueR']
        # ... procesás, guardás, etc.
        Rating.objects.create( title=titulo , text=descripcion, rating=rating, usuario =usuario, evento=event)
        return redirect('event_detail', id=idEvento)
    else:
        idEvento = request.POST.get('idEventoRating')
        event = get_object_or_404(Event, pk=idEvento)
        listaRating = Rating.objects.filter(evento=event)
        for r in listaRating:
            r.full_stars = range(r.rating)
            r.empty_stars = range(5 - r.rating)
        return render(request, "app/event_detail.html", {"event": event, "form": form,  "ratings": listaRating })
                                                         
# aca meto mi magia
@login_required
def edicionRating(request, id):
    rating = Rating.objects.get(id=id)
    form = RatingForm(initial={'idEventoRating': rating.evento.pk,'tituloR': rating.title,
    'descripcionR': rating.text, 'califiqueR': rating.rating })
    rating.full_stars = range(rating.rating)
    rating.empty_stars = range(5 - rating.rating)
    return render(request, "rating/edicionRating.html", {"rating": rating, "form": form})

@login_required
def editarRating(request):
    usuario = request.user
    idRating = request.POST.get('idRating') 
    form = RatingForm(request.POST)
    if form.is_valid():
        # Accedés a los datos con form.cleaned_data
        r = get_object_or_404(Rating, id=idRating)
        titulo = form.cleaned_data['tituloR']
        descripcion = form.cleaned_data['descripcionR']
        rating = form.cleaned_data['califiqueR']
        r.title=titulo
        r.text=descripcion
        r.rating=rating 
        r.save()
        # ... procesás, guardás, etc.
        return redirect("/rating")
    else:
        r = get_object_or_404(Rating, id=idRating)
        return render(request, "rating/edicionRating.html", {"rating": r, "form": form})

@login_required
def eliminarRating(request, id):
    rating = Rating.objects.get(id=id)
    evento = rating.evento
    rating.delete()

   # messages.success(request, '¡Curso eliminado!')
    if request.user.is_organizer:
        return redirect('event_detail', id=evento.pk)
    else:
        return redirect("/rating")

#Codigo de Rating - Fin
