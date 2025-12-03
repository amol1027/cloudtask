from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.TaskListView.as_view(), name='list'),
    path('kanban/', views.kanban_board, name='kanban'),
    path('create/', views.TaskCreateView.as_view(), name='create'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.TaskUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.TaskDeleteView.as_view(), name='delete'),
    path('<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('<int:pk>/update-status/', views.update_status, name='update_status'),
    path('update-status-ajax/', views.update_task_status_ajax, name='update_status_ajax'),
    
    # File attachments
    path('<int:pk>/upload/', views.upload_attachment, name='upload_attachment'),
    path('<int:pk>/attachment/<int:attachment_id>/delete/', views.delete_attachment, name='delete_attachment'),
    
    # Task dependencies
    path('<int:pk>/dependency/add/', views.add_dependency, name='add_dependency'),
    path('<int:pk>/dependency/<int:dependency_id>/remove/', views.remove_dependency, name='remove_dependency'),
    
    # Time tracking
    path('<int:pk>/timer/start/', views.start_timer, name='start_timer'),
    path('<int:pk>/timer/stop/', views.stop_timer, name='stop_timer'),
    path('<int:pk>/time/add/', views.add_time_entry, name='add_time_entry'),
    path('timer/active/', views.get_active_timer, name='get_active_timer'),
    
    # Task templates
    path('templates/', views.TaskTemplateListView.as_view(), name='template_list'),
    path('templates/create/', views.TaskTemplateCreateView.as_view(), name='template_create'),
    path('templates/<int:pk>/delete/', views.TaskTemplateDeleteView.as_view(), name='template_delete'),
    path('templates/<int:template_id>/use/', views.create_task_from_template, name='create_from_template'),
]
