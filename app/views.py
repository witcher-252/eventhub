import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.timezone import localtime
from .forms import CompraTicketForm, NotificationForm, RatingForm, RefundRequestForm, TicketForm
from .models import Comment, Event, Notification, Rating, RefundRequest, Ticket, User


# === CONTROLLERS PARA NOTIFICATIONS ===
@login_required
def notification_redirect(request):
    if request.user.is_organizer:
        return redirect('notification_list')
    else:
        return redirect('notification_list_user')

@login_required
def notification_list_user(request):
    notifications = Notification.objects.filter(
        Q(user=request.user) | Q(user__isnull=True)
    ).select_related('event')
    unread_count = notifications.filter(is_read=False).count()
    return render(request, 'notifications/list_user.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })

@login_required
def notification_list(request):
    notifications = Notification.objects.all().select_related('user', 'event')
    q = request.GET.get('q')
    event_id = request.GET.get('event')
    priority = request.GET.get('priority')

    if q:
        notifications = notifications.filter(title__icontains=q)
    if event_id:
        notifications = notifications.filter(event__id=event_id)
    if priority:
        notifications = notifications.filter(priority=priority)

    events = Event.objects.all()
    return render(request, 'notifications/list.html', {
        'notifications': notifications,
        'events': events
    })
    
@login_required
def mark_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk)

    if notification.user is None or notification.user == request.user:
        notification.is_read = True
        notification.save()

    return redirect('notification_list_user')

def notification_create(request):
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            notification = form.save(commit=False)
            if form.cleaned_data['destinatario_tipo'] == 'todos':
                notification.user = None
            notification.save()
            return redirect('notification_list')
    else:
        form = NotificationForm()
    return render(request, 'notifications/create.html', {'form': form})

def notification_detail(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    return render(request, 'notifications/detail.html', {'notification': notification})

def notification_edit(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    if request.method == 'POST':
        form = NotificationForm(request.POST, instance=notification)
        if form.is_valid():
            notification = form.save(commit=False)
            if form.cleaned_data['destinatario_tipo'] == 'todos':
                notification.user = None
            notification.save()
            return redirect('notification_list')
    else:
        form = NotificationForm(instance=notification)
    return render(request, 'notifications/edit.html', {'form': form, 'notification': notification})

def notification_delete(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    if request.method == 'POST':
        notification.delete()
        return redirect('notification_list')
    return render(request, 'notifications/delete.html', {'notification': notification})


# === CONTROLLERS PARA USERS ===
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
    if request.user.is_authenticated:
        return render(request, "home.html", {"user_is_organizer": request.user.is_organizer})
    else:
        return render(request, "home.html" )


# === CONTROLLERS PARA EVENTS ===
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
    listaRating = Rating.objects.filter(evento=event)
    form = RatingForm(initial={'idEventoRating': event.pk})
    for r in listaRating:
        r.full_stars = range(r.rating) # type: ignore
        r.empty_stars = range(5 - r.rating) # type: ignore
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


# === CONTROLLER PARA COMMENTS ===
@login_required
def comment(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    comments = Comment.objects.filter(event=event).order_by("-created_at")
    
    paginator = Paginator(comments, 20)
    page_number = request.GET.get("page")
    comments_page = paginator.get_page(page_number)
    
    return render(request, "comments/comments.html", {
        "event": event,
        "comments": comments_page
    })

@login_required
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

@login_required
def delete_comment(request, event_id, id):
    comment = get_object_or_404(Comment, id=id, event_id=event_id)

    # Un usuario común puede eliminar su comentario; un organizador puede eliminar cualquier comentario
    if not (request.user == comment.user or request.user.is_organizer):
        return HttpResponseForbidden("No tenés permiso para eliminar este comentario.")

    comment.delete()
    messages.success(request, "Comentario eliminado con éxito.")
    return redirect("comments", event_id=event_id)


@login_required
def edit_comment(request, event_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, event__id=event_id)

    # Solo el autor del comentario puede editarlo, siempre que NO sea organizador
    if request.user.is_organizer or request.user != comment.user:
        messages.error(request, "No tienes permiso para editar este comentario.")
        return redirect('comments/comments', event_id=event_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        text = request.POST.get('text')

        if title and text:
            comment.title = title
            comment.text = text
            comment.save()
            messages.success(request, "Comentario actualizado correctamente.")
        else:
            messages.error(request, "Ambos campos son obligatorios.")

        return redirect('comments', event_id=event_id)

    return redirect('comments', event_id=event_id)


# === CONTROLLERS PARA REFUNDREQUESTS ===
@login_required
def refund_create(request):
    if request.method == "POST":
        form = RefundRequestForm(request.POST)
        if form.is_valid():
            refund = form.save(commit=False)
            refund.user = request.user  # Asociar con el usuario logueado
            refund.save()
            return redirect("refund_list")
    else:
        form = RefundRequestForm()

    return render(request, "refunds/refund_form.html", {"form": form})

@login_required
def refund_list(request):
    user_is_organizer = request.user.is_organizer

    if user_is_organizer:
        refunds = RefundRequest.objects.all()
    else:
        refunds = RefundRequest.objects.filter(user=request.user)

    return render(request, "refunds/refund_list.html", {"refunds": refunds, "user_is_organizer": user_is_organizer})

@login_required
def refund_edit(request, id):
    refund = get_object_or_404(RefundRequest, pk=id, user=request.user)
    if request.method == 'POST':
        form = RefundRequestForm(request.POST, instance=refund)
        if form.is_valid():
            form.save()
            return redirect('refund_list')
    else:
        form = RefundRequestForm(instance=refund)
    return render(request, 'refunds/refund_edit.html', {'form': form})

@login_required
def refund_delete(request, id):
    if request.user.is_organizer:
        refund = get_object_or_404(RefundRequest, pk=id)
    else:
        refund = get_object_or_404(RefundRequest, pk=id, user=request.user)
    
    if request.method == "POST":
        refund.delete()
        return redirect("refund_list")
    return redirect("refund_list")

@login_required
def refund_accept(request, id):
    refund = get_object_or_404(RefundRequest, pk=id)

    # Solo el organizador puede aprobar las devoluciones
    if not request.user.is_organizer:
        return redirect("refund_list")

    refund.approved = True
    refund.approval_date = timezone.now()  # Asignar fecha de aprobación
    refund.save()

    return redirect("refund_list")

@login_required
def refund_reject(request, id):
    refund = get_object_or_404(RefundRequest, pk=id)

    # Solo el organizador puede rechazar devoluciones
    if not request.user.is_organizer:
        return redirect("refund_list")

    if request.method == "POST":
        refund.approved = False
        refund.approval_date = timezone.now()  # Registrar también la fecha del rechazo
        refund.save()

    return redirect("refund_list")

@login_required
def refund_detail(request, id):
    refund = get_object_or_404(RefundRequest, id=id)

    user_is_organizer = request.user.is_organizer

    if not user_is_organizer and refund.user != request.user:
        return redirect('refund_list')

    return render(request, "refunds/refund_detail.html", {"refund": refund})


# === CONTROLLERS PARA TICKETS ===
@login_required
def gestion_ticket(request, idEvento):
    usuarioTk = request.user
    listaTickets= None

    event = get_object_or_404(Event, pk=idEvento)
    if not usuarioTk.is_organizer:
        listaTickets=Ticket.objects.filter(usuario=usuarioTk)
    else:
        tiene_eventos = Event.objects.filter(organizer=usuarioTk, pk=idEvento).exists()
        if not tiene_eventos:
            return render(request, "ticket/gestionTicket.html", {"listaTickets": listaTickets,"user_is_organizer": request.user.is_organizer})
        eventosOrg = usuarioTk.organized_events.filter(pk=idEvento)
        listaTickets = Ticket.objects.filter(evento__in=eventosOrg)

    return render(request, "ticket/gestionTicket.html", 
                {"listaTickets": listaTickets,"user_is_organizer": request.user.is_organizer, "event": event})

@login_required
def create_ticket(request):
    usuario = request.user
    idEvento = request.POST['idEvento']
    event = get_object_or_404(Event, pk=idEvento)
    tipo = request.POST['tipoEntrada']
    cantidad = request.POST['cantidadTk']
    
    Ticket.objects.create( quantity=cantidad , buy_date=timezone.now(), type=tipo, usuario=usuario, evento = event)
    return redirect('gestion_ticket', idEvento= idEvento)

@login_required
def delete_ticket(request, id):
    tk = get_object_or_404(Ticket, ticket_code=id)
    evento = tk.evento
    tk.delete()
    return redirect('gestion_ticket', idEvento= evento.pk)

@login_required
def edit_ticket(request, id):
    tk = get_object_or_404(Ticket, ticket_code=id)
    form = TicketForm(initial={
    'ticketCode': tk.ticket_code,
    'buy_date': localtime(tk.buy_date).strftime('%Y-%m-%dT%H:%M'),
    'cantidadTk': tk.quantity,
    'tipoEntrada': tk.type,
    })
    return render(request, "ticket/edicionTicket.html",{ "form": form})

@login_required
def update_ticket(request):
    usuario = request.user
    form = TicketForm(request.POST)
    if form.is_valid():
            tipo = form.cleaned_data['tipoEntrada']
            cantidad = form.cleaned_data['cantidadTk']
            id = form.cleaned_data['ticketCode']
            tk = get_object_or_404(Ticket, ticket_code=id)
            event = tk.evento
            
            entradas_existentes = Ticket.objects.filter(
            usuario=usuario,
            evento=event).aggregate(total=Sum("quantity"))["total"] or 0

            entradas_existentes = entradas_existentes - tk.quantity

            if entradas_existentes + cantidad > 4:
                form.add_error('cantidadTk',f"Ya has comprado {entradas_existentes + tk.quantity} entradas para este evento. "
            f"Con esta compra ({cantidad - tk.quantity }) superarías el límite de 4 entradas.")
                return render(request, "ticket/edicionTicket.html",{ "form": form})
            tk.quantity = cantidad
            tk.type = tipo
            tk.save()
            return redirect('gestion_ticket', idEvento= tk.evento.pk)
    else:
            id = request.POST.get('ticketCode')
            tk = get_object_or_404(Ticket, ticket_code=id)
            form = TicketForm(initial={'ticketCode': tk.ticket_code,'buy_date': localtime(tk.buy_date).strftime('%Y-%m-%dT%H:%M'),
            'cantidadTk': tk.quantity,'tipoEntrada': tk.type})
            return render(request, "ticket/edicionTicket.html",{ "form": form})

@login_required
def buy_ticket(request, idEvento):
    event = get_object_or_404(Event, pk=idEvento)
    form = CompraTicketForm(initial={'id_evento': event.pk})
    return render(request, "ticket/entrada.html", {"user_is_organizer": request.user.is_organizer, "evento":event, "form": form})

@login_required
def confirm_ticket(request):
    usuario = request.user
    form = CompraTicketForm(request.POST)
    if form.is_valid():
        id_evento = form.cleaned_data['id_evento']
        event = get_object_or_404(Event, pk=id_evento)
        cantidad = form.cleaned_data['cantidad']
        tipo = form.cleaned_data['tipo']

         # Validación: no permitir más de 4 entradas por usuario por evento
        entradas_existentes = Ticket.objects.filter(
            usuario=usuario,
            evento=event
        ).aggregate(total=Sum("quantity"))["total"] or 0

        if entradas_existentes + cantidad > 4:
            form.add_error('cantidad',f"Ya has comprado {entradas_existentes} entradas para este evento. "
            f"Con esta compra ({cantidad}) superarías el límite de 4 entradas.")
            return render(request, "ticket/entrada.html", {
                "user_is_organizer": usuario.is_organizer,
                "evento": event,
                "form": form
            })
        
        Ticket.objects.create( quantity=cantidad , buy_date=timezone.now(), type=tipo, usuario=usuario, evento = event)
        return redirect('gestion_ticket', idEvento= id_evento)
    else:
        id_evento = request.POST.get('id_evento')
        event = get_object_or_404(Event, pk=id_evento)
        return render(request, "ticket/entrada.html", {"user_is_organizer": request.user.is_organizer, "evento":event, "form": form})


# === CONTROLLERS PARA RATINGS ===
@login_required
def inicio_rating(request):
    if request.user.is_organizer:
        return redirect('events')
    listaRating = Rating.objects.filter(usuario=request.user)

    for r in listaRating:
        r.full_stars = range(r.rating) # type: ignore
        r.empty_stars = range(5 - r.rating) # type: ignore

    return render(request, "rating/inicioRating.html", {"listaRating": listaRating})

@login_required
def formulario_rating(request):
    usuario = request.user
    form = RatingForm(request.POST)
    if form.is_valid():
        idEvento = form.cleaned_data['idEventoRating']
        event = get_object_or_404(Event, pk=idEvento)
        if Rating.objects.filter(usuario=usuario, evento=event).exists():
            form.add_error(None, "Ya has calificado este evento.")
        else:    
            titulo = form.cleaned_data['tituloR']
            descripcion = form.cleaned_data['descripcionR']
            rating = form.cleaned_data['califiqueR']
            Rating.objects.create( title=titulo , text=descripcion, rating=rating, usuario =usuario, evento=event)
            return redirect('event_detail', id=idEvento)
    else:
        idEvento = request.POST.get('idEventoRating')
        event = get_object_or_404(Event, pk=idEvento)

    listaRating = Rating.objects.filter(evento=event)
    for r in listaRating:
        r.full_stars = range(r.rating) # type: ignore
        r.empty_stars = range(5 - r.rating) # type: ignore
    return render(request, "app/event_detail.html", {"event": event, "form": form,  "ratings": listaRating })

@login_required
def edicionRating(request, id):
    rating = Rating.objects.get(id=id)
    form = RatingForm(initial={'idEventoRating': rating.evento.pk,'tituloR': rating.title,
    'descripcionR': rating.text, 'califiqueR': rating.rating })
    rating.full_stars = range(rating.rating) # type: ignore
    rating.empty_stars = range(5 - rating.rating) # type: ignore
    return render(request, "rating/edicionRating.html", {"rating": rating, "form": form})

@login_required
def editarRating(request):
    idRating = request.POST.get('idRating') 
    form = RatingForm(request.POST)
    if form.is_valid():
        r = get_object_or_404(Rating, id=idRating)
        titulo = form.cleaned_data['tituloR']
        descripcion = form.cleaned_data['descripcionR']
        rating = form.cleaned_data['califiqueR']
        r.title=titulo
        r.text=descripcion
        r.rating=rating 
        r.save()
        return redirect("/rating")
    else:
        r = get_object_or_404(Rating, id=idRating)
        return render(request, "rating/edicionRating.html", {"rating": r, "form": form})

@login_required
def eliminarRating(request, id):
    rating = Rating.objects.get(id=id)
    evento = rating.evento
    rating.delete()

    if request.user.is_organizer:
        return redirect('event_detail', id=evento.pk)
    else:
        return redirect("/rating")


