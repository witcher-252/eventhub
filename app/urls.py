
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
    path('rating/edicionRating/<id>', views.edicionRating, name="edicionRating"),
    #url comments
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
    # urls de ticket
    path('tickets/gestion/<idEvento>', views.gestion_ticket, name='gestion_ticket'),
    path('tickets/crearTicket', views.create_ticket, name='create_ticket'),
    path('tickets/editar/<id>', views.edit_ticket, name='edit_ticket'),
    path('tickets/eliminar/<id>', views.delete_ticket, name='delete_ticket'),
    path('tickets/entrada/<idEvento>', views.buy_ticket, name='buy_ticket'),
    path('tickets/confirmarEntrada', views.confirm_ticket, name='confirm_ticket'),
    path('tickets/update', views.update_ticket, name='update_ticket'),

]
    