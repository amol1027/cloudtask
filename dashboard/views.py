from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

@login_required
def index(request):
    """Dashboard index view - routes based on user role"""
    user = request.user
    user_role = user.profile.role
    organization = user.profile.organization
    
    # Import models
    from projects.models import Project
    from tasks.models import Task
    from accounts.models import UserProfile
    from notifications.models import ActivityLog
    
    context = {}
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    
    if user_role == 'ENTERPRISE':
        # Enterprise admin dashboard
        if organization:
            # Project stats
            all_projects = Project.objects.filter(organization=organization)
            context['project_count'] = all_projects.count()
            context['projects_this_week'] = all_projects.filter(created_at__gte=week_ago).count()
            context['projects'] = all_projects.order_by('-created_at')[:5]
            
            # Task stats
            all_tasks = Task.objects.filter(project__organization=organization)
            context['task_count'] = all_tasks.count()
            context['active_task_count'] = all_tasks.filter(status__in=['TODO', 'IN_PROGRESS', 'IN_REVIEW']).count()
            context['todo_count'] = all_tasks.filter(status='TODO').count()
            context['in_progress_count'] = all_tasks.filter(status='IN_PROGRESS').count()
            context['in_review_count'] = all_tasks.filter(status='IN_REVIEW').count()
            context['done_count'] = all_tasks.filter(status='DONE').count()
            context['tasks_completed_this_week'] = all_tasks.filter(status='DONE', updated_at__gte=week_ago).count()
            
            # Team stats
            context['manager_count'] = UserProfile.objects.filter(organization=organization, role='MANAGER').count()
            context['employee_count'] = UserProfile.objects.filter(organization=organization, role='EMPLOYEE').count()
            context['team_count'] = context['manager_count'] + context['employee_count']
            
            # Calculate efficiency (completed tasks / total tasks this week)
            tasks_this_week = all_tasks.filter(created_at__gte=week_ago).count()
            if tasks_this_week > 0:
                context['efficiency'] = round((context['tasks_completed_this_week'] / tasks_this_week) * 100)
            else:
                context['efficiency'] = 100 if context['done_count'] > 0 else 0
            
            # Recent activity
            context['recent_activities'] = ActivityLog.objects.filter(
                organization_id=organization.id
            ).select_related('user').order_by('-created_at')[:10]
            
            # Recent tasks
            context['recent_tasks'] = all_tasks.order_by('-updated_at')[:5]
            
            # Overdue tasks
            context['overdue_count'] = all_tasks.filter(
                due_date__lt=now.date(),
                status__in=['TODO', 'IN_PROGRESS', 'IN_REVIEW']
            ).count()
            
        return render(request, 'dashboard/index.html', context)
    
    elif user_role == 'MANAGER':
        # Manager dashboard
        context['projects'] = Project.objects.filter(manager=user)[:5]
        context['project_count'] = Project.objects.filter(manager=user).count()
        context['tasks'] = Task.objects.filter(project__manager=user)
        context['task_count'] = context['tasks'].count()
        context['todo_count'] = context['tasks'].filter(status='TODO').count()
        context['in_progress_count'] = context['tasks'].filter(status='IN_PROGRESS').count()
        context['done_count'] = context['tasks'].filter(status='DONE').count()
        context['recent_tasks'] = context['tasks'].order_by('-updated_at')[:5]
        
        # Team members count (employees in their projects)
        if organization:
            context['team_count'] = UserProfile.objects.filter(organization=organization, role='EMPLOYEE').count()
        
        return render(request, 'dashboard/manager_dashboard.html', context)
    
    else:  # EMPLOYEE
        # Employee dashboard
        context['assigned_tasks'] = Task.objects.filter(assigned_to=user)
        context['task_count'] = context['assigned_tasks'].count()
        context['todo_count'] = context['assigned_tasks'].filter(status='TODO').count()
        context['in_progress_count'] = context['assigned_tasks'].filter(status='IN_PROGRESS').count()
        context['done_count'] = context['assigned_tasks'].filter(status='DONE').count()
        
        # Projects the employee is part of
        from projects.models import ProjectMember
        context['projects'] = Project.objects.filter(members__user=user).distinct()
        context['project_count'] = context['projects'].count()
        
        return render(request, 'dashboard/employee_dashboard.html', context)


@login_required
def team(request):
    """Team view showing all managers and employees"""
    from accounts.models import UserProfile
    
    user = request.user
    organization = user.profile.organization
    
    if not organization:
        staff_members = UserProfile.objects.none()
    else:
        # Get all staff members in the same organization
        staff_members = UserProfile.objects.filter(
            organization=organization,
            role__in=['MANAGER', 'EMPLOYEE']
        ).select_related('user').order_by('role', 'user__username')
    
    # Calculate counts
    manager_count = staff_members.filter(role='MANAGER').count()
    employee_count = staff_members.filter(role='EMPLOYEE').count()
    
    context = {
        'staff_members': staff_members,
        'manager_count': manager_count,
        'employee_count': employee_count,
        'is_enterprise': user.profile.role == 'ENTERPRISE',
    }
    return render(request, 'dashboard/team.html', context)
