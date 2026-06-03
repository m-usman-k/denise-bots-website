from django.urls import path
from . import views

urlpatterns = [
    path('', views.bot_list, name='bot_list'),
    path('set_guild/', views.set_guild, name='set_guild'),
    path('manage/', views.manage_bot, name='manage_bot'),
    
    # File Manager APIs
    path('api/fs/list/', views.api_fs_list, name='api_fs_list'),
    path('api/fs/read/', views.api_fs_read, name='api_fs_read'),
    path('api/fs/write/', views.api_fs_write, name='api_fs_write'),
    
    path('logs/<str:pm2_name>/', views.bot_logs, name='bot_logs'),
    path('<str:bot_name>/editor/', views.bot_editor, name='bot_editor'),
    path('<str:bot_name>/', views.bot_detail, name='bot_detail'),
]
