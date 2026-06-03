from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/server_health/', views.server_health, name='server_health'),
    path('dashboard/admins/', views.manage_admins, name='manage_admins'),
]
