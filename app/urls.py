from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
]
