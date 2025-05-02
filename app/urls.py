from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
     path("admin/", admin.site.urls),  # Añadir esta línea para que puedas acceder al admin
    path("", views.home, name="home"),
    path("accounts/register/", views.register, name="register"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    path("accounts/login/", views.login_view, name="login"),
    path("events/", views.events, name="events"),
    path("events/create/", views.event_form, name="event_form"),
    path("events/<int:id>/edit/", views.event_form, name="event_edit"),
    path("events/<int:id>/", views.event_detail, name="event_detail"),
    path("events/<int:id>/delete/", views.event_delete, name="event_delete"),
    path("comments/<int:event_id>/", views.comment, name="comments"),
    path('registrar_comentario/', views.registrar_comentario, name='registrar_comentario'),
    path('comments/<int:event_id>/deleteComment/<int:id>/', views.delete_comment, name='delete_comment'),
    path("comments/<int:event_id>/editComment/<int:comment_id>/", views.edit_comment, name="edit_comment"),
    path('notifications/', views.notification_redirect, name='notification_redirect'),
    path('notifications/organizador/', views.notification_list, name='notification_list'),
    path('notificaciones/usuario/', views.notification_list_user, name='notification_list_user'),
    path('notificaciones/marcar-leida/<int:pk>/', views.mark_as_read, name='mark_as_read'),
    path('notifications/create/', views.notification_create, name='notification_create'),
    path('notifications/detail/<int:pk>/', views.notification_detail, name='notification_detail'),
    path('notifications/edit/<int:pk>/', views.notification_edit, name='notification_edit'),
    path('notifications/delete/<int:pk>/', views.notification_delete, name='notification_delete'),
    path('refunds/create/', views.refund_create, name='refund_create'),
    path('refunds/', views.refund_list, name='refund_list'),
    path('refunds/<int:id>/edit/', views.refund_edit, name='refund_edit'),
    path('refunds/<int:id>/delete/', views.refund_delete, name='refund_delete'),
    path('refund/<int:id>/accept/', views.refund_accept, name='refund_accept'),
    path('refund/<int:id>/reject/', views.refund_reject, name='refund_reject'),
    path('refund/<int:id>/', views.refund_detail, name='refund_detail'),

]
