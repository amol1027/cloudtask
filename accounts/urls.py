from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(next_page='landing:index'), name='logout'),
    
    # Staff Management
    path('add-manager/', views.AddManagerView.as_view(), name='add_manager'),
    path('add-employee/', views.AddEmployeeView.as_view(), name='add_employee'),
]
