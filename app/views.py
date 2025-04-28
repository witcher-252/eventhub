import datetime
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Event, User, RefundRequest
from .forms.refund_request_form import RefundRequestForm


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
    refund = get_object_or_404(RefundRequest, pk=id, user=request.user)
    return render(request, "refunds/refund_detail.html", {"refund": refund})


@login_required
def refund_detail(request, id):
    refund = get_object_or_404(RefundRequest, id=id)

    user_is_organizer = request.user.is_organizer

    if not user_is_organizer and refund.user != request.user:
        return redirect('refund_list')

    return render(request, "refunds/refund_detail.html", {"refund": refund})


