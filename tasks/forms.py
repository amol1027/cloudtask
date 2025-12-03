from django import forms
from django.contrib.auth.models import User
from .models import Task, TaskComment


class TaskForm(forms.ModelForm):
    """Form for creating and editing tasks"""
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'project', 'assigned_to', 'status', 'priority', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Task title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 4,
                'placeholder': 'Task description'
            }),
            'project': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'type': 'date'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        
        if user:
            from projects.models import Project
            # Filter projects based on user role
            if user.profile.role == 'MANAGER':
                # Manager sees only their managed projects
                self.fields['project'].queryset = Project.objects.filter(manager=user)
            elif user.profile.role == 'ENTERPRISE':
                # Enterprise sees all projects in their organization
                self.fields['project'].queryset = Project.objects.filter(
                    organization=user.profile.organization
                )
            
            # Filter assignees to project team members + manager
            if project:
                team_member_ids = list(project.members.values_list('user_id', flat=True))
                if project.manager:
                    team_member_ids.append(project.manager.id)
                self.fields['assigned_to'].queryset = User.objects.filter(id__in=team_member_ids)
            else:
                # Show all employees in the organization
                from accounts.models import UserProfile
                employee_profiles = UserProfile.objects.filter(
                    organization=user.profile.organization,
                    role='EMPLOYEE'
                )
                employee_ids = [p.user.id for p in employee_profiles]
                self.fields['assigned_to'].queryset = User.objects.filter(id__in=employee_ids)
        
        self.fields['assigned_to'].required = False
        self.fields['assigned_to'].empty_label = "-- Unassigned --"
        
        # Pre-select project if provided
        if project:
            self.fields['project'].initial = project
            self.fields['project'].widget = forms.HiddenInput()


class TaskCommentForm(forms.ModelForm):
    """Form for adding comments/progress updates to tasks"""
    
    class Meta:
        model = TaskComment
        fields = ['comment', 'status_changed_to']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 3,
                'placeholder': 'Add a comment or progress update...'
            }),
            'status_changed_to': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status_changed_to'].required = False
        self.fields['status_changed_to'].empty_label = "-- No status change --"
        # Add empty choice at the beginning
        self.fields['status_changed_to'].choices = [('', '-- No status change --')] + list(Task.STATUS_CHOICES)


class TaskStatusUpdateForm(forms.Form):
    """Simple form for updating task status"""
    status = forms.ChoiceField(
        choices=Task.STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
        })
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
            'rows': 2,
            'placeholder': 'Optional: Add a note about this update...'
        })
    )
