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
    # url rating-----------------------
    path("rating/", views.inicio_rating, name="inicio_rating"),
    # url formulario
    path("rating/crearRating", views.formulario_rating, name="formulario_rating"),
    path('rating/editarRating', views.editarRating, name="editarRating"),
    path('rating/eliminarRating/<id>', views.eliminarRating, name="eliminarRating"),
    path('rating/edicionRating/<id>', views.edicionRating, name="edicionRating")
]
