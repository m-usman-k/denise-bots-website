from django.urls import path
from . import views

urlpatterns = [
    path('', views.bot_list, name='bot_list'),
    path('<str:bot_name>/', views.bot_detail, name='bot_detail'),
]
