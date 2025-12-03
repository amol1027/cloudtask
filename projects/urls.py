from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='list'),
    path('create/', views.ProjectCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='delete'),
    path('<int:pk>/add-member/', views.add_project_member, name='add_member'),
    path('<int:pk>/remove-member/<int:member_id>/', views.remove_project_member, name='remove_member'),
    path('<int:pk>/comment/', views.add_project_comment, name='add_comment'),
]
