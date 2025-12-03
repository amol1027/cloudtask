from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='list'),
    path('<int:pk>/read/', views.mark_as_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('unread-count/', views.get_unread_count, name='unread_count'),
    path('recent/', views.get_recent_notifications, name='recent'),
    path('activity/', views.ActivityLogView.as_view(), name='activity_log'),
]
