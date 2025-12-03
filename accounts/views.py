from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.urls import reverse_lazy

# Create your views here.

class RegisterView(CreateView):
    """User registration view for Enterprise admin with organization creation"""
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def get_form_class(self):
        from .forms import EnterpriseRegistrationForm
        return EnterpriseRegistrationForm
    
    def form_valid(self, form):
        # Save the user (this also creates Organization and UserProfile)
        response = super().form_valid(form)
        
        # Add success message
        messages.success(self.request, 'Account and organization created successfully! Please log in.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Register'
        return context


class LoginView(DjangoLoginView):
    """User login view"""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_form_class(self):
        from .forms import StaffAuthenticationForm
        return StaffAuthenticationForm
    
    def get_success_url(self):
        # Redirect to dashboard after login, or to next parameter if provided
        return self.get_redirect_url() or reverse_lazy('dashboard:index')
    
    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().username}!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Login'
        return context

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import ManagerCreationForm, EmployeeCreationForm

class BaseAddStaffView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Base view for adding staff"""
    template_name = 'accounts/add_staff.html'
    success_url = reverse_lazy('dashboard:team')
    
    def test_func(self):
        # Only Enterprise users can add staff
        return self.request.user.profile.role == 'ENTERPRISE'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass the organization to the form
        kwargs['organization'] = self.request.user.profile.organization
        return kwargs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'{self.staff_type} account created successfully!')
        return response


class AddManagerView(BaseAddStaffView):
    form_class = ManagerCreationForm
    staff_type = 'Manager'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Manager'
        context['staff_type'] = 'Manager'
        return context


class AddEmployeeView(BaseAddStaffView):
    form_class = EmployeeCreationForm
    staff_type = 'Employee'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Employee'
        context['staff_type'] = 'Employee'
        return context
