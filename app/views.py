from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import CustomUserCreationForm
from .models import Event


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = CustomUserCreationForm()
    return render(request, "app/register.html", {"form": form})


@login_required
def dashboard(request):
    events = Event.objects.all().order_by("date")
    return render(request, "app/dashboard.html", {"events": events})


@login_required
def event_detail(request, event_id):
    event = Event.objects.get(id=event_id)
    return render(request, "app/event_detail.html", {"event": event})
