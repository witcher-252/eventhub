import datetime
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Event, User, Ticket


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

# codigo de ticket - inicio

@login_required
def gestion_ticket(request):
    usuarioTk = request.user

    if not usuarioTk.is_organizer:
        listaTickets=Ticket.objects.filter(usuario=usuarioTk)
    else:
        listaTickets = Ticket.objects.all()
    return render(request, "ticket/gestionTicket.html", 
                  {"listaTickets": listaTickets,"user_is_organizer": request.user.is_organizer})

@login_required
def create_ticket(request):
    usuario = request.user
    tipo = request.POST['tipoEntrada']
    cantidad = request.POST['cantidadTk']
    
    Ticket.objects.create( quantity=cantidad , buy_date=timezone.now(), type=tipo, usuario=usuario)
    return redirect("/tickets")

@login_required
def delete_ticket(request, id):
    tk = get_object_or_404(Ticket, ticket_code=id)
    tk.delete()
    return redirect("/tickets")

@login_required
def edit_ticket(request, id):
    tk = get_object_or_404(Ticket, ticket_code=id)
    return render(request, "ticket/edicionTicket.html",{"ticket":tk})

@login_required
def update_ticket(request):
    
    tipo = request.POST['tipoEntrada']
    cantidad = request.POST['cantidadTk']
    id = request.POST['ticketCode']
    tk = get_object_or_404(Ticket, ticket_code=id)
    tk.quantity = cantidad
    tk.type = tipo
    tk.save()
    return redirect("/tickets")
# codigo de ticket - fin