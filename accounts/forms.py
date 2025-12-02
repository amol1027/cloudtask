from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile

class StaffAuthenticationForm(AuthenticationForm):
    """Custom authentication form that allows login with staff_id or username and validates role"""
    login_type = forms.CharField(required=False, widget=forms.HiddenInput())
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        login_type = self.cleaned_data.get('login_type', 'enterprise')
        
        if username and password:
            # Try to find user by staff_id first
            try:
                profile = UserProfile.objects.get(staff_id=username)
                self.cleaned_data['username'] = profile.user.username
            except UserProfile.DoesNotExist:
                # If not found by staff_id, use username as is
                pass
        
        # Call parent clean to authenticate
        cleaned_data = super().clean()
        
        # Validate role matches login type
        if self.user_cache:
            try:
                user_role = self.user_cache.profile.role
                
                # Map login types to expected roles
                role_mapping = {
                    'enterprise': 'ENTERPRISE',
                    'manager': 'MANAGER',
                    'employee': 'EMPLOYEE'
                }
                
                expected_role = role_mapping.get(login_type, 'ENTERPRISE')
                
                if user_role != expected_role:
                    role_names = {
                        'ENTERPRISE': 'Enterprise',
                        'MANAGER': 'Manager',
                        'EMPLOYEE': 'Employee'
                    }
                    raise forms.ValidationError(
                        f'Invalid login. This account is registered as {role_names[user_role]}. '
                        f'Please use the {role_names[user_role]} login tab.'
                    )
            except UserProfile.DoesNotExist:
                raise forms.ValidationError('User profile not found.')
        
        return cleaned_data

class BaseStaffCreationForm(UserCreationForm):
    """Base form for creating staff (Manager/Employee)"""
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    department = forms.CharField(required=True)
    staff_id = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Create profile
            UserProfile.objects.create(
                user=user,
                role=self.role,
                department=self.cleaned_data['department'],
                staff_id=self.cleaned_data['staff_id']
            )
        return user

class ManagerCreationForm(BaseStaffCreationForm):
    role = 'MANAGER'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['staff_id'].label = "Manager ID"

class EmployeeCreationForm(BaseStaffCreationForm):
    role = 'EMPLOYEE'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['staff_id'].label = "Employee ID"
