from django import forms
from django.contrib.auth.models import User
from .models import Organization, Project, ProjectMember


class ProjectForm(forms.ModelForm):
    """Form for creating and editing projects"""
    
    class Meta:
        model = Project
        fields = ['name', 'description', 'manager', 'status', 'start_date', 'end_date']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary focus:border-secondary',
                'placeholder': 'Project name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary focus:border-secondary',
                'rows': 4,
                'placeholder': 'Project description'
            }),
            'manager': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary focus:border-secondary'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary focus:border-secondary'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary focus:border-secondary',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary focus:border-secondary',
                'type': 'date'
            }),
        }

    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        
        # Filter managers to only show those in the same organization
        if organization:
            from accounts.models import UserProfile
            manager_profiles = UserProfile.objects.filter(
                organization=organization,
                role='MANAGER'
            ).select_related('user')
            manager_ids = [p.user.id for p in manager_profiles]
            self.fields['manager'].queryset = User.objects.filter(id__in=manager_ids)
        
        self.fields['manager'].required = False
        self.fields['manager'].empty_label = "-- Select Manager (optional) --"


class ProjectMemberForm(forms.ModelForm):
    """Form for adding team members to a project"""
    
    class Meta:
        model = ProjectMember
        fields = ['user', 'role']
        widgets = {
            'user': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary focus:border-secondary'
            }),
            'role': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary focus:border-secondary'
            }),
        }

    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        
        # Filter users to only show employees in the same organization
        # Exclude users already in the project
        if organization:
            from accounts.models import UserProfile
            employee_profiles = UserProfile.objects.filter(
                organization=organization,
                role='EMPLOYEE'
            ).select_related('user')
            employee_ids = [p.user.id for p in employee_profiles]
            
            # Exclude existing members
            if project:
                existing_member_ids = project.members.values_list('user_id', flat=True)
                employee_ids = [id for id in employee_ids if id not in existing_member_ids]
            
            self.fields['user'].queryset = User.objects.filter(id__in=employee_ids)
        
        self.fields['user'].empty_label = "-- Select Employee --"
