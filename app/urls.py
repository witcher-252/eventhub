from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("accounts/register/", views.register, name="register"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    path("accounts/login/", views.login_view, name="login"),
    path("events/", views.events, name="events"),
    path("events/create/", views.event_form, name="event_form"),
    path("events/<int:id>/edit/", views.event_form, name="event_edit"),
    path("events/<int:id>/", views.event_detail, name="event_detail"),
    path("events/<int:id>/delete/", views.event_delete, name="event_delete"),


    # urls de ticket
    path('tickets/gestion/<idEvento>', views.gestion_ticket, name='gestion_ticket'),
    path('tickets/crearTicket', views.create_ticket, name='create_ticket'),
    path('tickets/editar/<id>', views.edit_ticket, name='edit_ticket'),
    path('tickets/eliminar/<id>', views.delete_ticket, name='delete_ticket'),
    path('tickets/update', views.update_ticket, name='update_ticket'),
    path('tickets/entrada/<idEvento>', views.buy_ticket, name='buy_ticket'),
    path('tickets/confirmarEntrada', views.confirm_ticket, name='confirm_ticket'),
]
