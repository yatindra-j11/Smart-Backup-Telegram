from django.urls import path
from . import views

urlpatterns = [
    path('api/backup/', views.create_backup, name='create_backup'),
    path('api/backup/status/<str:task_id>/', views.backup_status, name='backup_status'),
    path('api/backups/', views.list_backups, name='list_backups'),
    path('api/restore/<int:backup_id>/', views.restore_backup, name='restore_backup'),
    path('api/backups/<int:backup_id>/', views.delete_backup, name='delete_backup'),
    path('api/config/', views.get_config, name='get_config'),
    path('api/config/save/', views.save_config, name='save_config'),
    path('api/config/test/', views.test_connection, name='test_connection'),
    path('api/watcher/open-folder/', views.open_watch_folder, name='open_watch_folder'),
]
