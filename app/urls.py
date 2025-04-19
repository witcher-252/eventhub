from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("accounts/register/", views.register, name="register"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    path("accounts/login/", views.login_view, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("event/<int:event_id>/", views.event_detail, name="event_detail"),
]
