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
    path('refunds/create/', views.refund_create, name='refund_create'),
    path('refunds/', views.refund_list, name='refund_list'),
    path('refunds/<int:id>/edit/', views.refund_edit, name='refund_edit'),
    path('refunds/<int:id>/delete/', views.refund_delete, name='refund_delete'),
    path('refund/<int:id>/accept/', views.refund_accept, name='refund_accept'),
    path('refund/<int:id>/reject/', views.refund_reject, name='refund_reject'),
    path('refund/<int:id>/', views.refund_detail, name='refund_detail'),

]
